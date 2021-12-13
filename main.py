# Discord imports
import discord
from discord.ext import commands, tasks

#Misc imports
from datetime import datetime
import os

# File imports
from indicators import TA
TechnicalAnalyzer = TA()
from chart import Charter
from stream import Streamer
DataStreamer = Streamer()
from alert_logger import Logger
AlertLogger = Logger()


#-------------------------------------- Bot initiation and loop --------------------------------------#


# Sets the command prefix for calling the bot
bot = commands.Bot(command_prefix = ".")

@bot.event
async def on_ready():
    print("Bot is ready to scrape coins!!")
    scrape_market.start()

@tasks.loop(seconds = 10)
async def scrape_market():
    symbols = list(AlertLogger.get_symbols())
    df = DataStreamer.getKlines(symbols)
    print(f"{datetime.utcnow()} - Scraping market...")

@scrape_market.before_loop
async def set_status():
    await bot.change_presence(activity = discord.Activity(type = discord.ActivityType.watching, name = "candlesticks"))
    await bot.wait_until_ready() 


#--------------------------------------------- Commands ----------------------------------------------#


# Add an alert for a symbol pair when certain price is crossed
@bot.command(name = "alert", description = "Add an alert for a symbol pair")
async def alert(ctx, symbol='', type='', price=''):
    symbol = symbol.upper()
    # Get user ID
    uid = ctx.message.author.id
    
    if '' in (symbol, type, price):
        await ctx.send("Please remember to specify symbol, type(up/down) and price")
    else:
        AlertLogger.add_alert(uid, symbol, type, price)
        await ctx.send(f"<@{uid}> set an alert for {symbol}!")


# Remove alert
@bot.command(name = "rmalert")
async def rmalert(ctx, symbol='', type='', price=''):
    symbol = symbol.upper()
    uid = ctx.message.author.id
    AlertLogger.rm_alert(uid, symbol, type, price)
    await ctx.send(f"Alert for {symbol} deleted!")


# Chart symbol pair last 24H
@bot.command(name = "chart", description = "Plot a currency pair 24H back")
async def chart(ctx, symbol=''):
    symbol = symbol.upper()    
    if symbol == '':
        await ctx.send("Oooops, you forgot a symbol pair (BTCUSDT, ETHBTC ...):wink:")
    elif not DataStreamer.check_symbol(symbol):
        await ctx.send("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    else:
        candles = DataStreamer.getKlines(symbol, 288)
        chart = Charter(symbol, candles)
        chart_path = chart.create_chart()

        # Send chart in given path and delete after done
        with open(chart_path, 'rb') as image:
            img = discord.File(image)
            await ctx.send(file = img)

        os.remove(chart_path)


# Get the value of a certain indicator from at certain symbol pair
@bot.command(name = "indicator", description = "Get the latest value of a certain indicator on a certain timeframe")
async def indicator(ctx, symbol, indicator = '0', timeframe = '1h', window = '0'):
    available_indicators = TechnicalAnalyzer.available_indicators()
    symbol = symbol.upper()
    if indicator == '0':
        await ctx.send(f"Whooops, not too fast! You forgot an indicator, {available_indicators}:wink:")
    elif not DataStreamer.check_symbol(symbol):
        await ctx.send("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    elif not DataStreamer.check_timeframe(timeframe):
        await ctx.send("Whooops, that looks like an incorrect timeframe:alarm_clock: Please check your command!")
    elif window == '0' and indicator != 'bms':
        await ctx.send(f"Did you add an incorrect window for the indicator? For example rsi **14** or ema **21**.")
    else:
        candles = DataStreamer.getKlines(symbol, 100, timeframe)
        val = TechnicalAnalyzer.do_indicator(indicator, candles, window)
        await ctx.send(f"Indicator, \"{indicator}\", for symbol, {symbol}, is currently at:\n{val}\n- on {timeframe} timeframe.")



# Parse trendline information
# TODO Figure out a way to parse trendline information
# @bot.command(name = "parse", description = "Parse trendline information to add to an alert")
# async def parse(ctx, price1, bar1, price2, bar2, timeframe):
#     point1 = [price1, bar1]
#     point2 = [price2, bar2]
#     parsed_trendline = AlertLogger.parse_trendline(point1, point2, timeframe)
#     await ctx.send("Unfortunately this is still work in progress...")
#     # await ctx.send(f"Here's your parsed trendline ready to be added to an alert!: {parsed_trendline}")


# Run bot
bot.run("token")
