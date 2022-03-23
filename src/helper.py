import json, os
from datetime import datetime

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
            pairs = parsed_file["pairs"]

            return token, parameters, ids, pairs

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
    

    # Check if TFS has already been reported for any coins caught in current breakout
    # If coin TFS has already been logged then remove the coin from the dataframe
    def check_tfs(triggers):
        path = "tfs_log.json"
        trigger_time = str(datetime.utcnow().strftime("%a. %d-%b. %H:%M"))

        # Check if TFS log file already exists
        if os.path.isfile(path):
            with open(path, "r+") as log_file:
                file = json.load(log_file)
                
                # Iterrate over each row of dataframe to look for identical TFS triggers
                for index, row in triggers.iterrows():
                    symbol, candle_open = row["Coins"], row["Open price"]

                    # If symbol is not in log file, add it
                    if symbol not in list(file.keys()):
                        file[symbol] = {"Open price": candle_open, "Time": trigger_time}

                    # If TFS has already been alerted then delete from trigger dataframe
                    elif file[symbol]["Open price"] == candle_open and file[symbol]["Time"] != trigger_time:
                        triggers.drop(index, inplace=True)
                    
                    # If not, update with new signal
                    elif file[symbol]["Open price"] != candle_open:
                        file[symbol] = {"Open price": candle_open, "Time": trigger_time}
                    
                log_file.seek(0)
                json.dump(file, log_file, indent = 4)
                log_file.close()
        else:
            with open(path, "w") as log_file:
                data = {coin: {"Open price": open_price, "Time": trigger_time} for coin, open_price in zip(triggers["Coins"], triggers["Open price"])}
                json.dump(data, log_file, indent = 4)
                log_file.close()
        
        triggers.reset_index(drop=True, inplace=True)
        return triggers

        
    