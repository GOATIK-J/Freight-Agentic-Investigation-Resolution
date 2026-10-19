"""Ten read-only investigation query tools for F.A.I.R. agents."""
import sqlite3
from typing import Any

from data.database import get_connection


class FreightTools:
    """Read-only tool suite for freight investigation."""

    @staticmethod
    def get_shipment_info(shipment_id: str) -> dict[str, Any]:
        """Retrieve core shipment metadata."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM shipments WHERE shipment_id = ?", (shipment_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"status": "NOT_FOUND", "data": None}
        return {"status": "FOUND", "data": dict(row)}

    @staticmethod
    def get_tracking_timeline(shipment_id: str) -> dict[str, Any]:
        """Retrieve chronological scan events."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT timestamp, location, event_type, description
            FROM tracking_events
            WHERE shipment_id = ?
            ORDER BY timestamp
        """, (shipment_id,))
        rows = cur.fetchall()
        conn.close()
        return {"status": "FOUND" if rows else "NOT_FOUND", "events": [dict(r) for r in rows]}

    @staticmethod
    def get_pod_details(shipment_id: str) -> dict[str, Any]:
        """Retrieve proof of delivery details."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM pod_details WHERE shipment_id = ?", (shipment_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"status": "NOT_FOUND", "data": None}
        return {"status": "FOUND", "data": dict(row)}

    @staticmethod
    def get_damage_photos(shipment_id: str) -> dict[str, Any]:
        """Retrieve damage documentation."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM damage_photos WHERE shipment_id = ?", (shipment_id,))
        rows = cur.fetchall()
        conn.close()
        return {"status": "FOUND" if rows else "NOT_FOUND", "photos": [dict(r) for r in rows]}

    @staticmethod
    def get_customs_entry(shipment_id: str) -> dict[str, Any]:
        """Retrieve customs declaration and status."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM customs_entries WHERE shipment_id = ?", (shipment_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"status": "NOT_FOUND", "data": None}
        return {"status": "FOUND", "data": dict(row)}

    @staticmethod
    def get_weather_alerts(shipment_id: str) -> dict[str, Any]:
        """Retrieve severe weather events along transit corridor."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM weather_alerts WHERE shipment_id = ?", (shipment_id,))
        rows = cur.fetchall()
        conn.close()
        return {"status": "FOUND" if rows else "NOT_FOUND", "alerts": [dict(r) for r in rows]}

    @staticmethod
    def get_carrier_performance(carrier_id: str) -> dict[str, Any]:
        """Retrieve historical on-time and damage rates for carrier."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM carrier_performance WHERE carrier_id = ?", (carrier_id,))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"status": "NOT_FOUND", "data": None}
        return {"status": "FOUND", "data": dict(row)}

    @staticmethod
    def get_customer_history(customer_id: str) -> dict[str, Any]:
        """Retrieve past exceptions and claims for customer."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM customer_history WHERE customer_id = ?
            ORDER BY occurred_at DESC
        """, (customer_id,))
        rows = cur.fetchall()
        conn.close()
        return {"status": "FOUND" if rows else "NOT_FOUND", "history": [dict(r) for r in rows]}

    @staticmethod
    def get_sla_terms(customer_tier: str, carrier_id: str) -> dict[str, Any]:
        """Retrieve contractual delivery commitment and liability cap."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT * FROM sla_terms WHERE customer_tier = ? AND carrier_id = ?
        """, (customer_tier, carrier_id))
        row = cur.fetchone()
        conn.close()
        if not row:
            return {"status": "NOT_FOUND", "data": None}
        return {"status": "FOUND", "data": dict(row)}

    @staticmethod
    def get_claims_history(shipment_id: str) -> dict[str, Any]:
        """Retrieve previous similar claims and outcomes."""
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM claims_history WHERE shipment_id = ?", (shipment_id,))
        rows = cur.fetchall()
        conn.close()
        return {"status": "FOUND" if rows else "NOT_FOUND", "claims": [dict(r) for r in rows]}