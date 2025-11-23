import pandas as pd
import numpy as np
import talib
from typing import Dict, List

class TechnicalIndicators:
    def __init__(self):
        pass
    
    def calculate_returns(self, df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
        """Calculate daily returns and cumulative returns"""
        df = df.copy()
        df['daily_return'] = df[price_column].pct_change()
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        return df
    
    def calculate_moving_averages(self, df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
        """Calculate various moving averages"""
        df = df.copy()
        
        # Simple Moving Averages
        df['sma_20'] = talib.SMA(df[price_column], timeperiod=20)
        df['sma_50'] = talib.SMA(df[price_column], timeperiod=50)
        df['sma_200'] = talib.SMA(df[price_column], timeperiod=200)
        
        # Exponential Moving Averages
        df['ema_12'] = talib.EMA(df[price_column], timeperiod=12)
        df['ema_26'] = talib.EMA(df[price_column], timeperiod=26)
        
        return df
    
    def calculate_rsi(self, df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
        """Calculate Relative Strength Index"""
        df = df.copy()
        df['rsi_14'] = talib.RSI(df[price_column], timeperiod=14)
        return df
    
    def calculate_macd(self, df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
        """Calculate MACD indicator"""
        df = df.copy()
        macd, macd_signal, macd_hist = talib.MACD(df[price_column])
        df['macd'] = macd
        df['macd_signal'] = macd_signal
        df['macd_hist'] = macd_hist
        return df
    
    def calculate_bollinger_bands(self, df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df = df.copy()
        upper, middle, lower = talib.BBANDS(df[price_column], timeperiod=20, nbdevup=2, nbdevdn=2)
        df['bb_upper'] = upper
        df['bb_middle'] = middle
        df['bb_lower'] = lower
        df['bb_width'] = (upper - lower) / middle  # Bollinger Band Width
        return df
    
    def calculate_volatility(self, df: pd.DataFrame, price_column: str = 'Close') -> pd.DataFrame:
        """Calculate volatility indicators"""
        df = df.copy()
        df['volatility_20'] = df[price_column].pct_change().rolling(window=20).std()
        df['atr_14'] = talib.ATR(df['High'], df['Low'], df[price_column], timeperiod=14)
        return df
    
    def calculate_all_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate all technical indicators"""
        df = self.calculate_returns(df)
        df = self.calculate_moving_averages(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_bollinger_bands(df)
        df = self.calculate_volatility(df)
        
        # Additional derived indicators
        df['price_vs_sma_20'] = (df['Close'] / df['sma_20'] - 1) * 100
        df['sma_20_vs_sma_50'] = (df['sma_20'] / df['sma_50'] - 1) * 100
        
        return df