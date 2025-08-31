"""
Executive Summary page - High-level KPIs and dashboard overview.
"""

import streamlit as st
import polars as pl
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from ..components.metrics import render_kpi_cards, render_trend_metrics, render_performance_summary
from ..components.charts import render_time_series_chart, render_correlation_heatmap
from ..components.tables import render_top_performers_table
from ..data.data_loader import get_data_loader
from ..data.data_processor import get_data_processor
from ..data.cache_manager import get_cache_manager, cache_metrics

def render_executive_summary_page(filters: Dict[str, Any]) -> None:
    """
    Render the executive summary page.
    
    Args:
        filters: Applied filters from sidebar
    """
    st.title("📈 Executive Summary")
    st.markdown("High-level KPIs and performance overview for Olist operations")
    
    # Initialize data loader
    data_loader = get_data_loader()
    data_processor = get_data_processor()
    
    # Check data connection
    if not data_loader.test_connection():
        render_connection_error()
        return
    
    # Load key metrics
    with st.spinner("Loading executive metrics..."):
        start_date = filters.get("date_range", {}).get("start_date", "2017-01-01")
        end_date = filters.get("date_range", {}).get("end_date", "2018-09-30")
        
        metrics_data = load_executive_metrics(data_loader, start_date, end_date)
        trends_data = load_trends_data(data_loader, start_date, end_date)
        geographic_data = load_geographic_data(data_loader, start_date, end_date)
    
    if metrics_data is None:
        st.error("Failed to load executive metrics")
        return
    
    # Render main KPI cards
    render_main_kpis(metrics_data)
    
    st.markdown("---")
    
    # Create two columns for charts and metrics
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Trends section
        if trends_data is not None and not trends_data.is_empty():
            render_trend_metrics(trends_data)
            st.markdown("### 📊 Performance Trends")
            render_time_series_chart(
                trends_data, 
                "date_value", 
                "daily_on_time_rate",
                "On-Time Delivery Rate Trend",
                "#1f77b4"
            )
        else:
            st.info("Trend data not available")
    
    with col2:
        # Performance summary
        render_performance_overview(metrics_data, trends_data)
    
    st.markdown("---")
    
    # Geographic performance section
    st.subheader("🗺️ Geographic Performance")
    if geographic_data is not None and not geographic_data.is_empty():
        render_geographic_performance(geographic_data)
    else:
        st.info("Geographic data not available")
    
    # Alerts and recommendations
    render_alerts_and_recommendations(metrics_data, trends_data)

@cache_metrics()
def load_executive_metrics(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load key executive metrics."""
    try:
        return _data_loader.get_executive_metrics(start_date=start_date, end_date=end_date)
    except Exception as e:
        st.error(f"Error loading executive metrics: {str(e)}")
        return None

@cache_metrics()
def load_trends_data(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load trends data."""
    try:
        return _data_loader.get_daily_trends(start_date=start_date, end_date=end_date)
    except Exception as e:
        st.warning(f"Error loading trends data: {str(e)}")
        return None

@cache_metrics()
def load_geographic_data(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load geographic data."""
    try:
        return _data_loader.get_geographic_performance(start_date=start_date, end_date=end_date)
    except Exception as e:
        st.warning(f"Error loading geographic data: {str(e)}")
        return None

def render_main_kpis(metrics_data: pl.DataFrame) -> None:
    """Render main KPI cards."""
    if metrics_data.is_empty():
        st.warning("No metrics data available")
        return
    
    # Convert to dictionary for KPI cards
    metrics_dict = {}
    if len(metrics_data) > 0:
        row = metrics_data.row(0, named=True)
        metrics_dict = {
            "on_time_delivery_rate": row.get("on_time_delivery_rate"),
            "avg_rating": row.get("avg_rating"),
            "total_revenue": row.get("total_revenue"),
            "active_customers": row.get("active_customers"),
            "total_orders": row.get("total_orders")
        }
    
    render_kpi_cards(metrics_dict, columns=4)

def render_performance_overview(metrics_data: pl.DataFrame, trends_data: pl.DataFrame) -> None:
    """Render performance overview sidebar."""
    st.subheader("🎯 Performance Overview")
    
    # Performance indicators
    if metrics_data is not None and not metrics_data.is_empty():
        row = metrics_data.row(0, named=True)
        
        # On-time delivery status
        on_time_rate = row.get("on_time_delivery_rate", 0)
        if on_time_rate is None:
            on_time_rate = 0
        if on_time_rate >= 90:
            st.success(f"🟢 Delivery: {on_time_rate:.1f}% (Excellent)")
        elif on_time_rate >= 80:
            st.warning(f"🟡 Delivery: {on_time_rate:.1f}% (Good)")
        else:
            st.error(f"🔴 Delivery: {on_time_rate:.1f}% (Needs Improvement)")
        
        # Customer satisfaction status
        avg_rating = row.get("avg_rating", 0)
        if avg_rating is None:
            avg_rating = 0
        if avg_rating >= 4.5:
            st.success(f"🟢 Satisfaction: {avg_rating:.2f}/5.0 (Excellent)")
        elif avg_rating >= 4.0:
            st.warning(f"🟡 Satisfaction: {avg_rating:.2f}/5.0 (Good)")
        else:
            st.error(f"🔴 Satisfaction: {avg_rating:.2f}/5.0 (Needs Improvement)")
        
        # Revenue growth (simplified calculation)
        total_revenue = row.get("total_revenue", 0)
        if total_revenue is None:
            total_revenue = 0
        st.info(f"💰 Revenue: R${total_revenue:,.0f}")
        
        # Customer engagement
        active_customers = row.get("active_customers", 0)
        total_orders = row.get("total_orders", 0)
        if active_customers > 0:
            orders_per_customer = total_orders / active_customers
            st.info(f"👥 Engagement: {orders_per_customer:.1f} orders/customer")
    
    # Key insights
    with st.expander("📊 Key Insights"):
        st.markdown("""
        **Top Insights:**
        - Monitor delivery performance closely
        - Customer satisfaction correlates with delivery times
        - Geographic variations in performance
        - Seasonal trends in order volume
        
        **Action Items:**
        - Focus on delayed delivery routes
        - Improve heavy product logistics
        - Enhance customer communication
        """)

def render_geographic_performance(geographic_data: pl.DataFrame) -> None:
    """Render geographic performance section."""
    # Top performing states
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Top States by Orders**")
        render_top_performers_table(
            geographic_data, 
            "order_count", 
            top_n=5
        )
    
    with col2:
        st.markdown("**⭐ Top States by Rating**")
        # Filter states with minimum order volume for rating ranking
        min_orders_for_rating = 100
        filtered_data = geographic_data.filter(pl.col("order_count") >= min_orders_for_rating)
        if not filtered_data.is_empty():
            render_top_performers_table(
                filtered_data,
                "avg_rating",
                top_n=5
            )
        else:
            st.info("Insufficient data for rating analysis")

def render_alerts_and_recommendations(metrics_data: pl.DataFrame, trends_data: pl.DataFrame) -> None:
    """Render alerts and recommendations section."""
    st.subheader("🚨 Alerts & Recommendations")
    
    alerts = generate_alerts(metrics_data, trends_data)
    
    if alerts:
        for alert in alerts:
            if alert["type"] == "critical":
                st.error(f"🔴 **{alert['title']}**: {alert['message']}")
            elif alert["type"] == "warning":
                st.warning(f"🟡 **{alert['title']}**: {alert['message']}")
            else:
                st.info(f"🔵 **{alert['title']}**: {alert['message']}")
    else:
        st.success("✅ No critical alerts at this time")
    
    # Recommendations
    with st.expander("💡 Recommendations"):
        recommendations = generate_recommendations(metrics_data)
        for rec in recommendations:
            st.markdown(f"- {rec}")

def generate_alerts(metrics_data: pl.DataFrame, trends_data: pl.DataFrame) -> list:
    """Generate alerts based on performance data."""
    alerts = []
    
    if metrics_data is not None and not metrics_data.is_empty():
        row = metrics_data.row(0, named=True)
        
        # Delivery performance alert
        on_time_rate = row.get("on_time_delivery_rate", 0)
        if on_time_rate is None:
            on_time_rate = 0
        if on_time_rate < 75:
            alerts.append({
                "type": "critical",
                "title": "Low Delivery Performance",
                "message": f"On-time delivery rate is {on_time_rate:.1f}%, below target of 90%"
            })
        elif on_time_rate < 85:
            alerts.append({
                "type": "warning",
                "title": "Delivery Performance Warning",
                "message": f"On-time delivery rate is {on_time_rate:.1f}%, approaching critical threshold"
            })
        
        # Customer satisfaction alert
        avg_rating = row.get("avg_rating", 0)
        if avg_rating is None:
            avg_rating = 0
        if avg_rating < 3.5:
            alerts.append({
                "type": "critical",
                "title": "Low Customer Satisfaction",
                "message": f"Average rating is {avg_rating:.2f}/5.0, immediate action needed"
            })
        elif avg_rating < 4.0:
            alerts.append({
                "type": "warning",
                "title": "Customer Satisfaction Warning",
                "message": f"Average rating is {avg_rating:.2f}/5.0, monitor closely"
            })
    
    return alerts

def generate_recommendations(metrics_data: pl.DataFrame) -> list:
    """Generate recommendations based on performance data."""
    recommendations = []
    
    if metrics_data is not None and not metrics_data.is_empty():
        row = metrics_data.row(0, named=True)
        
        on_time_rate = row.get("on_time_delivery_rate", 0)
        if on_time_rate is None:
            on_time_rate = 0
        avg_rating = row.get("avg_rating", 0)
        if avg_rating is None:
            avg_rating = 0
        
        if on_time_rate < 90:
            recommendations.append(
                "**Improve Delivery Performance**: Focus on route optimization and carrier partnerships"
            )
        
        if avg_rating < 4.5:
            recommendations.append(
                "**Enhance Customer Experience**: Implement proactive communication about delivery status"
            )
        
        recommendations.extend([
            "**Monitor Geographic Variations**: Identify underperforming regions for targeted improvements",
            "**Analyze Product Categories**: Focus on categories with high delivery delays",
            "**Optimize Heavy Product Logistics**: Develop specialized handling for large/heavy items",
            "**Implement Predictive Analytics**: Use data to predict and prevent delivery delays"
        ])
    
    return recommendations

def render_connection_error() -> None:
    """Render error message for connection issues."""
    st.error("🔌 Unable to connect to data source")
    st.markdown("""
    **Possible solutions:**
    - Check your internet connection
    - Verify BigQuery credentials
    - Contact system administrator
    
    **Using cached data if available**
    """)
    
    # Try to load cached/sample data
    try:
        from ..data.data_loader import get_sample_data
        sample_data = get_sample_data()
        if sample_data:
            st.info("📋 Displaying sample data for demonstration")
            # Render with sample data
            if "executive_metrics" in sample_data:
                render_kpi_cards(sample_data["executive_metrics"].row(0, named=True))
    except Exception:
        st.warning("No cached data available")
