"""Deterministic policy, financial, and safeguard computations."""
from models.state import Severity, ExceptionType


SEVERITY_THRESHOLDS = {
    "LOW": (0, 5000),
    "MEDIUM": (5000, 15000),
    "HIGH": (15000, 50000),
    "CRITICAL": (50000, float("inf")),
}

BUDGET_MAP = {
    Severity.LOW: 5,
    Severity.MEDIUM: 8,
    Severity.HIGH: 10,
    Severity.CRITICAL: 12,
}

PERMITTED_ACTIONS = {
    ExceptionType.DAMAGE: ["NO_ACTION", "CUSTOMER_CREDIT", "FILE_CARRIER_CLAIM", "ESCALATE_TO_HUMAN"],
    ExceptionType.DELAY: ["NO_ACTION", "CUSTOMER_NOTIFICATION", "EXPEDITE_AND_CHARGE", "ESCALATE_TO_HUMAN"],
    ExceptionType.CUSTOMS_HOLD: ["NO_ACTION", "CUSTOMER_NOTIFICATION", "SUBMIT_CUSTOMS_DOCS", "ESCALATE_TO_HUMAN"],
    ExceptionType.MISROUTE: ["NO_ACTION", "CUSTOMER_NOTIFICATION", "REROUTE", "ESCALATE_TO_HUMAN"],
    ExceptionType.REFUSED_DELIVERY: ["NO_ACTION", "RETURN_TO_SHIPPER", "CUSTOMER_CREDIT", "ESCALATE_TO_HUMAN"],
    ExceptionType.UNKNOWN: ["ESCALATE_TO_HUMAN"],
}


def compute_severity(cargo_value: float) -> Severity:
    """Compute severity based on cargo value thresholds."""
    if cargo_value < 5000:
        return Severity.LOW
    elif cargo_value < 15000:
        return Severity.MEDIUM
    elif cargo_value < 50000:
        return Severity.HIGH
    else:
        return Severity.CRITICAL


def compute_investigation_budget(severity: Severity) -> int:
    """Return tool-call budget for severity tier."""
    return BUDGET_MAP.get(severity, 5)


def compute_evidence_gap_ratio(expected: int, missing: int) -> float:
    """Calculate evidence gap ratio; returns 0.0 if no expected evidence."""
    if expected <= 0:
        return 0.0
    return min(1.0, missing / expected)


def compute_liability_cap(cargo_value: float, customer_tier: str) -> float:
    """Compute maximum permitted resolution amount."""
    tier_multiplier = {"Standard": 0.5, "Premium": 0.75, "Strategic": 1.0}
    mult = tier_multiplier.get(customer_tier, 0.5)
    cap = cargo_value * mult
    return min(cap, 50000.0)


def check_human_review_required(
    proposed_amount: float,
    confidence: float,
    critic_verdict: str,
    evidence_gap_ratio: float,
    customer_tier: str,
) -> tuple[bool, list[str]]:
    """Check if case requires human review; return (required, reasons)."""
    reasons = []
    if proposed_amount > 10000:
        reasons.append("Proposed amount exceeds $10,000 threshold")
    if confidence < 0.7:
        reasons.append("Confidence below 0.7 threshold")
    if critic_verdict == "REJECT":
        reasons.append("Critic returned REJECT verdict")
    if evidence_gap_ratio > 0.30:
        reasons.append("Evidence gaps exceed 30% threshold")
    if customer_tier == "Strategic":
        reasons.append("Customer tier is Strategic")
    return len(reasons) > 0, reasons


def compute_resolution_amount(action: str, cargo_value: float, severity: str) -> float:
    """Deterministic resolution amount calculator."""
    if action in ["NO_ACTION", "CUSTOMER_NOTIFICATION", "ESCALATE_TO_HUMAN", "SUBMIT_CUSTOMS_DOCS", "REROUTE"]:
        return 0.0
    if action == "CUSTOMER_CREDIT":
        return min(cargo_value * 0.15, 2500.0)
    if action == "FILE_CARRIER_CLAIM":
        return min(cargo_value * 0.5, 15000.0)
    if action == "EXPEDITE_AND_CHARGE":
        return min(cargo_value * 0.1, 5000.0)
    if action == "RETURN_TO_SHIPPER":
        return min(cargo_value * 0.25, 8000.0)
    return 0.0


def is_action_permitted(action: str, exception_type: ExceptionType) -> bool:
    """Check if resolution action is permitted for exception type."""
    permitted = PERMITTED_ACTIONS.get(exception_type, [])
    return action in permitted