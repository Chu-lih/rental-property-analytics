-- ============================================================
-- Expense Summary
-- ============================================================

-- Expenses by category
SELECT
    category,
    COUNT(*) AS expense_count,
    ROUND(SUM(amount), 0) AS total_amount,
    ROUND(AVG(amount), 0) AS avg_amount,
    ROUND(100.0 * SUM(amount) / (SELECT SUM(amount) FROM expenses), 1) AS pct_of_total
FROM expenses
GROUP BY category
ORDER BY total_amount DESC;


-- Monthly expenses
SELECT
    strftime('%Y-%m', expense_date) AS month,
    COUNT(*) AS expense_count,
    ROUND(SUM(amount), 0) AS total_expenses
FROM expenses
GROUP BY month
ORDER BY month;


-- Recurring vs one-time expenses
SELECT
    CASE WHEN is_recurring = 1 THEN 'Recurring' ELSE 'One-time' END AS expense_type,
    COUNT(*) AS expense_count,
    ROUND(SUM(amount), 0) AS total_amount,
    ROUND(AVG(amount), 0) AS avg_amount
FROM expenses
GROUP BY is_recurring
ORDER BY total_amount DESC;


-- Top vendors by total spend
SELECT
    vendor,
    COUNT(*) AS expense_count,
    ROUND(SUM(amount), 0) AS total_spent
FROM expenses
WHERE vendor IS NOT NULL
GROUP BY vendor
ORDER BY total_spent DESC
LIMIT 10;


-- Largest individual expenses
SELECT
    expense_id,
    category,
    description,
    amount,
    expense_date,
    vendor
FROM expenses
ORDER BY amount DESC
LIMIT 10;
