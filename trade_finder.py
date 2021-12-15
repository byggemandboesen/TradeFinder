import pandas as pd

class TradeFinder:
    def __init__(self, DataStreamer, TechnicalAnalyzer):
        self.DataStreamer = DataStreamer
        self.all_coins = [coin for coin in self.DataStreamer.get_symbols() if "USDT" in coin] # ["ETHUSDT", "BTCUSDT", "BNBUSDT", "SOLUSDT", "ADAUSDT"]
        self.TechnicalAnalyzer = TechnicalAnalyzer
        self.VOL_THREASHOLD = 4
        
    def check_vol(self):
        # Empty dataframe that contains all coins with a volume greater than 3X the volume moving average
        columns = ["Coins", "Percent volume increase", "Percent price increase"]
        df = pd.DataFrame()
        for coin in self.all_coins:
            try:
                candles = self.DataStreamer.getKlines(coin, 21, "3m")
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
