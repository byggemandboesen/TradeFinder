from ta import momentum, trend
import numpy as np
import pandas as pd

class TA:
    def __init__(self):
        self.indicators = {
            "RSI": self.rsi,
            "EMA": self.ema,
            "SMA": self.sma,
            "VMA": self.vma,
            "BMS": self.bms
        }

    def available_indicators(self):
        return list(self.indicators.keys())
    
    def rsi(self, candles, window):
        rsi = momentum.RSIIndicator(candles["Close"], window)
        return f"RSI = {round(rsi.rsi().iloc[-1], 2)}"

    def ema(self, candles, window):
        ema = trend.EMAIndicator(candles["Close"], window)
        return f"EMA = {round(ema.ema_indicator().iloc[-1], 2)}"

    def sma(self, candles, window):
        sma = trend.SMAIndicator(candles["Close"], window)
        return f"SMA = {round(sma.sma_indicator().iloc[-1], 2)}"

    def vma(self, candles, window):
        vma = candles["Volume"].rolling(window).mean()
        return round(vma.iloc[-1], 2)

    def bms(self, candles, window):
        sma20 = self.sma(candles, 20)
        ema21 = self.ema(candles, 21)
        return f"SMA20 = {sma20}\nEMA21 = {ema21})"

    def do_indicator(self, indicator, candles, window):
        indicator = indicator.upper()
        try:
            result = self.indicators[indicator](candles, int(window))
            return result
        except:
            return f"Did you type in the correct indicator: {list(self.indicators.keys())}?"