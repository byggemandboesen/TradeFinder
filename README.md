# TradeFinder
A discord bot that gives you more time for everyday tasks without needing to stare at charts all the time...

### Features
1. Scrape the Binance exchange for high volume breakouts
2. Create alerts on coins and get alerted when the coin reaches the price target of the alert
3. Get a quick 24H chart of 5m candles for a symbol pair together with the trading volume
4. Show indicator value for symbol pair, eg. *BTCUSDT 1w ema 8* for 8-week EMA on weekly timeframe.

## Installing
As with many other programs written in python, the required packages can be retreived with pip:
```bash
pip install -r requirements.txt
```
You may need to install py-cord with the following command to allow the use of slash-commands:
```bash
pip install -U git+https://github.com/Pycord-Development/pycord
```

**NOTE WHEN ADDING BOT TO SERVER** - Remember to give the bot permission to use commands and to be a bot when adding the bot to your server! <br>
https://discord.com/developers/applications/your-application-id/oauth2/url-generator <br>
And remember to add the bot token as well, in the bottom of the main file...

## Customizing the bot
In ```config.json``` one can set the chat that the bot should send alerts in. This includes different types of alerts: Volume breakouts, added price alerts.
```json
{
    "guild_id": 01234567890123456789,
    "alerts_channel": 09876543210987654321,
    "volume_breakout_channel": ""
}
```
One should also add the guild id (server id) when using the bot. This will make slash-commands available immediately after the bot is run.<br>
**NOTE** that the ```"volume_breakout_channel"``` is left empty, or rather as "". This will disable high volume breakout scraping. If this is not desired, please insert the id of the channel you wish to receive alerts in.

*More documentation coming soon*