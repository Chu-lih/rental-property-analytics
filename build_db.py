#!/usr/bin/env python3
"""
build_db.py — Build rental_property.db from schema.sql and seed CSV files.

Usage:
    python build_db.py

Creates (or recreates) rental_property.db in the current directory by:
  1. Executing db/schema.sql to create all tables
  2. Loading each CSV file from db/seed/ into the matching table
  3. Printing a summary of all tables and row counts
"""

import os
import sqlite3
import pandas as pd

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
DB_FILE = "rental_property.db"
SCHEMA_FILE = os.path.join("db", "schema.sql")
SEED_DIR = os.path.join("db", "seed")

# Map CSV filenames (without .csv) to table names
CSV_TABLE_MAP = {
    "units": "units",
    "tenants": "tenants",
    "leases": "leases",
    "payments": "payments",
    "parking_slots": "parking_slots",
    "parking_leases": "parking_leases",
    "storefront": "storefront",
    "expenses": "expenses",
}

# Loading order respects foreign key dependencies
LOAD_ORDER = [
    "units",
    "tenants",
    "parking_slots",
    "storefront",
    "leases",
    "payments",
    "parking_leases",
    "expenses",
]


def main():
    # Remove existing database
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"♻  Removed existing {DB_FILE}")

    # Connect and enable foreign keys
    conn = sqlite3.connect(DB_FILE)
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # -------------------------------------------------------------------
    # Step 1: Execute schema
    # -------------------------------------------------------------------
    print(f"\n📐 Executing schema from {SCHEMA_FILE} ...")
    with open(SCHEMA_FILE, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    conn.commit()
    print("   ✅ Schema created successfully")

    # -------------------------------------------------------------------
    # Step 2: Load seed CSVs
    # -------------------------------------------------------------------
    print(f"\n🌱 Loading seed data from {SEED_DIR}/ ...")
    for csv_name in LOAD_ORDER:
        table_name = CSV_TABLE_MAP[csv_name]
        csv_path = os.path.join(SEED_DIR, f"{csv_name}.csv")

        if not os.path.exists(csv_path):
            print(f"   ⚠  {csv_path} not found — skipping")
            continue

        df = pd.read_csv(csv_path)
        df.to_sql(table_name, conn, if_exists="append", index=False)
        print(f"   ✅ {table_name}: loaded {len(df)} rows")

    conn.commit()

    # -------------------------------------------------------------------
    # Step 3: Summary
    # -------------------------------------------------------------------
    print(f"\n📊 Database summary ({DB_FILE}):")
    print("   " + "-" * 35)
    tables = cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    total_rows = 0
    for (table_name,) in tables:
        count = cursor.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        total_rows += count
        print(f"   {table_name:<20} {count:>6} rows")
    print("   " + "-" * 35)
    print(f"   {'TOTAL':<20} {total_rows:>6} rows")
    print(f"\n✅ Done! Database saved to {DB_FILE}\n")

    conn.close()


if __name__ == "__main__":
    main()
