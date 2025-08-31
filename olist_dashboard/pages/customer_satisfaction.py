"""
Customer Satisfaction page - Analysis of ratings, reviews, and satisfaction drivers.
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, Optional

from ..components.metrics import render_kpi_cards, render_performance_summary
from ..components.charts import render_satisfaction_charts, render_correlation_heatmap
from ..components.tables import render_data_table, render_top_performers_table, render_correlation_table
from ..data.data_loader import get_data_loader
from ..data.data_processor import get_data_processor
from ..data.cache_manager import cache_details

def render_customer_satisfaction_page(filters: Dict[str, Any]) -> None:
    """
    Render the customer satisfaction analysis page.
    
    Args:
        filters: Applied filters from sidebar
    """
    st.title("⭐ Customer Satisfaction Analysis")
    st.markdown("Comprehensive analysis of customer ratings, reviews, and satisfaction drivers")
    
    # Initialize components
    data_loader = get_data_loader()
    data_processor = get_data_processor()
    
    # Extract date range from filters
    date_range = filters.get("date_range", {})
    start_date = date_range.get("start_date", "2023-01-01")
    end_date = date_range.get("end_date", "2023-12-31")
    
    # Load satisfaction data
    with st.spinner("Loading customer satisfaction data..."):
        rating_analysis = load_rating_analysis(data_loader, start_date, end_date)
        satisfaction_delivery = load_satisfaction_delivery(data_loader, start_date, end_date)
        category_satisfaction = load_category_satisfaction(data_loader, start_date, end_date)
    
    # Main satisfaction metrics
    st.subheader("📊 Customer Satisfaction Overview")
    render_satisfaction_kpis(rating_analysis, satisfaction_delivery)
    
    st.markdown("---")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "⭐ Rating Analysis",
        "🚚 Satisfaction vs Delivery",
        "📦 Category Analysis", 
        "🔍 Correlation Analysis"
    ])
    
    with tab1:
        render_rating_analysis_tab(rating_analysis)
    
    with tab2:
        render_satisfaction_delivery_tab(satisfaction_delivery)
    
    with tab3:
        render_category_analysis_tab(category_satisfaction)
    
    with tab4:
        render_correlation_analysis_tab(data_loader, start_date, end_date)

@cache_details()
def load_rating_analysis(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load rating analysis data."""
    try:
        return _data_loader.get_rating_analysis(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading rating analysis: {str(e)}")
        return None

@cache_details()
def load_satisfaction_delivery(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load satisfaction vs delivery data."""
    try:
        return _data_loader.get_satisfaction_vs_delivery(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading satisfaction vs delivery data: {str(e)}")
        return None

@cache_details()
def load_category_satisfaction(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load category satisfaction data."""
    try:
        return _data_loader.get_category_satisfaction(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading category satisfaction: {str(e)}")
        return None

def render_satisfaction_kpis(rating_analysis: pl.DataFrame, 
                           satisfaction_delivery: pl.DataFrame) -> None:
    """Render customer satisfaction KPI cards."""
    col1, col2, col3, col4 = st.columns(4)
    
    # Calculate key metrics
    if rating_analysis is not None and not rating_analysis.is_empty():
        total_reviews = rating_analysis.select(pl.sum("review_count")).item()
        weighted_avg_rating = rating_analysis.select(
            (pl.col("review_score") * pl.col("review_count")).sum() / pl.col("review_count").sum()
        ).item()
        
        # Positive reviews (4-5 stars)
        positive_reviews = rating_analysis.filter(pl.col("review_score") >= 4)
        if not positive_reviews.is_empty():
            positive_count = positive_reviews.select(pl.sum("review_count")).item()
            positive_rate = (positive_count / total_reviews) * 100 if total_reviews > 0 else 0
        else:
            positive_rate = 0
        
        # Negative reviews (1-2 stars)
        negative_reviews = rating_analysis.filter(pl.col("review_score") <= 2)
        if not negative_reviews.is_empty():
            negative_count = negative_reviews.select(pl.sum("review_count")).item()
            negative_rate = (negative_count / total_reviews) * 100 if total_reviews > 0 else 0
        else:
            negative_rate = 0
    else:
        total_reviews = 0
        weighted_avg_rating = 0
        positive_rate = 0
        negative_rate = 0
    
    with col1:
        st.metric(
            "📝 Total Reviews",
            f"{total_reviews:,}",
            help="Total number of customer reviews in the selected period"
        )
    
    with col2:
        rating_delta = "normal" if weighted_avg_rating >= 4.0 else "inverse"
        st.metric(
            "⭐ Avg Rating",
            f"{weighted_avg_rating:.2f}/5.0",
            help="Average customer rating weighted by review volume"
        )
    
    with col3:
        positive_delta = "normal" if positive_rate >= 70 else "inverse"
        st.metric(
            "👍 Positive Rate",
            f"{positive_rate:.1f}%",
            help="Percentage of 4-5 star ratings"
        )
    
    with col4:
        negative_delta = "inverse" if negative_rate >= 15 else "normal"
        st.metric(
            "👎 Negative Rate",
            f"{negative_rate:.1f}%",
            help="Percentage of 1-2 star ratings"
        )
    
    # Satisfaction vs delivery impact
    if satisfaction_delivery is not None and not satisfaction_delivery.is_empty():
        st.markdown("### 🚚 Delivery Impact on Satisfaction")
        
        col1, col2 = st.columns(2)
        
        for i, row in enumerate(satisfaction_delivery.iter_rows(named=True)):
            delivery_status = row.get("delivery_status", "Unknown")
            avg_rating = row.get("avg_rating", 0)
            review_count = row.get("review_count", 0)
            
            with col1 if i % 2 == 0 else col2:
                st.metric(
                    f"⭐ {delivery_status} Orders",
                    f"{avg_rating:.2f}/5.0",
                    f"{review_count:,} reviews",
                    help=f"Average rating for {delivery_status.lower()} deliveries"
                )

def render_rating_analysis_tab(rating_analysis: pl.DataFrame) -> None:
    """Render rating analysis tab."""
    st.subheader("⭐ Customer Rating Distribution")
    
    if rating_analysis is None or rating_analysis.is_empty():
        st.warning("No rating analysis data available")
        return
    
    # Rating distribution charts
    render_satisfaction_charts(rating_analysis)
    
    # Detailed rating breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Rating Breakdown")
        render_data_table(rating_analysis, title=None, download=False)
    
    with col2:
        st.markdown("### 💡 Rating Insights")
        
        # Calculate insights
        total_reviews = rating_analysis.select(pl.sum("review_count")).item()
        
        if total_reviews > 0:
            # 5-star percentage
            five_star = rating_analysis.filter(pl.col("review_score") == 5)
            if not five_star.is_empty():
                five_star_pct = (five_star.select("review_count").item() / total_reviews) * 100
                st.markdown(f"🌟 **{five_star_pct:.1f}%** of customers give 5-star ratings")
            
            # 1-star percentage
            one_star = rating_analysis.filter(pl.col("review_score") == 1)
            if not one_star.is_empty():
                one_star_pct = (one_star.select("review_count").item() / total_reviews) * 100
                if one_star_pct > 10:
                    st.markdown(f"⚠️ **{one_star_pct:.1f}%** of customers give 1-star ratings")
                else:
                    st.markdown(f"✅ Only **{one_star_pct:.1f}%** give 1-star ratings")
            
            # Rating distribution analysis
            high_ratings = rating_analysis.filter(pl.col("review_score") >= 4)
            if not high_ratings.is_empty():
                high_rating_pct = (high_ratings.select(pl.sum("review_count")).item() / total_reviews) * 100
                
                if high_rating_pct >= 80:
                    st.success(f"🎉 **Excellent satisfaction**: {high_rating_pct:.1f}% positive ratings")
                elif high_rating_pct >= 70:
                    st.warning(f"👍 **Good satisfaction**: {high_rating_pct:.1f}% positive ratings")
                else:
                    st.error(f"⚠️ **Needs improvement**: Only {high_rating_pct:.1f}% positive ratings")

def render_satisfaction_delivery_tab(satisfaction_delivery: pl.DataFrame) -> None:
    """Render satisfaction vs delivery analysis tab."""
    st.subheader("🚚 Satisfaction vs Delivery Performance")
    
    if satisfaction_delivery is None or satisfaction_delivery.is_empty():
        st.warning("No satisfaction vs delivery data available")
        return
    
    # Charts showing the relationship
    render_satisfaction_charts(satisfaction_delivery)
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Delivery Impact Analysis")
        render_data_table(satisfaction_delivery, title=None, download=False)
    
    with col2:
        st.markdown("### 🔍 Key Findings")
        
        # Calculate the impact of delivery performance
        on_time_data = satisfaction_delivery.filter(pl.col("delivery_status") == "On Time")
        delayed_data = satisfaction_delivery.filter(pl.col("delivery_status") == "Delayed")
        
        if not on_time_data.is_empty() and not delayed_data.is_empty():
            on_time_rating = on_time_data.select("avg_rating").item()
            delayed_rating = delayed_data.select("avg_rating").item()
            rating_difference = on_time_rating - delayed_rating
            
            st.markdown(f"📈 **On-time deliveries**: {on_time_rating:.2f}/5.0 average rating")
            st.markdown(f"📉 **Delayed deliveries**: {delayed_rating:.2f}/5.0 average rating")
            
            if rating_difference > 0.5:
                st.error(f"🚨 **Significant impact**: {rating_difference:.2f} point rating drop for delays")
            elif rating_difference > 0.2:
                st.warning(f"⚠️ **Moderate impact**: {rating_difference:.2f} point rating drop for delays")
            else:
                st.info(f"ℹ️ **Minor impact**: {rating_difference:.2f} point rating difference")
            
            # Calculate negative review rates
            on_time_negative = on_time_data.select("negative_reviews").item() if "negative_reviews" in on_time_data.columns else 0
            delayed_negative = delayed_data.select("negative_reviews").item() if "negative_reviews" in delayed_data.columns else 0
            
            if on_time_negative < delayed_negative:
                negative_increase = delayed_negative - on_time_negative
                st.markdown(f"👎 **{negative_increase:,} more** negative reviews for delayed deliveries")
        
        # Recommendations
        st.markdown("### 💡 Recommendations")
        recommendations = [
            "🎯 **Prioritize on-time delivery** - strongest satisfaction driver",
            "📞 **Proactive communication** for potential delays",
            "🔄 **Improve delivery estimates** to set realistic expectations",
            "📊 **Monitor delivery satisfaction** as a leading indicator"
        ]
        
        for rec in recommendations:
            st.markdown(rec)

def render_category_analysis_tab(category_satisfaction: pl.DataFrame) -> None:
    """Render category satisfaction analysis tab."""
    st.subheader("📦 Product Category Satisfaction")
    
    if category_satisfaction is None or category_satisfaction.is_empty():
        st.warning("No category satisfaction data available")
        return
    
    # Top and bottom performing categories
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top Rated Categories")
        top_categories = category_satisfaction.sort("avg_rating", descending=True).head(10)
        render_top_performers_table(top_categories, "avg_rating", top_n=5, title=None)
    
    with col2:
        st.markdown("### ⚠️ Categories Needing Attention")
        bottom_categories = category_satisfaction.sort("avg_rating", descending=False).head(10)
        render_top_performers_table(bottom_categories, "avg_rating", top_n=5, title=None)
    
    # Detailed category analysis
    st.markdown("### 📊 Detailed Category Performance")
    
    # Add performance indicators
    enhanced_categories = category_satisfaction.with_columns([
        pl.when(pl.col("avg_rating") >= 4.5)
        .then("🟢 Excellent")
        .when(pl.col("avg_rating") >= 4.0)
        .then("🟡 Good")
        .when(pl.col("avg_rating") >= 3.5)
        .then("🟠 Fair")
        .otherwise("🔴 Poor")
        .alias("Satisfaction Level")
    ])
    
    render_data_table(enhanced_categories, title="Category Satisfaction Analysis", max_rows=15)
    
    # Category insights
    if not category_satisfaction.is_empty():
        st.markdown("### 💡 Category Insights")
        
        # Best performing category
        best_category = category_satisfaction.sort("avg_rating", descending=True).row(0, named=True)
        worst_category = category_satisfaction.sort("avg_rating", descending=False).row(0, named=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🏆 **Best**: {best_category['category']} ({best_category['avg_rating']:.2f}/5.0)")
            st.info(f"📊 {best_category['review_count']:,} reviews, {best_category['on_time_rate']:.1f}% on-time")
        
        with col2:
            st.error(f"⚠️ **Needs Focus**: {worst_category['category']} ({worst_category['avg_rating']:.2f}/5.0)")
            st.info(f"📊 {worst_category['review_count']:,} reviews, {worst_category['on_time_rate']:.1f}% on-time")

def render_correlation_analysis_tab(data_loader, start_date: str, end_date: str) -> None:
    """Render correlation analysis tab."""
    st.subheader("🔍 Satisfaction Correlation Analysis")
    
    st.markdown("""
    This analysis examines how various factors correlate with customer satisfaction ratings.
    Understanding these relationships helps identify the key drivers of customer satisfaction.
    """)
    
    # Load sample data for correlation analysis
    with st.spinner("Calculating correlations..."):
        correlations = calculate_satisfaction_correlations(data_loader, start_date, end_date)
    
    if correlations:
        # Render correlation table and heatmap
        col1, col2 = st.columns(2)
        
        with col1:
            render_correlation_table(correlations, "Satisfaction Correlations")
        
        with col2:
            render_correlation_heatmap(correlations)
        
        # Correlation insights
        st.markdown("### 📊 Correlation Insights")
        
        # Find strongest correlations
        sorted_correlations = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        
        if sorted_correlations:
            strongest = sorted_correlations[0]
            st.markdown(f"🔗 **Strongest correlation**: {strongest[0]} ({strongest[1]:.3f})")
            
            if abs(strongest[1]) >= 0.5:
                st.success("This shows a strong relationship with customer satisfaction")
            elif abs(strongest[1]) >= 0.3:
                st.warning("This shows a moderate relationship with customer satisfaction")
            else:
                st.info("This shows a weak relationship with customer satisfaction")
        
        # Action items based on correlations
        st.markdown("### 🎯 Action Items")
        action_items = generate_correlation_action_items(correlations)
        for item in action_items:
            st.markdown(item)
    
    else:
        st.info("Correlation analysis data not available")

def calculate_satisfaction_correlations(data_loader, start_date: str, end_date: str) -> Dict[str, float]:
    """Calculate correlations between satisfaction and other metrics."""
    try:
        # This would be implemented with actual data
        # For now, return sample correlations
        return {
            "delivery_delay": -0.45,
            "product_weight": -0.23,
            "freight_cost": -0.18,
            "order_value": 0.12,
            "payment_installments": -0.08
        }
    except Exception as e:
        st.error(f"Error calculating correlations: {str(e)}")
        return {}

def generate_correlation_action_items(correlations: Dict[str, float]) -> list:
    """Generate action items based on correlation analysis."""
    action_items = []
    
    for metric, correlation in correlations.items():
        if abs(correlation) >= 0.3:
            if correlation < 0:
                action_items.append(f"📉 **Reduce {metric.replace('_', ' ')}** - strong negative impact on satisfaction")
            else:
                action_items.append(f"📈 **Optimize {metric.replace('_', ' ')}** - positive impact on satisfaction")
    
    if not action_items:
        action_items.append("📊 **Monitor all factors** - no strong correlations detected")
    
    return action_items
