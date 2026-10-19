"""Agent 3 — Evidence Collector: Executes investigation plan via tool calls."""
from datetime import datetime
from models.state import InvestigationState, EvidenceItem, EvidenceBundle, AuditEvent
from tools.freight_tools import FreightTools
from utils.policy import compute_evidence_gap_ratio


class EvidenceAgent:
    """Executes read-only tool calls against synthetic data store."""

    def collect(self, state: InvestigationState) -> InvestigationState:
        tools = FreightTools()
        bundle = EvidenceBundle()
        tool_calls = 0
        budget = state.case.investigation_budget

        for tool_name in state.plan.tools_required:
            if tool_calls >= budget:
                bundle.gaps.append(f"Tool {tool_name} skipped: budget exhausted")
                continue

            try:
                result = self._call_tool(tools, tool_name, state.case.shipment_id, state.case.customer_tier, state.case.carrier_id)
                status = "RETRIEVED" if result.get("status") == "FOUND" else "MISSING"
                finding = self._summarize(tool_name, result)
                item = EvidenceItem(
                    tool_name=tool_name,
                    status=status,
                    finding=finding,
                    source="synthetic_db",
                    timestamp=datetime.now().isoformat(),
                    details=result,
                )
                bundle.items.append(item)
                if status == "MISSING":
                    bundle.gaps.append(f"{tool_name}: no data found")
                tool_calls += 1
            except Exception as e:
                bundle.items.append(EvidenceItem(
                    tool_name=tool_name,
                    status="ERROR",
                    finding=str(e),
                    source="synthetic_db",
                    timestamp=datetime.now().isoformat(),
                    details={},
                ))
                bundle.gaps.append(f"{tool_name}: error - {e}")
                tool_calls += 1

        expected = len(state.plan.tools_required)
        missing = len(bundle.gaps)
        bundle.gap_ratio = compute_evidence_gap_ratio(expected, missing)
        state.bundle = bundle
        state.status = "EVIDENCE_COLLECTED"
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=state.case.case_id,
            agent="EvidenceAgent",
            event_type="EVIDENCE_COLLECTION",
            status="SUCCESS",
            details={"tool_calls": tool_calls, "gaps": missing, "gap_ratio": round(bundle.gap_ratio, 2)},
        ))
        return state

    def _call_tool(self, tools: FreightTools, tool_name: str, shipment_id: str, customer_tier: str, carrier_id: str) -> dict:
        if tool_name == "get_shipment_info":
            return tools.get_shipment_info(shipment_id)
        elif tool_name == "get_tracking_timeline":
            return tools.get_tracking_timeline(shipment_id)
        elif tool_name == "get_pod_details":
            return tools.get_pod_details(shipment_id)
        elif tool_name == "get_damage_photos":
            return tools.get_damage_photos(shipment_id)
        elif tool_name == "get_customs_entry":
            return tools.get_customs_entry(shipment_id)
        elif tool_name == "get_weather_alerts":
            return tools.get_weather_alerts(shipment_id)
        elif tool_name == "get_carrier_performance":
            return tools.get_carrier_performance(carrier_id)
        elif tool_name == "get_customer_history":
            return tools.get_customer_history(shipment_id)
        elif tool_name == "get_sla_terms":
            return tools.get_sla_terms(customer_tier, carrier_id)
        elif tool_name == "get_claims_history":
            return tools.get_claims_history(shipment_id)
        return {"status": "UNKNOWN_TOOL"}

    def _summarize(self, tool_name: str, result: dict) -> str:
        if result.get("status") != "FOUND":
            return "No data available"
        if tool_name == "get_shipment_info":
            d = result.get("data", {})
            return f"Shipment {d.get('shipment_id')}: {d.get('commodity')}, value ${d.get('cargo_value', 0):,.2f}"
        elif tool_name == "get_tracking_timeline":
            events = result.get("events", [])
            return f"{len(events)} tracking events retrieved"
        elif tool_name == "get_pod_details":
            d = result.get("data", {})
            return f"POD condition: {d.get('condition_notes', 'N/A')}"
        elif tool_name == "get_damage_photos":
            photos = result.get("photos", [])
            return f"{len(photos)} damage photo(s) found"
        elif tool_name == "get_customs_entry":
            d = result.get("data", {})
            return f"Customs status: {d.get('entry_status', 'N/A')}, missing: {d.get('missing_docs', 'None')}"
        elif tool_name == "get_weather_alerts":
            alerts = result.get("alerts", [])
            return f"{len(alerts)} weather alert(s) found"
        elif tool_name == "get_carrier_performance":
            d = result.get("data", {})
            return f"On-time: {d.get('on_time_rate', 0)*100:.1f}%, Damage: {d.get('damage_rate', 0)*100:.1f}%"
        elif tool_name == "get_customer_history":
            hist = result.get("history", [])
            return f"{len(hist)} historical record(s) found"
        elif tool_name == "get_sla_terms":
            d = result.get("data", {})
            return f"Transit commit: {d.get('transit_days_commit')} days, liability cap: ${d.get('liability_cap', 0):,.2f}"
        elif tool_name == "get_claims_history":
            claims = result.get("claims", [])
            return f"{len(claims)} prior claim(s) found"
        return "Data retrieved"