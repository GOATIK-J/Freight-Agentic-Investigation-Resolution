"""Synthetic SQLite database for F.A.I.R. freight data."""
import os
import random
import sqlite3
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "fair_freight.db")

DEMO_CLOCK = datetime(2026, 10, 15, 14, 0, 0)

CARRIERS = [
    {"id": "CR-001", "name": "Pacific Freight Lines", "on_time_rate": 0.87, "damage_rate": 0.03},
    {"id": "CR-002", "name": "Continental Cargo Co.", "on_time_rate": 0.92, "damage_rate": 0.02},
    {"id": "CR-003", "name": "Atlantic Express", "on_time_rate": 0.78, "damage_rate": 0.05},
    {"id": "CR-004", "name": "Northern Star Logistics", "on_time_rate": 0.95, "damage_rate": 0.01},
    {"id": "CR-005", "name": "Global Transit Partners", "on_time_rate": 0.81, "damage_rate": 0.04},
    {"id": "CR-006", "name": "Summit Shipping", "on_time_rate": 0.89, "damage_rate": 0.025},
    {"id": "CR-007", "name": "Delta Freight Services", "on_time_rate": 0.73, "damage_rate": 0.06},
    {"id": "CR-008", "name": "Horizon Cargo Solutions", "on_time_rate": 0.91, "damage_rate": 0.015},
]

CUSTOMERS = [
    {"id": "CU-001", "name": "Apex Manufacturing", "tier": "Strategic", "region": "North America"},
    {"id": "CU-002", "name": "Bright Tech Industries", "tier": "Premium", "region": "Europe"},
    {"id": "CU-003", "name": "Crestwood Distributors", "tier": "Standard", "region": "Asia Pacific"},
    {"id": "CU-004", "name": "Dawson Enterprises", "tier": "Standard", "region": "North America"},
    {"id": "CU-005", "name": "Evergreen Supply Co.", "tier": "Premium", "region": "Europe"},
    {"id": "CU-006", "name": "Frontier Imports", "tier": "Standard", "region": "Asia Pacific"},
    {"id": "CU-007", "name": "Granite Logistics", "tier": "Strategic", "region": "North America"},
    {"id": "CU-008", "name": "Highland Traders", "tier": "Standard", "region": "Europe"},
]

ORIGINS = ["Los Angeles, CA", "Hamburg, DE", "Shanghai, CN", "Rotterdam, NL", "Singapore, SG"]
DESTINATIONS = ["Chicago, IL", "Paris, FR", "Tokyo, JP", "New York, NY", "Mumbai, IN", "London, UK"]
COMMODITIES = ["Electronics", "Automotive Parts", "Textiles", "Pharmaceuticals", "Machinery", "Food Products", "Chemicals"]

EXCEPTION_CASES = [
    # (shipment_idx, exception_type, severity, description, root_cause, expected_action)
    (0, "DAMAGE", "HIGH", "Cargo visible damage on arrival", "improper_handling", "FILE_CARRIER_CLAIM"),
    (1, "DELAY", "MEDIUM", "Shipment missed committed delivery", "weather_event", "CUSTOMER_NOTIFICATION"),
    (2, "CUSTOMS_HOLD", "HIGH", "Shipment detained at customs", "missing_documents", "SUBMIT_CUSTOMS_DOCS"),
    (3, "MISROUTE", "MEDIUM", "Cargo delivered to wrong hub", "label_error", "REROUTE"),
    (4, "REFUSED_DELIVERY", "LOW", "Consignee rejected cargo", "wrong_item", "RETURN_TO_SHIPPER"),
    (5, "DAMAGE", "CRITICAL", "Severe damage to high-value cargo", "inadequate_packaging", "ESCALATE_TO_HUMAN"),
    (6, "DELAY", "HIGH", "Carrier operational failure", "carrier_delay", "EXPEDITE_AND_CHARGE"),
    (7, "CUSTOMS_HOLD", "MEDIUM", "HS code mismatch flagged", "hs_code_mismatch", "SUBMIT_CUSTOMS_DOCS"),
    (8, "DAMAGE", "LOW", "Minor cosmetic damage reported", "cosmetic_defect", "CUSTOMER_CREDIT"),
    (9, "DELAY", "LOW", "Minor delay within grace period", "minor_delay", "NO_ACTION"),
    (10, "MISROUTE", "HIGH", "Critical shipment sent to wrong country", "sorting_mistake", "REROUTE"),
    (11, "CUSTOMS_HOLD", "CRITICAL", "Regulatory inspection required", "regulatory_inspection", "ESCALATE_TO_HUMAN"),
    (12, "REFUSED_DELIVERY", "MEDIUM", "Quality issue with delivered goods", "quality_issue", "RETURN_TO_SHIPPER"),
    (13, "DAMAGE", "MEDIUM", "Water damage to packaging", "weather_exposure", "FILE_CARRIER_CLAIM"),
    (14, "DELAY", "CRITICAL", "Perishable cargo at risk", "cold_chain_failure", "ESCALATE_TO_HUMAN"),
    (15, "CUSTOMS_HOLD", "LOW", "Duty payment pending", "duty_pending", "CUSTOMER_NOTIFICATION"),
    (16, "MISROUTE", "LOW", "Slight detour, still en route", "routing_error", "NO_ACTION"),
    (17, "DAMAGE", "MEDIUM", "Packing insufficient per weight class", "poor_packaging", "CUSTOMER_CREDIT"),
    (18, "DELAY", "HIGH", "Missed connection at hub", "missed_connection", "EXPEDITE_AND_CHARGE"),
    (19, "REFUSED_DELIVERY", "HIGH", "Order cancellation after dispatch", "order_cancellation", "RETURN_TO_SHIPPER"),
    (20, "CUSTOMS_HOLD", "HIGH", "Missing commercial invoice", "missing_invoice", "SUBMIT_CUSTOMS_DOCS"),
    (21, "DAMAGE", "LOW", "Concealed damage found after delivery", "concealed_damage", "FILE_CARRIER_CLAIM"),
    (22, "DELAY", "MEDIUM", "Port congestion causing delay", "port_congestion", "CUSTOMER_NOTIFICATION"),
    (23, "MISROUTE", "MEDIUM", "Address discrepancy on BOL", "address_discrepancy", "REROUTE"),
    (24, "REFUSED_DELIVERY", "MEDIUM", "Damaged upon arrival, consignee refused", "damage_refusal", "FILE_CARRIER_CLAIM"),
]


def get_db_path() -> str:
    return DB_PATH


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _generate_shipment_id(idx: int) -> str:
    return f"SH-{2026}{idx+1:05d}"


def _generate_case_id(idx: int) -> str:
    return f"CASE-{2026}{idx+1:04d}"


def _random_date(start: datetime, end: datetime) -> datetime:
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def init_db() -> None:
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = get_connection()
    cur = conn.cursor()

    # Shipments
    cur.execute("""
    CREATE TABLE shipments (
        shipment_id TEXT PRIMARY KEY,
        origin TEXT,
        destination TEXT,
        carrier_id TEXT,
        customer_id TEXT,
        cargo_value REAL,
        commodity TEXT,
        promised_delivery TEXT,
        actual_delivery TEXT,
        status TEXT,
        weight_kg REAL,
        packages INTEGER
    )
    """)

    # Tracking events
    cur.execute("""
    CREATE TABLE tracking_events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id TEXT,
        timestamp TEXT,
        location TEXT,
        event_type TEXT,
        description TEXT
    )
    """)

    # POD
    cur.execute("""
    CREATE TABLE pod_details (
        pod_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id TEXT,
        delivered_at TEXT,
        signed_by TEXT,
        condition_notes TEXT,
        photo_reference TEXT
    )
    """)

    # Damage photos
    cur.execute("""
    CREATE TABLE damage_photos (
        photo_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id TEXT,
        taken_at TEXT,
        severity_tag TEXT,
        description TEXT,
        photo_reference TEXT
    )
    """)

    # Customs entries
    cur.execute("""
    CREATE TABLE customs_entries (
        entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id TEXT,
        hs_code TEXT,
        duty_status TEXT,
        inspection_flag INTEGER,
        missing_docs TEXT,
        entry_status TEXT
    )
    """)

    # Weather alerts
    cur.execute("""
    CREATE TABLE weather_alerts (
        alert_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id TEXT,
        alert_date TEXT,
        location TEXT,
        severity TEXT,
        description TEXT
    )
    """)

    # Carrier performance
    cur.execute("""
    CREATE TABLE carrier_performance (
        carrier_id TEXT PRIMARY KEY,
        on_time_rate REAL,
        damage_rate REAL,
        avg_transit_days REAL,
        total_shipments INTEGER
    )
    """)

    # Customer history
    cur.execute("""
    CREATE TABLE customer_history (
        history_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        shipment_id TEXT,
        exception_type TEXT,
        resolution TEXT,
        resolution_amount REAL,
        occurred_at TEXT
    )
    """)

    # SLA terms
    cur.execute("""
    CREATE TABLE sla_terms (
        sla_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_tier TEXT,
        carrier_id TEXT,
        transit_days_commit INTEGER,
        grace_period_hours INTEGER,
        liability_cap REAL
    )
    """)

    # Claims history
    cur.execute("""
    CREATE TABLE claims_history (
        claim_id INTEGER PRIMARY KEY AUTOINCREMENT,
        shipment_id TEXT,
        claim_type TEXT,
        amount_claimed REAL,
        amount_approved REAL,
        status TEXT,
        filed_at TEXT
    )
    """)

    # Exceptions
    cur.execute("""
    CREATE TABLE exceptions (
        case_id TEXT PRIMARY KEY,
        shipment_id TEXT,
        exception_type TEXT,
        severity TEXT,
        description TEXT,
        reported_at TEXT,
        status TEXT,
        root_cause TEXT,
        expected_action TEXT
    )
    """)

    # Audit log
    cur.execute("""
    CREATE TABLE audit_log (
        audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        case_id TEXT,
        agent TEXT,
        event_type TEXT,
        status TEXT,
        details TEXT
    )
    """)

    # Human decisions
    cur.execute("""
    CREATE TABLE human_decisions (
        decision_id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT,
        decision TEXT,
        reason TEXT,
        decided_by TEXT,
        decided_at TEXT
    )
    """)

    random.seed(42)

    # Insert carriers
    for c in CARRIERS:
        cur.execute("""
            INSERT INTO carrier_performance (carrier_id, on_time_rate, damage_rate, avg_transit_days, total_shipments)
            VALUES (?, ?, ?, ?, ?)
        """, (c["id"], c["on_time_rate"], c["damage_rate"], random.uniform(3, 10), random.randint(500, 5000)))

    # Insert SLA terms
    for tier in ["Standard", "Premium", "Strategic"]:
        for carrier in CARRIERS:
            transit = {"Standard": 7, "Premium": 5, "Strategic": 4}[tier]
            grace = {"Standard": 24, "Premium": 12, "Strategic": 6}[tier]
            liability = {"Standard": 5000, "Premium": 15000, "Strategic": 50000}[tier]
            cur.execute("""
                INSERT INTO sla_terms (customer_tier, carrier_id, transit_days_commit, grace_period_hours, liability_cap)
                VALUES (?, ?, ?, ?, ?)
            """, (tier, carrier["id"], transit, grace, liability))

    # Generate 60 shipments
    shipments = []
    for i in range(60):
        sid = _generate_shipment_id(i)
        carrier = CARRIERS[i % len(CARRIERS)]
        customer = CUSTOMERS[i % len(CUSTOMERS)]
        origin = ORIGINS[i % len(ORIGINS)]
        dest = DESTINATIONS[i % len(DESTINATIONS)]
        commodity = COMMODITIES[i % len(COMMODITIES)]
        cargo_value = round(random.uniform(800, 75000), 2)
        promised = DEMO_CLOCK - timedelta(days=random.randint(2, 10), hours=random.randint(0, 23))
        actual = promised + timedelta(hours=random.randint(-12, 72)) if random.random() > 0.3 else None
        status = "DELIVERED" if actual else "IN_TRANSIT"
        if i < 25:
            status = random.choice(["DELIVERED", "IN_TRANSIT", "EXCEPTION"])
        weight = round(random.uniform(50, 2000), 1)
        packages = random.randint(1, 20)
        shipments.append({
            "id": sid, "origin": origin, "destination": dest, "carrier": carrier["id"],
            "customer": customer["id"], "cargo_value": cargo_value, "commodity": commodity,
            "promised": promised, "actual": actual, "status": status,
            "weight": weight, "packages": packages
        })
        cur.execute("""
            INSERT INTO shipments (shipment_id, origin, destination, carrier_id, customer_id, cargo_value, commodity, promised_delivery, actual_delivery, status, weight_kg, packages)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (sid, origin, dest, carrier["id"], customer["id"], cargo_value, commodity,
              promised.isoformat(), actual.isoformat() if actual else None, status, weight, packages))

    # Insert 25 exceptions
    for idx, (s_idx, ex_type, severity, desc, root_cause, expected_action) in enumerate(EXCEPTION_CASES):
        case_id = _generate_case_id(idx)
        sid = _generate_shipment_id(s_idx)
        reported = DEMO_CLOCK - timedelta(days=random.randint(1, 5), hours=random.randint(0, 23))
        cur.execute("""
            INSERT INTO exceptions (case_id, shipment_id, exception_type, severity, description, reported_at, status, root_cause, expected_action)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (case_id, sid, ex_type, severity, desc, reported.isoformat(), "OPEN", root_cause, expected_action))

    # Generate tracking events
    event_types = ["PICKUP", "DEPARTURE", "ARRIVAL", "TRANSFER", "CUSTOMS_CLEARANCE", "OUT_FOR_DELIVERY", "DELIVERED", "EXCEPTION_SCAN"]
    event_id = 1
    for s in shipments:
        num_events = random.randint(4, 10)
        base_time = DEMO_CLOCK - timedelta(days=random.randint(5, 15))
        for j in range(num_events):
            ts = base_time + timedelta(hours=j * random.randint(4, 24))
            loc = random.choice([s["origin"], s["destination"], "Transit Hub"])
            etype = event_types[min(j, len(event_types)-1)]
            desc = f"{etype} at {loc}"
            if s["id"] in ["SH-202600001", "SH-202600006", "SH-202600014"] and etype == "TRANSFER":
                desc = "DELAYED_TRANSFER - missed connection"
            cur.execute("""
                INSERT INTO tracking_events (shipment_id, timestamp, location, event_type, description)
                VALUES (?, ?, ?, ?, ?)
            """, (s["id"], ts.isoformat(), loc, etype, desc))
            event_id += 1

    # POD records for delivered shipments
    for s in shipments:
        if s["status"] == "DELIVERED" and s["actual"]:
            condition = "GOOD"
            if s["id"] in ["SH-202600001", "SH-202600005", "SH-202600008", "SH-202600013", "SH-202600017", "SH-202600021"]:
                condition = random.choice(["DAMAGED", "WET", "CRUSHED"])
            cur.execute("""
                INSERT INTO pod_details (shipment_id, delivered_at, signed_by, condition_notes, photo_reference)
                VALUES (?, ?, ?, ?, ?)
            """, (s["id"], s["actual"].isoformat(), f"Signer {random.randint(1,99)}", condition, f"POD_{s['id']}.jpg"))

    # Damage photos
    damage_shipments = ["SH-202600001", "SH-202600005", "SH-202600008", "SH-202600013", "SH-202600017", "SH-202600021"]
    for sid in damage_shipments:
        severity_tag = random.choice(["MINOR", "MODERATE", "SEVERE"])
        if sid == "SH-202600005":
            severity_tag = "SEVERE"
        cur.execute("""
            INSERT INTO damage_photos (shipment_id, taken_at, severity_tag, description, photo_reference)
            VALUES (?, ?, ?, ?, ?)
        """, (sid, DEMO_CLOCK.isoformat(), severity_tag, f"{severity_tag} damage visible", f"DMG_{sid}.jpg"))

    # Customs entries
    customs_shipments = ["SH-202600003", "SH-202600007", "SH-202600011", "SH-202600015", "SH-202600020"]
    for sid in customs_shipments:
        hs = random.choice(["8471.30", "8708.99", "6203.42", "3004.90", "8411.21"])
        duty = random.choice(["PAID", "PENDING", "DISPUTED"])
        inspection = 1 if sid in ["SH-202600011", "SH-202600015"] else 0
        missing = ""
        if sid == "SH-202600003":
            missing = "Commercial Invoice"
        elif sid == "SH-202600007":
            missing = "Certificate of Origin"
        elif sid == "SH-202600020":
            missing = "Commercial Invoice, Packing List"
        entry_status = "HOLD" if missing or inspection else "CLEARED"
        cur.execute("""
            INSERT INTO customs_entries (shipment_id, hs_code, duty_status, inspection_flag, missing_docs, entry_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sid, hs, duty, inspection, missing, entry_status))

    # Weather alerts
    weather_shipments = ["SH-202600001", "SH-202600006", "SH-202600010", "SH-202600014", "SH-202600018"]
    for sid in weather_shipments:
        cur.execute("""
            INSERT INTO weather_alerts (shipment_id, alert_date, location, severity, description)
            VALUES (?, ?, ?, ?, ?)
        """, (sid, DEMO_CLOCK.isoformat(), "Transit Corridor", "MODERATE", "Severe weather causing delays"))

    # Customer history
    for cust in CUSTOMERS:
        for _ in range(random.randint(1, 3)):
            s = random.choice(shipments)
            cur.execute("""
                INSERT INTO customer_history (customer_id, shipment_id, exception_type, resolution, resolution_amount, occurred_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (cust["id"], s["id"], random.choice(["DAMAGE", "DELAY", "NONE"]),
                  random.choice(["CREDIT", "CLAIM", "NONE"]), round(random.uniform(100, 2000), 2),
                  (DEMO_CLOCK - timedelta(days=random.randint(30, 180))).isoformat()))

    # Claims history
    claim_shipments = ["SH-202600001", "SH-202600005", "SH-202600013", "SH-202600017", "SH-202600021"]
    for sid in claim_shipments:
        claimed = round(random.uniform(500, 15000), 2)
        approved = claimed * random.uniform(0.5, 1.0)
        cur.execute("""
            INSERT INTO claims_history (shipment_id, claim_type, amount_claimed, amount_approved, status, filed_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (sid, "DAMAGE", claimed, round(approved, 2), random.choice(["APPROVED", "PENDING", "DENIED"]),
              DEMO_CLOCK.isoformat()))

    conn.commit()
    conn.close()

    # Verify counts
    conn = get_connection()
    cur = conn.cursor()
    tables = ["shipments", "tracking_events", "exceptions", "pod_details", "damage_photos",
              "customs_entries", "weather_alerts", "carrier_performance", "customer_history",
              "sla_terms", "claims_history"]
    counts = {}
    for t in tables:
        cur.execute(f"SELECT COUNT(*) FROM {t}")
        counts[t] = cur.fetchone()[0]
    conn.close()
    return counts


if __name__ == "__main__":
    counts = init_db()
    print("Database initialized. Record counts:")
    for t, c in counts.items():
        print(f"  {t}: {c}")