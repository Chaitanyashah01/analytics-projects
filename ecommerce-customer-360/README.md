# E-Commerce Customer 360 Dashboard

A comprehensive customer analytics platform providing 360-degree visibility into customer behavior, segmentation, and engagement patterns.

## Features

### Analytics Capabilities
- **Customer Demographics**: Age, gender, location, and income analysis
- **Purchase Behavior**: Spending patterns, cart abandonment, order value analysis
- **Customer Segmentation**: RFM-based loyalty segmentation
- **Engagement Metrics**: App usage, session time, and ad performance
- **Statistical Analysis**: Hypothesis testing and correlation analysis

### Technical Highlights
- Customer value scoring and segmentation
- Engagement score calculations
- Interactive cohort analysis
- Statistical hypothesis testing (ANOVA)
- Correlation analysis for behavioral insights

## Dashboard Pages

1. **Customer Overview** - KPIs and segment distribution
2. **Demographics** - Customer profile analysis
3. **Purchase Behavior** - Spending and cart analysis
4. **Segmentation** - Loyalty segments and cohort analysis
5. **Engagement** - App usage and platform engagement metrics

## Data Dictionary

### customers.csv (60+ columns)
| Category | Key Columns |
|----------|-------------|
| Demographics | user_id, age, gender, country, income_level |
| Shopping | weekly_purchases, monthly_spend, cart_abandonment_rate |
| Engagement | daily_session_time, product_views, ad_clicks |
| Lifestyle | health_conscious, environmental_consciousness |

### Derived Metrics
| Metric | Description |
|--------|-------------|
| age_group | Bucketed age ranges |
| income_segment | Low to High income categories |
| spend_segment | Low to Premium spending tiers |
| engagement_score | Composite engagement metric (0-100) |
| customer_value_score | RFM-inspired value score |
| loyalty_segment | At Risk to Champion segments |

## Customer Segments

| Segment | Description |
|---------|-------------|
| Champion | Highest value, most engaged |
| Loyal | Consistent high-value customers |
| Regular | Moderate engagement and spend |
| Occasional | Sporadic purchasers |
| At Risk | Low engagement, potential churn |

## Installation

```bash
# Clone repository
git clone <repository-url>
cd ecommerce-customer-360

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Data Setup

The customer dataset needs to be placed in the `data/` directory:

1. Place `e_commerce_shopper_behaviour_and_lifestyle.csv` in the `data/` folder
2. Run the dashboard: `streamlit run app.py`
3. The database will auto-initialize on first run

Note: Initial database creation may take 1-2 minutes due to large dataset size.

## Key Business Questions

- Who are our most valuable customers?
- What drives customer engagement?
- Which segments have highest cart abandonment?
- How does spending vary by demographics?
- What factors predict customer value?

## Statistical Methods

- **Segmentation**: RFM-based customer value scoring
- **ANOVA**: Spend differences across segments
- **Correlation Analysis**: Behavioral relationships
- **Regression**: Predictors of customer value

## Project Structure

```
ecommerce-customer-360/
├── app.py
├── pages/
│   ├── 1_Demographics.py
│   ├── 2_Purchase_Behavior.py
│   ├── 3_Segmentation.py
│   └── 4_Engagement.py
├── database/
│   ├── init_db.py
│   └── queries.py
├── utils/
│   └── statistics.py
├── data/
├── requirements.txt
└── README.md
```

## License

MIT License
