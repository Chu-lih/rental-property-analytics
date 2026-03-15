# Rental Property Management & Analytics System

An end-to-end data analytics project that models a real-world rental property in Taiwan — tracking occupancy, revenue, expenses, payment behavior, and profitability through SQL analytics, automated data validation, and an interactive Streamlit dashboard.

> **Built for portfolio demonstration** — showcases SQL, Python, ETL, data quality, KPI design, and data visualization skills relevant to Data Analyst and Data Scientist roles.

## Property Overview

| Asset | Details |
|-------|----------|
| **Building** | 3-story townhouse |
| **Residential** | 9 units (3 per floor, 6–12 ping, NT$6K–12K/mo) |
| **Commercial** | 1 ground-floor storefront (breakfast shop, NT$25K/mo) |
| **Parking** | 5 scooter/motorcycle slots (NT$400–600/mo) |

## Project Structure

```
rental-property-analytics/
├── README.md
├── project_summary.md              # Business context + KPI reference
├── portfolio_description.md        # Portfolio-ready project writeup
├── resume_bullets.md               # Copy-paste resume bullets
├── interview_talking_points.md     # Interview prep notes
├── requirements.txt
├── .gitignore
├── build_db.py                     # Builds rental_property.db
├── rental_property.db              # Generated SQLite database (git-ignored)
├── db/
│   ├── schema.sql                  # 8-table schema
│   └── seed/                       # CSV seed data (8 files, 242 rows)
├── analytics/
│   ├── kpi_metrics.py              # KPI calculations
│   ├── run_analytics.py            # Full analytics report
│   ├── validate_data.py            # 25 data quality checks
│   └── queries/                    # SQL query files (6 files)
└── app/
    ├── dashboard.py                # Streamlit dashboard
    └── db_helpers.py               # DB query helpers
```

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Build the database
python build_db.py
```

## Analytics Commands

```bash
# KPI dashboard (summary metrics)
python analytics/kpi_metrics.py

# Full analytics report (all analyses)
python analytics/run_analytics.py

# Data quality validation (22 checks)
python analytics/validate_data.py
```

## Dashboard

```bash
streamlit run app/dashboard.py
```

Opens at http://localhost:8501 with KPI cards, cash flow chart, rent breakdown, payment status, and parking/storefront tables.

## Database Tables

| Table | Records | Description |
|-------|---------|-------------|
| `units` | 9 | Residential units with floor, size, rent, and features |
| `tenants` | 12 | Tenant contact information |
| `leases` | 17 | Lease agreements linking tenants to units |
| `payments` | 159 | Monthly rent payment records |
| `parking_slots` | 5 | Scooter/motorcycle parking spaces |
| `parking_leases` | 6 | Parking slot rental agreements |
| `storefront` | 1 | Commercial storefront lease details |
| `expenses` | 33 | Property expenses (maintenance, tax, insurance, utilities) |

## Key KPIs

- Occupancy rate
- Total / avg monthly residential revenue
- Storefront & parking revenue
- Average rent by floor and rent per ping
- On-time vs overdue payment rate
- Monthly expenses and net cash flow
- Net operating income (NOI)

See [project_summary.md](project_summary.md) for full details.

## Tech Stack

- **Python 3.10+** — ETL, analytics, data validation
- **SQLite** — lightweight embedded relational database
- **pandas** — data manipulation and reporting
- **Streamlit** — interactive dashboard framework
- **Plotly** — interactive chart visualizations

## Documentation

- [project_summary.md](project_summary.md) — business context, KPIs, decision support
- [portfolio_description.md](portfolio_description.md) — portfolio-ready project writeup
- [resume_bullets.md](resume_bullets.md) — copy-paste resume bullets
- [interview_talking_points.md](interview_talking_points.md) — interview prep notes

## Future Work

- ML models (churn prediction, rent forecasting, anomaly detection)
- Time-series analysis and seasonal patterns
- Multi-property portfolio support
