"""Policy domain event definitions."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class PolicyDomainEvent:
    """Base class for all policy domain events."""

    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    correlation_id: str = ""
    module: str = "defenses.policy"
    severity: str = "info"
    metadata: dict = field(default_factory=dict)


@dataclass
class PolicyRegisteredEvent(PolicyDomainEvent):
    """Published when a new policy is registered."""

    event_type: str = "policy.registered"
    policy_id: str = ""
    policy_name: str = ""
    category: str = ""


@dataclass
class PolicyEnabledEvent(PolicyDomainEvent):
    """Published when a policy is enabled."""

    event_type: str = "policy.enabled"
    policy_id: str = ""
    policy_name: str = ""


@dataclass
class PolicyDisabledEvent(PolicyDomainEvent):
    """Published when a policy is disabled."""

    event_type: str = "policy.disabled"
    policy_id: str = ""
    policy_name: str = ""
    reason: str = ""


@dataclass
class PolicyEvaluatedEvent(PolicyDomainEvent):
    """Published after a policy is evaluated against an event."""

    event_type: str = "policy.evaluated"
    policy_id: str = ""
    event_type_evaluated: str = ""
    result: str = ""
    execution_time_ms: float = 0.0


@dataclass
class PolicyDecisionEvent(PolicyDomainEvent):
    """Published when a policy produces a decision."""

    event_type: str = "policy.decision"
    policy_id: str = ""
    decision: str = ""
    reason: str = ""
    risk_score: float = 0.0


@dataclass
class RuleEvaluatedEvent(PolicyDomainEvent):
    """Published when a rule is evaluated."""

    event_type: str = "rule.evaluated"
    rule_id: str = ""
    rule_name: str = ""
    all_conditions_met: bool = False
    actions_count: int = 0
