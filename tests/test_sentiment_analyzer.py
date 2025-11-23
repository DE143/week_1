import pytest
import pandas as pd
from src.sentiment_analyzer import SentimentAnalyzer

class TestSentimentAnalyzer:
    def setup_method(self):
        self.analyzer = SentimentAnalyzer()
    
    def test_clean_text(self):
        text = "Hello! This is a TEST with numbers 123."
        cleaned = self.analyzer.clean_text(text)
        assert cleaned == "hello this is a test with numbers"
    
    def test_analyze_sentiment_textblob(self):
        text = "This is great and amazing!"
        result = self.analyzer.analyze_sentiment_textblob(text)
        assert 'polarity' in result
        assert 'subjectivity' in result
        assert result['polarity'] > 0
    
    def test_get_sentiment_label(self):
        # Test positive sentiment
        assert self.analyzer.get_sentiment_label(0.5) == 'positive'
        # Test negative sentiment
        assert self.analyzer.get_sentiment_label(-0.5) == 'negative'
        # Test neutral sentiment
        assert self.analyzer.get_sentiment_label(0.05) == 'neutral'