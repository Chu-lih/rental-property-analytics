"""
db_helpers.py — Database connection and query helpers for the Streamlit dashboard.
"""

import os
import sqlite3

import pandas as pd

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "rental_property.db")


def get_connection():
    """Return a read-only SQLite connection."""
    return sqlite3.connect(DB_FILE)


def query_df(sql, params=None):
    """Execute SQL and return a pandas DataFrame."""
    conn = get_connection()
    df = pd.read_sql_query(sql, conn, params=params)
    conn.close()
    return df


def query_scalar(sql):
    """Execute SQL and return a single scalar value."""
    conn = get_connection()
    result = conn.execute(sql).fetchone()[0]
    conn.close()
    return result


# ── KPI Queries ────────────────────────────────────────────


def get_occupancy_kpis():
    return query_df("""
        SELECT
            COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END) AS occupied,
            COUNT(DISTINCT u.unit_id) AS total,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END)
                / COUNT(DISTINCT u.unit_id), 1) AS occupancy_rate
        FROM units u
        LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
    """).iloc[0]


def get_payment_kpis():
    return query_df("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS on_time,
            SUM(CASE WHEN status IN ('late','partial','missed') THEN 1 ELSE 0 END) AS overdue,
            ROUND(100.0 * SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct,
            ROUND(100.0 * SUM(CASE WHEN status IN ('late','partial','missed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS overdue_pct
        FROM payments
    """).iloc[0]


def get_revenue_total():
    return query_scalar("SELECT ROUND(SUM(amount), 0) FROM payments") or 0


def get_expense_total():
    return query_scalar("SELECT ROUND(SUM(amount), 0) FROM expenses") or 0


def get_storefront_monthly_rent():
    return query_scalar("SELECT COALESCE(monthly_rent, 0) FROM storefront WHERE status = 'active'") or 0


def get_parking_monthly_revenue():
    return query_scalar("SELECT COALESCE(SUM(monthly_fee), 0) FROM parking_leases WHERE status = 'active'") or 0


# ── Table Queries ──────────────────────────────────────────


def get_unit_summary():
    return query_df("""
        SELECT
            u.unit_name AS "Unit",
            u.floor AS "Floor",
            u.size_ping AS "Size (坪)",
            u.base_rent AS "Base Rent",
            COALESCE(l.monthly_rent, 0) AS "Current Rent",
            CASE WHEN l.lease_id IS NOT NULL THEN 'Occupied' ELSE 'Vacant' END AS "Status",
            COALESCE(t.first_name || ' ' || t.last_name, '—') AS "Tenant",
            u.has_balcony AS "Balcony",
            u.has_private_wc AS "Private WC",
            u.has_washer AS "Washer",
            ROUND(u.base_rent / u.size_ping, 0) AS "Rent/Ping"
        FROM units u
        LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
        LEFT JOIN tenants t ON l.tenant_id = t.tenant_id
        ORDER BY u.floor, u.unit_name
    """)


def get_avg_rent_by_floor():
    return query_df("""
        SELECT
            floor AS "Floor",
            COUNT(*) AS "Units",
            ROUND(AVG(base_rent), 0) AS "Avg Rent",
            ROUND(AVG(size_ping), 1) AS "Avg Size (坪)",
            ROUND(AVG(base_rent / size_ping), 0) AS "Rent/Ping"
        FROM units
        GROUP BY floor ORDER BY floor
    """)


def get_monthly_revenue():
    return query_df("""
        SELECT
            strftime('%Y-%m', payment_date) AS month,
            ROUND(SUM(amount), 0) AS revenue
        FROM payments
        GROUP BY month ORDER BY month
    """)


def get_monthly_expenses():
    return query_df("""
        SELECT
            strftime('%Y-%m', expense_date) AS month,
            ROUND(SUM(amount), 0) AS expenses
        FROM expenses
        GROUP BY month ORDER BY month
    """)


def get_monthly_cash_flow():
    return query_df("""
        WITH rev AS (
            SELECT strftime('%Y-%m', payment_date) AS month, ROUND(SUM(amount), 0) AS revenue
            FROM payments GROUP BY month
        ),
        exp AS (
            SELECT strftime('%Y-%m', expense_date) AS month, ROUND(SUM(amount), 0) AS expenses
            FROM expenses GROUP BY month
        ),
        months AS (SELECT month FROM rev UNION SELECT month FROM exp)
        SELECT m.month,
            COALESCE(r.revenue, 0) AS revenue,
            COALESCE(e.expenses, 0) AS expenses,
            COALESCE(r.revenue, 0) - COALESCE(e.expenses, 0) AS net_cash_flow
        FROM months m
        LEFT JOIN rev r ON m.month = r.month
        LEFT JOIN exp e ON m.month = e.month
        ORDER BY m.month
    """)


def get_expense_by_category():
    return query_df("""
        SELECT
            category AS "Category",
            COUNT(*) AS "Count",
            ROUND(SUM(amount), 0) AS "Total",
            ROUND(100.0 * SUM(amount) / (SELECT SUM(amount) FROM expenses), 1) AS "% of Total"
        FROM expenses
        GROUP BY category ORDER BY "Total" DESC
    """)


def get_late_payments():
    return query_df("""
        SELECT
            t.first_name || ' ' || t.last_name AS "Tenant",
            u.unit_name AS "Unit",
            p.amount AS "Amount",
            p.due_date AS "Due Date",
            p.payment_date AS "Paid Date",
            CAST(julianday(p.payment_date) - julianday(p.due_date) AS INTEGER) AS "Days Late",
            p.status AS "Status",
            p.note AS "Note"
        FROM payments p
        JOIN leases l ON p.lease_id = l.lease_id
        JOIN tenants t ON p.tenant_id = t.tenant_id
        JOIN units u ON l.unit_id = u.unit_id
        WHERE p.status IN ('late', 'partial', 'missed')
        ORDER BY p.due_date
    """)


def get_parking_summary():
    return query_df("""
        SELECT
            ps.slot_name AS "Slot",
            ps.slot_type AS "Type",
            ps.monthly_fee AS "Fee",
            CASE WHEN pl.parking_lease_id IS NOT NULL THEN 'Leased' ELSE 'Available' END AS "Status",
            COALESCE(t.first_name || ' ' || t.last_name, '—') AS "Tenant"
        FROM parking_slots ps
        LEFT JOIN parking_leases pl ON ps.slot_id = pl.slot_id AND pl.status = 'active'
        LEFT JOIN tenants t ON pl.tenant_id = t.tenant_id
        ORDER BY ps.slot_name
    """)


def get_storefront_summary():
    return query_df("""
        SELECT
            business_name AS "Business",
            business_type AS "Type",
            tenant_name AS "Tenant",
            monthly_rent AS "Monthly Rent",
            lease_start AS "Start",
            lease_end AS "End",
            status AS "Status"
        FROM storefront
    """)


def get_monthly_revenue_by_floor():
    return query_df("""
        SELECT
            strftime('%Y-%m', p.payment_date) AS month,
            u.floor,
            ROUND(SUM(p.amount), 0) AS revenue
        FROM payments p
        JOIN leases l ON p.lease_id = l.lease_id
        JOIN units u ON l.unit_id = u.unit_id
        GROUP BY month, u.floor
        ORDER BY month, u.floor
    """)
