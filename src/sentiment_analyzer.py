import pandas as pd
import numpy as np
from textblob import TextBlob
import nltk
from nltk.sentiment import SentimentIntensityAnalyzer
from typing import Dict, List, Tuple
import re

# Download required NLTK data
try:
    nltk.data.find('vader_lexicon')
except LookupError:
    nltk.download('vader_lexicon')

class SentimentAnalyzer:
    def __init__(self):
        self.sia = SentimentIntensityAnalyzer()
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if pd.isna(text):
            return ""
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', str(text))
        # Convert to lowercase
        text = text.lower()
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text
    
    def analyze_sentiment_textblob(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using TextBlob"""
        cleaned_text = self.clean_text(text)
        blob = TextBlob(cleaned_text)
        
        return {
            'polarity': blob.sentiment.polarity,
            'subjectivity': blob.sentiment.subjectivity
        }
    
    def analyze_sentiment_vader(self, text: str) -> Dict[str, float]:
        """Analyze sentiment using VADER"""
        cleaned_text = self.clean_text(text)
        scores = self.sia.polarity_scores(cleaned_text)
        
        return {
            'vader_compound': scores['compound'],
            'vader_positive': scores['pos'],
            'vader_negative': scores['neg'],
            'vader_neutral': scores['neu']
        }
    
    def get_sentiment_label(self, score: float, method: str = 'textblob') -> str:
        """Convert sentiment score to label"""
        if method == 'textblob':
            if score > 0.1:
                return 'positive'
            elif score < -0.1:
                return 'negative'
            else:
                return 'neutral'
        else:  # vader
            if score >= 0.05:
                return 'positive'
            elif score <= -0.05:
                return 'negative'
            else:
                return 'neutral'
    
    def analyze_news_sentiment(self, news_df: pd.DataFrame, text_column: str = 'headline') -> pd.DataFrame:
        """Perform sentiment analysis on news dataframe"""
        df = news_df.copy()
        
        print("Performing sentiment analysis...")
        
        # TextBlob sentiment
        textblob_scores = df[text_column].apply(self.analyze_sentiment_textblob)
        df['polarity'] = textblob_scores.apply(lambda x: x['polarity'])
        df['subjectivity'] = textblob_scores.apply(lambda x: x['subjectivity'])
        df['sentiment_label'] = df['polarity'].apply(
            lambda x: self.get_sentiment_label(x, 'textblob')
        )
        
        # VADER sentiment
        vader_scores = df[text_column].apply(self.analyze_sentiment_vader)
        df['vader_compound'] = vader_scores.apply(lambda x: x['vader_compound'])
        df['vader_positive'] = vader_scores.apply(lambda x: x['vader_positive'])
        df['vader_negative'] = vader_scores.apply(lambda x: x['vader_negative'])
        df['vader_neutral'] = vader_scores.apply(lambda x: x['vader_neutral'])
        df['vader_sentiment_label'] = df['vader_compound'].apply(
            lambda x: self.get_sentiment_label(x, 'vader')
        )
        
        # Combined sentiment score (average of TextBlob and VADER)
        df['combined_sentiment'] = (df['polarity'] + df['vader_compound']) / 2
        df['final_sentiment_label'] = df['combined_sentiment'].apply(
            lambda x: self.get_sentiment_label(x, 'textblob')
        )
        
        print("Sentiment analysis completed!")
        return df
    
    def get_daily_sentiment_scores(self, news_df: pd.DataFrame) -> pd.DataFrame:
        """Aggregate sentiment scores by date"""
        daily_sentiment = news_df.groupby('date').agg({
            'combined_sentiment': ['mean', 'std', 'count'],
            'polarity': 'mean',
            'vader_compound': 'mean',
            'final_sentiment_label': lambda x: x.value_counts().index[0] if len(x) > 0 else 'neutral'
        }).reset_index()
        
        # Flatten column names
        daily_sentiment.columns = [
            'date', 'avg_sentiment', 'sentiment_std', 'article_count',
            'avg_polarity', 'avg_vader', 'dominant_sentiment'
        ]
        
        return daily_sentiment