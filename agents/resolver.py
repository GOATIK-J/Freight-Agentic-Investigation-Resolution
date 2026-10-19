"""Agent 4 — Resolver: Correlates evidence and proposes resolution."""
from datetime import datetime
from models.state import InvestigationState, ProposedResolution, AuditEvent, ExceptionType
from utils.policy import compute_resolution_amount, compute_liability_cap, is_action_permitted


class ResolverAgent:
    """Deterministic root cause classification and resolution proposal."""

    def resolve(self, state: InvestigationState) -> InvestigationState:
        case = state.case
        bundle = state.bundle

        # Extract evidence signals
        pod_condition = "UNKNOWN"
        damage_photos_count = 0
        customs_status = "UNKNOWN"
        missing_docs = ""
        weather_alert = False
        tracking_delays = 0
        carrier_on_time = 1.0

        for item in bundle.items:
            if item.tool_name == "get_pod_details" and item.status == "RETRIEVED":
                pod_condition = item.details.get("data", {}).get("condition_notes", "UNKNOWN")
            elif item.tool_name == "get_damage_photos" and item.status == "RETRIEVED":
                damage_photos_count = len(item.details.get("photos", []))
            elif item.tool_name == "get_customs_entry" and item.status == "RETRIEVED":
                customs_status = item.details.get("data", {}).get("entry_status", "UNKNOWN")
                missing_docs = item.details.get("data", {}).get("missing_docs", "")
            elif item.tool_name == "get_weather_alerts" and item.status == "RETRIEVED":
                weather_alert = len(item.details.get("alerts", [])) > 0
            elif item.tool_name == "get_tracking_timeline" and item.status == "RETRIEVED":
                events = item.details.get("events", [])
                tracking_delays = sum(1 for e in events if "DELAY" in e.get("description", "").upper())
            elif item.tool_name == "get_carrier_performance" and item.status == "RETRIEVED":
                carrier_on_time = item.details.get("data", {}).get("on_time_rate", 1.0)

        # Determine root cause and action by exception type
        root_cause = "UNKNOWN"
        action = "ESCALATE_TO_HUMAN"
        confidence = 0.5

        if case.exception_type == ExceptionType.DAMAGE:
            if damage_photos_count > 0 and pod_condition in ["DAMAGED", "CRUSHED", "WET"]:
                root_cause = "improper_handling"
                action = "FILE_CARRIER_CLAIM"
                confidence = 0.85
            elif damage_photos_count > 0 and pod_condition == "GOOD":
                root_cause = "concealed_damage"
                action = "FILE_CARRIER_CLAIM"
                confidence = 0.75
            elif pod_condition == "GOOD" and damage_photos_count == 0:
                root_cause = "inadequate_packaging"
                action = "CUSTOMER_CREDIT"
                confidence = 0.70
            else:
                root_cause = "damage_unverified"
                action = "ESCALATE_TO_HUMAN"
                confidence = 0.55

        elif case.exception_type == ExceptionType.DELAY:
            if weather_alert:
                root_cause = "weather_event"
                action = "CUSTOMER_NOTIFICATION"
                confidence = 0.80
            elif tracking_delays > 0:
                root_cause = "carrier_delay"
                action = "EXPEDITE_AND_CHARGE"
                confidence = 0.78
            elif carrier_on_time < 0.80:
                root_cause = "carrier_operational_failure"
                action = "EXPEDITE_AND_CHARGE"
                confidence = 0.75
            else:
                root_cause = "minor_delay"
                action = "NO_ACTION"
                confidence = 0.65

        elif case.exception_type == ExceptionType.CUSTOMS_HOLD:
            if missing_docs:
                root_cause = "missing_documents"
                action = "SUBMIT_CUSTOMS_DOCS"
                confidence = 0.88
            elif customs_status == "HOLD":
                root_cause = "regulatory_inspection"
                action = "ESCALATE_TO_HUMAN"
                confidence = 0.72
            else:
                root_cause = "customs_unverified"
                action = "CUSTOMER_NOTIFICATION"
                confidence = 0.60

        elif case.exception_type == ExceptionType.MISROUTE:
            root_cause = "label_error"
            action = "REROUTE"
            confidence = 0.82

        elif case.exception_type == ExceptionType.REFUSED_DELIVERY:
            if pod_condition in ["DAMAGED", "CRUSHED"]:
                root_cause = "damage_refusal"
                action = "FILE_CARRIER_CLAIM"
                confidence = 0.80
            else:
                root_cause = "wrong_item"
                action = "RETURN_TO_SHIPPER"
                confidence = 0.75

        # Check action permitted
        if not is_action_permitted(action, case.exception_type):
            action = "ESCALATE_TO_HUMAN"
            confidence = 0.5

        # Compute amount
        amount = compute_resolution_amount(action, case.cargo_value, case.severity.value)
        liability_cap = compute_liability_cap(case.cargo_value, case.customer_tier)
        amount = min(amount, liability_cap)

        # Confidence adjustment for evidence gaps
        if bundle.gap_ratio > 0.20:
            confidence = max(0.3, confidence - 0.15)

        state.resolution = ProposedResolution(
            action=action,
            amount=amount,
            rationale=f"Root cause: {root_cause}. Based on evidence signals.",
            confidence=round(confidence, 2),
            root_cause=root_cause,
            policy_references=[f"Policy-{case.exception_type.value}-001"],
            responsible_team="Operations",
            urgency="HIGH" if case.severity.value in ["HIGH", "CRITICAL"] else "NORMAL",
        )
        state.status = "RESOLVED"
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=case.case_id,
            agent="ResolverAgent",
            event_type="RESOLUTION",
            status="SUCCESS",
            details={"root_cause": root_cause, "action": action, "amount": amount, "confidence": confidence},
        ))
        return state