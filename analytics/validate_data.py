#!/usr/bin/env python3
"""
validate_data.py — Data quality and validation checks on rental_property.db.

Usage:
    python analytics/validate_data.py

Checks:
  1. Missing values in critical fields
  2. Invalid rent amounts (zero or negative)
  3. Lease date consistency (end >= start)
  4. Payments reference valid leases
  5. Parking leases reference valid slots and tenants
  6. Duplicate detection on key columns
  7. Orphaned records
"""

import os
import sqlite3
import sys

DB_FILE = os.path.join(os.path.dirname(__file__), "..", "rental_property.db")

# Track results
results = []


def check(name, passed, detail=""):
    """Record a check result."""
    status = "✅ PASS" if passed else "❌ FAIL"
    results.append((name, passed, detail))
    print(f"  {status}  {name}")
    if detail and not passed:
        print(f"         → {detail}")


def main():
    if not os.path.exists(DB_FILE):
        print(f"❌ Database not found: {DB_FILE}")
        print("   Run 'python build_db.py' first.")
        sys.exit(1)

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    print("=" * 60)
    print("  DATA VALIDATION REPORT")
    print("=" * 60)

    # ── 1. Missing Values ─────────────────────────────────────
    print("\n── Missing Values ──")

    # Units: unit_name, floor, base_rent should not be null
    c.execute("SELECT COUNT(*) FROM units WHERE unit_name IS NULL OR floor IS NULL OR base_rent IS NULL OR size_ping IS NULL")
    count = c.fetchone()[0]
    check("Units: no null unit_name/floor/base_rent/size_ping", count == 0, f"{count} rows with nulls")

    # Tenants: first_name, last_name should not be null
    c.execute("SELECT COUNT(*) FROM tenants WHERE first_name IS NULL OR last_name IS NULL")
    count = c.fetchone()[0]
    check("Tenants: no null first_name/last_name", count == 0, f"{count} rows with nulls")

    # Leases: unit_id, tenant_id, start_date, end_date, monthly_rent
    c.execute("""
        SELECT COUNT(*) FROM leases
        WHERE unit_id IS NULL OR tenant_id IS NULL OR start_date IS NULL
            OR end_date IS NULL OR monthly_rent IS NULL
    """)
    count = c.fetchone()[0]
    check("Leases: no nulls in required fields", count == 0, f"{count} rows with nulls")

    # Payments: lease_id, tenant_id, amount, payment_date, due_date
    c.execute("""
        SELECT COUNT(*) FROM payments
        WHERE lease_id IS NULL OR tenant_id IS NULL OR amount IS NULL
            OR payment_date IS NULL OR due_date IS NULL
    """)
    count = c.fetchone()[0]
    check("Payments: no nulls in required fields", count == 0, f"{count} rows with nulls")

    # Storefront: business_name, monthly_rent, lease_start
    c.execute("""
        SELECT COUNT(*) FROM storefront
        WHERE business_name IS NULL OR monthly_rent IS NULL OR lease_start IS NULL
    """)
    count = c.fetchone()[0]
    check("Storefront: no nulls in required fields", count == 0, f"{count} rows with nulls")

    # ── 2. Invalid Rent Amounts ───────────────────────────────
    print("\n── Invalid Amounts ──")

    c.execute("SELECT COUNT(*) FROM units WHERE base_rent <= 0")
    count = c.fetchone()[0]
    check("Units: all base_rent > 0", count == 0, f"{count} units with rent <= 0")

    c.execute("SELECT COUNT(*) FROM leases WHERE monthly_rent <= 0")
    count = c.fetchone()[0]
    check("Leases: all monthly_rent > 0", count == 0, f"{count} leases with rent <= 0")

    c.execute("SELECT COUNT(*) FROM payments WHERE amount <= 0")
    count = c.fetchone()[0]
    check("Payments: all amounts > 0", count == 0, f"{count} payments with amount <= 0")

    c.execute("SELECT COUNT(*) FROM expenses WHERE amount <= 0")
    count = c.fetchone()[0]
    check("Expenses: all amounts > 0", count == 0, f"{count} expenses with amount <= 0")

    c.execute("SELECT COUNT(*) FROM storefront WHERE monthly_rent <= 0")
    count = c.fetchone()[0]
    check("Storefront: all monthly_rent > 0", count == 0, f"{count} with rent <= 0")

    # ── 3. Date Consistency ───────────────────────────────────
    print("\n── Date Consistency ──")

    c.execute("SELECT COUNT(*) FROM leases WHERE end_date < start_date")
    count = c.fetchone()[0]
    check("Leases: end_date >= start_date", count == 0, f"{count} leases with end < start")

    c.execute("SELECT COUNT(*) FROM storefront WHERE lease_end IS NOT NULL AND lease_end < lease_start")
    count = c.fetchone()[0]
    check("Storefront: lease_end >= lease_start", count == 0, f"{count} with end < start")

    c.execute("""
        SELECT COUNT(*) FROM parking_leases
        WHERE end_date IS NOT NULL AND end_date < start_date
    """)
    count = c.fetchone()[0]
    check("Parking leases: end_date >= start_date", count == 0, f"{count} with end < start")

    # ── 4. Referential Integrity ──────────────────────────────
    print("\n── Referential Integrity ──")

    # Payments → Leases
    c.execute("""
        SELECT COUNT(*) FROM payments p
        WHERE NOT EXISTS (SELECT 1 FROM leases l WHERE l.lease_id = p.lease_id)
    """)
    count = c.fetchone()[0]
    check("Payments: all reference valid leases", count == 0, f"{count} orphaned payments")

    # Payments → Tenants
    c.execute("""
        SELECT COUNT(*) FROM payments p
        WHERE NOT EXISTS (SELECT 1 FROM tenants t WHERE t.tenant_id = p.tenant_id)
    """)
    count = c.fetchone()[0]
    check("Payments: all reference valid tenants", count == 0, f"{count} orphaned payments")

    # Leases → Units
    c.execute("""
        SELECT COUNT(*) FROM leases l
        WHERE NOT EXISTS (SELECT 1 FROM units u WHERE u.unit_id = l.unit_id)
    """)
    count = c.fetchone()[0]
    check("Leases: all reference valid units", count == 0, f"{count} orphaned leases")

    # Leases → Tenants
    c.execute("""
        SELECT COUNT(*) FROM leases l
        WHERE NOT EXISTS (SELECT 1 FROM tenants t WHERE t.tenant_id = l.tenant_id)
    """)
    count = c.fetchone()[0]
    check("Leases: all reference valid tenants", count == 0, f"{count} orphaned leases")

    # Parking leases → Parking slots
    c.execute("""
        SELECT COUNT(*) FROM parking_leases pl
        WHERE NOT EXISTS (SELECT 1 FROM parking_slots ps WHERE ps.slot_id = pl.slot_id)
    """)
    count = c.fetchone()[0]
    check("Parking leases: all reference valid slots", count == 0, f"{count} orphaned")

    # Parking leases → Tenants
    c.execute("""
        SELECT COUNT(*) FROM parking_leases pl
        WHERE NOT EXISTS (SELECT 1 FROM tenants t WHERE t.tenant_id = pl.tenant_id)
    """)
    count = c.fetchone()[0]
    check("Parking leases: all reference valid tenants", count == 0, f"{count} orphaned")

    # ── 5. Duplicate Detection ────────────────────────────────
    print("\n── Duplicate Detection ──")

    c.execute("SELECT COUNT(*) - COUNT(DISTINCT unit_name) FROM units")
    count = c.fetchone()[0]
    check("Units: no duplicate unit_name", count == 0, f"{count} duplicates")

    c.execute("SELECT COUNT(*) - COUNT(DISTINCT slot_name) FROM parking_slots")
    count = c.fetchone()[0]
    check("Parking slots: no duplicate slot_name", count == 0, f"{count} duplicates")

    # Check for duplicate payments (same lease, same due_date, same amount, same status=paid)
    c.execute("""
        SELECT COUNT(*) FROM (
            SELECT lease_id, due_date, amount, COUNT(*) AS cnt
            FROM payments
            WHERE status = 'paid'
            GROUP BY lease_id, due_date, amount
            HAVING cnt > 1
        )
    """)
    count = c.fetchone()[0]
    check("Payments: no duplicate paid payments for same lease+due_date", count == 0, f"{count} duplicates found")

    # ── 6. Business Rule Checks ───────────────────────────────
    print("\n── Business Rules ──")

    # Valid payment status values
    c.execute("""
        SELECT COUNT(*) FROM payments
        WHERE status NOT IN ('paid', 'late', 'partial', 'missed')
    """)
    count = c.fetchone()[0]
    check("Payments: all have valid status values", count == 0, f"{count} invalid statuses")

    # Valid lease status values
    c.execute("""
        SELECT COUNT(*) FROM leases
        WHERE status NOT IN ('active', 'expired', 'terminated')
    """)
    count = c.fetchone()[0]
    check("Leases: all have valid status values", count == 0, f"{count} invalid statuses")

    # Unit sizes are reasonable (1-50 ping)
    c.execute("SELECT COUNT(*) FROM units WHERE size_ping < 1 OR size_ping > 50")
    count = c.fetchone()[0]
    check("Units: size_ping in reasonable range (1-50)", count == 0, f"{count} outliers")

    # ── Summary ───────────────────────────────────────────────
    total = len(results)
    passed = sum(1 for _, p, _ in results if p)
    failed = total - passed

    print(f"\n{'=' * 60}")
    print(f"  VALIDATION SUMMARY: {passed}/{total} checks passed", end="")
    if failed:
        print(f", {failed} FAILED")
    else:
        print(" — ALL CLEAR ✅")
    print(f"{'=' * 60}\n")

    conn.close()
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
