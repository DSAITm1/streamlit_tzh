"""
Main Streamlit application entry point.
Multi-page Olist analytics dashboard with navigation and global filtering.
"""

import streamlit as st
import polars as pl
from datetime import datetime
from typing import Dict, Any

# Page imports
from olist_dashboard.pages.executive_summary import render_executive_summary_page
from olist_dashboard.pages.delivery_performance import render_delivery_performance_page
from olist_dashboard.pages.customer_satisfaction import render_customer_satisfaction_page
from olist_dashboard.pages.product_analysis import render_product_analysis_page
from olist_dashboard.pages.payment_insights import render_payment_insights_page

# Component imports
from olist_dashboard.components.sidebar import render_sidebar
from olist_dashboard.config.settings import STREAMLIT_CONFIG, UI_CONFIG, APP_CONFIG
from olist_dashboard.data.cache_manager import initialize_cache

def main():
    """Main application entry point."""
    
    # Configure Streamlit page
    st.set_page_config(
        page_title=STREAMLIT_CONFIG["page_title"],
        page_icon=STREAMLIT_CONFIG["page_icon"],
        layout=STREAMLIT_CONFIG["layout"],
        initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"]
    )
    
    # Initialize cache
    initialize_cache()
    
    # Custom CSS for styling
    apply_custom_styling()
    
    # Render sidebar and get selected page + filters
    sidebar_data = render_sidebar()
    selected_page = sidebar_data["page"]
    global_filters = sidebar_data["filters"]
    auth_status = sidebar_data["auth_status"]
    
    # Main content area
    render_main_content(selected_page, global_filters, auth_status)
    
    # Footer
    render_footer()

def apply_custom_styling():
    """Apply custom CSS styling to the application."""
    st.markdown(
        f"""
        <style>
        /* Main app styling */
        .main .block-container {{
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: {STREAMLIT_CONFIG['max_width']}px;
        }}
        
        /* Header styling */
        .main-header {{
            background: linear-gradient(90deg, {UI_CONFIG['primary_color']}, {UI_CONFIG['secondary_color']});
            padding: 1rem;
            border-radius: 0.5rem;
            margin-bottom: 2rem;
            color: white;
        }}
        
        /* Metric cards styling */
        .metric-card {{
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid {UI_CONFIG['primary_color']};
            margin-bottom: 1rem;
        }}
        
        /* Chart containers */
        .chart-container {{
            background: white;
            padding: 1rem;
            border-radius: 0.5rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }}
        
        /* Sidebar styling */
        .css-1d391kg {{
            background-color: {UI_CONFIG['sidebar_color']};
        }}
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 2px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background-color: {UI_CONFIG['tab_background']};
            border-radius: 0.5rem 0.5rem 0 0;
            padding: 0.5rem 1rem;
        }}
        
        .stTabs [aria-selected="true"] {{
            background-color: {UI_CONFIG['primary_color']};
            color: white;
        }}
        
        /* Success/warning/error message styling */
        .stSuccess, .stWarning, .stError, .stInfo {{
            border-radius: 0.5rem;
            border: none;
            margin: 1rem 0;
        }}
        
        /* Button styling */
        .stButton > button {{
            background-color: {UI_CONFIG['primary_color']};
            color: white;
            border: none;
            border-radius: 0.5rem;
            padding: 0.5rem 1rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            background-color: {UI_CONFIG['secondary_color']};
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        
        /* Data table styling */
        .dataframe {{
            border-radius: 0.5rem;
            border: 1px solid #e0e0e0;
        }}
        
        /* Hide Streamlit default elements */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Loading spinner styling */
        .stSpinner > div > div {{
            border-top-color: {UI_CONFIG['primary_color']};
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def render_main_content(selected_page: str, global_filters: Dict[str, Any], auth_status: Dict[str, Any]):
    """
    Render the main content area based on selected page.
    
    Args:
        selected_page: The currently selected page (internal name)
        global_filters: Applied global filters
        auth_status: Authentication status information
    """
    
    # Check authentication before rendering content
    if not auth_status.get("is_authenticated", False):
        st.error("🔐 Authentication Required")
        st.info("Please authenticate using the sidebar to access BigQuery data.")
        
        # Show sample/mock data option
        st.markdown("---")
        st.subheader("Demo Mode")
        st.info("You can view the dashboard with sample data while authentication is set up.")
        
        if st.button("🎭 View with Sample Data"):
            st.session_state["use_sample_data"] = True
            st.rerun()
        
        return
    
    # Remove sample data mode if user is authenticated
    if "use_sample_data" in st.session_state:
        del st.session_state["use_sample_data"]
    
    # Show authentication info briefly
    auth_method = auth_status.get("auth_method", "unknown")
    if auth_method == "oauth":
        st.success(f"🔐 Authenticated via OAuth ({auth_status.get('user_email', 'Unknown User')})")
    else:
        st.info("🔑 Authenticated via Service Account")
    
    # Page routing using internal page names
    try:
        if selected_page == "executive_summary":
            render_executive_summary_page(global_filters)
            
        elif selected_page == "delivery_performance":
            render_delivery_performance_page(global_filters)
            
        elif selected_page == "customer_satisfaction":
            render_customer_satisfaction_page(global_filters)
            
        elif selected_page == "product_analysis":
            render_product_analysis_page(global_filters)
            
        elif selected_page == "payment_insights":
            render_payment_insights_page(global_filters)
            
        else:
            # Fallback to executive summary
            st.warning(f"Page '{selected_page}' not found. Redirecting to Executive Summary.")
            render_executive_summary_page(global_filters)
            
    except Exception as e:
        st.error(f"Error rendering page '{selected_page}': {str(e)}")
        st.info("Please try refreshing the page or check your data connection.")
        
        # Debug information in development mode
        if APP_CONFIG.get("debug_mode", False):
            st.exception(e)
        
        # Debug information in development mode
        if APP_CONFIG.get("debug_mode", False):
            st.exception(e)

def render_footer():
    """Render application footer."""
    st.markdown("---")
    
    col1, col2, col3 = st.columns([2, 1, 2])
    
    with col1:
        st.markdown(
            f"""
            <div style='text-align: left; color: {UI_CONFIG['text_secondary']}; font-size: 0.85rem;'>
                📊 <b>Olist Analytics Dashboard</b><br>
                Powered by BigQuery, Streamlit & Polars
            </div>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        # Cache status indicator
        if st.button("🔄 Clear Cache", help="Clear all cached data"):
            st.cache_data.clear()
            st.success("Cache cleared successfully!")
            st.rerun()
    
    with col3:
        st.markdown(
            f"""
            <div style='text-align: right; color: {UI_CONFIG['text_secondary']}; font-size: 0.85rem;'>
                Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br>
                Data source: Google BigQuery
            </div>
            """,
            unsafe_allow_html=True
        )

def show_app_info():
    """Show application information in sidebar."""
    with st.sidebar:
        st.markdown("---")
        
        with st.expander("ℹ️ About This Dashboard"):
            st.markdown(
                f"""
                ### 📊 Olist Analytics Dashboard
                
                **Version**: {APP_CONFIG.get('version', '1.0.0')}
                
                **Data Source**: 
                - Google BigQuery
                - Dataset: `{APP_CONFIG.get('dataset_id', 'project-olist-470307.dbt_olist_stg')}`
                
                **Technologies**:
                - 🐍 Python 3.12+
                - 📊 Streamlit
                - ⚡ Polars
                - 📈 Plotly/Altair
                - ☁️ Google Cloud BigQuery
                
                **Features**:
                - Real-time data analysis
                - Interactive visualizations
                - Advanced filtering
                - Export capabilities
                - Multi-level caching
                
                **Business Areas**:
                - Executive KPIs
                - Delivery Performance
                - Customer Satisfaction
                - Product Analysis
                - Payment Insights
                """
            )
        
        # Performance indicators
        with st.expander("⚡ Performance Metrics"):
            # Cache statistics (simplified since st.cache_data.get_stats() doesn't exist)
            st.info("Cache statistics not available in current Streamlit version")
            
            # Memory usage (mock data - replace with actual monitoring)
            st.metric("Active Queries", "5", help="Number of active BigQuery connections")
            st.metric("Response Time", "1.2s", help="Average query response time")

def handle_errors():
    """Global error handler for the application."""
    try:
        main()
    except Exception as e:
        st.error("🚨 Application Error")
        st.error(f"An unexpected error occurred: {str(e)}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Refresh Page"):
                st.rerun()
        
        with col2:
            if st.button("🧹 Clear Cache & Restart"):
                st.cache_data.clear()
                st.rerun()
        
        # Show debug information if in development mode
        if APP_CONFIG.get("debug_mode", False):
            with st.expander("🔍 Debug Information"):
                st.exception(e)

if __name__ == "__main__":
    # Show app info in sidebar
    show_app_info()
    
    # Run application with error handling
    handle_errors()
