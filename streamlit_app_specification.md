# Olist Operational Metrics Dashboard - Software Specification

## Table of Contents

1. [Project Overview](#project-overview)
2. [Technical Requirements](#technical-requirements)
3. [Application Architecture](#application-architecture)
4. [User Interface Specification](#user-interface-specification)
5. [Data Requirements](#data-requirements)
6. [Feature Specifications](#feature-specifications)

---

## Project Overview

### Purpose

Develop a comprehensive Streamlit dashboard application to visualize and analyze operational metrics for the Olist e-commerce marketplace, focusing on delivery performance, customer satisfaction, and business growth indicators.

### Target Users

- **Business Analysts**: Strategic insights and trend analysis
- **Operations Managers**: Delivery performance monitoring
- **Product Managers**: Customer experience optimization
- **Executives**: High-level KPI tracking and decision support

### Core Objectives

- Provide real-time visibility into operational performance
- Enable data-driven decision making
- Support hypothesis testing for business improvements
- Facilitate cross-functional collaboration through shared metrics

---

## Technical Requirements

### Technology Stack

- **Frontend**: Streamlit 1.28+
- **Backend**: Python 3.12+
- **Database**: Google BigQuery (existing dbt_olist_stg dataset)
- **Data Processing**: Polars, NumPy
- **Visualization**: Plotly, Altair, Streamlit native charts
- **Authentication**: Streamlit built-in authentication
- **Deployment**: Streamlit Cloud or Docker containers

### Dependencies

```python
streamlit>=1.28.0
polars>=0.20.0
plotly>=5.15.0
altair>=5.0.0
google-cloud-bigquery>=3.11.0
numpy>=1.24.0
datetime
seaborn>=0.12.0
scipy>=1.10.0
streamlit-authenticator>=0.2.0
```

### System Requirements

- **Memory**: Minimum 4GB RAM, Recommended 8GB+
- **Storage**: 2GB available space
- **Network**: Stable internet connection for BigQuery access
- **Browser**: Chrome, Firefox, Safari (latest versions)

---

## Application Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   Data Layer     │    │   BigQuery      │
│   Frontend      │◄──►│   (Polars)       │◄──►│   Database      │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Visualization │    │   Business       │    │   dbt Models    │
│   Components    │    │   Logic Layer    │    │   (existing)    │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Module Structure

```
olist_dashboard/
├── main.py                 # Main Streamlit application
├── config/
│   ├── __init__.py
│   ├── settings.py         # Configuration settings
│   └── queries.py          # SQL queries repository
├── data/
│   ├── __init__.py
│   ├── data_loader.py      # BigQuery connection and data loading
│   ├── data_processor.py   # Data transformation and aggregation
│   └── cache_manager.py    # Caching strategies
├── components/
│   ├── __init__.py
│   ├── sidebar.py          # Navigation and filters
│   ├── metrics.py          # KPI cards and summary metrics
│   ├── charts.py           # Chart components
│   └── tables.py           # Data table components
├── pages/
│   ├── __init__.py
│   ├── delivery_performance.py
│   ├── customer_satisfaction.py
│   ├── product_analysis.py
│   ├── payment_insights.py
│   └── executive_summary.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py          # Utility functions
│   └── constants.py        # Application constants
└── requirements.txt
```

---

## User Interface Specification

### Navigation Structure

```
📊 Executive Summary (Landing Page)
├── 🚚 Delivery Performance
│   ├── On-Time Delivery Metrics
│   ├── Geographic Analysis
│   └── Route Performance
├── ⭐ Customer Satisfaction
│   ├── Rating Analysis
│   ├── Review Sentiment
│   └── Customer Retention
├── 📦 Product & Order Analysis
│   ├── Weight/Size Impact
│   ├── Category Performance
│   └── Order Complexity
├── 💳 Payment Insights
│   ├── Payment Method Analysis
│   ├── Installment Performance
│   └── Revenue Optimization
└── 📈 Advanced Analytics
    ├── Predictive Models
    ├── Correlation Analysis
    └── Custom Queries
```

### Layout Specifications

#### Common Elements

- **Header**: App title, refresh timestamp, data freshness indicator
- **Sidebar**: Navigation menu, global filters, date range selector
- **Main Content**: Page-specific visualizations and metrics
- **Footer**: Data source information, last update timestamp

#### Responsive Design

- **Desktop (>1200px)**: 3-column layout with full sidebar
- **Tablet (768-1200px)**: 2-column layout with collapsible sidebar
- **Mobile (<768px)**: Single-column layout with hamburger menu

---

## Data Requirements

### Data Sources

- **Primary**: BigQuery dataset `project-olist-470307.dbt_olist_stg`
- **Tables Used**:
  - `fact_order_items` (primary fact table)
  - `dim_customer`, `dim_orders`, `dim_product`
  - `dim_seller`, `dim_payment`, `dim_order_reviews`
  - `dim_date`, `dim_geolocation`

### Data Refresh Strategy

- **Real-time**: Not required (daily refresh acceptable)
- **Batch Updates**: Daily refresh at 6 AM UTC
- **Cache Duration**: 4 hours for aggregated metrics, 1 hour for detail views
- **Fallback**: Local cached data if BigQuery unavailable

### Data Quality Requirements

- **Completeness**: Handle missing values gracefully
- **Accuracy**: Validate data ranges and business rules
- **Consistency**: Ensure metric calculations match business definitions
- **Timeliness**: Display data freshness indicators

---

## Feature Specifications

### 1. Executive Summary Page

#### Key Metrics Cards

```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ On-Time     │ Avg Rating  │ Revenue     │ Active      │
│ Delivery    │ 4.2/5.0     │ Growth      │ Customers   │
│ 87.3%       │ ↑ 0.2       │ +12.5%      │ 45,123      │
│ ↓ 2.1%      │             │ ↑ 3.2%      │ ↑ 1,234     │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### Executive Dashboard

- High-level KPI trends (last 30/90/365 days)
- Geographic performance heatmap
- Category performance overview
- Alert indicators for critical metrics

### 2. Delivery Performance Page

#### 2.1 On-Time Delivery Metrics

- **Primary Visualizations**:
  - Time series chart: Daily/weekly on-time delivery rate
  - Geographic heatmap: Delivery performance by state/city
  - Distribution chart: Delivery time vs. estimated time
  - Pareto chart: Top delay causes

#### 2.2 Geographic Analysis

- **Interactive Map**: State/city performance with drill-down capability
- **Route Analysis**: Seller-to-customer shipping lanes
- **Distance Impact**: Correlation between distance and delivery time

#### 2.3 Delivery Time Analysis

- Delivery time distribution by product category
- Seasonal delivery performance trends
- Weekend vs. weekday performance comparison

### 3. Customer Satisfaction Page

#### 3.1 Rating Analysis

- **Rating Distribution**: Histogram of review scores
- **Rating vs. Delivery**: Scatter plot with trend line
- **Category Performance**: Average rating by product category
- **Time Series**: Rating trends over time

#### 3.2 Review Sentiment Analysis

- Word cloud from review comments
- Sentiment distribution (positive/neutral/negative)
- Correlation between delivery delay and sentiment

#### 3.3 Customer Retention Metrics

- Repeat purchase rate by rating given
- Customer lifetime value by satisfaction level
- Churn prediction indicators

### 4. Product & Order Analysis Page

#### 4.1 Weight/Size Impact

- **Scatter Plots**: Weight/volume vs. delivery time
- **Category Analysis**: Performance by product category
- **Threshold Analysis**: Identify weight/size breakpoints

#### 4.2 Order Complexity

- Single vs. multi-item order performance
- Order value impact on delivery time
- Freight cost optimization analysis

### 5. Payment Insights Page

#### 5.1 Payment Method Performance

- Processing time by payment type
- Success rate by payment method
- Geographic payment preferences

#### 5.2 Installment Analysis

- AOV by number of installments
- Customer retention by payment terms
- Revenue impact of installment options

### 6. Advanced Analytics Page

#### 6.1 Correlation Analysis

- Interactive correlation matrix
- Statistical significance testing
- Causal relationship exploration

#### 6.2 Predictive Models

- Delivery delay prediction model results
- Customer satisfaction prediction
- Revenue forecasting

---

## Interactive Features

### Filtering and Navigation

- **Date Range Picker**: Custom date ranges with preset options
- **Geographic Filters**: State, city, region selection
- **Category Filters**: Product categories, seller tiers
- **Performance Filters**: Rating ranges, delivery status

### Export Capabilities

- **Chart Export**: PNG, SVG, PDF formats
- **Data Export**: CSV, Excel downloads
- **Report Generation**: Automated summary reports

### Real-time Features

- **Auto-refresh**: Configurable refresh intervals
- **Data Alerts**: Threshold-based notifications
- **Bookmark Views**: Save custom filter combinations

---

_This specification serves as the definitive guide for developing the Olist Operational Metrics Dashboard and should be updated as requirements evolve during development._

---

## Performance Requirements

### Response Time Targets

- **Page Load**: < 3 seconds initial load
- **Chart Rendering**: < 2 seconds for standard visualizations
- **Data Refresh**: < 10 seconds for incremental updates
- **Export Operations**: < 30 seconds for large datasets

### Scalability Requirements

- **Concurrent Users**: Support 50+ simultaneous users
- **Data Volume**: Handle 1M+ records efficiently
- **Memory Usage**: < 2GB RAM per user session
- **Cache Efficiency**: 80%+ cache hit rate for common queries

### Optimization Strategies

- **Data Caching**: Multi-level caching (memory, disk, CDN)
- **Query Optimization**: Pre-aggregated metrics, indexed queries
- **Lazy Loading**: Load visualizations on-demand
- **Compression**: Gzip compression for data transfer

---

## Deployment Specification

### Environment Configuration

- **Development**: Local development with sample data
- **Staging**: Pre-production testing environment
- **Production**: Scalable production deployment

### Deployment Options

#### Option 1: Streamlit Cloud

```yaml
# streamlit_config.toml
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false

[global]
dataFrameSerialization = "arrow"
```

#### Option 2: Docker Deployment (KIV)

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "main.py", "--server.port=8501"]
```

### Environment Variables

```bash
# BigQuery Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
BQ_PROJECT_ID=project-olist-470307
BQ_DATASET=dbt_olist_stg

# Application Configuration
STREAMLIT_ENV=production
CACHE_TTL=3600
MAX_CONCURRENT_USERS=50
```

---

## Testing Strategy

### Testing Levels

1. **Unit Tests**: Individual component testing
2. **Integration Tests**: Database connection and data processing
3. **UI Tests**: User interface functionality
4. **Performance Tests**: Load and stress testing
5. **User Acceptance Tests**: Business requirement validation

### Test Data Strategy

- **Sample Dataset**: Representative subset for development
- **Synthetic Data**: Generated test data for edge cases
- **Production Snapshots**: Anonymized production data for testing

### Quality Assurance

- **Code Review**: Peer review for all changes
- **Automated Testing**: CI/CD pipeline integration
- **Manual Testing**: User experience validation
- **Performance Monitoring**: Real-time performance tracking

---

_This specification serves as the definitive guide for developing the Olist Operational Metrics Dashboard and should be updated as requirements evolve during development._
