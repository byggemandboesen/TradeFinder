import ccxt
import pandas as pd

# Stream OHLCV data
class Streamer:
    def __init__(self):
        self.exchange = ccxt.binance()
        print("Fetching available symbol pairs from exchange...")
        self.TICKERS = [ticker.replace("/","") for ticker in list(self.exchange.fetch_tickers())]
        print("Fetching available timeframes...")
        self.TIMEFRAMES = list(self.exchange.timeframes.keys())
    

    # Returns historic klines
    def getKlines(self, symbols, limit = 1, timeframe = '5m'):
        # Create dataframe with OHLCV data for each symbol pair
        if limit == 1:
            candles = [self.exchange.fetch_ohlcv(symbol, timeframe = timeframe, limit=limit)[0] for symbol in symbols]
        else:
            candles = self.exchange.fetch_ohlcv(symbols, timeframe = timeframe, limit=limit)
        
        df = pd.DataFrame(candles, columns = ["Open time","Open","High","Low","Close","Volume"])
        # Convert unix to datetime
        df["Open time"] = pd.to_datetime(df["Open time"], unit = "ms")
        if limit == 1:
            # Add symbols
            df["Symbols"] = symbols
            df.set_index("Symbols", inplace=True, drop=True)
        
        return df


    # Check if symbol is available
    def check_symbol(self, symbol):
        is_symbol = True if symbol in self.TICKERS else False
        return is_symbol
    
    
    # Check if timeframe is available
    def check_timeframe(self, timeframe):
        is_timeframe = True if timeframe in self.TIMEFRAMES else False
        return is_timeframe

    
    # Returns all the tickers on exchange
    def get_symbols(self):
        return self.TICKERS