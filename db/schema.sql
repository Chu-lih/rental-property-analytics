-- ============================================================
-- Rental Property Management & Analytics System
-- SQLite Schema
-- ============================================================

-- Residential units (9 rooms: 4 on 2F, 4 on 3F, 1 on 4F)
CREATE TABLE IF NOT EXISTS units (
    unit_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_name       TEXT NOT NULL UNIQUE,          -- e.g. '201', '302', '401'
    floor           INTEGER NOT NULL,              -- 2, 3, 4
    size_ping       REAL NOT NULL,                 -- size in ping (坪)
    base_rent       REAL NOT NULL,                 -- monthly rent in NT$
    has_balcony     INTEGER NOT NULL DEFAULT 0,    -- 0/1
    has_ac          INTEGER NOT NULL DEFAULT 1,    -- 0/1
    has_private_wc  INTEGER NOT NULL DEFAULT 1,    -- private bathroom 0/1 (all units = 1)
    has_washer      INTEGER NOT NULL DEFAULT 0,    -- private washer 0/1
    description     TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Tenant information
CREATE TABLE IF NOT EXISTS tenants (
    tenant_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT NOT NULL,
    last_name       TEXT NOT NULL,
    phone           TEXT,
    email           TEXT,
    id_number       TEXT,                          -- national ID (masked)
    move_in_date    TEXT,                          -- first ever move-in
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Lease agreements linking tenants to units
CREATE TABLE IF NOT EXISTS leases (
    lease_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    unit_id         INTEGER NOT NULL REFERENCES units(unit_id),
    tenant_id       INTEGER NOT NULL REFERENCES tenants(tenant_id),
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL,
    monthly_rent    REAL NOT NULL,                 -- actual rent (may differ from base_rent)
    deposit         REAL NOT NULL,                 -- security deposit
    status          TEXT NOT NULL DEFAULT 'active', -- active, expired, terminated
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Monthly rent payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    lease_id        INTEGER NOT NULL REFERENCES leases(lease_id),
    tenant_id       INTEGER NOT NULL REFERENCES tenants(tenant_id),
    amount          REAL NOT NULL,
    payment_date    TEXT NOT NULL,
    due_date        TEXT NOT NULL,
    method          TEXT NOT NULL DEFAULT 'bank_transfer', -- bank_transfer, cash, line_pay
    status          TEXT NOT NULL DEFAULT 'paid',          -- paid, late, partial, missed
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Basement (B1) motorcycle parking slots
CREATE TABLE IF NOT EXISTS parking_slots (
    slot_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_name       TEXT NOT NULL UNIQUE,           -- e.g. 'B1-1', 'B1-2'
    slot_type       TEXT NOT NULL DEFAULT 'motorcycle', -- motorcycle
    monthly_fee     REAL NOT NULL,
    is_covered      INTEGER NOT NULL DEFAULT 1,     -- 0/1 (basement = covered)
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Parking lease agreements
CREATE TABLE IF NOT EXISTS parking_leases (
    parking_lease_id INTEGER PRIMARY KEY AUTOINCREMENT,
    slot_id          INTEGER NOT NULL REFERENCES parking_slots(slot_id),
    tenant_id        INTEGER NOT NULL REFERENCES tenants(tenant_id),
    start_date       TEXT NOT NULL,
    end_date         TEXT,                          -- NULL = ongoing
    monthly_fee      REAL NOT NULL,
    status           TEXT NOT NULL DEFAULT 'active', -- active, expired
    created_at       TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Ground-floor commercial storefront
CREATE TABLE IF NOT EXISTS storefront (
    storefront_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    business_name   TEXT NOT NULL,
    business_type   TEXT NOT NULL,                  -- e.g. 'breakfast_shop', 'convenience_store'
    tenant_name     TEXT NOT NULL,
    phone           TEXT,
    lease_start     TEXT NOT NULL,
    lease_end       TEXT,
    monthly_rent    REAL NOT NULL,
    deposit         REAL NOT NULL,
    status          TEXT NOT NULL DEFAULT 'active',
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- Property expenses (maintenance, insurance, tax, utilities)
CREATE TABLE IF NOT EXISTS expenses (
    expense_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT NOT NULL,                  -- maintenance, insurance, property_tax, utilities, management, repair
    description     TEXT NOT NULL,
    amount          REAL NOT NULL,
    expense_date    TEXT NOT NULL,
    vendor          TEXT,
    is_recurring    INTEGER NOT NULL DEFAULT 0,     -- 0/1
    note            TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
