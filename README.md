# Olist Analytics Dashboard

A comprehensive Streamlit dashboard for analyzing Olist e-commerce operational metrics using Google BigQuery and dimensional modeling.

## 🚀 Quick Start

### Prerequisites

- Python 3.12+
- Google Cloud Project with BigQuery access
- Service account credentials for BigQuery

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd BDE_streamlit
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Google Cloud credentials**

   ```bash
   # Set environment variable for service account
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/service-account.json"

   # Or configure in config/settings.py
   ```

4. **Run the application**
   ```bash
   streamlit run main.py
   ```

## 📊 Features

### Dashboard Pages

- **📈 Executive Summary**: High-level KPIs, trends, and performance overview
- **🚚 Delivery Performance**: Detailed delivery metrics and geographic analysis
- **⭐ Customer Satisfaction**: Rating analysis and satisfaction drivers
- **📦 Product Analysis**: Weight impact, category performance, and product insights
- **💳 Payment Insights**: Payment methods, installments, and revenue optimization

### Core Capabilities

- **Real-time Analytics**: Live data from BigQuery with multi-level caching
- **Interactive Filtering**: Date range, geography, product categories
- **Advanced Visualizations**: Plotly and Altair charts with drill-down capabilities
- **Export Functions**: CSV, Excel, and PDF export options
- **Performance Optimization**: Smart caching with configurable TTL
- **Responsive Design**: Mobile-friendly layouts and adaptive charts

## 🏗️ Architecture

### Project Structure

```
olist_dashboard/
├── main.py                    # Streamlit application entry point
├── config/
│   ├── settings.py           # Configuration and BigQuery connection
│   └── queries.py            # SQL query templates
├── data/
│   ├── data_loader.py        # BigQuery data fetching
│   ├── data_processor.py     # Polars data transformations
│   └── cache_manager.py      # Multi-level caching
├── components/               # Reusable UI components
│   ├── sidebar.py           # Navigation and filters
│   ├── metrics.py           # KPI cards and metrics
│   ├── charts.py            # Chart components
│   └── tables.py            # Data table components
├── pages/                    # Dashboard page modules
│   ├── executive_summary.py
│   ├── delivery_performance.py
│   ├── customer_satisfaction.py
│   ├── product_analysis.py
│   └── payment_insights.py
└── utils/                    # Helper functions
    ├── helpers.py           # Data validation and formatting
    └── __init__.py
```

### Technology Stack

- **Frontend**: Streamlit 1.28+
- **Data Processing**: Polars (high-performance DataFrames)
- **Database**: Google BigQuery
- **Visualizations**: Plotly, Altair
- **Caching**: Multi-level (memory + disk + Streamlit native)
- **Authentication**: Google Cloud service accounts

## 📈 Data Model

### Star Schema Design

The dashboard uses a dimensional model optimized for analytical queries:

**Fact Table**:

- `fact_order_items` - Central fact table with all business metrics

**Dimension Tables**:

- `dim_customer` - Customer demographics and geography
- `dim_orders` - Order details and status
- `dim_product` - Product catalog and categories
- `dim_seller` - Seller information and location
- `dim_payment` - Payment methods and installments
- `dim_order_reviews` - Customer reviews and ratings
- `dim_date` - Date dimension for time-based analysis
- `dim_geolocation` - Geographic coordinates and regions

### Key Business Metrics

- **Delivery Performance**: On-time rate, delivery days, geographic routes
- **Customer Satisfaction**: Rating distribution, satisfaction vs delivery correlation
- **Product Analysis**: Weight impact, category performance, order complexity
- **Payment Insights**: Method preferences, installment patterns, revenue optimization

## ⚙️ Configuration

### Environment Variables

```bash
# Google Cloud
GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account.json"
GOOGLE_CLOUD_PROJECT="your-project-id"

# BigQuery
BQ_DATASET_ID="dsai-468212.dbt_olist_stg"
BQ_LOCATION="US"

# Application
STREAMLIT_THEME="light"
DEBUG_MODE="false"
CACHE_TTL_HOURS="4"
```

### Configuration Files

Edit `olist_dashboard/config/settings.py` for:

- BigQuery connection parameters
- UI styling and themes
- Caching strategies
- Performance settings

## 🚀 Deployment

### Streamlit Cloud

1. **Connect repository** to Streamlit Cloud
2. **Set secrets** in Streamlit Cloud dashboard:
   ```toml
   # .streamlit/secrets.toml
   [gcp_service_account]
   type = "service_account"
   project_id = "your-project-id"
   private_key_id = "key-id"
   private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
   client_email = "service-account@project.iam.gserviceaccount.com"
   # ... other service account fields
   ```
3. **Deploy** application

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "main.py"]
```

### Local Development

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug mode
STREAMLIT_DEBUG=true streamlit run main.py

# Run tests
pytest tests/
```

## 📊 Usage Examples

### Basic Analytics

```python
# Example: Get delivery performance metrics
from olist_dashboard.data.data_loader import get_data_loader

loader = get_data_loader()
delivery_data = loader.get_delivery_performance("2023-01-01", "2023-12-31")
```

### Custom Queries

```python
# Example: Custom BigQuery analysis
custom_query = """
SELECT
    c.customer_state,
    AVG(f.delivery_days) as avg_delivery,
    COUNT(*) as order_count
FROM fact_order_items f
JOIN dim_customer c ON f.customer_sk = c.customer_sk
WHERE f.order_date_sk BETWEEN 20230101 AND 20231231
GROUP BY c.customer_state
ORDER BY avg_delivery DESC
"""

results = loader.execute_query(custom_query)
```

## 🔧 Development

### Adding New Pages

1. **Create page module** in `olist_dashboard/pages/`
2. **Implement render function** following existing patterns
3. **Add navigation** in `components/sidebar.py`
4. **Update main routing** in `main.py`

### Adding New Charts

1. **Extend chart functions** in `components/charts.py`
2. **Follow naming conventions**: `render_[domain]_[chart_type]`
3. **Include error handling** and fallbacks
4. **Add export capabilities**

### Performance Optimization

- Use `@cache_details()` decorator for expensive operations
- Implement data pagination for large datasets
- Optimize BigQuery queries with proper indexing
- Monitor cache hit rates and adjust TTL accordingly

## 📚 Business Intelligence

### Key Insights

1. **Delivery Performance**

   - Heavy products (5kg+) have 2-3 day longer delivery times
   - Geographic distance strongly correlates with delivery delays
   - Product categories show distinct delivery patterns

2. **Customer Satisfaction**

   - Strong negative correlation between delivery delays and ratings
   - Product category significantly impacts satisfaction scores
   - Review patterns indicate actionable improvement areas

3. **Product Analysis**

   - Weight-based logistics optimization opportunities
   - Category performance varies significantly by region
   - Order complexity affects delivery and satisfaction

4. **Payment Insights**
   - Installment options drive higher order values
   - Payment method preferences vary by geography
   - Revenue optimization through payment strategy

### Business Questions Answered

See `business_questions.md` for detailed analysis of:

- Delivery performance drivers
- Customer satisfaction factors
- Product category optimization
- Payment method effectiveness
- Geographic performance patterns

## 🤝 Contributing

1. **Fork the repository**
2. **Create feature branch**: `git checkout -b feature/new-analysis`
3. **Follow coding conventions** (see Python instructions file)
4. **Add tests** for new functionality
5. **Submit pull request** with detailed description

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🆘 Support

- **Documentation**: See `/docs` folder for detailed guides
- **Issues**: GitHub Issues for bug reports and feature requests
- **Discussions**: GitHub Discussions for questions and ideas

## 🔄 Changelog

### v1.0.0 (Current)

- Initial release with complete dashboard functionality
- All 5 dashboard pages implemented
- Multi-level caching system
- Responsive design and mobile support
- Export capabilities and advanced filtering

---

**Built with ❤️ using Streamlit, Polars, and Google BigQuery**
