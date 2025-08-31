"""
Utility functions for data validation, formatting, and common operations.
"""

import polars as pl
import pandas as pd
import streamlit as st
from typing import Any, Dict, List, Optional, Union, Tuple
from datetime import datetime, timedelta
import re
import json

def validate_date_range(start_date: str, end_date: str) -> Tuple[bool, str]:
    """
    Validate date range inputs.
    
    Args:
        start_date: Start date string
        end_date: End date string
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        if start > end:
            return False, "Start date must be before end date"
        
        if end > datetime.now():
            return False, "End date cannot be in the future"
        
        # Check if date range is too large (more than 2 years)
        if (end - start).days > 730:
            return False, "Date range cannot exceed 2 years"
        
        return True, ""
        
    except ValueError as e:
        return False, f"Invalid date format: {str(e)}"

def validate_bigquery_response(df: pl.DataFrame, required_columns: List[str]) -> Tuple[bool, str]:
    """
    Validate BigQuery response data.
    
    Args:
        df: Polars DataFrame from BigQuery
        required_columns: List of required column names
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if df is None:
        return False, "No data returned from BigQuery"
    
    if df.is_empty():
        return False, "Empty dataset returned"
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return False, f"Missing required columns: {', '.join(missing_columns)}"
    
    return True, ""

def format_currency(value: float, currency: str = "R$") -> str:
    """
    Format currency values for display.
    
    Args:
        value: Numeric value to format
        currency: Currency symbol
        
    Returns:
        Formatted currency string
    """
    if pd.isna(value) or value is None:
        return f"{currency}0.00"
    
    if value >= 1_000_000:
        return f"{currency}{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{currency}{value/1_000:.1f}K"
    else:
        return f"{currency}{value:,.2f}"

def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format percentage values for display.
    
    Args:
        value: Numeric value (0-100)
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    if pd.isna(value) or value is None:
        return "0.0%"
    
    return f"{value:.{decimal_places}f}%"

def format_number(value: Union[int, float], compact: bool = True) -> str:
    """
    Format large numbers for display.
    
    Args:
        value: Numeric value to format
        compact: Whether to use compact notation (K, M, B)
        
    Returns:
        Formatted number string
    """
    if pd.isna(value) or value is None:
        return "0"
    
    if not compact:
        return f"{value:,.0f}"
    
    if value >= 1_000_000_000:
        return f"{value/1_000_000_000:.1f}B"
    elif value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.1f}K"
    else:
        return f"{value:.0f}"

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """
    Safely divide two numbers, handling division by zero.
    
    Args:
        numerator: Numerator value
        denominator: Denominator value
        default: Default value if division by zero
        
    Returns:
        Division result or default value
    """
    if denominator == 0 or pd.isna(denominator):
        return default
    return numerator / denominator

def calculate_percentage_change(current: float, previous: float) -> float:
    """
    Calculate percentage change between two values.
    
    Args:
        current: Current value
        previous: Previous value
        
    Returns:
        Percentage change
    """
    if previous == 0 or pd.isna(previous) or pd.isna(current):
        return 0.0
    
    return ((current - previous) / previous) * 100

def clean_column_names(df: pl.DataFrame) -> pl.DataFrame:
    """
    Clean and standardize column names.
    
    Args:
        df: Input DataFrame
        
    Returns:
        DataFrame with cleaned column names
    """
    # Convert to snake_case and remove special characters
    new_columns = []
    for col in df.columns:
        # Convert to lowercase and replace spaces/special chars with underscore
        clean_col = re.sub(r'[^a-zA-Z0-9_]', '_', col.lower())
        # Remove duplicate underscores
        clean_col = re.sub(r'_+', '_', clean_col)
        # Remove leading/trailing underscores
        clean_col = clean_col.strip('_')
        new_columns.append(clean_col)
    
    return df.rename(dict(zip(df.columns, new_columns)))

def detect_outliers(df: pl.DataFrame, column: str, method: str = 'iqr') -> pl.DataFrame:
    """
    Detect outliers in a numeric column.
    
    Args:
        df: Input DataFrame
        column: Column name to analyze
        method: Method for outlier detection ('iqr' or 'zscore')
        
    Returns:
        DataFrame with outlier flag column
    """
    if method == 'iqr':
        Q1 = df.select(pl.col(column).quantile(0.25)).item()
        Q3 = df.select(pl.col(column).quantile(0.75)).item()
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return df.with_columns([
            pl.when((pl.col(column) < lower_bound) | (pl.col(column) > upper_bound))
            .then(True)
            .otherwise(False)
            .alias(f"{column}_outlier")
        ])
    
    elif method == 'zscore':
        mean_val = df.select(pl.col(column).mean()).item()
        std_val = df.select(pl.col(column).std()).item()
        
        return df.with_columns([
            pl.when(pl.col(column).abs() > (mean_val + 3 * std_val))
            .then(True)
            .otherwise(False)
            .alias(f"{column}_outlier")
        ])
    
    return df

def create_time_series(df: pl.DataFrame, date_column: str, 
                      value_column: str, freq: str = 'D') -> pl.DataFrame:
    """
    Create a time series with specified frequency.
    
    Args:
        df: Input DataFrame
        date_column: Date column name
        value_column: Value column name
        freq: Frequency ('D', 'W', 'M', 'Q', 'Y')
        
    Returns:
        Aggregated time series DataFrame
    """
    # Convert to date if needed
    df = df.with_columns([
        pl.col(date_column).str.strptime(pl.Date, format='%Y-%m-%d').alias(date_column)
    ])
    
    if freq == 'D':
        return df.group_by(date_column).agg([
            pl.col(value_column).sum().alias(f"total_{value_column}"),
            pl.col(value_column).mean().alias(f"avg_{value_column}"),
            pl.count().alias("record_count")
        ]).sort(date_column)
    
    elif freq == 'W':
        return df.with_columns([
            pl.col(date_column).dt.truncate("1w").alias("week")
        ]).group_by("week").agg([
            pl.col(value_column).sum().alias(f"total_{value_column}"),
            pl.col(value_column).mean().alias(f"avg_{value_column}"),
            pl.count().alias("record_count")
        ]).sort("week")
    
    elif freq == 'M':
        return df.with_columns([
            pl.col(date_column).dt.truncate("1mo").alias("month")
        ]).group_by("month").agg([
            pl.col(value_column).sum().alias(f"total_{value_column}"),
            pl.col(value_column).mean().alias(f"avg_{value_column}"),
            pl.count().alias("record_count")
        ]).sort("month")
    
    return df

def log_performance(func_name: str, execution_time: float, record_count: int = None):
    """
    Log performance metrics for functions.
    
    Args:
        func_name: Name of the function
        execution_time: Execution time in seconds
        record_count: Number of records processed
    """
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "function": func_name,
        "execution_time": round(execution_time, 3),
        "status": "success"
    }
    
    if record_count is not None:
        log_entry["record_count"] = record_count
        log_entry["records_per_second"] = round(record_count / execution_time, 2)
    
    # In production, this would write to a proper logging system
    if st.session_state.get("debug_mode", False):
        st.info(f"⚡ {func_name}: {execution_time:.3f}s" + 
               (f" ({record_count:,} records)" if record_count else ""))

def handle_missing_values(df: pl.DataFrame, strategy: str = 'drop') -> pl.DataFrame:
    """
    Handle missing values in DataFrame.
    
    Args:
        df: Input DataFrame
        strategy: Strategy for handling missing values ('drop', 'fill_zero', 'fill_mean')
        
    Returns:
        DataFrame with missing values handled
    """
    if strategy == 'drop':
        return df.drop_nulls()
    
    elif strategy == 'fill_zero':
        # Fill numeric columns with 0, string columns with empty string
        fill_values = {}
        for col in df.columns:
            dtype = df[col].dtype
            if dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]:
                fill_values[col] = 0
            elif dtype == pl.Utf8:
                fill_values[col] = ""
        
        return df.fill_null(fill_values)
    
    elif strategy == 'fill_mean':
        # Fill numeric columns with mean, others with mode or zero
        fill_values = {}
        for col in df.columns:
            dtype = df[col].dtype
            if dtype in [pl.Int64, pl.Float64, pl.Int32, pl.Float32]:
                mean_val = df.select(pl.col(col).mean()).item()
                fill_values[col] = mean_val if mean_val is not None else 0
            else:
                fill_values[col] = ""
        
        return df.fill_null(fill_values)
    
    return df

def create_summary_stats(df: pl.DataFrame, numeric_columns: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Create summary statistics for numeric columns.
    
    Args:
        df: Input DataFrame
        numeric_columns: List of numeric column names
        
    Returns:
        Dictionary of summary statistics
    """
    stats = {}
    
    for col in numeric_columns:
        if col in df.columns:
            col_stats = df.select([
                pl.col(col).count().alias("count"),
                pl.col(col).mean().alias("mean"),
                pl.col(col).median().alias("median"),
                pl.col(col).std().alias("std"),
                pl.col(col).min().alias("min"),
                pl.col(col).max().alias("max"),
                pl.col(col).quantile(0.25).alias("q25"),
                pl.col(col).quantile(0.75).alias("q75")
            ]).to_dict(as_series=False)
            
            stats[col] = {k: v[0] if v else 0 for k, v in col_stats.items()}
    
    return stats

def export_to_excel(dataframes: Dict[str, pl.DataFrame], filename: str) -> bytes:
    """
    Export multiple DataFrames to Excel file.
    
    Args:
        dataframes: Dictionary mapping sheet names to DataFrames
        filename: Output filename
        
    Returns:
        Excel file as bytes
    """
    from io import BytesIO
    import pandas as pd
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for sheet_name, df in dataframes.items():
            # Convert Polars to Pandas for Excel export
            pandas_df = df.to_pandas()
            pandas_df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return output.getvalue()

def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid email format
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def create_download_link(data: bytes, filename: str, text: str) -> str:
    """
    Create a download link for data.
    
    Args:
        data: Data to download as bytes
        filename: Suggested filename
        text: Link text
        
    Returns:
        HTML download link
    """
    import base64
    
    b64 = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{text}</a>'
    return href
