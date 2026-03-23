# Aviation Fuel Analytics Dashboard

A comprehensive business analytics dashboard analyzing the impact of oil prices and geopolitical events on airline operations and financial performance.

## Features

### Data Analytics
- **Oil Price Impact Analysis**: Correlation studies between crude oil prices and airline profitability
- **Conflict Event Timeline**: Interactive visualization of geopolitical events and their measured impact
- **Airline Performance Benchmarking**: Cross-airline comparison of revenue, margins, and efficiency
- **Route Profitability Analysis**: Route-level fuel cost and revenue metrics
- **Statistical Analysis**: Hypothesis testing, regression analysis, and data quality assessment

### Technical Highlights
- SQLite database with optimized schema and indexing
- Interactive Plotly visualizations
- Real-time filtering and drill-down capabilities
- Statistical testing (ANOVA, t-tests, correlation analysis)
- Data quality monitoring and outlier detection

## Dashboard Pages

1. **Executive Overview** - KPIs and high-level metrics
2. **Oil Price Impact** - Correlation analysis with regression modeling
3. **Conflict Timeline** - Event impact visualization and statistical testing
4. **Airline Comparison** - Performance benchmarking across airlines and regions
5. **Route Analysis** - Route-level profitability and fuel cost analysis
6. **Statistical Analysis** - Comprehensive statistical testing and data quality

## Data Dictionary

### airline_financial_impact.csv
| Column | Description |
|--------|-------------|
| quarter | Fiscal quarter (e.g., 2019-Q1) |
| airline | Airline name |
| revenue_usd_m | Revenue in millions USD |
| fuel_cost_usd_m | Fuel costs in millions USD |
| profit_margin_pct | Profit margin percentage |
| passengers_carried_m | Passengers in millions |

### conflict_oil_events.csv
| Column | Description |
|--------|-------------|
| event_date | Date of event |
| event_type | Political/Military |
| severity | Low/Medium/High/Very High |
| oil_price_change_pct | Impact on oil prices |
| airfare_impact_pct | Impact on airfares |

## Installation

```bash
# Clone repository
git clone <repository-url>
cd aviation-fuel-analytics

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

## Usage

1. Launch the dashboard with `streamlit run app.py`
2. The database will auto-initialize on first run
3. Use sidebar filters to explore different data segments
4. Download analysis results using export buttons

## Statistical Methods

- **Correlation Analysis**: Pearson and Spearman correlation coefficients
- **Regression Analysis**: Simple and multiple linear regression
- **Hypothesis Testing**: ANOVA for group comparisons, t-tests for pairwise analysis
- **Data Quality**: Outlier detection (IQR, Z-score), normality testing

## Project Structure

```
aviation-fuel-analytics/
├── app.py                 # Main Streamlit application
├── pages/                 # Dashboard pages
│   ├── 1_Oil_Price_Impact.py
│   ├── 2_Conflict_Timeline.py
│   ├── 3_Airline_Comparison.py
│   ├── 4_Route_Analysis.py
│   └── 5_Statistical_Analysis.py
├── database/
│   ├── init_db.py        # Database initialization
│   └── queries.py        # SQL query functions
├── utils/
│   ├── statistics.py     # Statistical analysis utilities
│   ├── visualizations.py # Plotly chart functions
│   └── data_loader.py    # Data loading utilities
├── data/                  # CSV data files
├── requirements.txt
└── README.md
```

## License

MIT License
