#!/usr/bin/env python3
"""
kpi_metrics.py — Calculate all key performance indicators from rental_property.db.

Usage:
    python analytics/kpi_metrics.py
"""

import os
import sqlite3
import sys

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "rental_property.db")


def get_connection():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database not found: {DB_FILE}")
        print("   Run 'python build_db.py' first.")
        sys.exit(1)
    return sqlite3.connect(DB_FILE)


def compute_kpis():
    """Compute and return all KPIs as a dictionary."""
    conn = get_connection()
    c = conn.cursor()
    kpis = {}

    # ── Occupancy ──────────────────────────────────────────────
    c.execute("""
        SELECT
            COUNT(DISTINCT CASE WHEN l.lease_id IS NOT NULL THEN u.unit_id END),
            COUNT(DISTINCT u.unit_id)
        FROM units u
        LEFT JOIN leases l ON u.unit_id = l.unit_id AND l.status = 'active'
    """)
    occupied, total = c.fetchone()
    kpis["occupied_units"] = occupied
    kpis["total_units"] = total
    kpis["occupancy_rate_pct"] = round(100.0 * occupied / total, 1) if total else 0

    # ── Residential Revenue ────────────────────────────────────
    c.execute("SELECT ROUND(SUM(amount), 0) FROM payments")
    kpis["total_residential_revenue"] = c.fetchone()[0] or 0

    # ── Average Monthly Residential Revenue ────────────────────
    c.execute("""
        SELECT ROUND(AVG(monthly_total), 0) FROM (
            SELECT SUM(amount) AS monthly_total
            FROM payments
            GROUP BY strftime('%Y-%m', payment_date)
        )
    """)
    kpis["avg_monthly_residential_revenue"] = c.fetchone()[0] or 0

    # ── Average Rent by Floor ──────────────────────────────────
    c.execute("""
        SELECT floor, ROUND(AVG(base_rent), 0)
        FROM units GROUP BY floor ORDER BY floor
    """)
    kpis["avg_rent_by_floor"] = {f"Floor {row[0]}": row[1] for row in c.fetchall()}

    # ── Average Rent per Ping ──────────────────────────────────
    c.execute("SELECT ROUND(AVG(base_rent / size_ping), 0) FROM units")
    kpis["avg_rent_per_ping"] = c.fetchone()[0] or 0

    # ── Payment Status ─────────────────────────────────────────
    c.execute("SELECT COUNT(*) FROM payments")
    total_payments = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM payments WHERE status = 'paid'")
    on_time = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM payments WHERE status IN ('late', 'partial', 'missed')")
    overdue = c.fetchone()[0]

    kpis["total_payments"] = total_payments
    kpis["on_time_payments"] = on_time
    kpis["overdue_payments"] = overdue
    kpis["on_time_rate_pct"] = round(100.0 * on_time / total_payments, 1) if total_payments else 0
    kpis["overdue_rate_pct"] = round(100.0 * overdue / total_payments, 1) if total_payments else 0

    # ── Storefront Revenue ─────────────────────────────────────
    c.execute("""
        SELECT monthly_rent,
               CAST((julianday(COALESCE(lease_end, date('now'))) - julianday(lease_start)) / 30.44 AS INTEGER)
        FROM storefront WHERE status = 'active'
    """)
    row = c.fetchone()
    if row:
        kpis["storefront_monthly_rent"] = row[0]
        kpis["storefront_lease_months"] = row[1]
        kpis["storefront_total_revenue"] = row[0] * row[1]
    else:
        kpis["storefront_monthly_rent"] = 0
        kpis["storefront_lease_months"] = 0
        kpis["storefront_total_revenue"] = 0

    # ── Parking Revenue ────────────────────────────────────────
    c.execute("""
        SELECT
            COUNT(*),
            SUM(monthly_fee),
            SUM(monthly_fee * CAST(
                (julianday(COALESCE(end_date, date('now'))) - julianday(start_date)) / 30.44
                AS INTEGER
            ))
        FROM parking_leases WHERE status = 'active'
    """)
    row = c.fetchone()
    kpis["active_parking_leases"] = row[0] or 0
    kpis["monthly_parking_revenue"] = row[1] or 0
    kpis["total_parking_revenue"] = row[2] or 0

    # ── Expenses ───────────────────────────────────────────────
    c.execute("SELECT ROUND(SUM(amount), 0) FROM expenses")
    kpis["total_expenses"] = c.fetchone()[0] or 0

    c.execute("""
        SELECT ROUND(AVG(monthly_total), 0) FROM (
            SELECT SUM(amount) AS monthly_total
            FROM expenses
            GROUP BY strftime('%Y-%m', expense_date)
        )
    """)
    kpis["avg_monthly_expenses"] = c.fetchone()[0] or 0

    # ── Net Operating Income ───────────────────────────────────
    kpis["net_operating_income"] = kpis["total_residential_revenue"] - kpis["total_expenses"]

    # ── Monthly Net Cash Flow (avg) ────────────────────────────
    kpis["avg_monthly_net_cash_flow"] = (
        kpis["avg_monthly_residential_revenue"] - kpis["avg_monthly_expenses"]
    )

    conn.close()
    return kpis


def print_kpis(kpis):
    """Pretty-print all KPIs."""
    print("=" * 60)
    print("  RENTAL PROPERTY — KEY PERFORMANCE INDICATORS")
    print("=" * 60)

    print("\n📊 OCCUPANCY")
    print(f"   Occupied Units:          {kpis['occupied_units']} / {kpis['total_units']}")
    print(f"   Occupancy Rate:          {kpis['occupancy_rate_pct']}%")

    print("\n💰 REVENUE")
    print(f"   Total Residential Rev:   NT${kpis['total_residential_revenue']:,.0f}")
    print(f"   Avg Monthly Res Rev:     NT${kpis['avg_monthly_residential_revenue']:,.0f}")
    print(f"   Storefront Monthly Rent: NT${kpis['storefront_monthly_rent']:,.0f}")
    print(f"   Storefront Total Rev:    NT${kpis['storefront_total_revenue']:,.0f}")
    print(f"   Monthly Parking Rev:     NT${kpis['monthly_parking_revenue']:,.0f}")
    print(f"   Total Parking Rev:       NT${kpis['total_parking_revenue']:,.0f}")

    print("\n🏠 RENT ANALYSIS")
    for floor, avg_rent in kpis["avg_rent_by_floor"].items():
        print(f"   Avg Rent ({floor}):       NT${avg_rent:,.0f}")
    print(f"   Avg Rent per Ping:       NT${kpis['avg_rent_per_ping']:,.0f}/ping")

    print("\n📋 PAYMENT STATUS")
    print(f"   Total Payments:          {kpis['total_payments']}")
    print(f"   On-Time:                 {kpis['on_time_payments']} ({kpis['on_time_rate_pct']}%)")
    print(f"   Overdue/Late/Partial:    {kpis['overdue_payments']} ({kpis['overdue_rate_pct']}%)")

    print("\n📉 EXPENSES")
    print(f"   Total Expenses:          NT${kpis['total_expenses']:,.0f}")
    print(f"   Avg Monthly Expenses:    NT${kpis['avg_monthly_expenses']:,.0f}")

    print("\n📈 NET INCOME")
    print(f"   Net Operating Income:    NT${kpis['net_operating_income']:,.0f}")
    print(f"   Avg Monthly Net CF:      NT${kpis['avg_monthly_net_cash_flow']:,.0f}")

    print("\n" + "=" * 60)


def main():
    kpis = compute_kpis()
    print_kpis(kpis)


if __name__ == "__main__":
    main()
