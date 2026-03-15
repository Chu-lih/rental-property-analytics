-- ============================================================
-- Monthly Cash Flow & Net Income Summary
-- ============================================================

-- Monthly cash flow: revenue from payments vs expenses
WITH monthly_revenue AS (
    SELECT
        strftime('%Y-%m', payment_date) AS month,
        ROUND(SUM(amount), 0) AS residential_revenue
    FROM payments
    GROUP BY month
),
monthly_expenses AS (
    SELECT
        strftime('%Y-%m', expense_date) AS month,
        ROUND(SUM(amount), 0) AS total_expenses
    FROM expenses
    GROUP BY month
),
all_months AS (
    SELECT month FROM monthly_revenue
    UNION
    SELECT month FROM monthly_expenses
)
SELECT
    am.month,
    COALESCE(mr.residential_revenue, 0) AS residential_revenue,
    COALESCE(me.total_expenses, 0) AS expenses,
    COALESCE(mr.residential_revenue, 0) - COALESCE(me.total_expenses, 0) AS net_cash_flow
FROM all_months am
LEFT JOIN monthly_revenue mr ON am.month = mr.month
LEFT JOIN monthly_expenses me ON am.month = me.month
ORDER BY am.month;


-- Annual summary
WITH annual_revenue AS (
    SELECT
        strftime('%Y', payment_date) AS year,
        ROUND(SUM(amount), 0) AS residential_revenue
    FROM payments
    GROUP BY year
),
annual_expenses AS (
    SELECT
        strftime('%Y', expense_date) AS year,
        ROUND(SUM(amount), 0) AS total_expenses
    FROM expenses
    GROUP BY year
)
SELECT
    ar.year,
    ar.residential_revenue,
    COALESCE(ae.total_expenses, 0) AS expenses,
    ar.residential_revenue - COALESCE(ae.total_expenses, 0) AS net_income,
    ROUND(
        100.0 * (ar.residential_revenue - COALESCE(ae.total_expenses, 0))
        / ar.residential_revenue, 1
    ) AS net_margin_pct
FROM annual_revenue ar
LEFT JOIN annual_expenses ae ON ar.year = ae.year
ORDER BY ar.year;


-- Net operating income (NOI) summary — all-time
SELECT
    (SELECT ROUND(SUM(amount), 0) FROM payments) AS total_residential_revenue,
    (SELECT ROUND(SUM(amount), 0) FROM expenses) AS total_expenses,
    (SELECT ROUND(SUM(amount), 0) FROM payments)
        - (SELECT ROUND(SUM(amount), 0) FROM expenses) AS net_operating_income;
