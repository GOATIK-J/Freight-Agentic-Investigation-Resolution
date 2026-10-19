"""Agent 1 — Intake & Triage: Normalizes exceptions into structured FreightCase objects."""
from datetime import datetime
from models.state import FreightCase, InvestigationState, AuditEvent, ExceptionType, Severity
from utils.policy import compute_severity, compute_investigation_budget


class IntakeAgent:
    """Parses raw exception events and assigns severity and investigation budget."""

    def process(self, case_id: str, shipment_id: str, raw_exception: dict) -> InvestigationState:
        ex_type_str = raw_exception.get("exception_type", "UNKNOWN").upper()
        try:
            exception_type = ExceptionType[ex_type_str]
        except KeyError:
            exception_type = ExceptionType.UNKNOWN

        cargo_value = float(raw_exception.get("cargo_value", 0))
        severity = compute_severity(cargo_value)
        budget = compute_investigation_budget(severity)

        case = FreightCase(
            case_id=case_id,
            shipment_id=shipment_id,
            exception_type=exception_type,
            severity=severity,
            cargo_value=cargo_value,
            customer_tier=raw_exception.get("customer_tier", "Standard"),
            carrier_id=raw_exception.get("carrier_id", ""),
            origin=raw_exception.get("origin", ""),
            destination=raw_exception.get("destination", ""),
            commodity=raw_exception.get("commodity", ""),
            promised_delivery=raw_exception.get("promised_delivery", ""),
            reported_at=raw_exception.get("reported_at", datetime.now().isoformat()),
            description=raw_exception.get("description", ""),
            investigation_budget=budget,
        )

        state = InvestigationState(case=case, status="INTAKE_COMPLETE")
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=case_id,
            agent="IntakeAgent",
            event_type="INTAKE",
            status="SUCCESS",
            details={"severity": severity.value, "budget": budget, "exception_type": exception_type.value},
        ))
        return state