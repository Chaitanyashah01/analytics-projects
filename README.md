# Business Analytics Portfolio

A collection of four comprehensive business analytics dashboards demonstrating advanced data analysis, statistical modeling, and interactive visualization capabilities.

## Live Demos

[![Aviation Fuel Analytics](https://img.shields.io/badge/Aviation_Fuel_Analytics-Live_Demo-1f77b4?style=for-the-badge&logo=streamlit)](https://aviation-fuel-analytics.streamlit.app/)
[![Automotive Performance](https://img.shields.io/badge/Automotive_Performance-Live_Demo-e74c3c?style=for-the-badge&logo=streamlit)](https://automotive-performance.streamlit.app/)
[![Renewable Energy](https://img.shields.io/badge/Renewable_Energy-Live_Demo-27ae60?style=for-the-badge&logo=streamlit)](https://renewable-energy-insights.streamlit.app/)

## Projects

| Project | Domain | Key Analytics | Demo |
|---------|--------|---------------|------|
| [Aviation Fuel Analytics](./aviation-fuel-analytics/) | Transportation & Energy | Time series analysis, correlation studies, event impact analysis | [Launch App](https://aviation-fuel-analytics.streamlit.app/) |
| [Automotive Performance](./automotive-performance/) | Automotive | Regression analysis, market segmentation, performance benchmarking | [Launch App](https://automotive-performance.streamlit.app/) |
| [Renewable Energy Insights](./renewable-energy-insights/) | Energy & Sustainability | Seasonal decomposition, production forecasting, capacity optimization | [Launch App](https://renewable-energy-insights.streamlit.app/) |
| [E-Commerce Customer 360](./ecommerce-customer-360/) | Retail & Marketing | Customer segmentation, behavioral clustering, conversion analytics | Coming Soon |

## Technical Stack

- **Framework:** Streamlit
- **Database:** SQLite
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Statistical Analysis:** SciPy, Statsmodels, Scikit-learn
- **Data Processing:** Pandas, NumPy

## Features

### Data Engineering
- Automated data cleaning pipelines with quality metrics
- Schema validation and type inference
- Missing value analysis and imputation strategies
- Outlier detection using statistical methods (IQR, Z-score)

### Statistical Analysis
- Descriptive statistics with confidence intervals
- Correlation analysis (Pearson, Spearman)
- Hypothesis testing (t-tests, ANOVA, chi-square)
- Regression modeling (Linear, Polynomial)
- Time series decomposition and forecasting

### Interactive Dashboards
- Real-time filtering and drill-down capabilities
- Cross-filtering between visualizations
- Export functionality for reports
- Responsive design for all screen sizes

## Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd analytics-projects

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run any project
cd aviation-fuel-analytics  # or any other project
streamlit run app.py
```

## Project Structure

```
analytics-projects/
├── README.md
├── requirements.txt
├── .gitignore
│
├── aviation-fuel-analytics/
│   ├── app.py
│   ├── pages/
│   ├── database/
│   ├── utils/
│   └── data/
│
├── automotive-performance/
│   ├── app.py
│   ├── pages/
│   ├── database/
│   ├── utils/
│   └── data/
│
├── renewable-energy-insights/
│   ├── app.py
│   ├── pages/
│   ├── database/
│   ├── utils/
│   └── data/
│
└── ecommerce-customer-360/
    ├── app.py
    ├── pages/
    ├── database/
    ├── utils/
    └── data/
```

## Deployment

### Live Deployments

| Dashboard | URL |
|-----------|-----|
| Aviation Fuel Analytics | https://aviation-fuel-analytics.streamlit.app/ |
| Automotive Performance | https://automotive-performance.streamlit.app/ |
| Renewable Energy Insights | https://renewable-energy-insights.streamlit.app/ |

### Deploy Your Own

Each project is configured for Streamlit Cloud deployment:

1. Fork this repository
2. Create a [Streamlit Cloud](https://streamlit.io/cloud) account
3. Connect your GitHub repository
4. Select the project subdirectory (e.g., `aviation-fuel-analytics`)
5. Set `app.py` as the main file
6. Deploy

## License

MIT License - See individual project READMEs for details.
