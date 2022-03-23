# Discord imports
from tkinter import Pack
import discord
from discord.ext import tasks

#Misc imports
from datetime import datetime
import json
import os

# File imports
from src.indicators import TA
from src.chart import Charter
from src.stream import Streamer
from src.trade_finder import TradeFinder
from src.alert_logger import Logger
from src.helper import Helper


#-------------------------------------- Bot initiation and loop --------------------------------------#

bot = discord.Bot()

# Read config
TOKEN, PARAMETERS, ids, PAIRS = Helper.read_config()
# Make pairs upper case
PAIRS = [pair.upper() for pair in PAIRS]
GUILD_ID = ids["guild_id"]

# Initate classes
TechnicalAnalyzer = TA()
DataStreamer = Streamer()
TradeScraper = TradeFinder(DataStreamer, TechnicalAnalyzer, PARAMETERS["vol_breakout_threashold"], PARAMETERS["vol_breakout_timeframe"])
AlertLogger = Logger()

@bot.event
async def on_ready():
    print("Bot is ready to scrape coins!!")
    if not scrape_market.is_running():
        scrape_market.start()

@tasks.loop(seconds = PARAMETERS["scrape_interval"])
async def scrape_market():
    print(f"{datetime.utcnow()} - Busy scraping market!")

    # Do market scrape if channel is supplied in config.json
    vol_breakout_alerts = None if ids["volume_breakout_channel"] == "" else ids["volume_breakout_channel"]
    if vol_breakout_alerts is not None:
        # Check for high volume moves to the upside
        tfs_triggers = TradeScraper.check_vol(PAIRS)
        if tfs_triggers is None:
            print("No high volume breakouts!")
        else:
            channel = bot.get_channel(vol_breakout_alerts)
            await channel.send(f"Caught high volume breakouts!\n{tfs_triggers.to_string()}")

    # Check if any alerts have been triggered
    if os.path.isfile("alerts.json"):
        symbols = AlertLogger.get_symbols()
        price_triggers = TradeScraper.check_price_alerts(symbols)
        vol_triggers = TradeScraper.check_volume_alerts(symbols)

        # Alert users that their alert(s) has/have been triggered
        alerts = price_triggers + vol_triggers
        channel = bot.get_channel(ids["alerts_channel"])
        await Helper.alert_user(channel, alerts)

        # Remove alerts after being triggered
        [AlertLogger.rm_alert(alert) for alert in alerts if alert["delete"] == "true"]
    print(f"{datetime.utcnow()} - Done scraping!")

@scrape_market.before_loop
async def set_status():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "candlesticks"))
    await bot.wait_until_ready()


#--------------------------------------------- Commands ----------------------------------------------#


# Add an alert for a symbol pair when certain price is crossed
@bot.slash_command(guild_ids = [GUILD_ID], name = "pricealert", description = "Add an alert for a symbol pair price movement")
async def price_alert(ctx, symbol, type, price, delete_when_triggered = "true"):
    symbol = symbol.upper()
    delete_when_triggered = delete_when_triggered.lower()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    elif type not in ("up", "down", "volume"):
        await ctx.respond("Please add a valid type for this alert: up, down, volume")
    elif delete_when_triggered not in ("true", "false"):
        await ctx.respond("Incorrect value for \"delete_when_triggered\". Should be either true or false...")
    else:
        # Get user ID
        uid = ctx.author.id
        AlertLogger.add_alert(uid, symbol, type, price, timeframe = '', volume_multiple = 0, delete = delete_when_triggered)
        await ctx.respond(f"Set an alert for {symbol}!")


# Add a volume breakout alert for certain symbol on chosen timeframe
@bot.slash_command(guild_ids = [GUILD_ID], name = "volumealert", description = "Add a volume breakout alert for a symbol pair on certain timeframe")
async def volume_alert(ctx, symbol, timeframe, volume_multiple, delete_when_triggered = "true"):
    symbol = symbol.upper()
    delete_when_triggered = delete_when_triggered.lower()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    elif not DataStreamer.check_timeframe(timeframe):
        await ctx.respond("Please add a valid timeframe...")
    elif delete_when_triggered not in ("true", "false"):
        await ctx.respond("Incorrect value for \"delete_when_triggered\". Should be either true or false...")
    else:
        # Get user ID
        uid = ctx.author.id
        AlertLogger.add_alert(uid, symbol, type = "volume", price = 0, timeframe = timeframe, volume_multiple = volume_multiple, delete = delete_when_triggered)
        await ctx.respond(f"Set an alert for {symbol}!")


# Remove alert
@bot.slash_command(guild_ids = [GUILD_ID], name = "removealert", description = "Remove an alert. Get available alerts with \"/getalerts\"")
async def removemalert(ctx, alert):
    uid = ctx.author.id
    alert = json.loads(alert)
    if uid == alert["userid"]:
        try:
            AlertLogger.rm_alert(alert)
            await ctx.respond(f"Alert deleted!")
        except:
            await ctx.respond("An error occured... Did you include the \"{ *alert* }\" (curley brackets) around the alert?")
    else:
        await ctx.respond("Unfortunately you do not have permission to remove this alert (not created by you) :lock:")


# Sends all active alerts for some symbol
@bot.slash_command(guild_ids = [GUILD_ID], name = "getalerts", description = "Get all current alerts for chosen symbol")
async def get_alerts(ctx, symbol):
    symbol = symbol.upper()
    if not symbol in AlertLogger.get_symbols():
        await ctx.respond("There are currently no alerts for this symbol pair. Will you be the first to add one?")
    else:
        alerts = AlertLogger.get_alerts(symbol)
        parsed_alerts = json.dumps(alerts, indent = 4)
        await ctx.respond(f"Active alerts for {symbol}:\n ```json\n{parsed_alerts}\n```\n Copy one of the following if you wish to remove an alert:", delete_after = 30)
        for alert in alerts:
            await ctx.send(f"`{json.dumps(alert)}`", delete_after = 60)


# Chart symbol pair last 24H
@bot.slash_command(guild_ids = [GUILD_ID], name = "chart", description = "Plot a currency pair 24H back")
async def chart(ctx, symbol):
    symbol = symbol.upper()
    if not DataStreamer.check_symbol(symbol):
        await ctx.respond("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    else:
        await ctx.respond(f"Drawing chart for {symbol}...", delete_after = 60)
        # 5m candles over a span of 24H: 24*60/5 = 288
        candles = DataStreamer.getKlines(symbol, 288)
        chart = Charter(symbol, candles)
        chart_path = chart.create_chart()

        # Send chart in given path and delete after done
        with open(chart_path, 'rb') as image:
            img = discord.File(image)
            await ctx.send(file = img, delete_after = 60)
            image.close()

        os.remove(chart_path)


# Get the value of a certain indicator from at certain symbol pair
@bot.slash_command(guild_ids = [GUILD_ID], name = "indicator", description = "Get the latest value of a certain indicator on a certain timeframe")
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


# Get latest TFS from certain coin
@bot.slash_command(guild_ids = [GUILD_ID], name = "tfs", describtion = "Get time of last TFS from symbol")
async def tfs(ctx, symbol):
    symbol = symbol.upper()
    path = "tfs_log.json"

    with open(path, "r") as log_file:
        file = json.load(log_file)

        # Check if a trigger is logged
        if symbol in list(file.keys()):
            latest_trigger = file[symbol]["Time"]
            await ctx.respond(f"Latest trigger for {symbol} was at: {latest_trigger}")
        else:
            await ctx.respond(f"No triggers has been logged for {symbol} yet!!")
        
        log_file.close()


# For clearing chat
@bot.slash_command(guild_ids = [GUILD_ID], name = "clear", describtion = "Clear the previous, \"n\", bot messages")
async def clear(ctx, amount = 10):
    # First check if user is moderator/admin and has permission to delete messages
    if ctx.author.guild_permissions.administrator:
        await ctx.respond(f"Deleting {amount} messages!")
        channel = bot.get_channel(ids["alerts_channel"])
        await channel.purge(limit = int(amount))
    else:
        await ctx.respond("Unfortunately you do not have permission to use this command :cry:")


# Run bot
bot.run(TOKEN)
