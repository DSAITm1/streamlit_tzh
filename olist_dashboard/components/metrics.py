"""
Metrics components for displaying KPI cards and summary statistics.
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, List, Optional, Tuple
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..config.settings import COLOR_PALETTE, UI_CONFIG

def render_kpi_cards(metrics_data: Dict[str, Any], columns: int = 4) -> None:
    """
    Render KPI cards in a responsive grid layout.
    
    Args:
        metrics_data: Dictionary with metric names and values
        columns: Number of columns for the grid
    """
    if not metrics_data:
        st.warning("No metrics data available")
        return
    
    # Create columns for responsive layout
    cols = st.columns(columns)
    
    # Define default KPI configurations
    kpi_configs = {
        "on_time_delivery_rate": {
            "title": "On-Time Delivery",
            "format": "{:.1f}%",
            "icon": "🚚",
            "color": "success" if metrics_data.get("on_time_delivery_rate", 0) >= 85 else "warning",
            "target": 90,
        },
        "avg_rating": {
            "title": "Avg Rating",
            "format": "{:.2f}/5.0",
            "icon": "⭐",
            "color": "success" if metrics_data.get("avg_rating", 0) >= 4.0 else "warning",
            "target": 4.5,
        },
        "total_revenue": {
            "title": "Total Revenue",
            "format": "R${:,.0f}",
            "icon": "💰",
            "color": "info",
            "target": None,
        },
        "active_customers": {
            "title": "Active Customers",
            "format": "{:,}",
            "icon": "👥",
            "color": "info",
            "target": None,
        },
        "total_orders": {
            "title": "Total Orders",
            "format": "{:,}",
            "icon": "📦",
            "color": "info",
            "target": None,
        }
    }
    
    # Render each KPI card
    metric_keys = list(metrics_data.keys())
    for i, metric_key in enumerate(metric_keys[:columns]):
        with cols[i % columns]:
            render_single_kpi_card(
                metric_key,
                metrics_data.get(metric_key),
                kpi_configs.get(metric_key, {})
            )

def render_single_kpi_card(metric_key: str, value: Any, config: Dict[str, Any]) -> None:
    """
    Render a single KPI card.
    
    Args:
        metric_key: Key for the metric
        value: Metric value
        config: Configuration for the KPI display
    """
    title = config.get("title", metric_key.replace("_", " ").title())
    format_str = config.get("format", "{}")
    icon = config.get("icon", "📊")
    color = config.get("color", "info")
    target = config.get("target")
    
    # Handle None values
    if value is None:
        formatted_value = "N/A"
        delta = None
    else:
        try:
            formatted_value = format_str.format(value)
            # Calculate delta from target if available
            delta = None
            if target is not None:
                delta = value - target
        except (ValueError, TypeError):
            formatted_value = str(value)
            delta = None
    
    # Create metric container
    with st.container():
        # Use Streamlit's metric component
        st.metric(
            label=f"{icon} {title}",
            value=formatted_value,
            delta=f"{delta:+.1f}" if delta is not None else None,
            delta_color="normal" if delta is None else ("normal" if delta >= 0 else "inverse")
        )

def render_trend_metrics(trend_data: pl.DataFrame, date_col: str = "date_value") -> None:
    """
    Render trending metrics with sparklines.
    
    Args:
        trend_data: DataFrame with trending data
        date_col: Name of the date column
    """
    if trend_data is None or trend_data.is_empty():
        st.warning("No trend data available")
        return
    
    st.subheader("📈 Trends (Last 30 Days)")
    
    # Get the last 30 days of data
    recent_data = trend_data.tail(30)
    
    # Define metrics to show trends for
    trend_metrics = {
        "daily_orders": {"title": "Daily Orders", "color": COLOR_PALETTE["primary"]},
        "daily_revenue": {"title": "Daily Revenue", "color": COLOR_PALETTE["success"]},
        "daily_avg_rating": {"title": "Daily Rating", "color": COLOR_PALETTE["warning"]},
        "daily_on_time_rate": {"title": "On-Time Rate", "color": COLOR_PALETTE["info"]}
    }
    
    cols = st.columns(len(trend_metrics))
    
    for i, (metric_col, config) in enumerate(trend_metrics.items()):
        if metric_col in recent_data.columns:
            with cols[i]:
                render_sparkline_metric(
                    recent_data, 
                    date_col, 
                    metric_col, 
                    config["title"], 
                    config["color"]
                )

def hex_to_rgba(hex_color: str, alpha: float = 0.1) -> str:
    """
    Convert hex color to rgba format.
    
    Args:
        hex_color: Hex color string (e.g., "#1f77b4")
        alpha: Alpha transparency value (0-1)
        
    Returns:
        RGBA color string (e.g., "rgba(31, 119, 180, 0.1)")
    """
    # Remove # if present
    hex_color = hex_color.lstrip('#')
    
    # Convert hex to RGB
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    
    return f"rgba({r}, {g}, {b}, {alpha})"

def render_sparkline_metric(data: pl.DataFrame, date_col: str, metric_col: str, 
                          title: str, color: str) -> None:
    """
    Render a single metric with sparkline chart.
    
    Args:
        data: DataFrame with data
        date_col: Date column name
        metric_col: Metric column name
        title: Display title
        color: Chart color (hex format)
    """
    try:
        # Convert to pandas for plotly
        df_pandas = data.select([date_col, metric_col]).to_pandas()
        
        # Create sparkline chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df_pandas[date_col],
            y=df_pandas[metric_col],
            mode='lines',
            line=dict(color=color, width=2),
            fill='tonexty',
            fillcolor=hex_to_rgba(color, 0.1),  # Convert hex to rgba properly
            showlegend=False,
            hovertemplate=f'{title}: %{{y}}<br>Date: %{{x}}<extra></extra>'
        ))
        
        # Update layout for sparkline style
        fig.update_layout(
            height=100,
            margin=dict(l=0, r=0, t=20, b=0),
            xaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            yaxis=dict(showgrid=False, showticklabels=False, zeroline=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            title=dict(text=title, font=dict(size=12), y=0.9)
        )
        
        # Calculate current value and change
        current_value = df_pandas[metric_col].iloc[-1]
        previous_value = df_pandas[metric_col].iloc[-2] if len(df_pandas) > 1 else current_value
        
        # Handle None values
        if current_value is None:
            current_value = 0
        if previous_value is None:
            previous_value = current_value if current_value != 0 else 1
        
        change_pct = ((current_value - previous_value) / previous_value * 100) if previous_value != 0 else 0
        
        # Display metric with chart
        col1, col2 = st.columns([2, 1])
        with col1:
            st.plotly_chart(fig, width='stretch', config={'displayModeBar': False})
        
        with col2:
            st.metric(
                label="Current",
                value=f"{current_value:.1f}",
                delta=f"{change_pct:+.1f}%"
            )
            
    except Exception as e:
        st.error(f"Error rendering sparkline for {title}: {str(e)}")

def render_performance_summary(summary_data: Dict[str, Any]) -> None:
    """
    Render performance summary section.
    
    Args:
        summary_data: Dictionary with performance summary data
    """
    st.subheader("🎯 Performance Summary")
    
    # Create tabs for different performance areas
    tab1, tab2, tab3 = st.tabs(["🚚 Delivery", "⭐ Satisfaction", "💰 Revenue"])
    
    with tab1:
        render_delivery_summary(summary_data.get("delivery", {}))
    
    with tab2:
        render_satisfaction_summary(summary_data.get("satisfaction", {}))
    
    with tab3:
        render_revenue_summary(summary_data.get("revenue", {}))

def render_delivery_summary(delivery_data: Dict[str, Any]) -> None:
    """Render delivery performance summary."""
    if not delivery_data:
        st.info("No delivery data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        on_time_rate = delivery_data.get("on_time_rate", 0)
        st.metric(
            "On-Time Rate",
            f"{on_time_rate:.1f}%",
            delta=f"{delivery_data.get('on_time_rate_change', 0):+.1f}%"
        )
    
    with col2:
        avg_delivery_days = delivery_data.get("avg_delivery_days", 0)
        st.metric(
            "Avg Delivery Days",
            f"{avg_delivery_days:.1f}",
            delta=f"{delivery_data.get('delivery_days_change', 0):+.1f}"
        )
    
    with col3:
        delayed_orders = delivery_data.get("delayed_orders", 0)
        st.metric(
            "Delayed Orders",
            f"{delayed_orders:,}",
            delta=f"{delivery_data.get('delayed_orders_change', 0):+,}"
        )

def render_satisfaction_summary(satisfaction_data: Dict[str, Any]) -> None:
    """Render customer satisfaction summary."""
    if not satisfaction_data:
        st.info("No satisfaction data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_rating = satisfaction_data.get("avg_rating", 0)
        st.metric(
            "Average Rating",
            f"{avg_rating:.2f}/5.0",
            delta=f"{satisfaction_data.get('rating_change', 0):+.2f}"
        )
    
    with col2:
        positive_reviews = satisfaction_data.get("positive_reviews_pct", 0)
        st.metric(
            "Positive Reviews",
            f"{positive_reviews:.1f}%",
            delta=f"{satisfaction_data.get('positive_reviews_change', 0):+.1f}%"
        )
    
    with col3:
        negative_reviews = satisfaction_data.get("negative_reviews_pct", 0)
        st.metric(
            "Negative Reviews",
            f"{negative_reviews:.1f}%",
            delta=f"{satisfaction_data.get('negative_reviews_change', 0):+.1f}%"
        )

def render_revenue_summary(revenue_data: Dict[str, Any]) -> None:
    """Render revenue summary."""
    if not revenue_data:
        st.info("No revenue data available")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        total_revenue = revenue_data.get("total_revenue", 0)
        st.metric(
            "Total Revenue",
            f"R${total_revenue:,.0f}",
            delta=f"{revenue_data.get('revenue_change_pct', 0):+.1f}%"
        )
    
    with col2:
        avg_order_value = revenue_data.get("avg_order_value", 0)
        st.metric(
            "Avg Order Value",
            f"R${avg_order_value:.2f}",
            delta=f"{revenue_data.get('aov_change_pct', 0):+.1f}%"
        )
    
    with col3:
        order_count = revenue_data.get("order_count", 0)
        st.metric(
            "Total Orders",
            f"{order_count:,}",
            delta=f"{revenue_data.get('order_count_change', 0):+,}"
        )

def render_alerts_section(alerts: List[Dict[str, Any]]) -> None:
    """
    Render alerts and notifications section.
    
    Args:
        alerts: List of alert dictionaries
    """
    if not alerts:
        return
    
    st.subheader("🚨 Alerts & Notifications")
    
    # Group alerts by severity
    critical_alerts = [a for a in alerts if a.get("severity") == "critical"]
    warning_alerts = [a for a in alerts if a.get("severity") == "warning"]
    info_alerts = [a for a in alerts if a.get("severity") == "info"]
    
    # Display critical alerts first
    for alert in critical_alerts:
        st.error(f"🔴 **{alert.get('title', 'Alert')}**: {alert.get('message', '')}")
    
    # Display warnings
    for alert in warning_alerts:
        st.warning(f"🟡 **{alert.get('title', 'Warning')}**: {alert.get('message', '')}")
    
    # Display info alerts
    for alert in info_alerts:
        st.info(f"🔵 **{alert.get('title', 'Info')}**: {alert.get('message', '')}")

def create_gauge_chart(value: float, title: str, min_val: float = 0, 
                      max_val: float = 100, target: Optional[float] = None) -> go.Figure:
    """
    Create a gauge chart for metrics.
    
    Args:
        value: Current value
        title: Chart title
        min_val: Minimum value for gauge
        max_val: Maximum value for gauge
        target: Target value line
        
    Returns:
        Plotly gauge chart figure
    """
    # Determine color based on value
    if value >= 80:
        color = COLOR_PALETTE["success"]
    elif value >= 60:
        color = COLOR_PALETTE["warning"]
    else:
        color = COLOR_PALETTE["warning"]
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        delta={'reference': target} if target else None,
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': color},
            'steps': [
                {'range': [min_val, max_val * 0.6], 'color': "lightgray"},
                {'range': [max_val * 0.6, max_val * 0.8], 'color': "yellow"},
                {'range': [max_val * 0.8, max_val], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': target
            } if target else None
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=0, r=0, t=40, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig
