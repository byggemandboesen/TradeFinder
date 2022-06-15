import json
import pandas as pd

from src.helper import Helper

class TradeFinder:
    def __init__(self, DataStreamer, TechnicalAnalyzer, vol_threashold, vol_timeframe):
        self.DataStreamer = DataStreamer
        self.all_coins = self.DataStreamer.get_symbols()
        self.TechnicalAnalyzer = TechnicalAnalyzer
        
        self.VOL_THREASHOLD = vol_threashold
        self.VOL_TIMEFRAME = vol_timeframe
        
    # Scrape market for high volume breakouts
    async def check_vol(self, PAIRS):
        # Empty dataframe that contains all coins with a volume greater than 3X the volume moving average
        columns = ["Coins", "Volume increase", "Open price", "Percent increase",]
        df = pd.DataFrame(columns = columns)
        pairs = self.all_coins if len(PAIRS) == 0 else PAIRS

        for coin in pairs:
            try:
                candles = self.DataStreamer.getKlines(coin, 21, self.VOL_TIMEFRAME)
                open, close = float(candles["Open"].iloc[-1]), float(candles["Close"].iloc[-1])
                
                percent_up = round((close - open) * 100 / open, 2)
                # If current price < candle open price or price increase != > 1% don't bother going further
                if open > close or percent_up < 1.0:
                    continue
                else:
                    vma = self.TechnicalAnalyzer.vma(candles, 20)
                    vol_multiple = round(candles["Volume"].iloc[-1]/ vma, 2)
                    temp_df = pd.DataFrame([[coin, f"{vol_multiple}X", open, percent_up]], columns = columns)
                    df = pd.concat([df, temp_df], ignore_index = True) if (vol_multiple> self.VOL_THREASHOLD) else df
            except Exception as e:
                print(f"Skipping coin due to exception: \"{e}\"")

        # Check for identical triggers:
        result = Helper.check_tfs(df)
        return None if len(result.index) == 0 else result

        # TODO Check for increasing volume
        

    # Check if any price alerts should be triggered
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
    def check_volume_alerts(self, symbols):
        triggered = []

        with open("alerts.json", "r") as log_file:
            file = json.load(log_file)

            for symbol in symbols:
                alerts = file[symbol]
                # Get volume alerts
                vol_alerts = [alert for alert in alerts if alert["type"] == "volume"]

                for alert in vol_alerts:
                    vol_multiple = float(alert["vol_multiple"])
                    candles = self.DataStreamer.getKlines(symbol, 20, alert["timeframe"])
                    vma = self.TechnicalAnalyzer.vma(candles, 20)
                    volume, open_price, close_price = candles["Volume"].iloc[-1], candles["Open"].iloc[-1], candles["Close"].iloc[-1]
                    
                    if (volume > vol_multiple * vma) and (close_price > open_price):
                        triggered.append(alert)
            
            log_file.close()
        return triggered