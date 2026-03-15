# Project Summary — Rental Property Management & Analytics

## Business Context

This project models a **real-world rental property operation** in Taiwan: a 3-story townhouse with 9 residential units, 1 ground-floor storefront, and 5 scooter/motorcycle parking slots. The owner needs data-driven visibility into occupancy, revenue streams, payment behavior, expenses, and net profitability.

The system uses **SQLite** as a lightweight embedded database and **Python** for analytics, making it fully runnable on any laptop with zero infrastructure setup.

## Available Tables

| Table | Records | Description |
|-------|---------|-------------|
| `units` | 9 | Residential rooms across floors 2–4 (6–12 ping, NT$6,000–12,000/mo) |
| `tenants` | 12 | Tenant contact info (some historical, some current) |
| `leases` | 17 | Lease agreements (2024–2026, mix of active and expired) |
| `payments` | 159 | Monthly rent payments with on-time, late, and partial statuses |
| `parking_slots` | 5 | Scooter/motorcycle parking spaces |
| `parking_leases` | 6 | Parking rental agreements |
| `storefront` | 1 | Ground-floor breakfast shop lease |
| `expenses` | 33 | Property expenses (maintenance, tax, insurance, utilities, repairs) |

## Key KPIs

| KPI | Description |
|-----|-------------|
| **Occupancy Rate** | % of units with active leases |
| **Total Residential Revenue** | Sum of all rent payments collected |
| **Average Monthly Revenue** | Average rent collected per month |
| **Storefront Revenue** | Commercial tenant monthly rent |
| **Parking Revenue** | Monthly income from parking leases |
| **Average Rent by Floor** | Rent comparison across building floors |
| **Rent per Ping** | Efficiency metric: price per unit area |
| **On-Time Payment Rate** | % of payments made by due date |
| **Overdue Rate** | % of late, partial, or missed payments |
| **Total Expenses** | Sum of all property operating costs |
| **Monthly Net Cash Flow** | Revenue minus expenses per month |
| **Net Operating Income (NOI)** | Total revenue minus total expenses |

## Main Analysis Outputs

1. **Occupancy Analysis** — Current unit status, historical occupancy trends
2. **Rent Analysis** — Rent comparison by floor, by features, rent per ping ranking
3. **Payment Analysis** — On-time vs overdue rates, late payment details, tenant-level risk
4. **Revenue Analysis** — Monthly trends, per-unit breakdown, storefront and parking revenue
5. **Expense Analysis** — By category, recurring vs one-time, top vendors
6. **Cash Flow** — Monthly net cash flow, annual summary, all-time NOI
7. **Data Validation** — 22 automated quality checks on integrity, consistency, and business rules

## Decision Support

This analytics system helps property owners:

- **Identify vacancy risk** — Track occupancy trends and flag units approaching lease expiration
- **Optimize rent pricing** — Compare rent-per-ping across units and floors to find underpriced rooms
- **Monitor payment reliability** — Detect tenants with late payment patterns
- **Control expenses** — Track expense categories and spot cost escalation
- **Evaluate profitability** — See net operating income and monthly cash flow at a glance
- **Ensure data integrity** — Automated validation catches inconsistencies before they cause wrong decisions

## Portfolio & Job Application Relevance

This project demonstrates skills valued in **Data Analyst** and **Data Science** roles:

| Skill | How Demonstrated |
|-------|------------------|
| **SQL** | Complex queries with CTEs, window functions, aggregations, joins |
| **Python** | Data loading, validation scripts, analytics pipeline |
| **Data Modeling** | Normalized relational schema with proper FKs and constraints |
| **ETL** | CSV → SQLite loading with dependency ordering |
| **Data Quality** | Automated validation with 22 checks (nulls, FKs, ranges, business rules) |
| **KPI Design** | Business-focused metrics tied to real property management decisions |
| **Domain Knowledge** | Real estate operations, rental management, financial analysis |
| **Documentation** | Clear README, project summary, code comments |

## How to Run

```bash
# Setup
pip install -r requirements.txt
python build_db.py

# Analytics
python analytics/kpi_metrics.py        # Key Performance Indicators
python analytics/run_analytics.py       # Full analytics report
python analytics/validate_data.py       # Data quality checks
```
