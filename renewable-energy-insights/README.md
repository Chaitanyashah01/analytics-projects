# Renewable Energy Production Insights Dashboard

An analytics dashboard for analyzing wind and solar energy production patterns, seasonal variations, and capacity optimization opportunities.

## Features

### Analytics Capabilities
- **Source Comparison**: Wind vs Solar production analysis
- **Temporal Patterns**: Hourly, daily, and weekly production profiles
- **Seasonal Analysis**: Production variations across seasons
- **Capacity Planning**: Production reliability and optimization metrics
- **Statistical Testing**: ANOVA and t-tests for production differences

### Technical Highlights
- Time series analysis with hourly granularity
- Production variability and reliability metrics
- Capacity factor calculations
- Interactive heatmaps and trend visualizations
- Statistical hypothesis testing

## Dashboard Pages

1. **Production Overview** - Total production and source distribution
2. **Source Comparison** - Wind vs Solar statistical analysis
3. **Temporal Patterns** - Hour and day-of-week patterns with heatmaps
4. **Seasonal Analysis** - Monthly and seasonal production trends
5. **Capacity Planning** - Reliability metrics and optimization insights

## Data Dictionary

### energy_production.csv
| Column | Description |
|--------|-------------|
| date | Production date |
| start_hour | Hour of production (0-23) |
| end_hour | End hour |
| source | Wind or Solar |
| day_of_year | Day number in year |
| day_name | Day of week |
| month_name | Month name |
| season | Spring/Summer/Fall/Winter |
| production | Energy produced (MWh) |

### Derived Metrics
| Metric | Description |
|--------|-------------|
| time_of_day | Morning/Afternoon/Evening/Night |
| capacity_factor | Actual vs peak production ratio |
| variability (CV) | Coefficient of variation |

## Installation

```bash
# Clone repository
git clone <repository-url>
cd renewable-energy-insights

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

## Key Insights

The dashboard helps answer questions like:
- What are the peak production hours for wind vs solar?
- How does production vary by season?
- What is the capacity factor for each energy source?
- When can we expect the most reliable production?

## Statistical Methods

- **Descriptive Statistics**: Mean, median, variance, percentiles
- **ANOVA Testing**: Production differences across seasons
- **T-Tests**: Wind vs Solar comparison
- **Time Series Analysis**: Trend detection and seasonality

## Project Structure

```
renewable-energy-insights/
├── app.py
├── pages/
│   ├── 1_Source_Comparison.py
│   ├── 2_Temporal_Patterns.py
│   ├── 3_Seasonal_Analysis.py
│   └── 4_Capacity_Planning.py
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
