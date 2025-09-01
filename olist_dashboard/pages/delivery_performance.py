"""
Delivery Performance page - Analysis of delivery metrics and geographic performance.
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, Optional

from ..components.metrics import render_kpi_cards, create_gauge_chart
from ..components.charts import render_delivery_performance_charts
from ..components.tables import render_data_table, render_top_performers_table, render_comparison_table
from ..data.data_loader import get_data_loader
from ..data.data_processor import get_data_processor
from ..data.cache_manager import cache_details

def render_delivery_performance_page(filters: Dict[str, Any]) -> None:
    """
    Render the delivery performance analysis page.
    
    Args:
        filters: Applied filters from sidebar
    """
    st.title("🚚 Delivery Performance Analysis")
    st.markdown("Comprehensive analysis of delivery metrics, geographic performance, and route efficiency")
    
    # Initialize components
    data_loader = get_data_loader()
    data_processor = get_data_processor()
    
    # Extract date range from filters
    date_range = filters.get("date_range", {})
    start_date = date_range.get("start_date", "2023-01-01")
    end_date = date_range.get("end_date", "2023-12-31")
    
    # Load delivery data
    with st.spinner("Loading delivery performance data..."):
        delivery_metrics = load_delivery_metrics(data_loader, start_date, end_date)
        delivery_by_state = load_delivery_by_state(data_loader, start_date, end_date)
        delivery_distribution = load_delivery_distribution(data_loader, start_date, end_date)
    
    # Main metrics section
    st.subheader("📊 Key Delivery Metrics")
    render_delivery_kpis(delivery_metrics)
    
    st.markdown("---")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Performance Trends", 
        "🗺️ Geographic Analysis", 
        "⏱️ Time Analysis",
        "🔍 Detailed Data"
    ])
    
    with tab1:
        render_performance_trends_tab(delivery_metrics, delivery_distribution)
    
    with tab2:
        render_geographic_analysis_tab(delivery_by_state)
    
    with tab3:
        render_time_analysis_tab(delivery_distribution, delivery_metrics)
    
    with tab4:
        render_detailed_data_tab(delivery_by_state, filters)

@cache_details()
def load_delivery_metrics(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load delivery performance metrics."""
    try:
        return _data_loader.get_delivery_metrics(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading delivery metrics: {str(e)}")
        return None

@cache_details()
def load_delivery_by_state(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load delivery performance by state."""
    try:
        return _data_loader.get_delivery_by_state(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading state delivery data: {str(e)}")
        return None

@cache_details()
def load_delivery_distribution(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load delivery time distribution."""
    try:
        return _data_loader.get_delivery_time_distribution(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading delivery distribution: {str(e)}")
        return None

def render_delivery_kpis(delivery_metrics: pl.DataFrame) -> None:
    """Render delivery KPI cards."""
    if delivery_metrics is None or delivery_metrics.is_empty():
        st.warning("No delivery metrics available")
        return
    
    # Extract metrics from the first row
    row = delivery_metrics.row(0, named=True)
    
    metrics_dict = {
        "total_orders": row.get("total_orders", 0),
        "on_time_orders": row.get("on_time_orders", 0),
        "on_time_percentage": row.get("on_time_percentage", 0),
        "avg_delivery_days": row.get("avg_delivery_days", 0),
        "avg_delay_days": row.get("avg_delay_days", 0)
    }
    
    # Custom KPI configuration for delivery metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "📦 Total Orders",
            f"{metrics_dict['total_orders']:,}",
            help="Total number of delivered orders in the selected period"
        )
    
    with col2:
        on_time_pct = metrics_dict['on_time_percentage']
        delta_color = "normal" if on_time_pct >= 85 else "inverse"
        st.metric(
            "✅ On-Time Rate",
            f"{on_time_pct:.1f}%",
            f"Target: 90%",
            delta_color=delta_color,
            help="Percentage of orders delivered by the estimated date"
        )
    
    with col3:
        avg_days = metrics_dict['avg_delivery_days']
        st.metric(
            "⏱️ Avg Delivery Days",
            f"{avg_days:.1f}",
            help="Average time from order to delivery"
        )
    
    with col4:
        delay_days = metrics_dict['avg_delay_days']
        delta_color = "inverse" if delay_days > 0 else "normal"
        st.metric(
            "⚠️ Avg Delay",
            f"{delay_days:.1f} days",
            delta_color=delta_color,
            help="Average delay for late deliveries (negative means early)"
        )
    
    # Delivery performance gauge
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        gauge_fig = create_gauge_chart(
            value=on_time_pct,
            title="On-Time Delivery Performance",
            min_val=0,
            max_val=100,
            target=90
        )
        st.plotly_chart(gauge_fig, use_container_width=True)

def render_performance_trends_tab(delivery_metrics: pl.DataFrame, 
                                 delivery_distribution: pl.DataFrame) -> None:
    """Render performance trends analysis."""
    st.subheader("📈 Delivery Performance Trends")
    
    if delivery_distribution is not None and not delivery_distribution.is_empty():
        # Delivery time distribution chart
        render_delivery_performance_charts(delivery_distribution)
    else:
        st.info("Delivery distribution data not available")
    
    # Performance insights
    if delivery_metrics is not None and not delivery_metrics.is_empty():
        row = delivery_metrics.row(0, named=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 💡 Performance Insights")
            
            on_time_pct = row.get("on_time_percentage", 0)
            avg_delay = row.get("avg_delay_days", 0)
            
            insights = []
            
            if on_time_pct >= 90:
                insights.append("🟢 **Excellent delivery performance** - exceeding target")
            elif on_time_pct >= 80:
                insights.append("🟡 **Good delivery performance** - close to target")
            else:
                insights.append("🔴 **Delivery performance needs improvement** - below target")
            
            if avg_delay > 2:
                insights.append(f"⚠️ **High average delay** of {avg_delay:.1f} days")
            elif avg_delay > 0:
                insights.append(f"⚡ **Moderate delays** averaging {avg_delay:.1f} days")
            else:
                insights.append("✅ **Deliveries typically on-time or early**")
            
            for insight in insights:
                st.markdown(insight)
        
        with col2:
            st.markdown("### 🎯 Recommendations")
            
            recommendations = []
            
            if on_time_pct < 85:
                recommendations.append("🚛 **Optimize delivery routes** for better efficiency")
                recommendations.append("📞 **Improve carrier partnerships** and communication")
            
            if avg_delay > 1:
                recommendations.append("📋 **Review estimation algorithms** for more accurate ETAs")
                recommendations.append("🔄 **Implement real-time tracking** for proactive updates")
            
            recommendations.extend([
                "📊 **Monitor seasonal patterns** for capacity planning",
                "🎯 **Focus on underperforming regions** identified in geographic analysis"
            ])
            
            for rec in recommendations:
                st.markdown(rec)

def render_geographic_analysis_tab(delivery_by_state: pl.DataFrame) -> None:
    """Render geographic analysis."""
    st.subheader("🗺️ Geographic Performance Analysis")
    
    if delivery_by_state is None or delivery_by_state.is_empty():
        st.warning("No geographic delivery data available")
        return
    
    # Top and bottom performing states
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top Performing States")
        top_states = delivery_by_state.sort("on_time_rate", descending=True).head(10)
        render_top_performers_table(top_states, "on_time_rate", top_n=5, title=None)
    
    with col2:
        st.markdown("### ⚠️ States Needing Attention")
        bottom_states = delivery_by_state.sort("on_time_rate", descending=False).head(10)
        render_top_performers_table(bottom_states, "avg_delivery_days", top_n=5, title=None)
    
    # Detailed state analysis
    st.markdown("### 📊 Detailed State Performance")
    
    # Filter for states with significant volume
    significant_states = delivery_by_state.filter(pl.col("order_count") >= 50)
    
    if not significant_states.is_empty():
        # Add performance categories using map_elements
        def categorize_performance(rate):
            if rate >= 90:
                return "🟢 Excellent"
            elif rate >= 80:
                return "🟡 Good"
            elif rate >= 70:
                return "🟠 Fair"
            else:
                return "🔴 Poor"
        
        significant_states = significant_states.with_columns(
            pl.col("on_time_rate").map_elements(categorize_performance, return_dtype=pl.String).alias("Performance Category")
        )
        
        render_data_table(
            significant_states,
            title="State Performance Summary (Min 50 orders)",
            max_rows=20
        )
    else:
        st.info("Insufficient data for detailed state analysis")

def render_time_analysis_tab(delivery_distribution: pl.DataFrame, 
                           delivery_metrics: pl.DataFrame) -> None:
    """Render time-based analysis."""
    st.subheader("⏱️ Delivery Time Analysis")
    
    if delivery_distribution is not None and not delivery_distribution.is_empty():
        # Time distribution insights
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Delivery Time Breakdown")
            render_data_table(delivery_distribution, title=None, download=False)
        
        with col2:
            st.markdown("### 💡 Time Analysis Insights")
            
            # Calculate insights from distribution data
            total_orders = delivery_distribution.select(pl.sum("order_count")).item()
            
            if total_orders > 0:
                # Fast deliveries (1-7 days)
                fast_deliveries = delivery_distribution.filter(
                    pl.col("delivery_time_bucket") == "1-7 days"
                )
                if not fast_deliveries.is_empty():
                    fast_pct = (fast_deliveries.select("order_count").item() / total_orders) * 100
                    st.markdown(f"⚡ **{fast_pct:.1f}%** of orders delivered within 1 week")
                
                # Slow deliveries (30+ days)
                slow_deliveries = delivery_distribution.filter(
                    pl.col("delivery_time_bucket") == "30+ days"
                )
                if not slow_deliveries.is_empty():
                    slow_pct = (slow_deliveries.select("order_count").item() / total_orders) * 100
                    if slow_pct > 5:
                        st.markdown(f"⚠️ **{slow_pct:.1f}%** of orders take 30+ days")
                    else:
                        st.markdown(f"✅ Only **{slow_pct:.1f}%** of orders take 30+ days")
    
    # Seasonal analysis placeholder
    st.markdown("### 📅 Seasonal Patterns")
    st.info("💡 **Future Enhancement**: Seasonal delivery pattern analysis will show how delivery performance varies by month, holidays, and special events.")

def render_detailed_data_tab(delivery_by_state: pl.DataFrame, filters: Dict[str, Any]) -> None:
    """Render detailed data exploration."""
    st.subheader("🔍 Detailed Delivery Data")
    
    if delivery_by_state is None or delivery_by_state.is_empty():
        st.warning("No detailed delivery data available")
        return
    
    # Filter summary
    st.markdown("### 📋 Applied Filters")
    date_range = filters.get("date_range", {})
    st.info(f"📅 Date Range: {date_range.get('start_date')} to {date_range.get('end_date')}")
    
    # Detailed state data with interactive filtering
    st.markdown("### 📊 Interactive Data Exploration")
    
    from ..components.tables import render_table_with_filters
    
    filterable_columns = ["customer_state", "seller_state"]
    filtered_data = render_table_with_filters(
        delivery_by_state,
        title="Delivery Performance by State Pairs",
        filterable_columns=filterable_columns
    )
    
    # Data export options
    if not filtered_data.is_empty():
        st.markdown("### 📥 Export Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📊 Export to CSV"):
                csv_data = filtered_data.to_pandas().to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv_data,
                    "delivery_performance.csv",
                    "text/csv"
                )
        
        with col2:
            st.info("💡 Additional export formats available in full data table")
        
        with col3:
            if st.button("🔄 Refresh Data"):
                st.cache_data.clear()
                st.rerun()
