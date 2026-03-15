-- ============================================================
-- Revenue Analysis (Residential, Storefront, Parking)
-- ============================================================

-- Monthly residential rental revenue
SELECT
    strftime('%Y-%m', p.payment_date) AS month,
    COUNT(*) AS payment_count,
    ROUND(SUM(p.amount), 0) AS residential_revenue
FROM payments p
GROUP BY month
ORDER BY month;


-- Total residential revenue by year
SELECT
    strftime('%Y', p.payment_date) AS year,
    COUNT(*) AS payment_count,
    ROUND(SUM(p.amount), 0) AS residential_revenue
FROM payments p
GROUP BY year
ORDER BY year;


-- Revenue by unit
SELECT
    u.unit_name,
    u.floor,
    COUNT(p.payment_id) AS total_payments,
    ROUND(SUM(p.amount), 0) AS total_revenue,
    ROUND(AVG(p.amount), 0) AS avg_payment
FROM payments p
JOIN leases l ON p.lease_id = l.lease_id
JOIN units u ON l.unit_id = u.unit_id
GROUP BY u.unit_id, u.unit_name, u.floor
ORDER BY total_revenue DESC;


-- Storefront revenue summary
SELECT
    business_name,
    business_type,
    tenant_name,
    monthly_rent,
    lease_start,
    lease_end,
    -- Calculate months in lease
    CAST(
        (julianday(COALESCE(lease_end, date('now'))) - julianday(lease_start)) / 30.44
        AS INTEGER
    ) AS lease_months,
    monthly_rent * CAST(
        (julianday(COALESCE(lease_end, date('now'))) - julianday(lease_start)) / 30.44
        AS INTEGER
    ) AS estimated_total_revenue
FROM storefront
WHERE status = 'active';


-- Parking revenue summary
SELECT
    ps.slot_name,
    ps.slot_type,
    ps.monthly_fee,
    pl.status AS lease_status,
    t.first_name || ' ' || t.last_name AS tenant_name,
    pl.start_date,
    pl.end_date,
    CAST(
        (julianday(COALESCE(pl.end_date, date('now'))) - julianday(pl.start_date)) / 30.44
        AS INTEGER
    ) AS months_rented,
    pl.monthly_fee * CAST(
        (julianday(COALESCE(pl.end_date, date('now'))) - julianday(pl.start_date)) / 30.44
        AS INTEGER
    ) AS estimated_revenue
FROM parking_slots ps
LEFT JOIN parking_leases pl ON ps.slot_id = pl.slot_id
LEFT JOIN tenants t ON pl.tenant_id = t.tenant_id
ORDER BY ps.slot_name;


-- Total parking revenue (all active parking leases)
SELECT
    COUNT(*) AS active_parking_leases,
    SUM(monthly_fee) AS monthly_parking_revenue,
    SUM(
        monthly_fee * CAST(
            (julianday(COALESCE(end_date, date('now'))) - julianday(start_date)) / 30.44
            AS INTEGER
        )
    ) AS estimated_total_parking_revenue
FROM parking_leases
WHERE status = 'active';
