import os, json

class Logger:
    def __init__(self):
        self.log_path = f"alerts.json"


    # Add alert
    def add_alert(self, uid, symbol, type, price, timeframe, volume_multiple, delete):
        symbol = symbol.upper()
        parsed_alert = self.parse_alert(symbol, uid, type, price, timeframe, volume_multiple, delete)

        # Check if log file already exists
        if os.path.isfile(self.log_path):
            with open(self.log_path, "r+") as log_file:
                file = json.load(log_file)
                
                #Check if symbol pair is already in the alert list
                try:
                    file[symbol].append(parsed_alert)
                except:
                    file.update({symbol: [parsed_alert]})
                
                log_file.seek(0)
                json.dump(file, log_file, indent = 4)
                log_file.close()
        else:
            with open(self.log_path, "w") as log_file:
                data = {symbol: [parsed_alert]}
                json.dump(data, log_file, indent = 4)
                log_file.close()
    

    # Remove alert
    def rm_alert(self, alert_to_remove):
        # alert_to_remove = self.parse_alert(symbol, uid, type, price, timeframe)
        symbol = alert_to_remove["symbol"]
        
        with open(self.log_path, "r+") as log_file:
            file = json.load(log_file)
            
            # Filter alerts in symbol pair
            filtered = [alert for alert in file[symbol] if alert != alert_to_remove]
            
            # Remove symbol pair if no alerts are left, else overwrite with filtered alerts
            if len(filtered) == 0:
                del file[symbol]
            else:
                file[symbol] = filtered

            log_file.seek(0)
            json.dump(file, log_file, indent = 4)
            log_file.truncate()
            log_file.close()
            

    # Parse alert
    def parse_alert(self, symbol, uid, type, price, timeframe, volume_multiple, delete):
        parsed_alert = {
            "symbol": symbol,
            "userid": uid,
            "type": type,
            "price": price,
            "timeframe": timeframe,
            "vol_multiple": volume_multiple,
            "delete": delete
        }
        return parsed_alert


    # Return all alerts for certain symbol
    def get_alerts(self, symbol):
        with open(self.log_path, "r") as log_file:
            file = json.load(log_file)
            alerts = file[symbol]
            log_file.close()
        
        return alerts


    # Returns all coins with an alert
    def get_symbols(self):
        with open(self.log_path) as log_file:
            file = json.load(log_file)
            symbols = [*file]
            log_file.close()
        return symbols

    
