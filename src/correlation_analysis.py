import pandas as pd
import numpy as np
from scipy.stats import pearsonr, spearmanr
from sklearn.metrics import mutual_info_score
from typing import Dict, Tuple, List
import warnings
warnings.filterwarnings('ignore')

class CorrelationAnalysis:
    def __init__(self):
        pass
    
    def align_data(self, sentiment_df: pd.DataFrame, stock_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Align sentiment and stock data by date"""
        # Ensure both dataframes have date index
        sentiment_aligned = sentiment_df.set_index('date')
        stock_aligned = stock_df.set_index('date')
        
        # Align dates
        common_dates = sentiment_aligned.index.intersection(stock_aligned.index)
        sentiment_aligned = sentiment_aligned.loc[common_dates]
        stock_aligned = stock_aligned.loc[common_dates]
        
        return sentiment_aligned, stock_aligned
    
    def calculate_correlations(self, sentiment_series: pd.Series, stock_series: pd.Series) -> Dict[str, float]:
        """Calculate various correlation metrics"""
        # Remove NaN values
        valid_idx = ~(sentiment_series.isna() | stock_series.isna())
        sentiment_clean = sentiment_series[valid_idx]
        stock_clean = stock_series[valid_idx]
        
        if len(sentiment_clean) < 2:
            return {}
        
        # Pearson correlation
        pearson_corr, pearson_p = pearsonr(sentiment_clean, stock_clean)
        
        # Spearman correlation
        spearman_corr, spearman_p = spearmanr(sentiment_clean, stock_clean)
        
        # Lagged correlations
        correlations = {
            'pearson_correlation': pearson_corr,
            'pearson_p_value': pearson_p,
            'spearman_correlation': spearman_corr,
            'spearman_p_value': spearman_p,
            'sample_size': len(sentiment_clean)
        }
        
        # Calculate lagged correlations
        for lag in [1, 2, 3, 5]:
            if len(sentiment_clean) > lag:
                lagged_corr, _ = pearsonr(sentiment_clean[:-lag], stock_clean[lag:])
                correlations[f'pearson_lag_{lag}'] = lagged_corr
        
        return correlations
    
    def analyze_sentiment_impact(self, merged_data: pd.DataFrame) -> pd.DataFrame:
        """Analyze impact of sentiment on stock returns"""
        results = []
        
        # Group by sentiment and calculate average returns
        sentiment_groups = merged_data.groupby('final_sentiment_label')
        
        for sentiment, group in sentiment_groups:
            if len(group) > 0:
                avg_return = group['daily_return'].mean()
                std_return = group['daily_return'].std()
                count = len(group)
                
                results.append({
                    'sentiment': sentiment,
                    'avg_daily_return': avg_return,
                    'return_std': std_return,
                    'article_count': count,
                    'return_per_article': avg_return * count
                })
        
        return pd.DataFrame(results)
    
    def comprehensive_correlation_analysis(self, sentiment_df: pd.DataFrame, 
                                         stock_df: pd.DataFrame) -> Dict[str, Dict]:
        """Perform comprehensive correlation analysis"""
        
        sentiment_aligned, stock_aligned = self.align_data(sentiment_df, stock_df)
        
        analysis_results = {}
        
        # Sentiment vs Daily Returns
        returns_corr = self.calculate_correlations(
            sentiment_aligned['avg_sentiment'],
            stock_aligned['daily_return']
        )
        analysis_results['sentiment_vs_returns'] = returns_corr
        
        # Sentiment vs Volatility
        volatility_corr = self.calculate_correlations(
            sentiment_aligned['avg_sentiment'],
            stock_aligned['volatility_20']
        )
        analysis_results['sentiment_vs_volatility'] = volatility_corr
        
        # Sentiment vs Volume
        if 'Volume' in stock_aligned.columns:
            volume_corr = self.calculate_correlations(
                sentiment_aligned['avg_sentiment'],
                stock_aligned['Volume']
            )
            analysis_results['sentiment_vs_volume'] = volume_corr
        
        # Sentiment vs RSI
        if 'rsi_14' in stock_aligned.columns:
            rsi_corr = self.calculate_correlations(
                sentiment_aligned['avg_sentiment'],
                stock_aligned['rsi_14']
            )
            analysis_results['sentiment_vs_rsi'] = rsi_corr
        
        return analysis_results
    
    def generate_correlation_report(self, correlation_results: Dict) -> str:
        """Generate a readable correlation report"""
        report = "CORRELATION ANALYSIS REPORT\n"
        report += "=" * 50 + "\n\n"
        
        for analysis_type, results in correlation_results.items():
            report += f"{analysis_type.upper().replace('_', ' ')}:\n"
            report += "-" * 30 + "\n"
            
            for key, value in results.items():
                if 'p_value' in key:
                    significance = "***" if value < 0.001 else "**" if value < 0.01 else "*" if value < 0.05 else ""
                    report += f"{key}: {value:.4f} {significance}\n"
                elif 'correlation' in key:
                    report += f"{key}: {value:.4f}\n"
                else:
                    report += f"{key}: {value}\n"
            
            report += "\n"
        
        return report