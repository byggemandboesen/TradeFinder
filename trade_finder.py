import pandas as pd

class TradeFinder:
    def __init__(self, DataStreamer, TechnicalAnalyzer):
        self.DataStreamer = DataStreamer
        self.all_coins = [coin for coin in self.DataStreamer.get_symbols() if "USD" in coin and not "USDC" in coin] # ["BTCUSDT", "ETHUSDT", "ADAUSDT", "BNBUSDT", "SOLUSDT"]
        self.TechnicalAnalyzer = TechnicalAnalyzer
        self.VOL_THREASHOLD = 3
        
    def check_vol(self):
        # Empty dataframe that contains all coins with a volume greater than 3X the volume moving average
        columns = ["Coins", "Volume", "Volume avg", "Percent"]
        df = pd.DataFrame()
        for coin in self.all_coins:
            try:
                candles = self.DataStreamer.getKlines(coin, 20)
                open, close = float(candles["Open"].iloc[-1]), float(candles["Close"].iloc[-1])
                # If current price is lower than candle open price don't bother going further
                
                if open > close:
                    continue
                else:
                    vma = self.TechnicalAnalyzer.vma(candles, 20)
                    percent_up = round((close - open) * 100 / open, 2)
                    temp_df = pd.DataFrame([[coin, candles["Volume"].iloc[-1], vma, percent_up]], columns = columns)
                    df = pd.concat([df, temp_df], ignore_index = True) if (float(temp_df["Volume"]) > self.VOL_THREASHOLD * float(temp_df["Volume avg"])) else df
            except Exception as e:
                print(f"Skipping coin due to exception: \"{e}\"")
        
        df = df if len(df.index) == 0 else df.set_index("Coins", inplace=True, drop=True)
        print(df)
        return df
