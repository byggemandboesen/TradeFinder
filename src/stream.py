import ccxt, json, requests, math
import pandas as pd


# Stream OHLCV data
class Streamer:
    def __init__(self, rank):
        self.RANK_BY_MARKETCAP = rank
        self.exchange = ccxt.binance()
        print("Fetching available symbol pairs from exchange...")
        self.TICKERS = [ticker.replace("/","") for ticker in list(self.exchange.fetch_tickers())]
        print("Fetching available timeframes...")
        self.TIMEFRAMES = list(self.exchange.timeframes.keys())
    

    # Returns historic klines
    def getKlines(self, symbols, limit = 1, timeframe = '5m'):
        # Create dataframe with OHLCV data for each symbol pair
        try:
            if limit == 1:
                candles = [self.exchange.fetch_ohlcv(symbol, timeframe = timeframe, limit=limit)[0] for symbol in symbols]
            else:
                candles = self.exchange.fetch_ohlcv(symbols, timeframe = timeframe, limit=limit)
        except Exception as e:
            self.exchange = ccxt.binance()
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
    def checkSymbol(self, symbol):
        is_symbol = True if symbol in self.TICKERS else False
        return is_symbol
    
    
    # Check if timeframe is available
    def checkTimeframe(self, timeframe):
        is_timeframe = True if timeframe in self.TIMEFRAMES else False
        return is_timeframe

    
    # Returns all the tickers on exchange
    def getSymbols(self):
        if self.RANK_BY_MARKETCAP == 0:
            return self.TICKERS
        elif self.RANK_BY_MARKETCAP < 1 or self.RANK_BY_MARKETCAP > 1000:
            print("Desired rank range not within allowed range.\nPlease select a range from 1 to 1000.")
            quit()
        else:
            # Fetch list of top 500 cryptos by market cap using coingecko API
            # https://www.coingecko.com/en/api/documentation
            final_dict = []
            
            # Get top 1000 cryptos by market cap
            for i in range(1, int(math.ceil(self.RANK_BY_MARKETCAP / 250)) + 1):
                api = f"https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=250&page={i}&sparkline=false"
                response = requests.get(api)
                final_dict += json.loads(response.text)

            symbols = [coin["symbol"] for coin in final_dict]
            
            # Filter tickers by market cap rank
            filtered_tickers = [ticker for ticker in self.TICKERS if ticker[-4:] == "USDT" and ticker[:-4].lower() in symbols[:self.RANK_BY_MARKETCAP]]
            return filtered_tickers