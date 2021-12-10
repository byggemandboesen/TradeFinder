# Discord imports
import discord
from discord import message
from discord.ext import commands, tasks

#Misc imports
from datetime import datetime
import pandas as pd
import os

# File imports
from chart import Charter
from stream import Streamer
data_streamer = Streamer()
from alert_logger import Logger
alert_logger = Logger()


#-------------------------------------- Bot initiation and loop --------------------------------------#


# Sets the command prefix for calling the bot
bot = commands.Bot(command_prefix = ".")

@bot.event
async def on_ready():
    print("Bot is ready to scrape coins!!")
    scrape_market.start()

@tasks.loop(seconds = 10)
async def scrape_market():
    symbols = list(alert_logger.get_symbols())
    df = data_streamer.getKlines(symbols, 1)
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
        alert_logger.add_alert(uid, symbol, type, price)
        await ctx.send(f"<@{uid}> set an alert for {symbol}!")


# Remove alert
@bot.command(name = "rmalert")
async def rmalert(ctx, symbol='', type='', price=''):
    symbol = symbol.upper()
    uid = ctx.message.author.id
    alert_logger.rm_alert(uid, symbol, type, price)
    await ctx.send(f"Alert for {symbol} deleted!")


# Chart symbol pair last 24H
@bot.command(name = "chart", description = "Plot a currency pair 24H back")
async def chart(ctx, symbol=''):
    symbol = symbol.upper()    
    if symbol == '':
        await ctx.send("Oooops, you forgot a symbol pair (BTCUSDT, ETHBTC ...):wink:")
    elif not data_streamer.check_symbol(symbol):
        await ctx.send("That sucks.... I looked everywhere on Binance, but I can't find this symbol pair:cry:")
    else:
        candles = data_streamer.getKlines(symbol, 288)
        chart = Charter(symbol, candles)
        chart_path = chart.create_chart()

        # Send chart in given path and delete after done
        with open(chart_path, 'rb') as image:
            img = discord.File(image)
            await ctx.send(file = img)

        os.remove(chart_path)


# Run bot
bot.run("token")
