import ccxt
import pandas as pd

# Stream OHLCV data
class Streamer:
    def __init__(self):
        self.exchange = ccxt.binance()
        print("Fetching available symbol pairs from exchange...")
        self.TICKERS = [ticker.replace("/","") for ticker in list(self.exchange.fetch_tickers())]
    

    # Returns historic klines
    def getKlines(self, symbols, limit):
        # Create dataframe with OHLCV data for each symbol pair
        candles = [self.exchange.fetch_ohlcv(symbol, timeframe='5m', limit=limit)[0] for symbol in symbols]
        df = pd.DataFrame(candles, columns = ["Open time","Open","High","Low","Close","Volume"])
        
        # Convert unix to datetime
        df["Open time"] = pd.to_datetime(df["Open time"], unit = "ms")
        
        # Add symbols
        df["Symbols"] = symbols
        df.set_index("Symbols", inplace=True, drop=True)
        
        return df


    # Check if symbol is available
    def check_symbol(self, symbol):
        is_symbol = True if symbol in self.TICKERS else False
        return is_symbol