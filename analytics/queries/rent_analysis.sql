-- ============================================================
-- Rent Analysis by Floor and Unit Type
-- ============================================================

-- Average rent by floor
SELECT
    u.floor,
    COUNT(*) AS unit_count,
    ROUND(AVG(u.base_rent), 0) AS avg_base_rent,
    MIN(u.base_rent) AS min_rent,
    MAX(u.base_rent) AS max_rent,
    ROUND(AVG(u.size_ping), 1) AS avg_size_ping,
    ROUND(AVG(u.base_rent / u.size_ping), 0) AS avg_rent_per_ping
FROM units u
GROUP BY u.floor
ORDER BY u.floor;


-- Rent per ping analysis (value comparison)
SELECT
    u.unit_name,
    u.floor,
    u.size_ping,
    u.base_rent,
    ROUND(u.base_rent / u.size_ping, 0) AS rent_per_ping,
    u.has_balcony,
    u.has_private_wc,
    u.description
FROM units u
ORDER BY rent_per_ping DESC;


-- Current lease rents vs base rents (rent premium/discount)
SELECT
    u.unit_name,
    u.floor,
    u.base_rent,
    l.monthly_rent AS lease_rent,
    l.monthly_rent - u.base_rent AS rent_diff,
    ROUND(100.0 * (l.monthly_rent - u.base_rent) / u.base_rent, 1) AS rent_change_pct
FROM units u
INNER JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
ORDER BY rent_change_pct DESC;


-- Rent by feature analysis
SELECT
    CASE WHEN has_balcony = 1 THEN 'With Balcony' ELSE 'No Balcony' END AS balcony,
    CASE WHEN has_private_wc = 1 THEN 'Private WC' ELSE 'Shared WC' END AS bathroom,
    COUNT(*) AS units,
    ROUND(AVG(base_rent), 0) AS avg_rent,
    ROUND(AVG(base_rent / size_ping), 0) AS avg_rent_per_ping
FROM units
GROUP BY has_balcony, has_private_wc
ORDER BY avg_rent DESC;
