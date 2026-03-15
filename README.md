# Rental Property Management & Analytics System

A data project for managing and analyzing a rental property portfolio using Python and SQLite.

## Property Overview

- **Building**: 3-story townhouse
- **Residential Units**: 9 rooms (3 per floor)
- **Commercial**: 1 ground-floor storefront
- **Parking**: 5 scooter/motorcycle slots

## Project Structure

```
rental-property-analytics/
├── README.md
├── project_summary.md            # Business context, KPIs, portfolio relevance
├── requirements.txt
├── .gitignore
├── build_db.py                   # Builds rental_property.db from schema + seed data
├── rental_property.db            # Generated SQLite database (git-ignored)
├── db/
│   ├── schema.sql                # Table definitions
│   └── seed/                     # CSV seed data files
│       ├── units.csv
│       ├── tenants.csv
│       ├── leases.csv
│       ├── payments.csv
│       ├── parking_slots.csv
│       ├── parking_leases.csv
│       ├── storefront.csv
│       └── expenses.csv
└── analytics/
    ├── kpi_metrics.py            # KPI calculations
    ├── run_analytics.py          # Full analytics report
    ├── validate_data.py          # Data quality checks (22 validations)
    └── queries/                  # SQL query files
        ├── occupancy.sql
        ├── rent_analysis.sql
        ├── payment_status.sql
        ├── revenue.sql
        ├── expenses.sql
        └── cash_flow.sql
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

- **Python 3.10+**
- **SQLite** — lightweight embedded database
- **pandas** — data manipulation and reporting

## Future Phases

- **Phase 3**: Streamlit dashboard
- **Phase 4**: ML models (churn, forecasting, rent analysis)
