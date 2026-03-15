# Interview Talking Points

## Rental Property Management & Analytics System

Quick-reference notes for behavioral and technical interviews.

---

### "Tell me about a data project you've built."

> I built an end-to-end analytics system for a rental property — a townhouse-style building in Taiwan with basement parking, a ground-floor storefront, and 9 residential units across floors 2–4. I designed the database schema, wrote the ETL pipeline, created 25 automated data quality checks, computed 10+ business KPIs, and built a Streamlit dashboard — all from scratch. The system gives property owners real-time visibility into occupancy, revenue, expenses, and net profitability.

---

### "Walk me through the technical decisions."

- **SQLite over PostgreSQL**: Chose SQLite for zero-setup portability — the entire project runs from a single `python build_db.py` command. The schema is normalized and would migrate to PostgreSQL with minimal changes.
- **CSV seed data over SQL INSERTs**: CSVs are easier to review, diff in Git, and edit. The Python loader handles FK ordering automatically.
- **Separate SQL files**: Each analysis domain (occupancy, payments, cash flow) has its own `.sql` file — makes queries testable and reusable independently.
- **Streamlit + Plotly**: Lightweight dashboard framework that's fast to build and easy to share. Plotly gives interactive charts without JavaScript.

---

### "What KPIs did you track and why?"

| KPI | Business Decision |
|-----|-------------------|
| **Occupancy rate** | Flags vacancy risk, triggers marketing for empty units |
| **Rent per ping** | Compares value across units to optimize pricing |
| **On-time payment rate** | Identifies risky tenants for follow-up or non-renewal |
| **Monthly net cash flow** | Shows whether the property is cash-positive each month |
| **NOI (Net Operating Income)** | Overall profitability — the #1 metric for property investors |
| **Expense by category** | Spots cost escalation (e.g., rising maintenance costs) |

---

### "What was the hardest part?"

> Designing seed data that's realistic enough to produce meaningful analytics. I needed lease overlaps, tenant turnover, a few late payments, varied expense categories, and seasonal patterns — all while keeping FK integrity across 8 tables. I solved this by loading tables in dependency order and running 25 automated validation checks after every build.

---

### "What would you do next?"

1. **ML phase**: Churn prediction (which tenants won't renew), rent forecasting, and anomaly detection on payments
2. **Time-series analysis**: Seasonal revenue patterns and expense forecasting
3. **Multi-property scale**: Extend the schema to handle a portfolio of buildings
4. **Automated reporting**: Scheduled monthly PDF reports for the property owner
