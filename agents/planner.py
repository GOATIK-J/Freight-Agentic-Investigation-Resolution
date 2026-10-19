"""Agent 2 — Investigation Planner: Builds exception-specific evidence plans."""
from datetime import datetime
from models.state import InvestigationState, EvidencePlan, AuditEvent, ExceptionType


class PlannerAgent:
    """Generates tailored evidence plans per exception family."""

    EVIDENCE_MAP = {
        ExceptionType.DAMAGE: [
            ("get_shipment_info", "Core shipment metadata"),
            ("get_pod_details", "Proof of delivery condition"),
            ("get_damage_photos", "Damage documentation"),
            ("get_tracking_timeline", "Transit handling events"),
            ("get_carrier_performance", "Carrier damage history"),
            ("get_claims_history", "Prior similar claims"),
        ],
        ExceptionType.DELAY: [
            ("get_shipment_info", "Core shipment metadata"),
            ("get_tracking_timeline", "Route history and dwell times"),
            ("get_weather_alerts", "Weather along corridor"),
            ("get_sla_terms", "Contractual commitments"),
            ("get_carrier_performance", "Carrier on-time rate"),
            ("get_customer_history", "Customer delay history"),
        ],
        ExceptionType.CUSTOMS_HOLD: [
            ("get_shipment_info", "Core shipment metadata"),
            ("get_customs_entry", "Customs declaration and status"),
            ("get_tracking_timeline", "Last known location"),
            ("get_customer_history", "Customer customs history"),
            ("get_sla_terms", "Contractual commitments"),
        ],
        ExceptionType.MISROUTE: [
            ("get_shipment_info", "Core shipment metadata"),
            ("get_tracking_timeline", "Current and planned route"),
            ("get_pod_details", "Delivery attempt details"),
            ("get_carrier_performance", "Carrier routing accuracy"),
        ],
        ExceptionType.REFUSED_DELIVERY: [
            ("get_shipment_info", "Core shipment metadata"),
            ("get_pod_details", "Delivery attempt details"),
            ("get_damage_photos", "Condition at delivery"),
            ("get_tracking_timeline", "Transit history"),
            ("get_customer_history", "Customer refusal history"),
        ],
        ExceptionType.UNKNOWN: [
            ("get_shipment_info", "Core shipment metadata"),
            ("get_tracking_timeline", "All transit events"),
        ],
    }

    def plan(self, state: InvestigationState) -> InvestigationState:
        tools = self.EVIDENCE_MAP.get(state.case.exception_type, self.EVIDENCE_MAP[ExceptionType.UNKNOWN])
        plan = EvidencePlan(
            steps=[desc for _, desc in tools],
            tools_required=[tool for tool, _ in tools],
        )
        state.plan = plan
        state.status = "PLANNED"
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=state.case.case_id,
            agent="PlannerAgent",
            event_type="PLAN",
            status="SUCCESS",
            details={"steps": len(plan.steps), "tools": plan.tools_required},
        ))
        return state