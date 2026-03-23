# Automotive Performance Analytics Dashboard

A comprehensive analytics dashboard for analyzing vehicle specifications, performance metrics, and market positioning across leading automotive brands.

## Features

### Analytics Capabilities
- **Performance Benchmarking**: Compare horsepower, top speed, and acceleration metrics
- **Brand Comparison**: Cross-brand analysis with radar charts and statistical testing
- **Price-Performance Analysis**: Value analysis and price-to-performance ratios
- **EV vs ICE Comparison**: Electric vs traditional powertrain analysis
- **Market Segmentation**: Price segment and performance category analysis

### Technical Highlights
- Automated data cleaning and standardization
- SQLite database with derived metrics
- Interactive Plotly visualizations
- Statistical hypothesis testing (ANOVA, t-tests)
- Regression analysis for price-performance relationships

## Dashboard Pages

1. **Market Overview** - Summary metrics and brand distribution
2. **Performance Analysis** - HP, speed, acceleration analysis with correlations
3. **Brand Comparison** - Multi-metric brand benchmarking
4. **Price Analysis** - Value analysis and segmentation
5. **EV vs ICE** - Powertrain technology comparison

## Data Dictionary

### cars.csv
| Column | Description |
|--------|-------------|
| company | Brand/manufacturer |
| car_name | Model name |
| engine | Engine type |
| cc_capacity | Engine displacement |
| horsepower | Power output (HP) |
| top_speed | Maximum speed (km/h) |
| acceleration_0_100 | 0-100 km/h time (seconds) |
| price | Vehicle price (USD) |
| fuel_type | Fuel/power type |
| seats | Seating capacity |
| torque | Torque (Nm) |

### Derived Metrics
| Metric | Description |
|--------|-------------|
| price_per_hp | Price divided by horsepower |
| performance_score | Composite score (0-100) |
| price_segment | Budget/Mid/Premium/Luxury/Ultra-Luxury |

## Installation

```bash
# Clone repository
git clone <repository-url>
cd automotive-performance

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run dashboard
streamlit run app.py
```

## Data Cleaning Pipeline

The system automatically:
- Standardizes price formats (removes currency symbols, handles ranges)
- Normalizes horsepower values
- Cleans speed and acceleration data
- Standardizes fuel type categories
- Calculates derived performance metrics
- Removes duplicates

## Statistical Methods

- **Correlation Analysis**: Relationship between price, power, and speed
- **ANOVA Testing**: Compare performance across brands and fuel types
- **Linear Regression**: Price-performance modeling
- **Distribution Analysis**: Outlier detection and normality testing

## Project Structure

```
automotive-performance/
├── app.py
├── pages/
│   ├── 1_Performance_Analysis.py
│   ├── 2_Brand_Comparison.py
│   ├── 3_Price_Analysis.py
│   └── 4_EV_vs_ICE.py
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
