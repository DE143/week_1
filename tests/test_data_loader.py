import pytest
import pandas as pd
import os
from src.data_loader import DataLoader

class TestDataLoader:
    def test_initialization(self):
        loader = DataLoader()
        assert loader.data_path == "data/raw"
        assert loader.news_data is None
        assert loader.stock_data == {}
    
    def test_get_available_tickers(self, tmp_path):
        # Create temporary CSV files
        test_data_path = tmp_path / "data" / "raw"
        test_data_path.mkdir(parents=True)
        
        # Create test CSV files
        (test_data_path / "GOOGL.csv").write_text("date,Close\n2023-01-01,100")
        (test_data_path / "META.csv").write_text("date,Close\n2023-01-01,200")
        
        loader = DataLoader(str(test_data_path))
        tickers = loader.get_available_tickers()
        
        assert set(tickers) == {"GOOGL", "META"}