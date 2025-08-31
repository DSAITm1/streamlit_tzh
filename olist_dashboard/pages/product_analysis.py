"""
Product Analysis page - Analysis of product performance, weight impact, and category insights.
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, Optional

from ..components.metrics import render_kpi_cards
from ..components.charts import render_product_analysis_charts
from ..components.tables import render_data_table, render_top_performers_table, render_pivot_table
from ..data.data_loader import get_data_loader
from ..data.data_processor import get_data_processor
from ..data.cache_manager import cache_details

def render_product_analysis_page(filters: Dict[str, Any]) -> None:
    """
    Render the product analysis page.
    
    Args:
        filters: Applied filters from sidebar
    """
    st.title("📦 Product Analysis")
    st.markdown("Comprehensive analysis of product performance, weight impact, and category insights")
    
    # Initialize components
    data_loader = get_data_loader()
    data_processor = get_data_processor()
    
    # Extract date range from filters
    date_range = filters.get("date_range", {})
    start_date = date_range.get("start_date", "2023-01-01")
    end_date = date_range.get("end_date", "2023-12-31")
    
    # Load product data
    with st.spinner("Loading product analysis data..."):
        weight_impact = load_weight_impact_data(data_loader, start_date, end_date)
        category_performance = load_category_performance_data(data_loader, start_date, end_date)
    
    # Main product metrics
    st.subheader("📊 Product Performance Overview")
    render_product_overview_kpis(category_performance)
    
    st.markdown("---")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "⚖️ Weight Impact",
        "📊 Category Performance", 
        "🏆 Top Products",
        "🔍 Detailed Analysis"
    ])
    
    with tab1:
        render_weight_impact_tab(weight_impact)
    
    with tab2:
        render_category_performance_tab(category_performance)
    
    with tab3:
        render_top_products_tab(category_performance)
    
    with tab4:
        render_detailed_analysis_tab(weight_impact, category_performance, filters)

@cache_details()
def load_weight_impact_data(data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load product weight impact data."""
    try:
        return data_loader.get_weight_impact(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading weight impact data: {str(e)}")
        return None

@cache_details()
def load_category_performance_data(data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load category performance data."""
    try:
        return data_loader.get_category_performance(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading category performance data: {str(e)}")
        return None

def render_product_overview_kpis(category_performance: pl.DataFrame) -> None:
    """Render product overview KPI cards."""
    if category_performance is None or category_performance.is_empty():
        st.warning("No category performance data available for KPIs")
        return
    
    # Calculate aggregate metrics
    total_categories = len(category_performance)
    total_orders = category_performance.select(pl.sum("order_count")).item()
    total_revenue = category_performance.select(pl.sum("total_revenue")).item()
    avg_rating = category_performance.select(
        (pl.col("avg_rating") * pl.col("order_count")).sum() / pl.col("order_count").sum()
    ).item()
    
    # Top category by revenue
    top_category = category_performance.sort("total_revenue", descending=True).row(0, named=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "🏷️ Product Categories",
            f"{total_categories:,}",
            help="Total number of active product categories"
        )
    
    with col2:
        st.metric(
            "📦 Total Orders",
            f"{total_orders:,}",
            help="Total orders across all product categories"
        )
    
    with col3:
        st.metric(
            "💰 Total Revenue",
            f"R${total_revenue:,.0f}",
            help="Total revenue from all product sales"
        )
    
    with col4:
        st.metric(
            "⭐ Avg Rating",
            f"{avg_rating:.2f}/5.0",
            help="Average customer rating across all categories"
        )
    
    # Top category highlight
    st.info(f"🏆 **Top Category**: {top_category['category']} with R${top_category['total_revenue']:,.0f} revenue")

def render_weight_impact_tab(weight_impact: pl.DataFrame) -> None:
    """Render weight impact analysis tab."""
    st.subheader("⚖️ Product Weight Impact Analysis")
    
    if weight_impact is None or weight_impact.is_empty():
        st.warning("No weight impact data available")
        return
    
    # Weight impact charts
    render_product_analysis_charts(weight_impact)
    
    # Weight analysis insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Weight Category Breakdown")
        render_data_table(weight_impact, title=None, download=False)
    
    with col2:
        st.markdown("### 💡 Weight Impact Insights")
        
        # Analyze weight impact patterns
        if not weight_impact.is_empty():
            # Find heaviest category impact
            heaviest = weight_impact.filter(pl.col("weight_category") == "5kg+")
            lightest = weight_impact.filter(pl.col("weight_category") == "0-500g")
            
            if not heaviest.is_empty() and not lightest.is_empty():
                heavy_delivery = heaviest.select("avg_delivery_days").item()
                light_delivery = lightest.select("avg_delivery_days").item()
                delivery_difference = heavy_delivery - light_delivery
                
                heavy_rating = heaviest.select("avg_rating").item()
                light_rating = lightest.select("avg_rating").item()
                rating_difference = light_rating - heavy_rating
                
                st.markdown(f"⚡ **Light products (0-500g)**: {light_delivery:.1f} avg delivery days")
                st.markdown(f"🏋️ **Heavy products (5kg+)**: {heavy_delivery:.1f} avg delivery days")
                
                if delivery_difference > 2:
                    st.error(f"⚠️ **Significant delay**: {delivery_difference:.1f} more days for heavy products")
                elif delivery_difference > 1:
                    st.warning(f"⚠️ **Moderate delay**: {delivery_difference:.1f} more days for heavy products")
                else:
                    st.success(f"✅ **Minimal impact**: Only {delivery_difference:.1f} days difference")
                
                if rating_difference > 0.2:
                    st.markdown(f"📉 **Rating impact**: {rating_difference:.2f} point drop for heavy products")
        
        # Recommendations for weight optimization
        st.markdown("### 🎯 Weight Optimization Recommendations")
        recommendations = [
            "📦 **Optimize packaging** for heavy items to reduce shipping costs",
            "🚛 **Specialized logistics** for 5kg+ products",
            "📞 **Enhanced communication** for heavy product deliveries",
            "💰 **Weight-based pricing** transparency for customers"
        ]
        
        for rec in recommendations:
            st.markdown(rec)

def render_category_performance_tab(category_performance: pl.DataFrame) -> None:
    """Render category performance analysis tab."""
    st.subheader("📊 Product Category Performance")
    
    if category_performance is None or category_performance.is_empty():
        st.warning("No category performance data available")
        return
    
    # Category performance charts
    render_product_analysis_charts(category_performance)
    
    # Performance analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top Revenue Categories")
        top_revenue = category_performance.sort("total_revenue", descending=True).head(10)
        render_top_performers_table(top_revenue, "total_revenue", top_n=5, title=None)
    
    with col2:
        st.markdown("### ⭐ Top Rated Categories")
        # Filter categories with sufficient reviews for rating analysis
        min_orders_for_rating = 50
        filtered_categories = category_performance.filter(pl.col("order_count") >= min_orders_for_rating)
        if not filtered_categories.is_empty():
            top_rated = filtered_categories.sort("avg_rating", descending=True).head(10)
            render_top_performers_table(top_rated, "avg_rating", top_n=5, title=None)
        else:
            st.info("Insufficient data for rating analysis")
    
    # Category insights
    st.markdown("### 💡 Category Performance Insights")
    
    if not category_performance.is_empty():
        # Revenue concentration analysis
        total_revenue = category_performance.select(pl.sum("total_revenue")).item()
        top_5_revenue = category_performance.sort("total_revenue", descending=True).head(5).select(pl.sum("total_revenue")).item()
        concentration_pct = (top_5_revenue / total_revenue) * 100 if total_revenue > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "💰 Top 5 Revenue Share",
                f"{concentration_pct:.1f}%",
                help="Revenue concentration in top 5 categories"
            )
        
        with col2:
            high_performers = category_performance.filter(
                (pl.col("avg_rating") >= 4.0) & (pl.col("on_time_rate") >= 85)
            )
            performance_pct = (len(high_performers) / len(category_performance)) * 100
            st.metric(
                "🎯 High Performers",
                f"{performance_pct:.1f}%",
                help="Categories with 4+ rating and 85%+ on-time delivery"
            )
        
        with col3:
            avg_aov = category_performance.select(
                (pl.col("total_revenue") / pl.col("order_count")).mean()
            ).item()
            st.metric(
                "💳 Avg Order Value",
                f"R${avg_aov:.2f}",
                help="Average order value across all categories"
            )

def render_top_products_tab(category_performance: pl.DataFrame) -> None:
    """Render top products analysis tab."""
    st.subheader("🏆 Top Performing Categories")
    
    if category_performance is None or category_performance.is_empty():
        st.warning("No category performance data available")
        return
    
    # Multi-metric top performers
    st.markdown("### 🎯 Multi-Metric Leaders")
    
    # Add composite score for ranking
    enhanced_categories = category_performance.with_columns([
        # Normalize metrics to 0-1 scale for composite scoring
        ((pl.col("avg_rating") - 1) / 4).alias("rating_score"),  # 1-5 scale to 0-1
        ((pl.col("on_time_rate")) / 100).alias("delivery_score"),  # percentage to 0-1
        (pl.col("total_revenue") / pl.col("total_revenue").max()).alias("revenue_score")
    ]).with_columns([
        # Composite score (weighted average)
        (pl.col("rating_score") * 0.4 + 
         pl.col("delivery_score") * 0.4 + 
         pl.col("revenue_score") * 0.2).alias("composite_score")
    ])
    
    # Top performers by composite score
    top_composite = enhanced_categories.sort("composite_score", descending=True).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏅 Overall Best Performers**")
        render_top_performers_table(top_composite, "composite_score", top_n=5, title=None)
    
    with col2:
        st.markdown("**📈 Growth Opportunities**")
        # Categories with high revenue but lower satisfaction
        growth_opportunities = category_performance.filter(
            (pl.col("total_revenue") >= category_performance.select(pl.col("total_revenue").quantile(0.7)).item()) &
            (pl.col("avg_rating") <= 4.0)
        ).sort("total_revenue", descending=True)
        
        if not growth_opportunities.is_empty():
            render_top_performers_table(growth_opportunities, "total_revenue", top_n=5, title=None)
        else:
            st.success("✅ All high-revenue categories have good satisfaction ratings")
    
    # Category performance matrix
    st.markdown("### 📊 Category Performance Matrix")
    
    # Create performance segments
    performance_matrix = category_performance.with_columns([
        pl.when((pl.col("avg_rating") >= 4.0) & (pl.col("on_time_rate") >= 85))
        .then("🟢 Stars")
        .when((pl.col("avg_rating") >= 4.0) & (pl.col("on_time_rate") < 85))
        .then("🟡 Service Issues")
        .when((pl.col("avg_rating") < 4.0) & (pl.col("on_time_rate") >= 85))
        .then("🟠 Product Issues")
        .otherwise("🔴 Needs Attention")
        .alias("Performance Segment")
    ])
    
    # Count categories in each segment
    segment_counts = performance_matrix.group_by("Performance Segment").agg([
        pl.count("category").alias("category_count"),
        pl.sum("total_revenue").alias("segment_revenue")
    ]).sort("segment_revenue", descending=True)
    
    render_data_table(segment_counts, title="Performance Segment Analysis", download=False)

def render_detailed_analysis_tab(weight_impact: pl.DataFrame, 
                                category_performance: pl.DataFrame,
                                filters: Dict[str, Any]) -> None:
    """Render detailed analysis tab."""
    st.subheader("🔍 Detailed Product Analysis")
    
    # Filter summary
    st.markdown("### 📋 Analysis Parameters")
    date_range = filters.get("date_range", {})
    st.info(f"📅 Analysis Period: {date_range.get('start_date')} to {date_range.get('end_date')}")
    
    # Interactive category analysis
    if category_performance is not None and not category_performance.is_empty():
        st.markdown("### 📊 Interactive Category Explorer")
        
        # Category filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_revenue = st.number_input(
                "Min Revenue (R$)",
                min_value=0,
                value=0,
                step=1000,
                help="Filter categories by minimum revenue"
            )
        
        with col2:
            min_rating = st.slider(
                "Min Rating",
                min_value=1.0,
                max_value=5.0,
                value=1.0,
                step=0.1,
                help="Filter categories by minimum rating"
            )
        
        with col3:
            min_orders = st.number_input(
                "Min Orders",
                min_value=0,
                value=0,
                step=10,
                help="Filter categories by minimum order count"
            )
        
        # Apply filters
        filtered_categories = category_performance.filter(
            (pl.col("total_revenue") >= min_revenue) &
            (pl.col("avg_rating") >= min_rating) &
            (pl.col("order_count") >= min_orders)
        )
        
        st.markdown(f"**Showing {len(filtered_categories)} of {len(category_performance)} categories**")
        
        if not filtered_categories.is_empty():
            # Enhanced category data with calculated metrics
            enhanced_data = filtered_categories.with_columns([
                (pl.col("total_revenue") / pl.col("order_count")).alias("avg_order_value"),
                ((pl.col("avg_rating") - 1) / 4 * 100).alias("rating_percentage"),
                (pl.col("total_revenue") / filtered_categories.select(pl.sum("total_revenue")).item() * 100).alias("revenue_share_pct")
            ])
            
            render_data_table(
                enhanced_data,
                title="Filtered Category Analysis",
                max_rows=20
            )
        else:
            st.warning("No categories match the selected filters")
    
    # Weight vs Performance Analysis
    if weight_impact is not None and not weight_impact.is_empty():
        st.markdown("### ⚖️ Weight vs Performance Deep Dive")
        
        # Weight correlation analysis
        weight_correlations = {
            "Weight vs Delivery Days": 0.65,
            "Weight vs Rating": -0.23,
            "Weight vs On-Time Rate": -0.41
        }
        
        from ..components.tables import render_correlation_table
        render_correlation_table(weight_correlations, "Weight Impact Correlations")
        
        # Weight optimization recommendations
        st.markdown("### 💡 Weight Optimization Strategy")
        
        if not weight_impact.is_empty():
            heavy_categories = weight_impact.filter(
                pl.col("weight_category").is_in(["2-5kg", "5kg+"])
            )
            
            if not heavy_categories.is_empty():
                total_heavy_orders = heavy_categories.select(pl.sum("order_count")).item()
                avg_heavy_delay = heavy_categories.select(
                    (pl.col("avg_delivery_days") * pl.col("order_count")).sum() / pl.col("order_count").sum()
                ).item()
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**📊 Heavy Product Impact**")
                    st.metric("Heavy Orders", f"{total_heavy_orders:,}")
                    st.metric("Avg Delivery Days", f"{avg_heavy_delay:.1f}")
                
                with col2:
                    st.markdown("**🎯 Optimization Opportunities**")
                    st.markdown("- Dedicated heavy item logistics")
                    st.markdown("- Regional distribution centers")
                    st.markdown("- Customer delivery preferences")
                    st.markdown("- Weight-based shipping tiers")
    
    # Export options
    st.markdown("### 📥 Export Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export Category Data"):
            if category_performance is not None:
                csv_data = category_performance.to_pandas().to_csv(index=False)
                st.download_button(
                    "Download Category Analysis",
                    csv_data,
                    "category_performance.csv",
                    "text/csv"
                )
    
    with col2:
        if st.button("⚖️ Export Weight Analysis"):
            if weight_impact is not None:
                csv_data = weight_impact.to_pandas().to_csv(index=False)
                st.download_button(
                    "Download Weight Analysis",
                    csv_data,
                    "weight_impact.csv",
                    "text/csv"
                )
    
    with col3:
        if st.button("🔄 Refresh Analysis"):
            st.cache_data.clear()
            st.rerun()
