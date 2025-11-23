import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple
import yfinance as yf
from datetime import datetime, timedelta

class DataLoader:
    def __init__(self, data_path: str = "data/raw"):
        self.data_path = data_path
        self.news_data = None
        self.stock_data = {}
    
    def load_news_data(self, file_path: str = "financial_news.csv") -> pd.DataFrame:
        """Load financial news data from CSV file"""
        try:
            self.news_data = pd.read_csv(os.path.join(self.data_path, file_path))
            # Convert date column to datetime
            if 'date' in self.news_data.columns:
                self.news_data['date'] = pd.to_datetime(self.news_data['date'])
            print(f"Loaded news data with {len(self.news_data)} articles")
            return self.news_data
        except Exception as e:
            print(f"Error loading news data: {e}")
            return pd.DataFrame()
    
    def load_stock_data(self, tickers: List[str], start_date: str = "2020-01-01", 
                       end_date: str = "2025-01-01") -> Dict[str, pd.DataFrame]:
        """Load stock data for given tickers"""
        for ticker in tickers:
            try:
                # Try to load from local CSV first
                csv_path = os.path.join(self.data_path, f"{ticker}.csv")
                if os.path.exists(csv_path):
                    stock_df = pd.read_csv(csv_path)
                    stock_df['Date'] = pd.to_datetime(stock_df['Date'])
                    stock_df.set_index('Date', inplace=True)
                else:
                    # Download from yfinance
                    stock_data = yf.download(ticker, start=start_date, end=end_date)
                    stock_df = stock_data.reset_index()
                    stock_df.rename(columns={'Date': 'date'}, inplace=True)
                
                self.stock_data[ticker] = stock_df
                print(f"Loaded data for {ticker}: {len(stock_df)} records")
                
            except Exception as e:
                print(f"Error loading data for {ticker}: {e}")
        
        return self.stock_data
    
    def get_available_tickers(self) -> List[str]:
        """Get list of available stock tickers from CSV files"""
        tickers = []
        for file in os.listdir(self.data_path):
            if file.endswith('.csv') and not file.startswith('financial_news'):
                ticker = file.replace('.csv', '')
                tickers.append(ticker)
        return tickers
    
    def merge_news_stock_data(self, ticker: str) -> pd.DataFrame:
        """Merge news sentiment with stock data for a specific ticker"""
        if self.news_data is None or ticker not in self.stock_data:
            return pd.DataFrame()
        
        # Filter news for specific ticker
        ticker_news = self.news_data[self.news_data['stock'] == ticker].copy()
        
        # Merge with stock data on date
        merged_data = pd.merge(
            ticker_news,
            self.stock_data[ticker].reset_index(),
            on='date',
            how='inner'
        )
        
        return merged_data