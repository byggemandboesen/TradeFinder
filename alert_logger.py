import os, json

class Logger:
    def __init__(self):
        self.log_path = f"alerts.json"


    # Add alert
    def add_alert(self, uid, symbol, type, price):
        symbol = symbol.upper()
        parsed_alert = self.parse_alert(uid, type, price)

        # Check if log file already exists
        if os.path.isfile(self.log_path):
            with open(self.log_path, "r+") as log_file:
                file = json.load(log_file)
                
                #Check if symbol pair is already in the alert list
                try:
                    file[symbol].append(parsed_alert)
                except:
                    file.update({symbol: [parsed_alert]})
                    print("Symbol pair not added yet")
                
                log_file.seek(0)
                json.dump(file, log_file, indent = 4)
                log_file.close()
        else:
            with open(self.log_path, "w") as log_file:
                data = {symbol: [parsed_alert]}
                json.dump(data, log_file, indent = 4)
                log_file.close()
    

    # Remove alert
    def rm_alert(self, uid, symbol, type, price):
        alert_to_remove = self.parse_alert(uid, type, price)
        
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
    def parse_alert(self, uid, type, price):
        parsed_alert = {
            "userid": uid,
            "type": type,
            "price": price
        }
        return parsed_alert


    # Parse a trendline from Tradingview coordinates
    # TODO Needs work - See main.py
    # def parse_trendline(self, point1, point2, timeframe):
        
    #     # Calculate change in price pr. bar (pr. timeframe)
    #     slope = (point2[0] - point1[0]) / (point2[1] - point1[1])
    #     # Get change in price pr minute
    #     if "m" in timeframe:
    #         slope_min = slope / timeframe
    #     elif "h" in timeframe:
    #         slope_min = slope / (timeframe * 60)
    #     elif "d" in timeframe:
    #         slope_min = slope / (timeframe * 60 * 24)
    #     else:
    #         return "Check the given timeframe. Should be (m=min, h=hour, d=day)"

    #     parsed_trendline = f"{slope_min}X"

    #     print("Parsing trendline")

    # Returns all coins with an alert
    def get_symbols(self):
        with open(self.log_path) as log_file:
            file = json.load(log_file)
            symbols = file.keys()
            log_file.close()
        return symbols
