"""Agent 5 — Critic: Independent adversarial validation of Resolver output."""
from datetime import datetime
from models.state import InvestigationState, CriticVerdict, AuditEvent
from utils.policy import check_human_review_required


class CriticAgent:
    """Tests Resolver conclusions against alternative hypotheses and policy."""

    def validate(self, state: InvestigationState) -> InvestigationState:
        resolution = state.resolution
        if not resolution:
            state.critic_verdict = CriticVerdict.REJECT
            state.critic_notes = "No resolution found to validate."
            state.status = "CRITIC_REJECTED"
            state.audit_log.append(AuditEvent(
                timestamp=datetime.now().isoformat(),
                case_id=state.case.case_id,
                agent="CriticAgent",
                event_type="CRITIC",
                status="REJECT",
                details={"reason": "No resolution object"},
            ))
            return state

        issues = []

        # Check evidence supports root cause
        if state.bundle.gap_ratio > 0.25:
            issues.append("Evidence gaps exceed 25%; root cause may be speculative.")

        # Check confidence justification
        if resolution.confidence > 0.9 and state.bundle.gap_ratio > 0.15:
            issues.append("High confidence not justified by evidence quality.")
            resolution.confidence = min(resolution.confidence, 0.85)

        # Check contradictory facts
        for item in state.bundle.items:
            if item.tool_name == "get_pod_details" and item.status == "RETRIEVED":
                condition = item.details.get("data", {}).get("condition_notes", "")
                if resolution.root_cause == "improper_handling" and condition == "GOOD":
                    issues.append("Contradiction: POD shows GOOD condition but root cause is improper handling.")

        # Check alternative hypotheses
        alt_causes = []
        if resolution.root_cause != "weather_event" and any(
            item.tool_name == "get_weather_alerts" and item.status == "RETRIEVED" and item.details.get("alerts")
            for item in state.bundle.items
        ):
            alt_causes.append("weather_event")

        if alt_causes:
            issues.append(f"Alternative causes possible: {', '.join(alt_causes)}")

        # Check policy compliance
        if resolution.amount > 10000 and resolution.action not in ["ESCALATE_TO_HUMAN", "FILE_CARRIER_CLAIM"]:
            issues.append("High amount requires escalation action.")

        # Determine verdict
        if len(issues) >= 2 or "Contradiction" in str(issues):
            if state.revision_count >= 1:
                verdict = CriticVerdict.REJECT
                notes = f"REJECT after revision. Issues: {'; '.join(issues)}"
            else:
                verdict = CriticVerdict.REVISE
                notes = f"REVISE requested. Issues: {'; '.join(issues)}"
        elif len(issues) == 1:
            verdict = CriticVerdict.REVISE
            notes = f"REVISE with minor issue: {issues[0]}"
        else:
            verdict = CriticVerdict.VALID
            notes = "All checks passed. Resolver conclusion is well-supported."

        state.critic_verdict = verdict
        state.critic_notes = notes
        state.status = "CRITIC_VALID" if verdict == CriticVerdict.VALID else "CRITIC_REVISE" if verdict == CriticVerdict.REVISE else "CRITIC_REJECTED"

        # Human review check
        req, reasons = check_human_review_required(
            proposed_amount=resolution.amount,
            confidence=resolution.confidence,
            critic_verdict=verdict.value,
            evidence_gap_ratio=state.bundle.gap_ratio,
            customer_tier=state.case.customer_tier,
        )
        state.requires_human_review = req
        state.human_review_reasons = reasons

        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=state.case.case_id,
            agent="CriticAgent",
            event_type="CRITIC",
            status=verdict.value,
            details={"issues": issues, "human_required": req, "reasons": reasons},
        ))
        return state