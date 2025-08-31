"""
Sidebar component for navigation and global filters.
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

from ..config.settings import UI_CONFIG

def render_sidebar() -> Dict[str, Any]:
    """
    Render the sidebar with navigation and filters.
    
    Returns:
        Dictionary containing filter values and navigation state
    """
    with st.sidebar:
        # App Header
        st.title("📊 Olist Analytics")
        st.markdown("---")
        
        # Navigation Menu
        page = render_navigation()
        
        st.markdown("---")
        
        # Global Filters
        filters = render_global_filters()
        
        st.markdown("---")
        
        # Data Status
        render_data_status()
        
        # Cache Management
        render_cache_controls()
        
    return {
        "page": page,
        "filters": filters
    }

def render_navigation() -> str:
    """
    Render navigation menu.
    
    Returns:
        Selected page name
    """
    st.subheader("📋 Navigation")
    
    pages = {
        "📈 Executive Summary": "executive_summary",
        "🚚 Delivery Performance": "delivery_performance", 
        "⭐ Customer Satisfaction": "customer_satisfaction",
        "📦 Product Analysis": "product_analysis",
        "💳 Payment Insights": "payment_insights"
    }
    
    # Use radio buttons for navigation
    selected_page = st.radio(
        "Go to:",
        options=list(pages.keys()),
        index=0,
        label_visibility="collapsed"
    )
    
    return pages[selected_page]

def render_global_filters() -> Dict[str, Any]:
    """
    Render global filter controls.
    
    Returns:
        Dictionary of filter values
    """
    st.subheader("🔍 Filters")
    
    # Current Date Selector (for simulation purposes)
    st.markdown("**Analysis Date**")
    current_date = st.date_input(
        "Current date for analysis:",
        value=datetime(2018, 6, 1).date(),  # Default to June 2018
        min_value=datetime(2017, 1, 1).date(),
        max_value=datetime(2020, 12, 31).date(),
        help="Set the 'current' date for analysis. This affects relative date calculations and business logic."
    )
    
    # Date Range Filter
    st.markdown("**Date Range**")
    
    # Preset date ranges with custom defaults for Olist dataset
    date_presets = {
        "All Available Data": "all_data",
        "Full Dataset (2017-2018)": "full_dataset",
        "Last 7 days": 7,
        "Last 30 days": 30,
        "Last 90 days": 90,
        "Last 6 months": 180,
        "Last year": 365
    }
    
    preset = st.selectbox(
        "Quick select:",
        options=list(date_presets.keys()),
        index=1  # Default to "Full Dataset (2017-2018)"
    )
    
    # Calculate date range based on preset
    if preset == "All Available Data":
        # Use extended date range for all available data
        start_date = datetime(2016, 1, 1).date()  # Start earlier to capture all data
        end_date = datetime(2020, 12, 31).date()  # End later to capture all data
    elif preset == "Full Dataset (2017-2018)":
        # Use Olist dataset specific date range
        start_date = datetime(2017, 1, 1).date()
        end_date = datetime(2018, 9, 30).date()  # End of September 2018
    else:
        # Calculate relative date range based on selected current date
        end_date = current_date
        start_date = end_date - timedelta(days=date_presets[preset])
    
    # Allow custom date range
    col1, col2 = st.columns(2)
    
    # Set min/max dates based on selected preset
    if preset == "All Available Data":
        min_date = datetime(2016, 1, 1).date()
        max_date = datetime(2020, 12, 31).date()
    elif preset in ["Full Dataset (2017-2018)"]:
        min_date = datetime(2017, 1, 1).date()  # Minimum date for core Olist dataset
        max_date = datetime(2018, 9, 30).date()  # Maximum date for core Olist dataset
    else:
        # For relative dates, use current date as upper bound
        min_date = datetime(2016, 1, 1).date()
        max_date = current_date
    
    with col1:
        start_date = st.date_input(
            "From:",
            value=start_date,
            min_value=min_date,
            max_value=max_date
        )
    
    with col2:
        end_date = st.date_input(
            "To:",
            value=end_date,
            min_value=start_date,
            max_value=max_date
        )
    
    # Geographic Filters
    st.markdown("**Geography**")
    
    # State filter - in a real app, this would be populated from data
    default_states = ["All States", "SP", "RJ", "MG", "RS", "PR", "SC", "BA", "GO", "PE", "CE"]
    selected_states = st.multiselect(
        "States:",
        options=default_states,
        default=["All States"]
    )
    
    # Product Category Filters
    st.markdown("**Product Categories**")
    
    # Category filter - in a real app, this would be populated from data
    default_categories = [
        "All Categories", "bed_bath_table", "health_beauty", "sports_leisure",
        "furniture_decor", "computers_accessories", "housewares", "watches_gifts",
        "telephony", "garden_tools", "auto"
    ]
    selected_categories = st.multiselect(
        "Categories:",
        options=default_categories,
        default=["All Categories"]
    )
    
    # Performance Filters
    st.markdown("**Performance**")
    
    # Rating filter
    rating_range = st.slider(
        "Rating range:",
        min_value=1.0,
        max_value=5.0,
        value=(1.0, 5.0),
        step=0.1
    )
    
    # Delivery status filter
    delivery_status = st.selectbox(
        "Delivery status:",
        options=["All", "On Time", "Delayed"],
        index=0
    )
    
    return {
        "current_date": current_date.strftime("%Y-%m-%d"),
        "date_range": {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d")
        },
        "geography": {
            "states": selected_states if "All States" not in selected_states else [],
            "exclude_all_states": "All States" in selected_states
        },
        "categories": {
            "selected": selected_categories if "All Categories" not in selected_categories else [],
            "exclude_all_categories": "All Categories" in selected_categories
        },
        "performance": {
            "rating_range": rating_range,
            "delivery_status": delivery_status
        }
    }

def render_data_status():
    """Render data connection and freshness status."""
    st.subheader("📡 Data Status")
    
    # This would be connected to actual data status in a real app
    data_status = st.empty()
    
    # Simulate data status
    import random
    is_connected = random.choice([True, True, True, False])  # 75% chance of connection
    
    if is_connected:
        st.success("✅ Connected to BigQuery")
        last_update = datetime.now() - timedelta(minutes=random.randint(5, 120))
        st.info(f"🕐 Last updated: {last_update.strftime('%H:%M')}")
    else:
        st.error("❌ Connection issues")
        st.warning("Using cached data")
    
    # Data quality indicators
    with st.expander("Data Quality"):
        quality_metrics = {
            "Completeness": random.randint(85, 99),
            "Accuracy": random.randint(90, 99),
            "Timeliness": random.randint(80, 95)
        }
        
        for metric, value in quality_metrics.items():
            color = "green" if value >= 90 else "orange" if value >= 80 else "red"
            st.markdown(f"**{metric}**: :{color}[{value}%]")

def render_cache_controls():
    """Render cache management controls."""
    st.subheader("🗄️ Cache")
    
    # Cache statistics
    with st.expander("Cache Info"):
        # This would show real cache stats in a production app
        st.markdown("""
        **Hit Rate**: 87%  
        **Size**: 45 MB  
        **Files**: 23  
        **Last Cleared**: 2h ago
        """)
    
    # Cache controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Refresh", help="Refresh current page data"):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("🗑️ Clear All", help="Clear all cached data"):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.success("Cache cleared!")
            st.rerun()

def apply_filters_to_query(base_query: str, filters: Dict[str, Any]) -> str:
    """
    Apply sidebar filters to a SQL query.
    
    Args:
        base_query: Base SQL query string
        filters: Filter values from sidebar
        
    Returns:
        Modified query with filters applied
    """
    conditions = []
    
    # Date range filter
    date_range = filters.get("date_range", {})
    if date_range.get("start_date") and date_range.get("end_date"):
        conditions.append(
            f"o.order_purchase_timestamp >= '{date_range['start_date']}' "
            f"AND o.order_purchase_timestamp <= '{date_range['end_date']}'"
        )
    
    # State filter
    geography = filters.get("geography", {})
    if geography.get("states") and not geography.get("exclude_all_states"):
        states_list = "', '".join(geography["states"])
        conditions.append(f"c.customer_state IN ('{states_list}')")
    
    # Category filter
    categories = filters.get("categories", {})
    if categories.get("selected") and not categories.get("exclude_all_categories"):
        categories_list = "', '".join(categories["selected"])
        conditions.append(f"p.product_category_name_english IN ('{categories_list}')")
    
    # Rating filter
    performance = filters.get("performance", {})
    if performance.get("rating_range"):
        min_rating, max_rating = performance["rating_range"]
        conditions.append(f"r.review_score BETWEEN {min_rating} AND {max_rating}")
    
    # Delivery status filter
    delivery_status = performance.get("delivery_status")
    if delivery_status == "On Time":
        conditions.append("o.order_delivered_customer_date <= o.order_estimated_delivery_date")
    elif delivery_status == "Delayed":
        conditions.append("o.order_delivered_customer_date > o.order_estimated_delivery_date")
    
    # Add conditions to query
    if conditions:
        if "WHERE" in base_query.upper():
            # Query already has WHERE clause, add AND conditions
            base_query += " AND " + " AND ".join(conditions)
        else:
            # Add WHERE clause
            base_query += " WHERE " + " AND ".join(conditions)
    
    return base_query

def get_filter_summary(filters: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of applied filters.
    
    Args:
        filters: Filter values from sidebar
        
    Returns:
        Filter summary string
    """
    summary_parts = []
    
    # Current date for analysis
    current_date = filters.get("current_date")
    if current_date:
        summary_parts.append(f"📅 Analysis as of {current_date}")
    
    # Date range
    date_range = filters.get("date_range", {})
    if date_range.get("start_date") and date_range.get("end_date"):
        summary_parts.append(f"� Data: {date_range['start_date']} to {date_range['end_date']}")
    
    # Geography
    geography = filters.get("geography", {})
    if geography.get("states") and not geography.get("exclude_all_states"):
        count = len(geography["states"])
        summary_parts.append(f"🌎 {count} state{'s' if count > 1 else ''}")
    
    # Categories
    categories = filters.get("categories", {})
    if categories.get("selected") and not categories.get("exclude_all_categories"):
        count = len(categories["selected"])
        summary_parts.append(f"📦 {count} categor{'ies' if count > 1 else 'y'}")
    
    # Performance
    performance = filters.get("performance", {})
    if performance.get("delivery_status") != "All":
        summary_parts.append(f"🚚 {performance['delivery_status']} orders")
    
    if not summary_parts:
        return "📊 All data (no filters applied)"
    
    return " • ".join(summary_parts)
