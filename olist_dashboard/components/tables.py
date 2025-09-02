"""
Table components for displaying data in tabular format.
"""

import streamlit as st
import polars as pl
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

from ..config.settings import UI_CONFIG

def render_data_table(data: pl.DataFrame, title: str = None, 
                     max_rows: int = None, sortable: bool = True,
                     download: bool = True) -> None:
    """
    Render a data table with optional features.
    
    Args:
        data: DataFrame to display
        title: Optional table title
        max_rows: Maximum rows to display
        sortable: Whether table is sortable
        download: Whether to show download button
    """
    if data is None or data.is_empty():
        st.warning("No data available")
        return
    
    # Display title if provided
    if title:
        st.subheader(title)
    
    # Convert to pandas for display
    df_display = data.to_pandas()
    
    # Limit rows if specified
    max_display_rows = max_rows or UI_CONFIG.get("max_rows_display", 1000)
    if len(df_display) > max_display_rows:
        st.info(f"Showing first {max_display_rows} rows of {len(df_display)} total rows")
        df_display = df_display.head(max_display_rows)
    
    # Format numeric columns
    df_display = format_numeric_columns(df_display)
    
    # Display table
    st.dataframe(
        df_display,
        height=UI_CONFIG.get("table_height", 400),
        width='stretch'
    )
    
    # Add download button if requested
    if download:
        # Convert to pandas and check if data is not empty
        df_pandas = data.to_pandas()
        if not df_pandas.empty:
            # Create unique key based on title, schema, and data shape
            unique_id = f"{title or 'data'}_{hash(str(data.schema))}_{data.shape[0]}_{data.shape[1]}_{id(data) % 10000}"
            create_download_buttons(df_pandas, title or "data", key_prefix=f"data_table_{unique_id}")
        else:
            st.info("📊 No data available for download")

def render_summary_table(data: pl.DataFrame, group_cols: List[str], 
                        agg_cols: Dict[str, str], title: str = None) -> None:
    """
    Render a summary table with aggregations.
    
    Args:
        data: DataFrame to summarize
        group_cols: Columns to group by
        agg_cols: Dictionary of column -> aggregation function
        title: Optional table title
    """
    if data is None or data.is_empty():
        st.warning("No data available for summary")
        return
    
    try:
        # Create aggregation expressions
        agg_exprs = []
        for col, agg_func in agg_cols.items():
            if col in data.columns:
                if agg_func == 'mean':
                    agg_exprs.append(pl.col(col).mean().alias(f"avg_{col}"))
                elif agg_func == 'sum':
                    agg_exprs.append(pl.col(col).sum().alias(f"total_{col}"))
                elif agg_func == 'count':
                    agg_exprs.append(pl.col(col).count().alias(f"count_{col}"))
                elif agg_func == 'max':
                    agg_exprs.append(pl.col(col).max().alias(f"max_{col}"))
                elif agg_func == 'min':
                    agg_exprs.append(pl.col(col).min().alias(f"min_{col}"))
        
        # Group and aggregate
        if agg_exprs:
            summary_data = data.group_by(group_cols).agg(agg_exprs)
            render_data_table(summary_data, title, sortable=True)
        else:
            st.warning("No valid aggregation columns found")
            
    except Exception as e:
        st.error(f"Error creating summary table: {str(e)}")

def render_top_performers_table(data: pl.DataFrame, rank_col: str, 
                               top_n: int = 10, title: str = None) -> None:
    """
    Render a table showing top performers.
    
    Args:
        data: DataFrame with performance data
        rank_col: Column to rank by
        top_n: Number of top performers to show
        title: Optional table title
    """
    if data is None or data.is_empty():
        st.warning("No data available for top performers")
        return
    
    try:
        # Get top performers
        if rank_col in data.columns:
            top_data = data.sort(rank_col, descending=True).head(top_n)
            
            # Add rank column
            top_data = top_data.with_columns(
                pl.arange(1, len(top_data) + 1).alias("Rank")
            )
            
            # Reorder columns to put Rank first
            columns = ["Rank"] + [col for col in top_data.columns if col != "Rank"]
            top_data = top_data.select(columns)
            
            render_data_table(
                top_data, 
                title or f"Top {top_n} by {rank_col.replace('_', ' ').title()}",
                sortable=False
            )
        else:
            st.warning(f"Column '{rank_col}' not found in data")
            
    except Exception as e:
        st.error(f"Error creating top performers table: {str(e)}")

def render_comparison_table(data1: pl.DataFrame, data2: pl.DataFrame,
                          labels: Tuple[str, str], key_col: str,
                          compare_cols: List[str], title: str = None) -> None:
    """
    Render a comparison table between two datasets.
    
    Args:
        data1: First DataFrame
        data2: Second DataFrame
        labels: Labels for the two datasets
        key_col: Key column for joining
        compare_cols: Columns to compare
        title: Optional table title
    """
    if data1 is None or data2 is None or data1.is_empty() or data2.is_empty():
        st.warning("Insufficient data for comparison")
        return
    
    try:
        # Ensure both datasets have the required columns
        if key_col not in data1.columns or key_col not in data2.columns:
            st.warning(f"Key column '{key_col}' not found in both datasets")
            return
        
        # Select only relevant columns
        cols_to_select = [key_col] + [col for col in compare_cols if col in data1.columns and col in data2.columns]
        
        df1 = data1.select(cols_to_select)
        df2 = data2.select(cols_to_select)
        
        # Rename columns to indicate source
        rename_dict1 = {col: f"{col}_{labels[0]}" for col in cols_to_select if col != key_col}
        rename_dict2 = {col: f"{col}_{labels[1]}" for col in cols_to_select if col != key_col}
        
        df1 = df1.rename(rename_dict1)
        df2 = df2.rename(rename_dict2)
        
        # Join the datasets
        comparison_data = df1.join(df2, on=key_col, how="inner")
        
        # Calculate differences for numeric columns
        for col in compare_cols:
            col1 = f"{col}_{labels[0]}"
            col2 = f"{col}_{labels[1]}"
            if col1 in comparison_data.columns and col2 in comparison_data.columns:
                comparison_data = comparison_data.with_columns(
                    (pl.col(col2) - pl.col(col1)).alias(f"{col}_diff")
                )
        
        render_data_table(comparison_data, title or "Comparison Analysis")
        
    except Exception as e:
        st.error(f"Error creating comparison table: {str(e)}")

def render_pivot_table(data: pl.DataFrame, index_col: str, columns_col: str,
                      values_col: str, agg_func: str = 'sum', title: str = None) -> None:
    """
    Render a pivot table.
    
    Args:
        data: DataFrame to pivot
        index_col: Column for pivot index
        columns_col: Column for pivot columns
        values_col: Column for values
        agg_func: Aggregation function
        title: Optional table title
    """
    if data is None or data.is_empty():
        st.warning("No data available for pivot table")
        return
    
    try:
        # Convert to pandas for pivot functionality
        df_pandas = data.to_pandas()
        
        # Create pivot table
        pivot_df = pd.pivot_table(
            df_pandas,
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=agg_func,
            fill_value=0
        )
        
        # Reset index to make it a regular DataFrame
        pivot_df = pivot_df.reset_index()
        
        # Display title if provided
        if title:
            st.subheader(title)
        
        # Format and display
        pivot_df = format_numeric_columns(pivot_df)
        
        st.dataframe(
            pivot_df,
            height=UI_CONFIG.get("table_height", 400),
            width='stretch'
        )
        
        # Add download button
        create_download_buttons(pivot_df, title or "pivot_table", key_prefix=f"pivot_table_{hash(str(pivot_df.shape))}_{id(pivot_df) % 10000}")
        
    except Exception as e:
        st.error(f"Error creating pivot table: {str(e)}")

def render_correlation_table(correlations: Dict[str, float], title: str = None) -> None:
    """
    Render a correlation table.
    
    Args:
        correlations: Dictionary of correlations
        title: Optional table title
    """
    if not correlations:
        st.warning("No correlation data available")
        return
    
    try:
        # Convert to DataFrame
        corr_data = pl.DataFrame({
            "Metric": list(correlations.keys()),
            "Correlation": list(correlations.values())
        })
        
        # Add correlation strength categories
        corr_data = corr_data.with_columns([
            pl.when(pl.col("Correlation").abs() >= 0.7)
            .then("Strong")
            .when(pl.col("Correlation").abs() >= 0.3)
            .then("Moderate")
            .when(pl.col("Correlation").abs() >= 0.1)
            .then("Weak")
            .otherwise("Very Weak")
            .alias("Strength"),
            
            pl.when(pl.col("Correlation") > 0)
            .then("Positive")
            .when(pl.col("Correlation") < 0)
            .then("Negative")
            .otherwise("None")
            .alias("Direction")
        ])
        
        # Sort by absolute correlation value
        corr_data = corr_data.with_columns(
            pl.col("Correlation").abs().alias("abs_correlation")
        ).sort("abs_correlation", descending=True).drop("abs_correlation")
        
        render_data_table(corr_data, title or "Correlation Analysis")
        
    except Exception as e:
        st.error(f"Error creating correlation table: {str(e)}")

def format_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Format numeric columns for better display.
    
    Args:
        df: DataFrame to format
        
    Returns:
        Formatted DataFrame
    """
    try:
        formatted_df = df.copy()
        
        for col in formatted_df.columns:
            if formatted_df[col].dtype in ['float64', 'float32']:
                # Format based on column type
                if 'rate' in col.lower() or 'percentage' in col.lower() or 'pct' in col.lower():
                    # Percentage columns
                    formatted_df[col] = formatted_df[col].round(1)
                elif 'price' in col.lower() or 'revenue' in col.lower() or 'value' in col.lower():
                    # Currency columns
                    formatted_df[col] = formatted_df[col].round(2)
                elif 'rating' in col.lower() or 'score' in col.lower():
                    # Rating columns
                    formatted_df[col] = formatted_df[col].round(2)
                else:
                    # General numeric columns
                    formatted_df[col] = formatted_df[col].round(2)
        
        return formatted_df
        
    except Exception as e:
        st.error(f"Error formatting columns: {str(e)}")
        return df

def create_download_buttons(df: pd.DataFrame, filename: str, key_prefix: str = "") -> None:
    """
    Create download buttons for different formats.
    
    Args:
        df: DataFrame to download
        filename: Base filename
        key_prefix: Unique prefix for button keys to avoid conflicts
    """
    # Initialize session state counter if not exists
    if 'download_button_counter' not in st.session_state:
        st.session_state.download_button_counter = 0
    
    # Get unique counter for this set of buttons
    counter = st.session_state.download_button_counter
    st.session_state.download_button_counter += 1
    
    try:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # CSV download
            csv_data = df.to_csv(index=False)
            if csv_data and len(csv_data.strip()) > 0:
                st.download_button(
                    label="📥 Download CSV",
                    data=csv_data,
                    file_name=f"{filename}.csv",
                    mime="text/csv",
                    key=f"{key_prefix}_csv_{counter}"
                )
            else:
                st.info("📄 No CSV data available")
        
        with col2:
            # Excel download
            try:
                import io
                excel_buffer = io.BytesIO()
                
                # Try to use xlsxwriter first, fall back to openpyxl if not available
                try:
                    df.to_excel(excel_buffer, index=False, engine='xlsxwriter')
                except ImportError:
                    # Fall back to openpyxl if xlsxwriter is not available
                    df.to_excel(excel_buffer, index=False, engine='openpyxl')
                
                excel_data = excel_buffer.getvalue()
                
                if excel_data and len(excel_data) > 0:
                    st.download_button(
                        label="📥 Download Excel",
                        data=excel_data,
                        file_name=f"{filename}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        key=f"{key_prefix}_excel_{counter}"
                    )
                else:
                    st.info("📊 No Excel data available")
            except Exception as e:
                st.info("📊 Excel download not available - install xlsxwriter or openpyxl")
        
        with col3:
            # JSON download
            json_data = df.to_json(orient='records', indent=2)
            if json_data and len(json_data.strip()) > 0:
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"{filename}.json",
                    mime="application/json",
                    key=f"{key_prefix}_json_{counter}"
                )
            else:
                st.info("📋 No JSON data available")
            
    except Exception as e:
        st.error(f"Error creating download buttons: {str(e)}")

def render_table_with_filters(data: pl.DataFrame, title: str = None,
                            filterable_columns: List[str] = None) -> pl.DataFrame:
    """
    Render a table with interactive filters.
    
    Args:
        data: DataFrame to display
        title: Optional table title
        filterable_columns: Columns that can be filtered
        
    Returns:
        Filtered DataFrame
    """
    if data is None or data.is_empty():
        st.warning("No data available")
        return pl.DataFrame()
    
    try:
        # Display title
        if title:
            st.subheader(title)
        
        # Create filter controls
        filtered_data = data
        
        if filterable_columns:
            with st.expander("🔍 Table Filters"):
                filter_col1, filter_col2 = st.columns(2)
                
                for i, col in enumerate(filterable_columns[:4]):  # Limit to 4 filters
                    if col in data.columns:
                        unique_values = data[col].unique().to_list()
                        
                        # Remove None values
                        unique_values = [v for v in unique_values if v is not None]
                        
                        with filter_col1 if i % 2 == 0 else filter_col2:
                            selected_values = st.multiselect(
                                f"Filter {col.replace('_', ' ').title()}:",
                                options=unique_values,
                                default=unique_values[:10] if len(unique_values) > 10 else unique_values,
                                key=f"filter_{col}"
                            )
                            
                            if selected_values:
                                filtered_data = filtered_data.filter(pl.col(col).is_in(selected_values))
        
        # Display filtered table
        render_data_table(filtered_data, download=True)
        
        # Show filter summary
        if len(filtered_data) != len(data):
            st.info(f"Showing {len(filtered_data)} of {len(data)} rows after filtering")
        
        return filtered_data
        
    except Exception as e:
        st.error(f"Error rendering filtered table: {str(e)}")
        return data

def render_performance_metrics_table(data: pl.DataFrame) -> None:
    """
    Render a specialized table for performance metrics.
    
    Args:
        data: DataFrame with performance metrics
    """
    if data is None or data.is_empty():
        st.warning("No performance data available")
        return
    
    try:
        # Convert to pandas for formatting
        df = data.to_pandas()
        
        # Add performance indicators
        def get_performance_indicator(value, threshold_good, threshold_ok):
            if pd.isna(value):
                return "⚪ N/A"
            elif value >= threshold_good:
                return "🟢 Good"
            elif value >= threshold_ok:
                return "🟡 OK"
            else:
                return "🔴 Poor"
        
        # Apply indicators based on column type
        if 'on_time_rate' in df.columns:
            df['Delivery Status'] = df['on_time_rate'].apply(
                lambda x: get_performance_indicator(x, 90, 75)
            )
        
        if 'avg_rating' in df.columns:
            df['Rating Status'] = df['avg_rating'].apply(
                lambda x: get_performance_indicator(x, 4.0, 3.5)
            )
        
        # Format and display
        df = format_numeric_columns(df)
        
        st.dataframe(
            df,
            height=UI_CONFIG.get("table_height", 400),
            width='stretch'
        )
        
    except Exception as e:
        st.error(f"Error rendering performance metrics table: {str(e)}")
