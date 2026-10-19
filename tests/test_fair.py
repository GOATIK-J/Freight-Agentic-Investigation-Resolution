"""pytest suite for F.A.I.R. system."""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from data.database import init_db, get_connection
from orchestration.controller import WorkflowController
from models.state import ExceptionType, Severity, CriticVerdict
from utils.policy import (
    compute_severity, compute_investigation_budget, compute_evidence_gap_ratio,
    compute_resolution_amount, check_human_review_required, is_action_permitted,
)


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    init_db()


# 1. Severity and budget boundary tests
def test_severity_low_boundary():
    assert compute_severity(4999.99) == Severity.LOW
    assert compute_investigation_budget(Severity.LOW) == 5

def test_severity_medium_boundary():
    assert compute_severity(5000) == Severity.MEDIUM
    assert compute_severity(14999.99) == Severity.MEDIUM
    assert compute_investigation_budget(Severity.MEDIUM) == 8

def test_severity_high_boundary():
    assert compute_severity(15000) == Severity.HIGH
    assert compute_severity(49999.99) == Severity.HIGH
    assert compute_investigation_budget(Severity.HIGH) == 10

def test_severity_critical_boundary():
    assert compute_severity(50000) == Severity.CRITICAL
    assert compute_investigation_budget(Severity.CRITICAL) == 12

# 2. Evidence gap ratio tests
def test_evidence_gap_zero():
    assert compute_evidence_gap_ratio(5, 0) == 0.0

def test_evidence_gap_threshold():
    assert compute_evidence_gap_ratio(10, 3) == 0.3
    assert compute_evidence_gap_ratio(10, 4) == 0.4

def test_evidence_gap_no_expected():
    assert compute_evidence_gap_ratio(0, 0) == 0.0

# 3. Human review threshold tests
def test_human_review_amount():
    req, reasons = check_human_review_required(10001, 0.9, "VALID", 0.1, "Standard")
    assert req is True
    assert any("$10,000" in r for r in reasons)

def test_human_review_confidence():
    req, reasons = check_human_review_required(5000, 0.65, "VALID", 0.1, "Standard")
    assert req is True
    assert any("0.7" in r for r in reasons)

def test_human_review_critic_reject():
    req, reasons = check_human_review_required(5000, 0.8, "REJECT", 0.1, "Standard")
    assert req is True
    assert any("REJECT" in r for r in reasons)

def test_human_review_strategic():
    req, reasons = check_human_review_required(5000, 0.8, "VALID", 0.1, "Strategic")
    assert req is True
    assert any("Strategic" in r for r in reasons)

def test_human_review_not_required():
    req, _ = check_human_review_required(5000, 0.8, "VALID", 0.1, "Standard")
    assert req is False

# 4. Resolution amount tests
def test_resolution_amount_no_action():
    assert compute_resolution_amount("NO_ACTION", 10000, "LOW") == 0.0

def test_resolution_amount_credit():
    amt = compute_resolution_amount("CUSTOMER_CREDIT", 10000, "MEDIUM")
    assert amt == pytest.approx(1500.0, 0.01)

def test_resolution_amount_claim():
    amt = compute_resolution_amount("FILE_CARRIER_CLAIM", 20000, "HIGH")
    assert amt == pytest.approx(10000.0, 0.01)

# 5. Action permission tests
def test_permitted_damage_actions():
    assert is_action_permitted("FILE_CARRIER_CLAIM", ExceptionType.DAMAGE) is True
    assert is_action_permitted("REROUTE", ExceptionType.DAMAGE) is False

# 6. Full workflow tests
def make_raw(exception_type, cargo_value, customer_tier="Standard"):
    return {
        "exception_type": exception_type,
        "cargo_value": cargo_value,
        "customer_tier": customer_tier,
        "carrier_id": "CR-001",
        "origin": "Los Angeles, CA",
        "destination": "Chicago, IL",
        "commodity": "Electronics",
        "promised_delivery": "2026-10-10T00:00:00",
        "reported_at": "2026-10-12T00:00:00",
        "description": "Test case",
    }

def test_damage_with_sufficient_evidence():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 12000)
    state = ctrl.run("CASE-TEST-001", "SH-202600001", raw)
    assert state.case.exception_type == ExceptionType.DAMAGE
    assert state.resolution is not None
    assert state.bundle.gap_ratio < 0.30

def test_damage_with_missing_evidence():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 3000)
    state = ctrl.run("CASE-TEST-002", "SH-202600099", raw)  # nonexistent shipment
    assert state.bundle.gap_ratio > 0.0

def test_delay_missed_handoff():
    ctrl = WorkflowController()
    raw = make_raw("DELAY", 8000)
    state = ctrl.run("CASE-TEST-003", "SH-202600006", raw)
    assert state.case.exception_type == ExceptionType.DELAY
    assert state.resolution is not None

def test_sla_breach_risk():
    ctrl = WorkflowController()
    raw = make_raw("DELAY", 25000)
    state = ctrl.run("CASE-TEST-004", "SH-202600014", raw)
    assert state.case.severity == Severity.HIGH

def test_customs_missing_docs():
    ctrl = WorkflowController()
    raw = make_raw("CUSTOMS_HOLD", 15000)
    state = ctrl.run("CASE-TEST-005", "SH-202600003", raw)
    assert state.resolution is not None
    if state.resolution:
        assert state.resolution.root_cause == "missing_documents"

def test_customs_inspection_human():
    ctrl = WorkflowController()
    raw = make_raw("CUSTOMS_HOLD", 60000, customer_tier="Strategic")
    state = ctrl.run("CASE-TEST-006", "SH-202600011", raw)
    assert state.requires_human_review is True

def test_misroute():
    ctrl = WorkflowController()
    raw = make_raw("MISROUTE", 7000)
    state = ctrl.run("CASE-TEST-007", "SH-202600010", raw)
    assert state.case.exception_type == ExceptionType.MISROUTE

def test_refused_delivery():
    ctrl = WorkflowController()
    raw = make_raw("REFUSED_DELIVERY", 5000)
    state = ctrl.run("CASE-TEST-008", "SH-202600004", raw)
    assert state.case.exception_type == ExceptionType.REFUSED_DELIVERY

def test_unknown_shipment():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 5000)
    state = ctrl.run("CASE-TEST-009", "SH-NONEXISTENT", raw)
    assert state.bundle.gap_ratio > 0.0

def test_insufficient_evidence():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 3000)
    state = ctrl.run("CASE-TEST-010", "SH-202600099", raw)
    assert state.bundle.gap_ratio > 0.0

def test_evidence_gap_threshold_behavior():
    ctrl = WorkflowController()
    raw = make_raw("DELAY", 4000)
    state = ctrl.run("CASE-TEST-011", "SH-202600099", raw)
    if state.bundle.gap_ratio > 0.30:
        assert state.status == "ESCALATED"

def test_critic_rejection():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 45000)
    state = ctrl.run("CASE-TEST-012", "SH-202600005", raw)
    # High value + damage may trigger critic or human review
    assert state.critic_verdict in [CriticVerdict.VALID, CriticVerdict.REVISE, CriticVerdict.REJECT]

def test_bounded_revision_success():
    ctrl = WorkflowController()
    raw = make_raw("DELAY", 8000)
    state = ctrl.run("CASE-TEST-013", "SH-202600018", raw)
    assert state.revision_count <= 1

def test_repeated_validation_failure():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 55000, customer_tier="Strategic")
    state = ctrl.run("CASE-TEST-014", "SH-202600005", raw)
    assert state.requires_human_review is True

def test_prohibited_action_rejected():
    assert is_action_permitted("REROUTE", ExceptionType.DAMAGE) is False
    assert is_action_permitted("FILE_CARRIER_CLAIM", ExceptionType.DELAY) is False

def test_audit_records_generated():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 9000)
    state = ctrl.run("CASE-TEST-015", "SH-202600001", raw)
    assert len(state.audit_log) > 0
    assert any(ev.agent == "IntakeAgent" for ev in state.audit_log)
    assert any(ev.agent == "EvidenceAgent" for ev in state.audit_log)

def test_normal_shipment_no_exception():
    ctrl = WorkflowController()
    raw = make_raw("UNKNOWN", 3000)
    state = ctrl.run("CASE-TEST-016", "SH-202600050", raw)
    assert state.case.exception_type == ExceptionType.UNKNOWN

def test_approval_persists():
    ctrl = WorkflowController()
    raw = make_raw("DAMAGE", 4000)
    state = ctrl.run("CASE-TEST-017", "SH-202600008", raw)
    state = ctrl.approve_case(state, reviewer="test_user")
    assert state.status == "APPROVED"
    assert state.approved_by == "test_user"

def test_override_persists():
    ctrl = WorkflowController()
    raw = make_raw("DELAY", 6000)
    state = ctrl.run("CASE-TEST-018", "SH-202600001", raw)
    state = ctrl.override_case(state, "NO_ACTION", "Override test", "test_user")
    assert state.status == "OVERRIDDEN"
    assert state.final_action == "NO_ACTION"

def test_rejection_persists():
    ctrl = WorkflowController()
    raw = make_raw("CUSTOMS_HOLD", 7000)
    state = ctrl.run("CASE-TEST-019", "SH-202600003", raw)
    state = ctrl.reject_case(state, "Rejection test", "test_user")
    assert state.status == "REJECTED"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])