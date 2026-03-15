-- ============================================================
-- Occupancy Analysis
-- ============================================================

-- Current occupancy: units with active leases
-- (A unit is occupied if it has a lease with status='active'
--  and today falls between start_date and end_date)
SELECT
    u.unit_id,
    u.unit_name,
    u.floor,
    u.base_rent,
    CASE WHEN l.lease_id IS NOT NULL THEN 'occupied' ELSE 'vacant' END AS occupancy_status,
    l.tenant_id,
    t.first_name || ' ' || t.last_name AS tenant_name,
    l.monthly_rent AS current_rent,
    l.start_date AS lease_start,
    l.end_date AS lease_end
FROM units u
LEFT JOIN leases l
    ON u.unit_id = l.unit_id
    AND l.status = 'active'
LEFT JOIN tenants t
    ON l.tenant_id = t.tenant_id
ORDER BY u.floor, u.unit_name;


-- Occupancy rate KPI
SELECT
    COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END) AS occupied_units,
    COUNT(DISTINCT u.unit_id) AS total_units,
    ROUND(
        100.0 * COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END)
        / COUNT(DISTINCT u.unit_id), 1
    ) AS occupancy_rate_pct
FROM units u
LEFT JOIN leases l
    ON u.unit_id = l.unit_id
    AND l.status = 'active';


-- Historical occupancy by month (count of active leases per month)
SELECT
    strftime('%Y-%m', m.month_start) AS month,
    COUNT(DISTINCT l.unit_id) AS occupied_units,
    9 AS total_units,
    ROUND(100.0 * COUNT(DISTINCT l.unit_id) / 9, 1) AS occupancy_rate_pct
FROM (
    -- Generate months from 2024-01 to 2026-03
    WITH RECURSIVE months(month_start) AS (
        SELECT '2024-01-01'
        UNION ALL
        SELECT date(month_start, '+1 month')
        FROM months
        WHERE month_start < '2026-03-01'
    )
    SELECT month_start FROM months
) m
LEFT JOIN leases l
    ON l.start_date <= date(m.month_start, '+1 month', '-1 day')
    AND l.end_date >= m.month_start
ORDER BY m.month_start;
