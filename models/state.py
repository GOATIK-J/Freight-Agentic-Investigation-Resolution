"""Typed shared state for F.A.I.R. investigation workflow."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ExceptionType(Enum):
    DAMAGE = "DAMAGE"
    DELAY = "DELAY"
    CUSTOMS_HOLD = "CUSTOMS_HOLD"
    MISROUTE = "MISROUTE"
    REFUSED_DELIVERY = "REFUSED_DELIVERY"
    UNKNOWN = "UNKNOWN"


class Severity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CriticVerdict(Enum):
    VALID = "VALID"
    REVISE = "REVISE"
    REJECT = "REJECT"
    PENDING = "PENDING"


@dataclass
class FreightCase:
    case_id: str
    shipment_id: str
    exception_type: ExceptionType
    severity: Severity
    cargo_value: float
    customer_tier: str
    carrier_id: str
    origin: str
    destination: str
    commodity: str
    promised_delivery: str
    reported_at: str
    description: str
    investigation_budget: int = 0


@dataclass
class EvidencePlan:
    steps: list[str] = field(default_factory=list)
    tools_required: list[str] = field(default_factory=list)


@dataclass
class EvidenceItem:
    tool_name: str
    status: str  # RETRIEVED, MISSING, ERROR
    finding: str
    source: str
    timestamp: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class EvidenceBundle:
    items: list[EvidenceItem] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    gap_ratio: float = 0.0


@dataclass
class ProposedResolution:
    action: str
    amount: float
    rationale: str
    confidence: float
    root_cause: str
    policy_references: list[str] = field(default_factory=list)
    responsible_team: str = ""
    urgency: str = "NORMAL"


@dataclass
class AuditEvent:
    timestamp: str
    case_id: str
    agent: str
    event_type: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class InvestigationState:
    case: FreightCase
    plan: EvidencePlan = field(default_factory=EvidencePlan)
    bundle: EvidenceBundle = field(default_factory=EvidenceBundle)
    resolution: Optional[ProposedResolution] = None
    critic_verdict: CriticVerdict = CriticVerdict.PENDING
    critic_notes: str = ""
    requires_human_review: bool = False
    human_review_reasons: list[str] = field(default_factory=list)
    final_action: str = ""
    final_amount: float = 0.0
    approved_by: str = ""
    approval_timestamp: str = ""
    revision_count: int = 0
    audit_log: list[AuditEvent] = field(default_factory=list)
    status: str = "PENDING"  # PENDING, IN_PROGRESS, RESOLVED, ESCALATED, APPROVED, REJECTED
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "case_id": self.case.case_id,
            "shipment_id": self.case.shipment_id,
            "exception_type": self.case.exception_type.value,
            "severity": self.case.severity.value,
            "status": self.status,
            "resolution_action": self.resolution.action if self.resolution else None,
            "resolution_amount": self.resolution.amount if self.resolution else None,
            "confidence": self.resolution.confidence if self.resolution else None,
            "critic_verdict": self.critic_verdict.value,
            "requires_human_review": self.requires_human_review,
            "human_review_reasons": self.human_review_reasons,
            "revision_count": self.revision_count,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
        }