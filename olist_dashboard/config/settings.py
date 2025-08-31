"""
Configuration settings for the Olist Dashboard application.
"""

import os
from typing import Dict, Any
import streamlit as st
from google.oauth2 import service_account
import json

def get_bigquery_credentials():
    """
    Get BigQuery credentials from multiple sources (environment variable, Streamlit secrets, or file path).
    
    Returns:
        google.oauth2.service_account.Credentials or None
    """
    # Try environment variable first
    if "GOOGLE_APPLICATION_CREDENTIALS" in os.environ:
        return service_account.Credentials.from_service_account_file(
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
        )
    
    # Try Streamlit secrets
    try:
        if hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            return service_account.Credentials.from_service_account_info(
                st.secrets["gcp_service_account"]
            )
    except Exception:
        pass
    
    # Try relative path
    try:
        credentials_path = os.path.join(os.getcwd(), "dsai-468212-f4762cc666a5.json")
        if os.path.exists(credentials_path):
            return service_account.Credentials.from_service_account_file(credentials_path)
    except Exception:
        pass
    
    return None

def get_project_id():
    """Get project ID from credentials or configuration."""
    # Try Streamlit secrets first
    try:
        if hasattr(st, "secrets") and "bigquery" in st.secrets:
            return st.secrets["bigquery"]["project_id"]
        elif hasattr(st, "secrets") and "gcp_service_account" in st.secrets:
            return st.secrets["gcp_service_account"]["project_id"]
    except Exception:
        pass
    
    # Try environment variable
    project_id = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if project_id:
        return project_id
    
    # Default fallback
    return "dsai-468212"

# BigQuery Configuration
BQ_CONFIG: Dict[str, Any] = {
    "project_id": get_project_id(),
    "dataset": "project-olist-470307.dbt_olist_stg",
    "location": "US",  # Default location for BigQuery
    "timeout": 60,  # Query timeout in seconds
    "credentials": get_bigquery_credentials(),
}

# Streamlit Configuration
STREAMLIT_CONFIG: Dict[str, Any] = {
    "page_title": "Olist Analytics Dashboard",
    "page_icon": "📊",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "max_width": 1200,  # Maximum width for the main container
}

# Cache Configuration
CACHE_CONFIG: Dict[str, Any] = {
    "ttl": 3600,  # 1 hour default cache TTL
    "max_entries": 100,
    "allow_output_mutation": True,
}

# Data Refresh Settings
DATA_REFRESH: Dict[str, Any] = {
    "batch_update_time": "06:00",  # UTC time for daily refresh
    "metrics_ttl": 14400,  # 4 hours for aggregated metrics
    "detail_ttl": 3600,  # 1 hour for detail views
}

# UI Constants
UI_CONFIG: Dict[str, Any] = {
    "sidebar_width": 300,
    "chart_height": 400,
    "table_height": 300,
    "date_format": "%Y-%m-%d",
    "datetime_format": "%Y-%m-%d %H:%M:%S",
    "primary_color": "#1f77b4",
    "secondary_color": "#ff7f0e",
    "sidebar_color": "#f0f2f6",
    "tab_background": "#ffffff",
    "text_secondary": "#666666",
}

# Performance Settings
PERFORMANCE_CONFIG: Dict[str, Any] = {
    "max_concurrent_users": 50,
    "memory_limit_gb": 2,
    "query_limit_mb": 100,
    "max_rows_display": 10000,
}

# Color Palette for Charts
COLOR_PALETTE: Dict[str, str] = {
    "primary": "#1f77b4",
    "secondary": "#ff7f0e", 
    "success": "#2ca02c",
    "warning": "#d62728",
    "info": "#9467bd",
    "light": "#c5c5c5",
    "dark": "#2f2f2f",
}

# Chart Themes
CHART_THEMES: Dict[str, Any] = {
    "plotly": {
        "layout": {
            "font": {"family": "Arial", "size": 12},
            "colorway": list(COLOR_PALETTE.values()),
            "plot_bgcolor": "rgba(0,0,0,0)",
            "paper_bgcolor": "rgba(0,0,0,0)",
        }
    },
    "altair": {
        "config": {
            "view": {"strokeWidth": 0},
            "axis": {"grid": False},
        }
    }
}

# Authentication (if needed)
AUTH_CONFIG: Dict[str, Any] = {
    "enabled": False,  # Set to True to enable authentication
    "method": "streamlit",  # Options: streamlit, oauth, custom
}

# Application Configuration
APP_CONFIG: Dict[str, Any] = {
    "version": "1.0.0",
    "environment": os.getenv("STREAMLIT_ENV", "development"),
    "debug": os.getenv("DEBUG", "false").lower() == "true",
    "max_file_uploader_size": 200,  # MB
    "session_timeout": 3600,  # seconds
    "auto_refresh": False,
}

def get_env_config() -> Dict[str, Any]:
    """Get environment-specific configuration."""
    env = os.getenv("STREAMLIT_ENV", "development")
    
    configs = {
        "development": {
            "debug": True,
            "cache_ttl": 300,  # 5 minutes for development
            "sample_data": True,
        },
        "staging": {
            "debug": True,
            "cache_ttl": 1800,  # 30 minutes for staging
            "sample_data": False,
        },
        "production": {
            "debug": False,
            "cache_ttl": 3600,  # 1 hour for production
            "sample_data": False,
        }
    }
    
    return configs.get(env, configs["development"])

def init_streamlit_config():
    """Initialize Streamlit page configuration."""
    st.set_page_config(
        page_title=STREAMLIT_CONFIG["page_title"],
        page_icon=STREAMLIT_CONFIG["page_icon"],
        layout=STREAMLIT_CONFIG["layout"],
        initial_sidebar_state=STREAMLIT_CONFIG["initial_sidebar_state"],
    )

# Google Cloud credentials path (if using service account)
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")

# BigQuery tables mapping
TABLES: Dict[str, str] = {
    "fact_order_items": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.fact_order_items",
    "dim_customer": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_customer",
    "dim_orders": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_orders",
    "dim_product": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_product",
    "dim_seller": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_seller",
    "dim_payment": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_payment",
    "dim_order_reviews": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_order_reviews",
    "dim_date": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_date",
    "dim_geolocation": f"{BQ_CONFIG['project_id']}.{BQ_CONFIG['dataset']}.dim_geolocation",
}
