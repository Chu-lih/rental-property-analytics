#!/usr/bin/env python3
"""
run_analytics.py — Run all analytics queries and print results.

Usage:
    python analytics/run_analytics.py
"""

import os
import sqlite3
import sys

import pandas as pd

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "rental_property.db")


def get_connection():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database not found: {DB_FILE}")
        print("   Run 'python build_db.py' first.")
        sys.exit(1)
    return sqlite3.connect(DB_FILE)


def run_query(conn, title, sql):
    """Execute a SQL query and print the results as a formatted table."""
    print(f"\n{'─' * 60}")
    print(f"  {title}")
    print(f"{'─' * 60}")
    try:
        df = pd.read_sql_query(sql, conn)
        if df.empty:
            print("  (no results)")
        else:
            print(df.to_string(index=False))
        return df
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return pd.DataFrame()


def main():
    conn = get_connection()

    print("=" * 60)
    print("  RENTAL PROPERTY ANALYTICS REPORT")
    print("=" * 60)

    # ── 1. Occupancy Analysis ──────────────────────────────────
    run_query(conn, "📊 CURRENT OCCUPANCY STATUS", """
        SELECT
            u.unit_name, u.floor, u.base_rent,
            CASE WHEN l.lease_id IS NOT NULL THEN '✅ Occupied' ELSE '❌ Vacant' END AS status,
            t.first_name || ' ' || t.last_name AS tenant,
            l.monthly_rent, l.end_date AS lease_end
        FROM units u
        LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
        LEFT JOIN tenants t ON l.tenant_id = t.tenant_id
        ORDER BY u.floor, u.unit_name
    """)

    run_query(conn, "📊 OCCUPANCY RATE", """
        SELECT
            COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END) AS occupied,
            COUNT(DISTINCT u.unit_id) AS total,
            ROUND(100.0 * COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END)
                / COUNT(DISTINCT u.unit_id), 1) AS occupancy_rate_pct
        FROM units u
        LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
    """)

    # ── 2. Rent Analysis ──────────────────────────────────────
    run_query(conn, "🏠 AVERAGE RENT BY FLOOR", """
        SELECT floor, COUNT(*) AS units,
            ROUND(AVG(base_rent), 0) AS avg_rent,
            ROUND(AVG(size_ping), 1) AS avg_size_ping,
            ROUND(AVG(base_rent / size_ping), 0) AS avg_rent_per_ping
        FROM units GROUP BY floor ORDER BY floor
    """)

    run_query(conn, "🏠 RENT PER PING RANKING", """
        SELECT unit_name, floor, size_ping, base_rent,
            ROUND(base_rent / size_ping, 0) AS rent_per_ping,
            has_balcony, has_private_wc
        FROM units ORDER BY rent_per_ping DESC
    """)

    run_query(conn, "🏠 LEASE RENT vs BASE RENT", """
        SELECT u.unit_name, u.base_rent, l.monthly_rent AS lease_rent,
            l.monthly_rent - u.base_rent AS diff,
            ROUND(100.0 * (l.monthly_rent - u.base_rent) / u.base_rent, 1) AS change_pct
        FROM units u
        INNER JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
        ORDER BY change_pct DESC
    """)

    # ── 3. Payment Analysis ───────────────────────────────────
    run_query(conn, "📋 PAYMENT STATUS BREAKDOWN", """
        SELECT status, COUNT(*) AS count,
            ROUND(SUM(amount), 0) AS total_amount,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM payments), 1) AS pct
        FROM payments GROUP BY status ORDER BY count DESC
    """)

    run_query(conn, "📋 ON-TIME vs OVERDUE RATE", """
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS on_time,
            SUM(CASE WHEN status IN ('late','partial','missed') THEN 1 ELSE 0 END) AS overdue,
            ROUND(100.0 * SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) / COUNT(*), 1) AS on_time_pct,
            ROUND(100.0 * SUM(CASE WHEN status IN ('late','partial','missed') THEN 1 ELSE 0 END) / COUNT(*), 1) AS overdue_pct
        FROM payments
    """)

    run_query(conn, "⚠️  LATE/OVERDUE PAYMENTS DETAIL", """
        SELECT p.payment_id,
            t.first_name || ' ' || t.last_name AS tenant,
            u.unit_name, p.amount, p.due_date, p.payment_date,
            CAST(julianday(p.payment_date) - julianday(p.due_date) AS INTEGER) AS days_late,
            p.status, p.note
        FROM payments p
        JOIN leases l ON p.lease_id = l.lease_id
        JOIN tenants t ON p.tenant_id = t.tenant_id
        JOIN units u ON l.unit_id = u.unit_id
        WHERE p.status IN ('late', 'partial', 'missed')
        ORDER BY p.due_date
    """)

    run_query(conn, "📋 PAYMENT METHOD DISTRIBUTION", """
        SELECT method, COUNT(*) AS count,
            ROUND(SUM(amount), 0) AS total,
            ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM payments), 1) AS pct
        FROM payments GROUP BY method ORDER BY count DESC
    """)

    # ── 4. Revenue Analysis ───────────────────────────────────
    run_query(conn, "💰 MONTHLY RESIDENTIAL REVENUE", """
        SELECT strftime('%Y-%m', payment_date) AS month,
            COUNT(*) AS payments, ROUND(SUM(amount), 0) AS revenue
        FROM payments GROUP BY month ORDER BY month
    """)

    run_query(conn, "💰 REVENUE BY UNIT", """
        SELECT u.unit_name, u.floor,
            COUNT(p.payment_id) AS payments,
            ROUND(SUM(p.amount), 0) AS total_revenue
        FROM payments p
        JOIN leases l ON p.lease_id = l.lease_id
        JOIN units u ON l.unit_id = u.unit_id
        GROUP BY u.unit_id ORDER BY total_revenue DESC
    """)

    run_query(conn, "🏪 STOREFRONT REVENUE", """
        SELECT business_name, business_type, monthly_rent,
            lease_start, lease_end, status
        FROM storefront
    """)

    run_query(conn, "🅿️  PARKING REVENUE", """
        SELECT ps.slot_name, ps.slot_type, ps.monthly_fee,
            pl.status, t.first_name || ' ' || t.last_name AS tenant
        FROM parking_slots ps
        LEFT JOIN parking_leases pl ON ps.slot_id = pl.slot_id AND pl.status = 'active'
        LEFT JOIN tenants t ON pl.tenant_id = t.tenant_id
        ORDER BY ps.slot_name
    """)

    # ── 5. Expense Analysis ───────────────────────────────────
    run_query(conn, "📉 EXPENSES BY CATEGORY", """
        SELECT category, COUNT(*) AS count,
            ROUND(SUM(amount), 0) AS total,
            ROUND(100.0 * SUM(amount) / (SELECT SUM(amount) FROM expenses), 1) AS pct
        FROM expenses GROUP BY category ORDER BY total DESC
    """)

    run_query(conn, "📉 TOP 5 LARGEST EXPENSES", """
        SELECT category, description, amount, expense_date, vendor
        FROM expenses ORDER BY amount DESC LIMIT 5
    """)

    # ── 6. Cash Flow & Net Income ─────────────────────────────
    run_query(conn, "💵 MONTHLY CASH FLOW", """
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

    run_query(conn, "💵 ANNUAL SUMMARY", """
        WITH rev AS (
            SELECT strftime('%Y', payment_date) AS year, ROUND(SUM(amount), 0) AS revenue
            FROM payments GROUP BY year
        ),
        exp AS (
            SELECT strftime('%Y', expense_date) AS year, ROUND(SUM(amount), 0) AS expenses
            FROM expenses GROUP BY year
        )
        SELECT r.year, r.revenue, COALESCE(e.expenses, 0) AS expenses,
            r.revenue - COALESCE(e.expenses, 0) AS net_income,
            ROUND(100.0 * (r.revenue - COALESCE(e.expenses, 0)) / r.revenue, 1) AS margin_pct
        FROM rev r LEFT JOIN exp e ON r.year = e.year ORDER BY r.year
    """)

    run_query(conn, "💵 NET OPERATING INCOME (ALL-TIME)", """
        SELECT
            (SELECT ROUND(SUM(amount), 0) FROM payments) AS total_revenue,
            (SELECT ROUND(SUM(amount), 0) FROM expenses) AS total_expenses,
            (SELECT ROUND(SUM(amount), 0) FROM payments)
                - (SELECT ROUND(SUM(amount), 0) FROM expenses) AS net_operating_income
    """)

    print("\n" + "=" * 60)
    print("  ✅ Analytics report complete")
    print("=" * 60 + "\n")

    conn.close()


if __name__ == "__main__":
    main()
