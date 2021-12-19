import json
from numpy import log
import pandas as pd

class TradeFinder:
    def __init__(self, DataStreamer, TechnicalAnalyzer):
        self.DataStreamer = DataStreamer
        self.all_coins = [coin for coin in self.DataStreamer.get_symbols() if "USDT" in coin[3:]] # ["ETHUSDT", "BTCUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
        self.TechnicalAnalyzer = TechnicalAnalyzer
        
        # TODO Add option to customize these threasholds
        self.VOL_THREASHOLD = 5
        self.VOL_ALERT_THREASHOLD = 2
        
    def check_vol(self):
        # Empty dataframe that contains all coins with a volume greater than 3X the volume moving average
        columns = ["Coins", "Percent volume increase", "Percent price increase"]
        df = pd.DataFrame(columns = columns)
        for coin in self.all_coins:
            try:
                candles = self.DataStreamer.getKlines(coin, 21, "1m")
                open, close = float(candles["Open"].iloc[-2]), float(candles["Close"].iloc[-2])
                
                # If current price is lower than candle open price don't bother going further
                if open > close:
                    continue
                else:
                    vma = self.TechnicalAnalyzer.vma(candles, 20)
                    percent_up = round((close - open) * 100 / open, 2)
                    vol_diff = round((candles["Volume"].iloc[-2] - vma) * 100 / vma, 2)
                    temp_df = pd.DataFrame([[coin, vol_diff, percent_up]], columns = columns)
                    df = pd.concat([df, temp_df], ignore_index = True) if (float(temp_df["Percent volume increase"]) > self.VOL_THREASHOLD * 100) else df
            except Exception as e:
                print(f"Skipping coin due to exception: \"{e}\"")
        
        df = df.set_index("Coins", inplace = False) if len(df.index) > 0 else None
        return df
    
    def check_price_alerts(self, symbols):
        triggered = []
        # Open the alerts file for all symbols
        with open("alerts.json", "r") as log_file:
            file = json.load(log_file)

            for symbol in symbols:
                # Get the alerts for the symbol
                alerts = file[symbol]
                up = [alert for alert in alerts if alert["type"] == "up"]
                down = [alert for alert in alerts if alert["type"] == "down"]

                # Get the price of symbol pair
                candle = self.DataStreamer.getKlines(symbol, 2)
                price = candle["Close"].iloc[-1]

                # Check which alerts are triggered
                triggered_up = [alert for alert in up if float(alert["price"]) < price]
                triggered_down = [alert for alert in down if float(alert["price"]) > price]

                triggered += triggered_down + triggered_up
            
            log_file.close()

        return triggered
    
    # Check for volume breakout alerts on their corresponding timeframe
    # TODO Maybe merge function with function above
    def check_volume_alerts(self, symbols):
        triggered = []

        with open("alerts.json", "r") as log_file:
            file = json.load(log_file)

            for symbol in symbols:
                alerts = file[symbol]
                # Get volume alerts
                vol_alerts = [alert for alert in alerts if alert["type"] == "volume"]

                for alert in vol_alerts:
                    candles = self.DataStreamer.getKlines(symbol, 20, alert["timeframe"])
                    vma = self.TechnicalAnalyzer.vma(candles, 20)
                    volume, open_price, close_price = candles["Volume"].iloc[-1], candles["Open"].iloc[-1], candles["Close"].iloc[-1]
                    
                    # TODO Check TODO In top of file
                    if (volume > self.VOL_ALERT_THREASHOLD * vma) and (close_price > open_price):
                        triggered.append(alert)
            
            log_file.close()
        return triggered