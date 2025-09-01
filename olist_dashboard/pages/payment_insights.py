"""
Payment Insights page - Analysis of payment methods, installments, and financial performance.
"""

import streamlit as st
import polars as pl
from typing import Dict, Any, Optional

from ..components.metrics import render_kpi_cards, render_trend_metrics
from ..components.charts import render_payment_analysis_charts
from ..components.tables import render_data_table, render_top_performers_table, render_correlation_table
from ..data.data_loader import get_data_loader
from ..data.data_processor import get_data_processor
from ..data.cache_manager import cache_details

def render_payment_insights_page(filters: Dict[str, Any]) -> None:
    """
    Render the payment insights page.
    
    Args:
        filters: Applied filters from sidebar
    """
    st.title("💳 Payment Insights")
    st.markdown("Comprehensive analysis of payment methods, installment patterns, and financial performance")
    
    # Initialize components
    data_loader = get_data_loader()
    data_processor = get_data_processor()
    
    # Extract date range from filters
    date_range = filters.get("date_range", {})
    start_date = date_range.get("start_date", "2023-01-01")
    end_date = date_range.get("end_date", "2023-12-31")
    
    # Load payment data
    with st.spinner("Loading payment analysis data..."):
        payment_methods = load_payment_methods_data(data_loader, start_date, end_date)
        installment_analysis = load_installment_analysis_data(data_loader, start_date, end_date)
        revenue_optimization = load_revenue_optimization_data(data_loader, start_date, end_date)
    
    # Main payment metrics
    st.subheader("💰 Payment Performance Overview")
    render_payment_overview_kpis(payment_methods, installment_analysis)
    
    st.markdown("---")
    
    # Create tabs for different analyses
    tab1, tab2, tab3, tab4 = st.tabs([
        "💳 Payment Methods",
        "📊 Installment Analysis", 
        "💰 Revenue Optimization",
        "🔍 Advanced Analytics"
    ])
    
    with tab1:
        render_payment_methods_tab(payment_methods)
    
    with tab2:
        render_installment_analysis_tab(installment_analysis)
    
    with tab3:
        render_revenue_optimization_tab(revenue_optimization)
    
    with tab4:
        render_advanced_analytics_tab(payment_methods, installment_analysis, revenue_optimization, filters)

@cache_details()
def load_payment_methods_data(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load payment methods analysis data."""
    try:
        return _data_loader.get_payment_method_analysis(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading payment methods data: {str(e)}")
        return None

@cache_details()
def load_installment_analysis_data(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load installment analysis data."""
    try:
        return _data_loader.get_installment_analysis(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading installment analysis data: {str(e)}")
        return None

@cache_details()
def load_revenue_optimization_data(_data_loader, start_date: str, end_date: str) -> Optional[pl.DataFrame]:
    """Load revenue optimization data."""
    try:
        return _data_loader.get_revenue_optimization(start_date, end_date)
    except Exception as e:
        st.error(f"Error loading revenue optimization data: {str(e)}")
        return None

def render_payment_overview_kpis(payment_methods: pl.DataFrame, installment_analysis: pl.DataFrame) -> None:
    """Render payment overview KPI cards."""
    if payment_methods is None or payment_methods.is_empty():
        st.warning("No payment methods data available for KPIs")
        return
    
    # Calculate aggregate payment metrics
    total_transactions = payment_methods.select(pl.sum("order_count")).item()
    total_value = payment_methods.select(pl.sum("total_value")).item()
    avg_value = total_value / total_transactions if total_transactions > 0 else 0
    
    # Payment method distribution
    top_method = payment_methods.sort("order_count", descending=True).row(0, named=True)
    method_share = (top_method["order_count"] / total_transactions) * 100 if total_transactions > 0 else 0
    
    # Installment insights
    if installment_analysis is not None and not installment_analysis.is_empty():
        installment_usage = installment_analysis.filter(pl.col("payment_installments") > 1)
        if not installment_usage.is_empty():
            installment_rate = (installment_usage.select(pl.sum("order_count")).item() / 
                              installment_analysis.select(pl.sum("order_count")).item()) * 100
        else:
            installment_rate = 0
    else:
        installment_rate = 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "💳 Total Transactions",
            f"{total_transactions:,}",
            help="Total number of payment transactions"
        )
    
    with col2:
        st.metric(
            "💰 Total Value",
            f"R${total_value:,.0f}",
            help="Total value of all payment transactions"
        )
    
    with col3:
        st.metric(
            "📊 Avg Transaction",
            f"R${avg_value:.2f}",
            help="Average transaction value"
        )
    
    with col4:
        st.metric(
            "📈 Installment Rate",
            f"{installment_rate:.1f}%",
            help="Percentage of orders using installments"
        )
    
    # Payment insights highlight
    st.info(f"💳 **Dominant Payment Method**: {top_method['payment_type']} ({method_share:.1f}% of transactions)")

def render_payment_methods_tab(payment_methods: pl.DataFrame) -> None:
    """Render payment methods analysis tab."""
    st.subheader("💳 Payment Method Analysis")
    
    if payment_methods is None or payment_methods.is_empty():
        st.warning("No payment methods data available")
        return
    
    # Payment method charts
    render_payment_analysis_charts(payment_methods)
    
    # Payment method breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Payment Method Performance")
        
        # Add calculated metrics
        enhanced_methods = payment_methods.with_columns([
            (pl.col("total_value") / pl.col("order_count")).alias("avg_transaction_value"),
            (pl.col("order_count") / payment_methods.select(pl.sum("order_count")).item() * 100).alias("volume_share_pct"),
            (pl.col("total_value") / payment_methods.select(pl.sum("total_value")).item() * 100).alias("value_share_pct")
        ])
        
        render_data_table(enhanced_methods, title=None, download=False)
    
    with col2:
        st.markdown("### 💡 Payment Method Insights")
        
        if not payment_methods.is_empty():
            # Analyze payment method patterns
            credit_card = payment_methods.filter(pl.col("payment_type") == "credit_card")
            debit_card = payment_methods.filter(pl.col("payment_type") == "debit_card")
            boleto = payment_methods.filter(pl.col("payment_type") == "boleto")
            voucher = payment_methods.filter(pl.col("payment_type") == "voucher")
            
            # Payment method insights
            total_value = payment_methods.select(pl.sum("total_value")).item()
            
            if not credit_card.is_empty():
                cc_value = credit_card.select("total_value").item()
                cc_avg = credit_card.select("avg_transaction_value").item() if "avg_transaction_value" in credit_card.columns else 0
                cc_share = (cc_value / total_value) * 100 if total_value > 0 else 0
                st.markdown(f"💳 **Credit Card**: {cc_share:.1f}% of value, R${cc_avg:.2f} avg")
            
            if not debit_card.is_empty():
                dc_value = debit_card.select("total_value").item()
                dc_avg = debit_card.select("avg_transaction_value").item() if "avg_transaction_value" in debit_card.columns else 0
                dc_share = (dc_value / total_value) * 100 if total_value > 0 else 0
                st.markdown(f"💰 **Debit Card**: {dc_share:.1f}% of value, R${dc_avg:.2f} avg")
            
            if not boleto.is_empty():
                boleto_value = boleto.select("total_value").item()
                boleto_avg = boleto.select("avg_transaction_value").item() if "avg_transaction_value" in boleto.columns else 0
                boleto_share = (boleto_value / total_value) * 100 if total_value > 0 else 0
                st.markdown(f"🎫 **Boleto**: {boleto_share:.1f}% of value, R${boleto_avg:.2f} avg")
        
        # Payment optimization recommendations
        st.markdown("### 🎯 Payment Optimization")
        optimization_tips = [
            "💳 **Promote higher-value methods** for larger transactions",
            "🎯 **Target installment offers** for premium products",
            "📱 **Mobile payment integration** for younger demographics",
            "🔒 **Security features** to increase payment confidence"
        ]
        
        for tip in optimization_tips:
            st.markdown(tip)

def render_installment_analysis_tab(installment_analysis: pl.DataFrame) -> None:
    """Render installment analysis tab."""
    st.subheader("📊 Installment Payment Analysis")
    
    if installment_analysis is None or installment_analysis.is_empty():
        st.warning("No installment analysis data available")
        return
    
    # Installment charts
    render_payment_analysis_charts(installment_analysis)
    
    # Installment insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Installment Breakdown")
        
        # Enhanced installment data
        enhanced_installments = installment_analysis.with_columns([
            (pl.col("total_value") / pl.col("order_count")).alias("avg_order_value"),
            (pl.col("order_count") / installment_analysis.select(pl.sum("order_count")).item() * 100).alias("order_share_pct"),
            (pl.col("total_value") / installment_analysis.select(pl.sum("total_value")).item() * 100).alias("value_share_pct")
        ])
        
        render_data_table(enhanced_installments, title=None, download=False)
    
    with col2:
        st.markdown("### 💡 Installment Strategy Insights")
        
        if not installment_analysis.is_empty():
            # Calculate installment patterns
            single_payment = installment_analysis.filter(pl.col("payment_installments") == 1)
            multi_installment = installment_analysis.filter(pl.col("payment_installments") > 1)
            
            if not single_payment.is_empty() and not multi_installment.is_empty():
                single_avg = single_payment.select(
                    (pl.col("total_value") / pl.col("order_count")).mean()
                ).item()
                multi_avg = multi_installment.select(
                    (pl.col("total_value") / pl.col("order_count")).mean()
                ).item()
                
                single_orders = single_payment.select(pl.sum("order_count")).item()
                multi_orders = multi_installment.select(pl.sum("order_count")).item()
                
                installment_rate = (multi_orders / (single_orders + multi_orders)) * 100
                
                st.markdown(f"💰 **Single Payment**: R${single_avg:.2f} avg order value")
                st.markdown(f"📊 **Installments**: R${multi_avg:.2f} avg order value")
                st.markdown(f"📈 **Installment Rate**: {installment_rate:.1f}% of orders")
                
                if multi_avg > single_avg * 1.5:
                    st.success("✅ **Installments drive higher order values**")
                elif multi_avg > single_avg:
                    st.info("📈 **Moderate uplift** from installment offerings")
                else:
                    st.warning("⚠️ **Review installment strategy** - may not be driving value")
        
        # Installment recommendations
        st.markdown("### 🎯 Installment Optimization")
        installment_tips = [
            "🎯 **Promote 2-3 installments** for mid-range products",
            "💳 **Highlight 0% interest** options prominently",
            "📱 **Mobile-friendly** installment selection",
            "🔄 **Dynamic installment** offers based on cart value"
        ]
        
        for tip in installment_tips:
            st.markdown(tip)

def render_revenue_optimization_tab(revenue_optimization: pl.DataFrame) -> None:
    """Render revenue optimization tab."""
    st.subheader("💰 Revenue Optimization Analysis")
    
    if revenue_optimization is None or revenue_optimization.is_empty():
        st.warning("No revenue optimization data available")
        return
    
    # Revenue optimization charts
    render_payment_analysis_charts(revenue_optimization)
    
    # Revenue insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Revenue Performance Metrics")
        
        # Calculate revenue metrics
        revenue_metrics = revenue_optimization.with_columns([
            (pl.col("total_revenue") / pl.col("total_orders")).alias("avg_order_value"),
            (pl.col("total_revenue") / revenue_optimization.select(pl.sum("total_revenue")).item() * 100).alias("revenue_share_pct")
        ])
        
        render_data_table(revenue_metrics, title=None, download=False)
    
    with col2:
        st.markdown("### 💡 Revenue Optimization Opportunities")
        
        if not revenue_optimization.is_empty():
            # Identify optimization opportunities
            high_volume_low_value = revenue_optimization.filter(
                (pl.col("total_orders") >= revenue_optimization.select(pl.col("total_orders").quantile(0.7)).item()) &
                (pl.col("avg_order_value") <= revenue_optimization.select(pl.col("avg_order_value").quantile(0.3)).item())
            )
            
            low_volume_high_value = revenue_optimization.filter(
                (pl.col("total_orders") <= revenue_optimization.select(pl.col("total_orders").quantile(0.3)).item()) &
                (pl.col("avg_order_value") >= revenue_optimization.select(pl.col("avg_order_value").quantile(0.7)).item())
            )
            
            st.markdown("**🔍 Optimization Segments:**")
            
            if not high_volume_low_value.is_empty():
                st.markdown(f"📊 **High Volume, Low Value**: {len(high_volume_low_value)} segments")
                st.markdown("   → *Opportunity*: Upsell and cross-sell strategies")
            
            if not low_volume_high_value.is_empty():
                st.markdown(f"💎 **Low Volume, High Value**: {len(low_volume_high_value)} segments")
                st.markdown("   → *Opportunity*: Customer acquisition and retention")
        
        # Revenue optimization strategies
        st.markdown("### 🎯 Revenue Growth Strategies")
        revenue_strategies = [
            "🛒 **Cart abandonment** recovery campaigns",
            "💰 **Dynamic pricing** based on payment method",
            "🎁 **Bundling offers** for installment payments",
            "⭐ **Premium payment options** for faster processing"
        ]
        
        for strategy in revenue_strategies:
            st.markdown(strategy)

def render_advanced_analytics_tab(payment_methods: pl.DataFrame,
                                 installment_analysis: pl.DataFrame,
                                 revenue_optimization: pl.DataFrame,
                                 filters: Dict[str, Any]) -> None:
    """Render advanced analytics tab."""
    st.subheader("🔍 Advanced Payment Analytics")
    
    # Filter summary
    st.markdown("### 📋 Analysis Parameters")
    date_range = filters.get("date_range", {})
    st.info(f"📅 Analysis Period: {date_range.get('start_date')} to {date_range.get('end_date')}")
    
    # Payment correlation analysis
    st.markdown("### 🔗 Payment Behavior Correlations")
    
    # Mock correlation data (replace with actual calculations)
    payment_correlations = {
        "Order Value vs Installments": 0.73,
        "Payment Method vs Delivery Speed": 0.34,
        "Installments vs Customer Satisfaction": -0.12,
        "Payment Type vs Return Rate": 0.18
    }
    
    render_correlation_table(payment_correlations, "Payment Behavior Correlations")
    
    # Advanced payment insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Payment Trends Analysis")
        
        if payment_methods is not None and not payment_methods.is_empty():
            # Payment method trends
            st.markdown("**Payment Method Evolution:**")
            
            # Credit card dominance analysis
            credit_share = payment_methods.filter(pl.col("payment_type") == "credit_card")
            if not credit_share.is_empty():
                cc_volume_share = (credit_share.select("order_count").item() / 
                                 payment_methods.select(pl.sum("order_count")).item()) * 100
                
                if cc_volume_share > 70:
                    st.success(f"💳 Credit cards dominate: {cc_volume_share:.1f}% of transactions")
                elif cc_volume_share > 50:
                    st.info(f"💳 Credit cards lead: {cc_volume_share:.1f}% of transactions")
                else:
                    st.warning(f"💳 Credit cards: {cc_volume_share:.1f}% of transactions (consider promotion)")
        
        # Installment trends
        if installment_analysis is not None and not installment_analysis.is_empty():
            st.markdown("**Installment Preferences:**")
            
            max_installments = installment_analysis.select(pl.max("payment_installments")).item()
            popular_installments = installment_analysis.sort("order_count", descending=True).head(3)
            
            st.markdown(f"📈 Max installments offered: {max_installments}")
            st.markdown("🏆 Most popular installment options:")
            
            for row in popular_installments.iter_rows(named=True):
                installments = row["payment_installments"]
                orders = row["order_count"]
                st.markdown(f"   • {installments}x: {orders:,} orders")
    
    with col2:
        st.markdown("### 💡 Strategic Recommendations")
        
        # Payment strategy recommendations based on data
        st.markdown("**💳 Payment Method Strategy:**")
        recommendations = []
        
        if payment_methods is not None and not payment_methods.is_empty():
            # Analyze payment method performance
            total_value = payment_methods.select(pl.sum("total_value")).item()
            
            for method_data in payment_methods.iter_rows(named=True):
                method = method_data["payment_type"]
                value_share = (method_data["total_value"] / total_value) * 100
                
                if method == "credit_card" and value_share > 60:
                    recommendations.append("🎯 **Enhance credit card rewards** programs")
                elif method == "boleto" and value_share > 20:
                    recommendations.append("🎫 **Optimize boleto processing** for faster confirmation")
                elif method == "debit_card" and value_share < 20:
                    recommendations.append("💰 **Promote debit card** usage with discounts")
        
        if installment_analysis is not None and not installment_analysis.is_empty():
            multi_installment = installment_analysis.filter(pl.col("installments") > 1)
            if not multi_installment.is_empty():
                installment_revenue = multi_installment.select(pl.sum("total_value")).item()
                total_revenue = installment_analysis.select(pl.sum("total_value")).item()
                installment_share = (installment_revenue / total_revenue) * 100
                
                if installment_share > 40:
                    recommendations.append("📊 **Expand installment options** for high-value items")
                else:
                    recommendations.append("📈 **Promote installment benefits** to increase adoption")
        
        # Default recommendations if no specific data insights
        if not recommendations:
            recommendations = [
                "💳 **Diversify payment options** to reduce dependency",
                "📱 **Implement mobile wallets** for younger demographics",
                "🔒 **Enhance payment security** messaging",
                "🎁 **Create payment-based** loyalty programs"
            ]
        
        for rec in recommendations:
            st.markdown(rec)
    
    # Interactive payment analysis
    st.markdown("### 🎛️ Interactive Payment Explorer")
    
    # Payment filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        payment_type_filter = st.selectbox(
            "Payment Type",
            ["All"] + (payment_methods["payment_type"].unique().to_list() if payment_methods is not None else []),
            help="Filter analysis by payment type"
        )
    
    with col2:
        min_transaction_value = st.number_input(
            "Min Transaction Value (R$)",
            min_value=0.0,
            value=0.0,
            step=10.0,
            help="Filter by minimum transaction value"
        )
    
    with col3:
        max_installments = st.slider(
            "Max Installments",
            min_value=1,
            max_value=24,
            value=24,
            help="Filter by maximum number of installments"
        )
    
    # Apply filters and show results
    filtered_data = None
    if payment_methods is not None:
        filtered_data = payment_methods
        
        if payment_type_filter != "All":
            filtered_data = filtered_data.filter(pl.col("payment_type") == payment_type_filter)
        
        if "avg_transaction_value" in filtered_data.columns:
            filtered_data = filtered_data.filter(pl.col("avg_transaction_value") >= min_transaction_value)
    
    if filtered_data is not None and not filtered_data.is_empty():
        st.markdown(f"**Showing {len(filtered_data)} payment method(s) matching filters**")
        render_data_table(filtered_data, title="Filtered Payment Analysis", max_rows=10)
    
    # Export options
    st.markdown("### 📥 Export Payment Analysis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💳 Export Payment Methods"):
            if payment_methods is not None:
                csv_data = payment_methods.to_pandas().to_csv(index=False)
                st.download_button(
                    "Download Payment Methods",
                    csv_data,
                    "payment_methods_analysis.csv",
                    "text/csv"
                )
    
    with col2:
        if st.button("📊 Export Installment Data"):
            if installment_analysis is not None:
                csv_data = installment_analysis.to_pandas().to_csv(index=False)
                st.download_button(
                    "Download Installment Analysis",
                    csv_data,
                    "installment_analysis.csv",
                    "text/csv"
                )
    
    with col3:
        if st.button("🔄 Refresh Analysis"):
            st.cache_data.clear()
            st.rerun()
