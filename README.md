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
This will require python version >=3.8.0.

**NOTE WHEN ADDING BOT TO SERVER** - Remember to give the bot permission to use commands and to be a bot when adding the bot to your server! <br>
https://discord.com/developers/applications/your-application-id/oauth2/url-generator <br>
And remember to add the bot token as well, in the bottom of the main file...

### Running on Raspberry pi
Some Raspberry pi devices may throw an error like, ```Importing the numpy c-extensions failed```. For this, run:
```bash
sudo apt-get install libatlas-base-dev
```
This is taken from this [GitHub issue](https://github.com/numpy/numpy/issues/15744).

## Customizing the bot

In ```config.json``` one can set the chat in which the bot should send alerts in. This includes different types of alerts: Volume breakouts and added price/volume alerts.
It is also in the config file that one can change the time interval in seconds that the bot scrapes the market/checks if alerts are triggered together with the required volume multiplier for a low timeframe volume breakout.
```json
{
    "parameters": {
        "scrape_interval": 15,
        "vol_breakout_threashold": 5
    },
    "ids": {
        "guild_id": 01234567890123456789,
        "alerts_channel": 09876543210987654321,
        "volume_breakout_channel": ""
    }
}
```
One should also add the guild id (server id) when using the bot. This will make slash-commands available immediately after the bot is run.<br>
**NOTE** that the ```"volume_breakout_channel"``` is left empty, or rather as "". This will disable high volume breakout scraping. If this is not desired, please insert the id of the channel you wish to receive alerts in.


## Features
This section will cover the available commands and how to use them. This will be updated as commands change and when commands are removed/added. <br>

### Price alert (/pricealert)
Do you want to know exactly when a certain trading pair, BTCUSDT, ADAUSDT, BTCETH and etc, cross a certain valuation price? If so, this command is for you.
#### Requirements
- Symbol (BTCUSDT etc)
- Type (up/down)
- Price (self-explanatory)

Example usage:
```
/pricealert symbol:btcusdt type:up price:50000 
```
This will generate the following alert in alerts.json:
```json
{
    "symbol": "BTCUSDT",
    "userid": 1234567890,
    "type": "up",
    "price": "50000",
    "timeframe": "",
    "vol_multiple": 0,
    "delete": true
}
```
With every alert the user id of the user who created the alert will be stored. This is used to ping the user when the alert is triggered and to check if someone has the permission to remove the alert (see command for removing alerts).<br>
Also note the keyword ```delete``` which by default is true and optional when adding an alert. If set to false then the alert will not be removed after being triggered. The alert can still be removed with the ````/removealert``` command.

### Volume alert (/volumealert)
Are you watching for a breakout for a certain coin? If so, this command might be for you.
#### Requirements
- Symbol
- Timeframe (1m, 5m, 15m, 4h, 1d...)
- Volume multiple (2, 3, 4, 10...)

This alert will compare the volume of the latest candle on the chosen timeframe to the 20 candle volume moving average. If the volume of the current candle is greater than ```Volume multiple * VMA``` then the alert will be triggered.

Example usage:
```
/volumealert symbol:btcusdt timeframe:15m volume_multiple:3 
```
This will create the following alert:
```json
{
    "symbol": "BTCUSDT",
    "userid": 328543383771414528,
    "type": "volume",
    "price": 0,
    "timeframe": "15m",
    "vol_multiple": "3"
}
```

### Get alerts (/getalerts)
Get all alerts created for certain symbol.
#### Requirements
- Symbol

Example usage:
```
/getalerts symbol:btcusdt 
```
This will send the following message from the two alerts created above:<br>
![/getalerts example output](https://github.com/byggemandboesen/TradeFinder/blob/main/Images/getalerts.jpg)

### Remove alert (/removealert)
Rather self explanatory, this alert is used to remove a certain alert. However, you can ***only*** delete alerts that you created!
#### Requirements
- Alert

Use the ```/getalerts``` command to get the alert you wish to remove and copy it into the message field.<br>

Example usage:
```
/removealert alert:{"symbol": "BTCUSDT", "userid": 1234567890, "type": "up", "price": "50000", "timeframe": "", "vol_multiple": 0}
```
The bot will then reply if the alert was removed succesfully.

### Chart (/chart)
This command creates a candle stick chart for a given symbol the previous 24H on 5m candles.
#### Requirements
- Symbol

Example usage:
```
/chart symbol:btcusdt
```
Which generates the following chart and sends it in the chat. <br>
![Chart from chart command](https://github.com/byggemandboesen/TradeFinder/blob/main/Images/chart.jpg)


*More commands coming soon*
