# Discord imports
import discord
from discord.ext import tasks

#Misc imports
from datetime import datetime
import json
import os

# File imports
from indicators import TA
TechnicalAnalyzer = TA()
from chart import Charter
from stream import Streamer
DataStreamer = Streamer()
from trade_finder import TradeFinder
TradeScraper = TradeFinder(DataStreamer, TechnicalAnalyzer)
from alert_logger import Logger
AlertLogger = Logger()


#-------------------------------------- Bot initiation and loop --------------------------------------#

bot = discord.Bot()

# Define channels
with open("config.json", "r") as file:
    parameters = json.load(file)
    guild_id = parameters["guild_id"]
    bot_updates_channel = parameters["bot_updates_channel"]
    alerts_channel = parameters["alerts_channel"]
    vol_breakout_alerts = None if parameters["volume_breakout_channel"] == "" else parameters["volume_breakout_channel"]

@bot.event
async def on_ready():
    print("Bot is ready to scrape coins!!")
    if not scrape_market.is_running():
        scrape_market.start()

@tasks.loop(seconds = 300)
async def scrape_market():
    update_channel = bot.get_channel(bot_updates_channel)
    # await update_channel.send(f"{datetime.utcnow()} - Busy scraping market!")
    print(f"{datetime.utcnow()} - Busy scraping market!")

    # Do market scrape if channel is supplied in parameters.json
    if vol_breakout_alerts is not None:
        # Check for high volume moves to the upside
        movers = TradeScraper.check_vol()
        if movers is None:
            print("No high volume breakouts!")
        else:
            channel = bot.get_channel(vol_breakout_alerts)
            await channel.send(f"Caught high volume breakouts!\n{movers.to_string()}")

    # Check if any alerts have been triggered
    symbols = AlertLogger.get_symbols()
    price_triggers = TradeScraper.check_price_alerts(symbols)
    vol_triggers = TradeScraper.check_volume_alerts(symbols)

    # Alert users that created their alerts
    alert_channel = bot.get_channel(alerts_channel)
    for alert in (price_triggers + vol_triggers):
        user = alert["userid"]
        symbol = alert["symbol"]
        price = alert["price"]
        type_alert = alert["type"]
        timeframe = alert["timeframe"]
        price_alert = f"<@{user}> Price alert triggered! {symbol} at price {price}. Type: \"{type_alert}\""
        volume_alert = f"<@{user}> Volume alert triggered! {symbol} above 2X volume on {timeframe} timeframe."
        msg =  volume_alert if type_alert == "volume" else price_alert
        await alert_channel.send(msg)

    # Remove alerts after being triggered
    [AlertLogger.rm_alert(alert["userid"], alert["symbol"], alert["type"], alert["price"]) for alert in (price_triggers + vol_triggers)]

    # update_channel = bot.get_channel(bot_updates_channel)
    # await update_channel.send(f"{datetime.utcnow()} - Done scraping!")
    print(f"{datetime.utcnow()} - Done scraping!")

@scrape_market.before_loop
async def set_status():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "candlesticks"))
    await bot.wait_until_ready()


#--------------------------------------------- Commands ----------------------------------------------#


# Add an alert for a symbol pair when certain price is crossed
@bot.slash_command(guild_ids = [guild_id], name = "alert", description = "Add an alert for a price movement or volume breakout on certain timeframe")
async def alert(ctx, symbol, type, price = 0, timeframe = '1h'):
    symbol = symbol.upper()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    elif type not in ("up", "down", "volume"):
        await ctx.respond("Please add a valid type for this alert: up, down, volume")
    else:
        # Get user ID
        uid = ctx.author.id
        AlertLogger.add_alert(uid, symbol, type, price, timeframe)
        await ctx.respond(f"Set an alert for {symbol}!")


# Remove alert
@bot.slash_command(guild_ids = [guild_id], name = "rmalert", description = "Remove an alert")
async def rmalert(ctx, symbol, type, price = 0, timeframe = '1h'):
    symbol = symbol.upper()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    elif type not in ("up", "down", "volume"):
        await ctx.respond("Please add a valid type for this alert: up, down, volume")
    else:
        uid = ctx.author.id
        try:
            AlertLogger.rm_alert(uid, symbol, type, price, timeframe)
            await ctx.respond(f"Alert for {symbol} deleted!")
        except:
            await ctx.respond("An error occured... Are you sure the alert exists?")


# Chart symbol pair last 24H
@bot.slash_command(guild_ids = [guild_id], name = "chart", description = "Plot a currency pair 24H back")
async def chart(ctx, symbol):
    symbol = symbol.upper()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    else:
        candles = DataStreamer.getKlines(symbol, 288)
        chart = Charter(symbol, candles)
        chart_path = chart.create_chart()

        # Send chart in given path and delete after done
        with open(chart_path, 'rb') as image:
            img = discord.File(image)
            await ctx.respond(file = img)

        os.remove(chart_path)


# Get the value of a certain indicator from at certain symbol pair
@bot.slash_command(guild_ids = [guild_id], name = "indicator", description = "Get the latest value of a certain indicator on a certain timeframe")
async def indicator(ctx, symbol, indicator, window='0', timeframe = '1h'):
    symbol = symbol.upper()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    elif not DataStreamer.check_timeframe(timeframe):
        await ctx.respond("Whooops, that looks like an incorrect timeframe:alarm_clock: Please check your command!")
    elif window == '0' and indicator != 'bms':
        await ctx.respond(f"Did you add an incorrect window for the indicator? For example rsi **14** or ema **21**.")
    else:
        candles = DataStreamer.getKlines(symbol, 100, timeframe)
        val = TechnicalAnalyzer.do_indicator(indicator, candles, window)
        await ctx.respond(f"Indicator, \"{indicator}\", for symbol, {symbol}, is currently at:\n{val}\n- on {timeframe} timeframe.")


# Parse trendline information
# TODO Figure out a way to parse trendline information
# @bot.slash_command(guild_ids = [guild_id], name = "parse", description = "Parse trendline information to add to an alert")
# async def parse(ctx, price1, bar1, price2, bar2, timeframe):
#     point1 = [price1, bar1]
#     point2 = [price2, bar2]
#     parsed_trendline = AlertLogger.parse_trendline(point1, point2, timeframe)
#     await ctx.send("Unfortunately this is still work in progress...")
#     # await ctx.send(f"Here's your parsed trendline ready to be added to an alert!: {parsed_trendline}")


# Run bot
bot.run("token")
