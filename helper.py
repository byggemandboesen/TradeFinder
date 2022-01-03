import json

# Helper class will contain functions that the bot uses but are too large for it to make sense to keep it in main.py
class Helper():

    # Read config file
    def read_config():
        with open("config.json", "r") as file:
            parsed_file = json.load(file)

            # Get token, parameters and ids
            token = parsed_file["token"]
            parameters = parsed_file["parameters"]
            ids = parsed_file["ids"]

            return token, parameters, ids

    # Alert user if alert is triggered
    async def alert_user(channel, alerts):
        for alert in alerts:
            user = alert["userid"]
            symbol = alert["symbol"]
            price = alert["price"]
            type_alert = alert["type"]
            timeframe = alert["timeframe"]
            vol_multiple = alert["vol_multiple"]
            price_alert = f"<@{user}> Price alert triggered! {symbol} at price {price}. Type: \"{type_alert}\""
            volume_alert = f"<@{user}> Volume alert triggered! {symbol} volume {vol_multiple}X above average on {timeframe} timeframe."
            msg =  volume_alert if type_alert == "volume" else price_alert
            await channel.send(msg)