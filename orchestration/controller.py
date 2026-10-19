"""Central workflow controller for F.A.I.R. multi-agent orchestration."""
from datetime import datetime
from typing import Optional

from models.state import InvestigationState, AuditEvent, CriticVerdict
from agents.intake import IntakeAgent
from agents.planner import PlannerAgent
from agents.evidence import EvidenceAgent
from agents.resolver import ResolverAgent
from agents.critic import CriticAgent
from utils.policy import check_human_review_required


class WorkflowController:
    """Coordinates five agents through a typed state machine with conditional branching."""

    def __init__(self):
        self.intake = IntakeAgent()
        self.planner = PlannerAgent()
        self.evidence = EvidenceAgent()
        self.resolver = ResolverAgent()
        self.critic = CriticAgent()

    def run(self, case_id: str, shipment_id: str, raw_exception: dict) -> InvestigationState:
        """Execute full workflow for a freight exception case."""
        # Intake & Triage
        state = self.intake.process(case_id, shipment_id, raw_exception)

        # Investigation Planner
        state = self.planner.plan(state)

        # Evidence Collector
        state = self.evidence.collect(state)

        # Check evidence gap auto-escalation
        if state.bundle.gap_ratio > 0.30:
            state.requires_human_review = True
            state.human_review_reasons.append("Evidence gaps exceed 30%")
            state.status = "ESCALATED"
            state.audit_log.append(AuditEvent(
                timestamp=datetime.now().isoformat(),
                case_id=case_id,
                agent="Orchestrator",
                event_type="AUTO_ESCALATE",
                status="EVIDENCE_GAP",
                details={"gap_ratio": state.bundle.gap_ratio},
            ))
            return state

        # Resolver
        state = self.resolver.resolve(state)

        # Critic validation with bounded loop
        max_iterations = 2
        for iteration in range(max_iterations):
            state = self.critic.validate(state)
            if state.critic_verdict == CriticVerdict.VALID:
                break
            elif state.critic_verdict == CriticVerdict.REJECT:
                state.status = "ESCALATED"
                break
            elif state.critic_verdict == CriticVerdict.REVISE:
                if iteration < max_iterations - 1:
                    state.revision_count += 1
                    state.audit_log.append(AuditEvent(
                        timestamp=datetime.now().isoformat(),
                        case_id=case_id,
                        agent="Orchestrator",
                        event_type="REVISION",
                        status="RETRY",
                        details={"attempt": state.revision_count},
                    ))
                    state = self.resolver.resolve(state)
                else:
                    state.status = "ESCALATED"
                    state.human_review_reasons.append("Critic revision failed after bounded attempts")
                    state.requires_human_review = True
                    break

        # Final human review gate
        if state.resolution and not state.requires_human_review:
            req, reasons = check_human_review_required(
                proposed_amount=state.resolution.amount,
                confidence=state.resolution.confidence,
                critic_verdict=state.critic_verdict.value,
                evidence_gap_ratio=state.bundle.gap_ratio,
                customer_tier=state.case.customer_tier,
            )
            state.requires_human_review = req
            state.human_review_reasons.extend(reasons)

        if state.requires_human_review and state.status != "ESCALATED":
            state.status = "PENDING_APPROVAL"

        if not state.requires_human_review and state.critic_verdict == CriticVerdict.VALID:
            state.status = "APPROVED"
            state.final_action = state.resolution.action if state.resolution else ""
            state.final_amount = state.resolution.amount if state.resolution else 0.0
            state.completed_at = datetime.now().isoformat()

        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=case_id,
            agent="Orchestrator",
            event_type="WORKFLOW_COMPLETE",
            status=state.status,
            details={"requires_human_review": state.requires_human_review},
        ))
        return state

    def approve_case(self, state: InvestigationState, reviewer: str = "system") -> InvestigationState:
        """Human approval of resolution."""
        if state.resolution and not state.requires_human_review:
            # Auto-approved
            state.final_action = state.resolution.action
            state.final_amount = state.resolution.amount
        state.status = "APPROVED"
        state.approved_by = reviewer
        state.approval_timestamp = datetime.now().isoformat()
        state.completed_at = datetime.now().isoformat()
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=state.case.case_id,
            agent="HumanGate",
            event_type="APPROVAL",
            status="APPROVED",
            details={"reviewer": reviewer, "action": state.final_action, "amount": state.final_amount},
        ))
        return state

    def override_case(self, state: InvestigationState, new_action: str, reason: str, reviewer: str) -> InvestigationState:
        """Human override with alternative action."""
        state.final_action = new_action
        state.status = "OVERRIDDEN"
        state.approved_by = reviewer
        state.approval_timestamp = datetime.now().isoformat()
        state.completed_at = datetime.now().isoformat()
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=state.case.case_id,
            agent="HumanGate",
            event_type="OVERRIDE",
            status="OVERRIDDEN",
            details={"reviewer": reviewer, "new_action": new_action, "reason": reason},
        ))
        return state

    def reject_case(self, state: InvestigationState, reason: str, reviewer: str) -> InvestigationState:
        """Human rejection of resolution."""
        state.status = "REJECTED"
        state.approved_by = reviewer
        state.approval_timestamp = datetime.now().isoformat()
        state.completed_at = datetime.now().isoformat()
        state.audit_log.append(AuditEvent(
            timestamp=datetime.now().isoformat(),
            case_id=state.case.case_id,
            agent="HumanGate",
            event_type="REJECTION",
            status="REJECTED",
            details={"reviewer": reviewer, "reason": reason},
        ))
        return state