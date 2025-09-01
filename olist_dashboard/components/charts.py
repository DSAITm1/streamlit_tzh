"""
Chart components for data visualization using Plotly and Altair.
"""

import streamlit as st
import polars as pl
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import altair as alt
from typing import Dict, Any, List, Optional, Tuple

from ..config.settings import COLOR_PALETTE, CHART_THEMES, UI_CONFIG

# Configure Altair to use the full width
alt.data_transformers.enable('json')

def render_delivery_performance_charts(delivery_data: pl.DataFrame) -> None:
    """
    Render delivery performance charts.
    
    Args:
        delivery_data: DataFrame with delivery performance data
    """
    if delivery_data is None or delivery_data.is_empty():
        st.warning("No delivery data available for charts")
        return
    
    # Convert to pandas for plotting
    df = delivery_data.to_pandas()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Delivery Trends")
        render_delivery_trend_chart(df)
    
    with col2:
        st.subheader("🗺️ Geographic Performance")
        render_geographic_performance_chart(df)
    
    # Full width chart for detailed analysis
    st.subheader("📊 Delivery Time Distribution")
    render_delivery_distribution_chart(df)

def render_delivery_trend_chart(df) -> None:
    """Render delivery performance trend over time."""
    try:
        if 'date_value' not in df.columns or 'daily_on_time_rate' not in df.columns:
            st.info("Date or on-time rate data not available")
            return
        
        fig = px.line(
            df,
            x='date_value',
            y='daily_on_time_rate',
            title='On-Time Delivery Rate Trend',
            labels={
                'date_value': 'Date',
                'daily_on_time_rate': 'On-Time Rate (%)'
            }
        )
        
        # Add target line
        fig.add_hline(y=90, line_dash="dash", line_color="red", 
                     annotation_text="Target: 90%")
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            showlegend=False,
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering delivery trend chart: {str(e)}")

def render_geographic_performance_chart(df) -> None:
    """Render geographic performance chart."""
    try:
        if 'customer_state' not in df.columns:
            st.info("Geographic data not available")
            return
        
        # Group by state for visualization
        state_data = df.groupby('customer_state').agg({
            'order_count': 'sum',
            'on_time_rate': 'mean'
        }).reset_index()
        
        # Create bar chart
        fig = px.bar(
            state_data.head(10),  # Top 10 states
            x='customer_state',
            y='order_count',
            color='on_time_rate',
            title='Top 10 States by Order Volume',
            labels={
                'customer_state': 'State',
                'order_count': 'Order Count',
                'on_time_rate': 'On-Time Rate (%)'
            },
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering geographic chart: {str(e)}")

def render_delivery_distribution_chart(df) -> None:
    """Render delivery time distribution chart."""
    try:
        if 'delivery_time_bucket' not in df.columns:
            st.info("Delivery time distribution data not available")
            return
        
        fig = px.pie(
            df,
            values='order_count',
            names='delivery_time_bucket',
            title='Delivery Time Distribution',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering distribution chart: {str(e)}")

def render_satisfaction_charts(satisfaction_data: pl.DataFrame) -> None:
    """
    Render customer satisfaction charts.
    
    Args:
        satisfaction_data: DataFrame with satisfaction data
    """
    if satisfaction_data is None or satisfaction_data.is_empty():
        st.warning("No satisfaction data available for charts")
        return
    
    df = satisfaction_data.to_pandas()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⭐ Rating Distribution")
        render_rating_distribution_chart(df)
    
    with col2:
        st.subheader("📈 Satisfaction vs Delivery")
        render_satisfaction_delivery_chart(df)

def render_rating_distribution_chart(df) -> None:
    """Render rating distribution chart."""
    try:
        if 'review_score' not in df.columns:
            st.info("Rating data not available")
            return
        
        fig = px.bar(
            df,
            x='review_score',
            y='review_count',
            title='Customer Rating Distribution',
            labels={
                'review_score': 'Rating (1-5 stars)',
                'review_count': 'Number of Reviews'
            },
            color='review_score',
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            showlegend=False,
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering rating distribution: {str(e)}")

def render_satisfaction_delivery_chart(df) -> None:
    """Render satisfaction vs delivery performance chart."""
    try:
        if 'delivery_status' not in df.columns or 'avg_rating' not in df.columns:
            st.info("Satisfaction vs delivery data not available")
            return
        
        fig = px.bar(
            df,
            x='delivery_status',
            y='avg_rating',
            color='delivery_status',
            title='Average Rating by Delivery Status',
            labels={
                'delivery_status': 'Delivery Status',
                'avg_rating': 'Average Rating'
            },
            color_discrete_map={
                'On Time': COLOR_PALETTE["success"],
                'Delayed': COLOR_PALETTE["warning"]
            }
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            showlegend=False,
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering satisfaction vs delivery chart: {str(e)}")

def render_product_analysis_charts(product_data: pl.DataFrame) -> None:
    """
    Render product analysis charts.
    
    Args:
        product_data: DataFrame with product data
    """
    if product_data is None or product_data.is_empty():
        st.warning("No product data available for charts")
        return
    
    df = product_data.to_pandas()
    
    # Check what type of data we have and render appropriate charts
    has_weight_data = 'weight_category' in df.columns and 'avg_delivery_days' in df.columns
    has_category_data = 'category' in df.columns and 'total_revenue' in df.columns
    
    if has_weight_data:
        # Weight impact chart
        st.subheader("📦 Product Weight Impact on Delivery")
        render_weight_impact_chart(df)
    
    if has_category_data:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Categories by Revenue")
            render_category_revenue_chart(df)
        
        with col2:
            st.subheader("⭐ Category Performance")
            render_category_performance_chart(df)
    
    # If neither type of data is available, show a message
    if not has_weight_data and not has_category_data:
        st.info("Chart data not available for the selected analysis type")

def render_weight_impact_chart(df) -> None:
    """Render product weight impact chart."""
    try:
        if 'weight_category' not in df.columns or 'avg_delivery_days' not in df.columns:
            st.info("Weight impact data not available")
            return
        
        fig = px.scatter(
            df,
            x='weight_category',
            y='avg_delivery_days',
            size='order_count',
            color='on_time_rate',
            title='Delivery Days by Product Weight Category',
            labels={
                'weight_category': 'Weight Category',
                'avg_delivery_days': 'Average Delivery Days',
                'order_count': 'Order Count',
                'on_time_rate': 'On-Time Rate (%)'
            },
            color_continuous_scale='RdYlGn'
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering weight impact chart: {str(e)}")

def render_category_revenue_chart(df) -> None:
    """Render category revenue chart."""
    try:
        if 'category' not in df.columns or 'total_revenue' not in df.columns:
            st.info("Category revenue data not available")
            return
        
        # Top 10 categories by revenue
        top_categories = df.nlargest(10, 'total_revenue')
        
        fig = px.bar(
            top_categories,
            x='total_revenue',
            y='category',
            orientation='h',
            title='Top 10 Categories by Revenue',
            labels={
                'category': 'Product Category',
                'total_revenue': 'Total Revenue (R$)'
            },
            color='total_revenue',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            showlegend=False,
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering category revenue chart: {str(e)}")

def render_category_performance_chart(df) -> None:
    """Render category performance scatter chart."""
    try:
        if not all(col in df.columns for col in ['avg_rating', 'on_time_rate', 'order_count']):
            st.info("Category performance data not available")
            return
        
        fig = px.scatter(
            df,
            x='avg_rating',
            y='on_time_rate',
            size='order_count',
            hover_name='category',
            title='Category Performance: Rating vs Delivery',
            labels={
                'avg_rating': 'Average Rating',
                'on_time_rate': 'On-Time Rate (%)',
                'order_count': 'Order Count'
            },
            color='order_count',
            color_continuous_scale='Viridis'
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering category performance chart: {str(e)}")

def render_payment_analysis_charts(payment_data: pl.DataFrame) -> None:
    """
    Render payment analysis charts.
    
    Args:
        payment_data: DataFrame with payment data
    """
    if payment_data is None or payment_data.is_empty():
        st.warning("No payment data available for charts")
        return
    
    df = payment_data.to_pandas()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💳 Payment Methods")
        render_payment_methods_chart(df)
    
    with col2:
        st.subheader("📊 Installment Analysis")
        render_installment_chart(df)

def render_payment_methods_chart(df) -> None:
    """Render payment methods chart."""
    try:
        if 'payment_type' not in df.columns or 'order_count' not in df.columns:
            st.info("Payment method data not available")
            return
        
        fig = px.pie(
            df,
            values='order_count',
            names='payment_type',
            title='Payment Method Distribution',
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering payment methods chart: {str(e)}")

def render_installment_chart(df) -> None:
    """Render installment analysis chart."""
    try:
        if 'payment_installments' not in df.columns or 'avg_order_value' not in df.columns:
            st.info("Installment data not available")
            return
        
        fig = px.bar(
            df,
            x='payment_installments',
            y='avg_order_value',
            title='Average Order Value by Installments',
            labels={
                'payment_installments': 'Number of Installments',
                'avg_order_value': 'Average Order Value (R$)'
            },
            color='avg_order_value',
            color_continuous_scale='Blues'
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            showlegend=False,
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering installment chart: {str(e)}")

def render_correlation_heatmap(correlation_data: Dict[str, float]) -> None:
    """
    Render correlation heatmap.
    
    Args:
        correlation_data: Dictionary with correlation coefficients
    """
    if not correlation_data:
        st.info("No correlation data available")
        return
    
    try:
        # Prepare data for heatmap
        metrics = list(correlation_data.keys())
        values = list(correlation_data.values())
        
        # Create a square matrix (simplified for single target variable)
        fig = px.bar(
            x=metrics,
            y=values,
            title='Correlation with Customer Rating',
            labels={
                'x': 'Metrics',
                'y': 'Correlation Coefficient'
            },
            color=values,
            color_continuous_scale='RdBu_r',
            color_continuous_midpoint=0
        )
        
        fig.update_layout(
            height=UI_CONFIG["chart_height"],
            **CHART_THEMES["plotly"]["layout"]
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering correlation heatmap: {str(e)}")

def render_time_series_chart(data: pl.DataFrame, date_col: str, value_col: str, 
                           title: str, line_color: str = None) -> None:
    """
    Render a time series chart using Altair.
    
    Args:
        data: DataFrame with time series data
        date_col: Date column name
        value_col: Value column name
        title: Chart title
        line_color: Line color
    """
    if data is None or data.is_empty():
        st.info(f"No data available for {title}")
        return
    
    try:
        # Convert to pandas for Altair
        df = data.to_pandas()
        
        chart = alt.Chart(df).mark_line(
            point=True,
            color=line_color or COLOR_PALETTE["primary"]
        ).add_selection(
            alt.selection_interval(bind='scales')
        ).encode(
            x=alt.X(f'{date_col}:T', title='Date'),
            y=alt.Y(f'{value_col}:Q', title=value_col.replace('_', ' ').title()),
            tooltip=[
                alt.Tooltip(f'{date_col}:T', title='Date'),
                alt.Tooltip(f'{value_col}:Q', title=value_col.replace('_', ' ').title())
            ]
        ).properties(
            title=title,
            width='container',
            height=UI_CONFIG["chart_height"]
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error rendering time series chart: {str(e)}")

def create_download_button(fig: go.Figure, filename: str, format: str = 'png') -> None:
    """
    Create download button for charts.
    
    Args:
        fig: Plotly figure
        filename: Download filename
        format: File format ('png', 'svg', 'pdf')
    """
    try:
        if format == 'png':
            img_bytes = fig.to_image(format='png', width=1200, height=800)
            st.download_button(
                label=f"📥 Download {format.upper()}",
                data=img_bytes,
                file_name=f"{filename}.{format}",
                mime=f"image/{format}"
            )
        else:
            st.info(f"{format.upper()} download not yet implemented")
            
    except Exception as e:
        st.error(f"Error creating download button: {str(e)}")
