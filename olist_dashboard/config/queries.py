"""
SQL query templates for the Olist Dashboard application.
Organized by functional areas and optimized for BigQuery.
"""

from typing import Dict, Any

# Executive Summary Queries
EXECUTIVE_QUERIES: Dict[str, str] = {
    "key_metrics": """
        SELECT 
            -- On-time delivery rate
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_delivery_rate,
            
            -- Average rating
            ROUND(AVG(r.review_score), 2) as avg_rating,
            
            -- Total revenue
            ROUND(SUM(f.price + f.freight_value), 2) as total_revenue,
            
            -- Active customers
            COUNT(DISTINCT f.customer_sk) as active_customers,
            
            -- Order count
            COUNT(DISTINCT f.order_id) as total_orders
            
        FROM {fact_order_items} f
        LEFT JOIN {dim_orders} o ON f.order_sk = o.order_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        WHERE o.order_purchase_timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
    """,
    
    "daily_trends": """
        SELECT 
            d.date_value,
            COUNT(DISTINCT f.order_id) as daily_orders,
            ROUND(SUM(f.price + f.freight_value), 2) as daily_revenue,
            ROUND(AVG(r.review_score), 2) as daily_avg_rating,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as daily_on_time_rate
            
        FROM {fact_order_items} f
        LEFT JOIN {dim_orders} o ON f.order_sk = o.order_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        LEFT JOIN {dim_date} d ON f.order_date_sk = d.date_sk
        WHERE d.date_value >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        GROUP BY d.date_value
        ORDER BY d.date_value
    """,
    
    "geographic_performance": """
        SELECT 
            c.customer_state,
            COUNT(DISTINCT f.order_id) as order_count,
            ROUND(AVG(r.review_score), 2) as avg_rating,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_rate,
            ROUND(SUM(f.price + f.freight_value), 2) as total_revenue
            
        FROM {fact_order_items} f
        LEFT JOIN {dim_customer} c ON f.customer_sk = c.customer_sk
        LEFT JOIN {dim_orders} o ON f.order_sk = o.order_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        WHERE o.order_purchase_timestamp >= DATE_SUB(CURRENT_DATE(), INTERVAL 90 DAY)
        GROUP BY c.customer_state
        ORDER BY order_count DESC
    """
}

# Delivery Performance Queries
DELIVERY_QUERIES: Dict[str, str] = {
    "delivery_metrics": """
        SELECT 
            COUNT(*) as total_orders,
            SUM(CASE 
                WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                THEN 1 ELSE 0 
            END) as on_time_orders,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 2
            ) as on_time_percentage,
            ROUND(
                AVG(DATE_DIFF(
                    o.order_delivered_customer_date, 
                    o.order_purchase_timestamp, 
                    DAY
                )), 1
            ) as avg_delivery_days,
            ROUND(
                AVG(DATE_DIFF(
                    o.order_delivered_customer_date, 
                    o.order_estimated_delivery_date, 
                    DAY
                )), 1
            ) as avg_delay_days
            
        FROM {fact_order_items} f
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        WHERE o.order_delivered_customer_date IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
    """,
    
    "delivery_by_state": """
        SELECT 
            c.customer_state,
            s.seller_state,
            COUNT(*) as order_count,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_rate,
            ROUND(
                AVG(DATE_DIFF(
                    o.order_delivered_customer_date, 
                    o.order_purchase_timestamp, 
                    DAY
                )), 1
            ) as avg_delivery_days
            
        FROM {fact_order_items} f
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        JOIN {dim_customer} c ON f.customer_sk = c.customer_sk
        JOIN {dim_seller} s ON f.seller_sk = s.seller_sk
        WHERE o.order_delivered_customer_date IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY c.customer_state, s.seller_state
        HAVING order_count >= 10
        ORDER BY order_count DESC
    """,
    
    "delivery_time_distribution": """
        SELECT 
            CASE 
                WHEN DATE_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) <= 7 
                THEN '1-7 days'
                WHEN DATE_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) <= 14 
                THEN '8-14 days'
                WHEN DATE_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) <= 21 
                THEN '15-21 days'
                WHEN DATE_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY) <= 30 
                THEN '22-30 days'
                ELSE '30+ days'
            END as delivery_time_bucket,
            COUNT(*) as order_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage
            
        FROM {fact_order_items} f
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        WHERE o.order_delivered_customer_date IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY delivery_time_bucket
        ORDER BY 
            CASE delivery_time_bucket
                WHEN '1-7 days' THEN 1
                WHEN '8-14 days' THEN 2
                WHEN '15-21 days' THEN 3
                WHEN '22-30 days' THEN 4
                WHEN '30+ days' THEN 5
            END
    """
}

# Customer Satisfaction Queries
SATISFACTION_QUERIES: Dict[str, str] = {
    "rating_analysis": """
        SELECT 
            r.review_score,
            COUNT(*) as review_count,
            ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as percentage,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_rate
            
        FROM {fact_order_items} f
        JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        WHERE r.review_score IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY r.review_score
        ORDER BY r.review_score
    """,
    
    "satisfaction_vs_delivery": """
        SELECT 
            CASE 
                WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                THEN 'On Time'
                ELSE 'Delayed'
            END as delivery_status,
            ROUND(AVG(r.review_score), 2) as avg_rating,
            COUNT(*) as review_count,
            COUNTIF(r.review_score >= 4) as positive_reviews,
            COUNTIF(r.review_score <= 2) as negative_reviews
            
        FROM {fact_order_items} f
        JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        WHERE r.review_score IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY delivery_status
    """,
    
    "category_satisfaction": """
        SELECT 
            p.product_category_name_english as category,
            ROUND(AVG(r.review_score), 2) as avg_rating,
            COUNT(*) as review_count,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_rate
            
        FROM {fact_order_items} f
        JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        JOIN {dim_product} p ON f.product_sk = p.product_sk
        WHERE r.review_score IS NOT NULL
        AND p.product_category_name_english IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY p.product_category_name_english
        HAVING review_count >= 50
        ORDER BY avg_rating DESC
    """
}

# Product Analysis Queries
PRODUCT_QUERIES: Dict[str, str] = {
    "weight_impact": """
        SELECT 
            CASE 
                WHEN p.product_weight_g <= 500 THEN '0-500g'
                WHEN p.product_weight_g <= 1000 THEN '501-1000g'
                WHEN p.product_weight_g <= 2000 THEN '1-2kg'
                WHEN p.product_weight_g <= 5000 THEN '2-5kg'
                ELSE '5kg+'
            END as weight_category,
            COUNT(*) as order_count,
            ROUND(AVG(DATE_DIFF(o.order_delivered_customer_date, o.order_purchase_timestamp, DAY)), 1) as avg_delivery_days,
            ROUND(AVG(r.review_score), 2) as avg_rating,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_rate
            
        FROM {fact_order_items} f
        JOIN {dim_product} p ON f.product_sk = p.product_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        WHERE p.product_weight_g IS NOT NULL
        AND o.order_delivered_customer_date IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY weight_category
        ORDER BY 
            CASE weight_category
                WHEN '0-500g' THEN 1
                WHEN '501-1000g' THEN 2
                WHEN '1-2kg' THEN 3
                WHEN '2-5kg' THEN 4
                WHEN '5kg+' THEN 5
            END
    """,
    
    "category_performance": """
        SELECT 
            p.product_category_name_english as category,
            COUNT(*) as order_count,
            ROUND(SUM(f.price), 2) as total_revenue,
            ROUND(AVG(f.price), 2) as avg_price,
            ROUND(AVG(p.product_weight_g), 1) as avg_weight,
            ROUND(AVG(r.review_score), 2) as avg_rating,
            ROUND(
                AVG(CASE 
                    WHEN o.order_delivered_customer_date <= o.order_estimated_delivery_date 
                    THEN 1.0 ELSE 0.0 
                END) * 100, 1
            ) as on_time_rate
            
        FROM {fact_order_items} f
        JOIN {dim_product} p ON f.product_sk = p.product_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        WHERE p.product_category_name_english IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY p.product_category_name_english
        HAVING order_count >= 100
        ORDER BY order_count DESC
    """
}

# Payment Analysis Queries
PAYMENT_QUERIES: Dict[str, str] = {
    "payment_method_analysis": """
        SELECT 
            pm.payment_type,
            COUNT(*) as order_count,
            ROUND(SUM(f.price + f.freight_value), 2) as total_value,
            ROUND(AVG(f.price + f.freight_value), 2) as avg_order_value,
            ROUND(AVG(pm.payment_installments), 1) as avg_installments,
            ROUND(AVG(r.review_score), 2) as avg_rating
            
        FROM {fact_order_items} f
        JOIN {dim_payment} pm ON f.payment_sk = pm.payment_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        WHERE pm.payment_type IS NOT NULL
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY pm.payment_type
        ORDER BY order_count DESC
    """,
    
    "installment_analysis": """
        SELECT 
            pm.payment_installments,
            COUNT(*) as order_count,
            ROUND(AVG(f.price + f.freight_value), 2) as avg_order_value,
            ROUND(AVG(r.review_score), 2) as avg_rating
            
        FROM {fact_order_items} f
        JOIN {dim_payment} pm ON f.payment_sk = pm.payment_sk
        LEFT JOIN {dim_order_reviews} r ON f.order_sk = r.order_sk
        JOIN {dim_orders} o ON f.order_sk = o.order_sk
        WHERE pm.payment_installments IS NOT NULL
        AND pm.payment_installments <= 24
        AND o.order_purchase_timestamp >= '{start_date}'
        AND o.order_purchase_timestamp <= '{end_date}'
        GROUP BY pm.payment_installments
        ORDER BY pm.payment_installments
    """
}

def get_query(category: str, query_name: str, **kwargs) -> str:
    """
    Get a formatted SQL query with parameter substitution.
    
    Args:
        category: Query category (executive, delivery, satisfaction, product, payment)
        query_name: Specific query name within the category
        **kwargs: Parameters for string formatting
        
    Returns:
        Formatted SQL query string
    """
    query_maps = {
        "executive": EXECUTIVE_QUERIES,
        "delivery": DELIVERY_QUERIES,
        "satisfaction": SATISFACTION_QUERIES,
        "product": PRODUCT_QUERIES,
        "payment": PAYMENT_QUERIES,
    }
    
    if category not in query_maps:
        raise ValueError(f"Unknown query category: {category}")
    
    queries = query_maps[category]
    if query_name not in queries:
        raise ValueError(f"Unknown query name: {query_name} in category: {category}")
    
    query_template = queries[query_name]
    
    # Add table names from settings if not provided
    from .settings import TABLES
    kwargs.update(TABLES)
    
    return query_template.format(**kwargs)
