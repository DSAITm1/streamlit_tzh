"""
BigQuery data loader and connection management for the Olist Dashboard.
"""

import logging
from typing import Optional, Dict, Any, List
import pandas as pd
import polars as pl
from google.cloud import bigquery
from google.cloud.exceptions import NotFound, Forbidden
import streamlit as st

from ..config.settings import BQ_CONFIG, CACHE_CONFIG
from ..config.queries import get_query

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BigQueryDataLoader:
    """
    Handles BigQuery connections and data loading operations.
    """
    
    def __init__(self):
        """Initialize BigQuery client."""
        self.client = None
        self.project_id = BQ_CONFIG["project_id"]
        self.dataset = BQ_CONFIG["dataset"]
        self.credentials = BQ_CONFIG.get("credentials")
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize BigQuery client with proper authentication."""
        try:
            if self.credentials:
                # Determine credential type for logging
                cred_type = "OAuth" if hasattr(self.credentials, 'refresh_token') else "Service Account"
                
                self.client = bigquery.Client(
                    project=self.project_id,
                    credentials=self.credentials,
                    location=BQ_CONFIG.get("location", "US")
                )
                logger.info(f"BigQuery client initialized for project: {self.project_id} using {cred_type}")
            else:
                # Fallback to default credentials
                self.client = bigquery.Client(
                    project=self.project_id,
                    location=BQ_CONFIG.get("location", "US")
                )
                logger.info(f"BigQuery client initialized for project: {self.project_id} using default credentials")
        except Exception as e:
            logger.error(f"Failed to initialize BigQuery client: {str(e)}")
            st.error(f"Failed to connect to BigQuery: {str(e)}")
            self.client = None
    
    def test_connection(self) -> bool:
        """
        Test BigQuery connection and dataset access.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        if not self.client:
            return False
        
        try:
            # Try to access the dataset
            dataset_ref = f"{self.project_id}.{self.dataset}"
            dataset = self.client.get_dataset(dataset_ref)
            logger.info(f"Successfully connected to dataset: {dataset_ref}")
            return True
        except NotFound:
            logger.error(f"Dataset not found: {self.project_id}.{self.dataset}")
            return False
        except Forbidden:
            logger.error("Access denied to BigQuery dataset")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def execute_query(_self, query: str, use_polars: bool = True) -> Optional[pl.DataFrame]:
        """
        Execute BigQuery SQL query and return results.
        
        Args:
            query: SQL query string
            use_polars: Whether to return Polars DataFrame (default) or Pandas
            
        Returns:
            DataFrame with query results or None if failed
        """
        if not _self.client:
            logger.error("BigQuery client not initialized")
            return None
        
        try:
            # Configure query job
            job_config = bigquery.QueryJobConfig()
            job_config.timeout = BQ_CONFIG.get("timeout", 60)
            
            # Execute query
            logger.info("Executing BigQuery...")
            query_job = _self.client.query(query, job_config=job_config)
            
            # Get results
            results = query_job.result()
            
            # Convert to DataFrame
            if use_polars:
                # Convert to Pandas first, then to Polars
                df_pandas = results.to_dataframe()
                if df_pandas.empty:
                    return pl.DataFrame()
                df = pl.from_pandas(df_pandas)
            else:
                df = results.to_dataframe()
            
            logger.info(f"Query executed successfully, returned {len(df)} rows")
            return df
            
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            st.error(f"Database query failed: {str(e)}")
            return None
    
    def get_table_schema(self, table_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get schema information for a BigQuery table.
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of field information or None if failed
        """
        if not self.client:
            return None
        
        try:
            table_ref = f"{self.project_id}.{self.dataset}.{table_name}"
            table = self.client.get_table(table_ref)
            
            schema_info = []
            for field in table.schema:
                schema_info.append({
                    "name": field.name,
                    "type": field.field_type,
                    "mode": field.mode,
                    "description": field.description or ""
                })
            
            return schema_info
            
        except Exception as e:
            logger.error(f"Failed to get schema for {table_name}: {str(e)}")
            return None
    
    def get_executive_metrics(self) -> Optional[pl.DataFrame]:
        """Get key executive metrics."""
        query = get_query("executive", "key_metrics")
        return self.execute_query(query)
    
    def get_daily_trends(self, days: int = 90) -> Optional[pl.DataFrame]:
        """Get daily trends for the specified number of days."""
        query = get_query("executive", "daily_trends")
        return self.execute_query(query)
    
    def get_geographic_performance(self) -> Optional[pl.DataFrame]:
        """Get geographic performance metrics."""
        query = get_query("executive", "geographic_performance")
        return self.execute_query(query)
    
    def get_delivery_metrics(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get delivery performance metrics for date range."""
        query = get_query(
            "delivery", 
            "delivery_metrics", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_delivery_by_state(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get delivery performance by state."""
        query = get_query(
            "delivery", 
            "delivery_by_state", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_delivery_time_distribution(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get delivery time distribution."""
        query = get_query(
            "delivery", 
            "delivery_time_distribution", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_rating_analysis(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get customer rating analysis."""
        query = get_query(
            "satisfaction", 
            "rating_analysis", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_satisfaction_vs_delivery(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get satisfaction vs delivery performance."""
        query = get_query(
            "satisfaction", 
            "satisfaction_vs_delivery", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_category_satisfaction(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get satisfaction by product category."""
        query = get_query(
            "satisfaction", 
            "category_satisfaction", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_weight_impact(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get product weight impact analysis."""
        query = get_query(
            "product", 
            "weight_impact", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_category_performance(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get product category performance."""
        query = get_query(
            "product", 
            "category_performance", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_payment_method_analysis(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get payment method analysis."""
        query = get_query(
            "payment", 
            "payment_method_analysis", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)
    
    def get_installment_analysis(self, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
        """Get installment payment analysis."""
        query = get_query(
            "payment", 
            "installment_analysis", 
            start_date=start_date, 
            end_date=end_date
        )
        return self.execute_query(query)

# Global data loader instance
@st.cache_resource
def get_data_loader() -> BigQueryDataLoader:
    """Get cached BigQuery data loader instance."""
    return BigQueryDataLoader()

def check_data_connection() -> bool:
    """Check if data connection is working."""
    loader = get_data_loader()
    return loader.test_connection()

def get_sample_data() -> Dict[str, pl.DataFrame]:
    """
    Get sample data for development/testing purposes.
    Returns mock data when BigQuery is not available.
    """
    # Check if we should use sample data (for development/testing)
    use_sample_data = st.session_state.get("use_sample_data", False)
    
    if use_sample_data:
        # Return mock data for development
        sample_data = {
            "executive_metrics": pl.DataFrame({
                "on_time_delivery_rate": [87.3],
                "avg_rating": [4.2],
                "total_revenue": [125000.50],
                "active_customers": [45123],
                "total_orders": [78456]
            }),
            "daily_trends": pl.DataFrame({
                "date_value": pd.date_range("2024-01-01", periods=30, freq="D"),
                "daily_orders": range(100, 130),
                "daily_revenue": [1000 + i * 50 for i in range(30)],
                "daily_avg_rating": [4.0 + (i % 10) * 0.1 for i in range(30)],
                "daily_on_time_rate": [85 + (i % 15) for i in range(30)]
            })
        }
        return sample_data
    
    return {}
