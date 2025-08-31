"""
Data processing and transformation utilities using Polars.
"""

import logging
from typing import Optional, Dict, Any, List, Tuple
import polars as pl
import numpy as np
from datetime import datetime, timedelta
import streamlit as st

from ..config.settings import get_env_config

logger = logging.getLogger(__name__)

class DataProcessor:
    """
    Handles data processing and transformation operations using Polars.
    """
    
    def __init__(self):
        """Initialize data processor."""
        self.env_config = get_env_config()
    
    def clean_delivery_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Clean and prepare delivery performance data.
        
        Args:
            df: Raw delivery data DataFrame
            
        Returns:
            Cleaned DataFrame
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            # Ensure date columns are properly typed
            date_columns = [col for col in df.columns if 'date' in col.lower()]
            for col in date_columns:
                if col in df.columns:
                    df = df.with_columns(pl.col(col).str.strptime(pl.Date, "%Y-%m-%d", strict=False))
            
            # Calculate delivery performance metrics
            if all(col in df.columns for col in ['order_delivered_customer_date', 'order_estimated_delivery_date']):
                df = df.with_columns([
                    # On-time delivery flag
                    (pl.col('order_delivered_customer_date') <= pl.col('order_estimated_delivery_date')).alias('is_on_time'),
                    
                    # Delivery delay in days
                    (pl.col('order_delivered_customer_date') - pl.col('order_estimated_delivery_date')).dt.total_days().alias('delay_days')
                ])
            
            # Remove null values in critical columns
            df = df.drop_nulls(subset=['order_id'])
            
            logger.info(f"Cleaned delivery data: {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning delivery data: {str(e)}")
            return df
    
    def calculate_kpi_trends(self, df: pl.DataFrame, date_col: str, metric_col: str, 
                           window_days: int = 7) -> pl.DataFrame:
        """
        Calculate moving averages and trends for KPI metrics.
        
        Args:
            df: DataFrame with time series data
            date_col: Name of date column
            metric_col: Name of metric column
            window_days: Window size for moving average
            
        Returns:
            DataFrame with trend calculations
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            # Sort by date
            df = df.sort(date_col)
            
            # Calculate moving averages and trends
            df = df.with_columns([
                # Moving average
                pl.col(metric_col).rolling_mean(window_size=window_days).alias(f'{metric_col}_ma'),
                
                # Percentage change from previous period
                pl.col(metric_col).pct_change().alias(f'{metric_col}_pct_change'),
                
                # Trend direction (1: up, 0: flat, -1: down)
                pl.when(pl.col(metric_col).pct_change() > 0.01)
                .then(1)
                .when(pl.col(metric_col).pct_change() < -0.01)
                .then(-1)
                .otherwise(0)
                .alias(f'{metric_col}_trend')
            ])
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating KPI trends: {str(e)}")
            return df
    
    def aggregate_geographic_data(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Aggregate data by geographic regions.
        
        Args:
            df: DataFrame with geographic data
            
        Returns:
            Aggregated DataFrame by geography
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            # Group by state and calculate aggregates
            if 'customer_state' in df.columns:
                agg_df = df.group_by('customer_state').agg([
                    pl.count('order_id').alias('order_count'),
                    pl.mean('price').alias('avg_order_value'),
                    pl.sum('price').alias('total_revenue'),
                    pl.mean('review_score').alias('avg_rating'),
                    pl.mean('is_on_time').alias('on_time_rate') if 'is_on_time' in df.columns else pl.lit(None).alias('on_time_rate')
                ])
                
                # Calculate percentiles for ranking
                agg_df = agg_df.with_columns([
                    pl.col('order_count').rank(descending=True).alias('order_rank'),
                    pl.col('avg_rating').rank(descending=True).alias('rating_rank'),
                    pl.col('on_time_rate').rank(descending=True).alias('delivery_rank')
                ])
                
                return agg_df.sort('order_count', descending=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error aggregating geographic data: {str(e)}")
            return df
    
    def analyze_product_categories(self, df: pl.DataFrame) -> pl.DataFrame:
        """
        Analyze product category performance.
        
        Args:
            df: DataFrame with product data
            
        Returns:
            Category analysis DataFrame
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            if 'product_category_name_english' in df.columns:
                category_analysis = df.group_by('product_category_name_english').agg([
                    pl.count('order_id').alias('order_count'),
                    pl.mean('price').alias('avg_price'),
                    pl.sum('price').alias('total_revenue'),
                    pl.mean('product_weight_g').alias('avg_weight'),
                    pl.mean('review_score').alias('avg_rating'),
                    pl.mean('is_on_time').alias('on_time_rate') if 'is_on_time' in df.columns else pl.lit(None).alias('on_time_rate')
                ])
                
                # Calculate revenue share
                total_revenue = category_analysis.select(pl.sum('total_revenue')).item()
                if total_revenue and total_revenue > 0:
                    category_analysis = category_analysis.with_columns(
                        (pl.col('total_revenue') / total_revenue * 100).alias('revenue_share_pct')
                    )
                
                return category_analysis.sort('total_revenue', descending=True)
            
            return df
            
        except Exception as e:
            logger.error(f"Error analyzing product categories: {str(e)}")
            return df
    
    def calculate_satisfaction_correlations(self, df: pl.DataFrame) -> Dict[str, float]:
        """
        Calculate correlations between satisfaction and other metrics.
        
        Args:
            df: DataFrame with satisfaction and performance data
            
        Returns:
            Dictionary of correlation coefficients
        """
        if df is None or df.is_empty():
            return {}
        
        try:
            correlations = {}
            
            if 'review_score' in df.columns:
                numeric_cols = ['price', 'freight_value', 'product_weight_g', 'delay_days']
                
                for col in numeric_cols:
                    if col in df.columns:
                        # Calculate correlation using numpy after converting to pandas
                        corr_df = df.select(['review_score', col]).drop_nulls()
                        if len(corr_df) > 10:  # Minimum sample size
                            corr_matrix = corr_df.to_pandas().corr()
                            correlations[col] = corr_matrix.loc['review_score', col]
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {str(e)}")
            return {}
    
    def prepare_time_series_data(self, df: pl.DataFrame, date_col: str, 
                                value_col: str, freq: str = 'D') -> pl.DataFrame:
        """
        Prepare time series data for visualization.
        
        Args:
            df: DataFrame with time series data
            date_col: Name of date column
            value_col: Name of value column
            freq: Frequency for aggregation ('D', 'W', 'M')
            
        Returns:
            Prepared time series DataFrame
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            # Ensure date column is properly typed
            df = df.with_columns(pl.col(date_col).cast(pl.Date))
            
            # Aggregate by frequency
            if freq == 'W':
                df = df.with_columns(pl.col(date_col).dt.week().alias('period'))
            elif freq == 'M':
                df = df.with_columns(pl.col(date_col).dt.month().alias('period'))
            else:  # Daily
                df = df.with_columns(pl.col(date_col).alias('period'))
            
            # Group and aggregate
            if freq != 'D':
                agg_df = df.group_by('period').agg([
                    pl.mean(value_col).alias(value_col),
                    pl.min(date_col).alias(date_col)
                ])
                return agg_df.sort('period')
            
            return df.sort(date_col)
            
        except Exception as e:
            logger.error(f"Error preparing time series data: {str(e)}")
            return df
    
    def create_performance_segments(self, df: pl.DataFrame, metric_col: str, 
                                  segments: int = 4) -> pl.DataFrame:
        """
        Create performance segments based on quantiles.
        
        Args:
            df: DataFrame with performance data
            metric_col: Column to segment on
            segments: Number of segments to create
            
        Returns:
            DataFrame with segment information
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            # Calculate quantiles
            quantiles = [i / segments for i in range(1, segments)]
            q_values = df.select(pl.col(metric_col).quantile(q) for q in quantiles)
            
            # Create segment conditions
            segment_conditions = []
            for i, q in enumerate(quantiles):
                if i == 0:
                    condition = pl.col(metric_col) <= q_values[0, 0]
                elif i == len(quantiles) - 1:
                    condition = pl.col(metric_col) > q_values[i-1, 0]
                else:
                    condition = (pl.col(metric_col) > q_values[i-1, 0]) & (pl.col(metric_col) <= q_values[i, 0])
                
                segment_conditions.append(condition)
            
            # Add segment column
            segment_expr = pl.when(segment_conditions[0]).then(f'Low')
            for i, condition in enumerate(segment_conditions[1:], 1):
                if i == len(segment_conditions) - 1:
                    segment_expr = segment_expr.when(condition).then(f'High')
                else:
                    segment_expr = segment_expr.when(condition).then(f'Medium-{i}')
            
            df = df.with_columns(segment_expr.otherwise('Unknown').alias(f'{metric_col}_segment'))
            
            return df
            
        except Exception as e:
            logger.error(f"Error creating performance segments: {str(e)}")
            return df
    
    def format_for_display(self, df: pl.DataFrame, round_decimals: int = 2) -> pl.DataFrame:
        """
        Format DataFrame for display in Streamlit.
        
        Args:
            df: DataFrame to format
            round_decimals: Number of decimal places for rounding
            
        Returns:
            Formatted DataFrame
        """
        if df is None or df.is_empty():
            return pl.DataFrame()
        
        try:
            # Round numeric columns
            numeric_cols = df.select(pl.col(pl.Float64, pl.Float32)).columns
            for col in numeric_cols:
                df = df.with_columns(pl.col(col).round(round_decimals))
            
            # Format percentage columns
            pct_cols = [col for col in df.columns if 'rate' in col.lower() or 'pct' in col.lower()]
            for col in pct_cols:
                if col in df.columns:
                    df = df.with_columns((pl.col(col)).alias(col))
            
            return df
            
        except Exception as e:
            logger.error(f"Error formatting DataFrame: {str(e)}")
            return df

# Global processor instance
@st.cache_resource
def get_data_processor() -> DataProcessor:
    """Get cached data processor instance."""
    return DataProcessor()
