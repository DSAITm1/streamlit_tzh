# Olist Analytics Dashboard - AI Coding Agent Instructions

## Project Overview

This is a **Streamlit dashboard** for analyzing Olist e-commerce operational metrics using a star schema data warehouse in **Google BigQuery**. The project follows a dimensional modeling approach with fact/dimension tables optimized for analytical queries.

## Architecture & Data Flow

- **Data Source**: BigQuery dataset `dsai-468212.dbt_olist_stg` with dbt-transformed tables
- **Frontend**: Streamlit app with multi-page navigation and interactive visualizations
- **Data Access**: Python scripts using `google-cloud-bigquery` client
- **Processing**: Polars for data manipulation, Plotly/Altair for visualizations

### Key Tables (Star Schema)

- **Fact**: `fact_order_items` (central fact table with all business metrics)
- **Dimensions**: `dim_customer`, `dim_orders`, `dim_product`, `dim_seller`, `dim_payment`, `dim_order_reviews`, `dim_date`, `dim_geolocation`

## Application Structure

Follow the module structure specified in `streamlit_app_specification.md`:

```
olist_dashboard/
├── main.py                    # Main Streamlit entry point
├── config/
│   ├── settings.py           # BigQuery connection config
│   └── queries.py            # SQL query templates
├── data/
│   ├── data_loader.py        # BigQuery data fetching
│   ├── data_processor.py     # Polars-based transformations
│   └── cache_manager.py      # Streamlit caching strategies
├── components/               # Reusable UI components
├── pages/                    # Streamlit page modules
└── utils/                    # Helper functions
```

## Development Patterns

### Data Access Patterns

- Use surrogate keys (`*_sk`) for joins, not natural keys (`*_id`)
- Leverage date dimension (`dim_date`) for time-based filtering
- Always use `fact_order_items` as the primary fact table for metrics
- Cache BigQuery results using `@st.cache_data` for 1-4 hour TTL

### BigQuery Query Patterns

```sql
-- Standard fact-dimension join pattern
SELECT
    f.order_id,
    c.customer_state,
    p.product_category_name_english,
    f.price,
    f.freight_value
FROM fact_order_items f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
JOIN dim_product p ON f.product_sk = p.product_sk
WHERE f.order_date_sk BETWEEN 20220101 AND 20221231
```

### Streamlit UI Patterns

- Use `st.sidebar` for global filters (date range, geography, categories)
- Implement responsive 3-column metrics cards for KPIs
- Follow page structure: metrics cards → main visualization → detailed tables
- Use `st.columns()` for responsive layouts (3-col desktop, 2-col tablet, 1-col mobile)

### Performance Optimization

- Pre-aggregate metrics at appropriate grain (daily/weekly/monthly)
- Use `st.cache_data` with TTL for expensive BigQuery operations
- Implement lazy loading for chart components
- Limit initial data loads to recent time periods (last 90 days default)

## Key Business Logic

### Delivery Performance Metrics

- **On-time delivery**: Compare `order_delivered_customer_date` vs `order_estimated_delivery_date`
- **Geographic analysis**: Use `customer_geography_sk` and `seller_geography_sk` for route analysis
- **Category impact**: Join with `dim_product` for category-based performance

### Customer Satisfaction Correlation

- Primary insight: **Delayed orders correlate with lower ratings (1-2 vs 4-5 stars)**
- Use `review_score` from fact table and delivery status for correlation analysis
- Weight/price impact: Heavy/expensive orders (`product_weight_g`, `price`) tend to have longer delivery times

### Payment Analysis

- Join with `dim_payment` for payment method analysis
- Use `payment_installments` and `payment_value` for installment impact studies

## Schema Retrieval & Documentation

Use `Retrieve_schema_AQ.py` for schema documentation:

```bash
# Retrieve all dim_/fact_ table schemas
python Retrieve_schema_AQ.py --discover

# Custom table selection
python Retrieve_schema_AQ.py --tables dim_customer,fact_order_items
```

## Testing & Validation

- Validate business logic against `business_questions.md` requirements
- Test with sample data subsets before full dataset queries
- Verify metric calculations match business definitions in specification
- Use BigQuery query dry-run for cost estimation on large datasets

## Deployment Considerations

- **Environment**: Streamlit Cloud preferred, Docker as alternative
- **Authentication**: Use Google service account credentials for BigQuery
- **Caching**: Implement multi-level caching (memory + disk) for production
- **Performance**: Target <3s page loads, <2s chart rendering

## Common Gotchas

- Date fields have mixed types (TIMESTAMP vs STRING) - handle conversions carefully
- Use English category names (`product_category_name_english`) for user-facing displays
- Geography data may have missing lat/lng - handle nulls gracefully
- Review scores can be null - filter or handle appropriately for satisfaction metrics
