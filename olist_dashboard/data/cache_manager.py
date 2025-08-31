"""
Cache management for the Olist Dashboard application.
Implements multi-level caching strategies for optimal performance.
"""

import logging
from typing import Optional, Dict, Any, Callable
import streamlit as st
import polars as pl
from datetime import datetime, timedelta
import hashlib
import pickle
import os

from ..config.settings import CACHE_CONFIG, DATA_REFRESH

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Manages caching strategies for different types of data and operations.
    """
    
    def __init__(self):
        """Initialize cache manager."""
        self.cache_dir = ".streamlit_cache"
        self.ensure_cache_directory()
    
    def ensure_cache_directory(self):
        """Ensure cache directory exists."""
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir, exist_ok=True)
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        # Create a string representation of all arguments
        key_string = str(args) + str(sorted(kwargs.items()))
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cache_file_path(self, cache_key: str) -> str:
        """Get full path for cache file."""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _is_cache_valid(self, cache_file: str, ttl_seconds: int) -> bool:
        """Check if cache file is still valid based on TTL."""
        if not os.path.exists(cache_file):
            return False
        
        file_age = datetime.now() - datetime.fromtimestamp(os.path.getmtime(cache_file))
        return file_age.total_seconds() < ttl_seconds
    
    @st.cache_data(ttl=DATA_REFRESH["metrics_ttl"])
    def cache_executive_metrics(_self, data: pl.DataFrame) -> pl.DataFrame:
        """Cache executive metrics with longer TTL."""
        return data
    
    @st.cache_data(ttl=DATA_REFRESH["detail_ttl"])
    def cache_detail_data(_self, data: pl.DataFrame) -> pl.DataFrame:
        """Cache detailed data with shorter TTL."""
        return data
    
    @st.cache_data(ttl=CACHE_CONFIG["ttl"])
    def cache_chart_data(_self, data: pl.DataFrame, chart_type: str) -> pl.DataFrame:
        """Cache chart data with default TTL."""
        return data
    
    def save_to_disk_cache(self, key: str, data: Any, ttl_seconds: int = None) -> bool:
        """
        Save data to disk cache.
        
        Args:
            key: Cache key
            data: Data to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_file = self._get_cache_file_path(key)
            
            cache_data = {
                'data': data,
                'timestamp': datetime.now(),
                'ttl': ttl_seconds or CACHE_CONFIG["ttl"]
            }
            
            with open(cache_file, 'wb') as f:
                pickle.dump(cache_data, f)
            
            logger.info(f"Data cached to disk with key: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to disk cache: {str(e)}")
            return False
    
    def load_from_disk_cache(self, key: str) -> Optional[Any]:
        """
        Load data from disk cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached data if valid, None otherwise
        """
        try:
            cache_file = self._get_cache_file_path(key)
            
            if not os.path.exists(cache_file):
                return None
            
            with open(cache_file, 'rb') as f:
                cache_data = pickle.load(f)
            
            # Check if cache is still valid
            ttl_seconds = cache_data.get('ttl', CACHE_CONFIG["ttl"])
            timestamp = cache_data.get('timestamp')
            
            if timestamp and datetime.now() - timestamp > timedelta(seconds=ttl_seconds):
                # Cache expired, remove file
                os.remove(cache_file)
                return None
            
            logger.info(f"Data loaded from disk cache with key: {key}")
            return cache_data['data']
            
        except Exception as e:
            logger.error(f"Failed to load from disk cache: {str(e)}")
            return None
    
    def clear_expired_cache(self):
        """Clear all expired cache files."""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            
            cleared_count = 0
            for cache_file in cache_files:
                file_path = os.path.join(self.cache_dir, cache_file)
                
                try:
                    with open(file_path, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    ttl_seconds = cache_data.get('ttl', CACHE_CONFIG["ttl"])
                    timestamp = cache_data.get('timestamp')
                    
                    if timestamp and datetime.now() - timestamp > timedelta(seconds=ttl_seconds):
                        os.remove(file_path)
                        cleared_count += 1
                        
                except Exception:
                    # If we can't read the cache file, remove it
                    os.remove(file_path)
                    cleared_count += 1
            
            if cleared_count > 0:
                logger.info(f"Cleared {cleared_count} expired cache files")
            
        except Exception as e:
            logger.error(f"Failed to clear expired cache: {str(e)}")
    
    def clear_all_cache(self):
        """Clear all cache files."""
        try:
            # Clear Streamlit cache
            st.cache_data.clear()
            st.cache_resource.clear()
            
            # Clear disk cache
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            for cache_file in cache_files:
                os.remove(os.path.join(self.cache_dir, cache_file))
            
            logger.info("All cache cleared")
            
        except Exception as e:
            logger.error(f"Failed to clear cache: {str(e)}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        try:
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.pkl')]
            
            total_files = len(cache_files)
            total_size = sum(
                os.path.getsize(os.path.join(self.cache_dir, f)) 
                for f in cache_files
            )
            
            # Check cache hit rate (simplified)
            valid_files = 0
            for cache_file in cache_files:
                file_path = os.path.join(self.cache_dir, cache_file)
                try:
                    with open(file_path, 'rb') as f:
                        cache_data = pickle.load(f)
                    
                    ttl_seconds = cache_data.get('ttl', CACHE_CONFIG["ttl"])
                    timestamp = cache_data.get('timestamp')
                    
                    if timestamp and datetime.now() - timestamp <= timedelta(seconds=ttl_seconds):
                        valid_files += 1
                        
                except Exception:
                    continue
            
            return {
                'total_files': total_files,
                'valid_files': valid_files,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'hit_rate': round((valid_files / total_files * 100) if total_files > 0 else 0, 1)
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {str(e)}")
            return {}

def smart_cache_query(cache_manager: CacheManager, query_func: Callable, 
                     cache_key: str, ttl: int = None, **kwargs) -> Optional[pl.DataFrame]:
    """
    Smart caching wrapper for query functions.
    
    Args:
        cache_manager: CacheManager instance
        query_func: Function to execute if cache miss
        cache_key: Key for caching
        ttl: Time to live in seconds
        **kwargs: Arguments for query function
        
    Returns:
        Query results from cache or fresh execution
    """
    # Try to load from cache first
    cached_data = cache_manager.load_from_disk_cache(cache_key)
    if cached_data is not None:
        return cached_data
    
    # Cache miss, execute query
    try:
        result = query_func(**kwargs)
        
        # Save to cache if successful
        if result is not None and not result.is_empty():
            cache_manager.save_to_disk_cache(cache_key, result, ttl)
        
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {str(e)}")
        return None

# Global cache manager instance
@st.cache_resource
def get_cache_manager() -> CacheManager:
    """Get cached CacheManager instance."""
    return CacheManager()

# Cache decorators for common use cases
def cache_metrics(ttl: int = DATA_REFRESH["metrics_ttl"]):
    """Decorator for caching metrics data."""
    def decorator(func):
        return st.cache_data(ttl=ttl)(func)
    return decorator

def cache_details(ttl: int = DATA_REFRESH["detail_ttl"]):
    """Decorator for caching detailed data."""
    def decorator(func):
        return st.cache_data(ttl=ttl)(func)
    return decorator

def cache_charts(ttl: int = CACHE_CONFIG["ttl"]):
    """Decorator for caching chart data."""
    def decorator(func):
        return st.cache_data(ttl=ttl)(func)
    return decorator

def initialize_cache() -> CacheManager:
    """
    Initialize cache system for the application.
    
    Returns:
        CacheManager: Configured cache manager instance
    """
    cache_manager = get_cache_manager()
    
    # Clear expired cache on startup
    cache_manager.clear_expired_cache()
    
    # Log cache initialization
    logger.info("Cache system initialized successfully")
    
    return cache_manager
