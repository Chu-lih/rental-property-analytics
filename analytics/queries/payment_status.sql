-- ============================================================
-- Payment Status & Late Payment Analysis
-- ============================================================

-- Payment status breakdown
SELECT
    status,
    COUNT(*) AS payment_count,
    ROUND(SUM(amount), 0) AS total_amount,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM payments), 1) AS pct_of_total
FROM payments
GROUP BY status
ORDER BY payment_count DESC;


-- On-time vs late payment rate
SELECT
    COUNT(*) AS total_payments,
    SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS on_time,
    SUM(CASE WHEN status = 'late' THEN 1 ELSE 0 END) AS late,
    SUM(CASE WHEN status = 'partial' THEN 1 ELSE 0 END) AS partial,
    SUM(CASE WHEN status = 'missed' THEN 1 ELSE 0 END) AS missed,
    ROUND(100.0 * SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_rate_pct,
    ROUND(100.0 * SUM(CASE WHEN status IN ('late', 'partial', 'missed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS overdue_rate_pct
FROM payments;


-- Late payments detail
SELECT
    p.payment_id,
    t.first_name || ' ' || t.last_name AS tenant_name,
    u.unit_name,
    p.amount,
    p.due_date,
    p.payment_date,
    julianday(p.payment_date) - julianday(p.due_date) AS days_late,
    p.status,
    p.note
FROM payments p
JOIN leases l ON p.lease_id = l.lease_id
JOIN tenants t ON p.tenant_id = t.tenant_id
JOIN units u ON l.unit_id = u.unit_id
WHERE p.status IN ('late', 'partial', 'missed')
ORDER BY p.due_date;


-- Late payment frequency by tenant
SELECT
    t.tenant_id,
    t.first_name || ' ' || t.last_name AS tenant_name,
    COUNT(*) AS total_payments,
    SUM(CASE WHEN p.status IN ('late', 'partial', 'missed') THEN 1 ELSE 0 END) AS late_count,
    ROUND(100.0 * SUM(CASE WHEN p.status IN ('late', 'partial', 'missed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS late_rate_pct
FROM payments p
JOIN tenants t ON p.tenant_id = t.tenant_id
GROUP BY t.tenant_id, tenant_name
HAVING late_count > 0
ORDER BY late_rate_pct DESC;


-- Payment method distribution
SELECT
    method,
    COUNT(*) AS payment_count,
    ROUND(SUM(amount), 0) AS total_amount,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM payments), 1) AS pct_of_total
FROM payments
GROUP BY method
ORDER BY payment_count DESC;
