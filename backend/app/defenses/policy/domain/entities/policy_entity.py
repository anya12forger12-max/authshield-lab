"""Security policy entity."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class PolicyStatus(str, Enum):
    """Lifecycle status of a security policy."""

    ENABLED = "enabled"
    DISABLED = "disabled"
    DRAFT = "draft"
    TESTING = "testing"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"
    UNKNOWN = "unknown"


class PolicyCategory(str, Enum):
    """Functional category for security policies."""

    AUTHENTICATION = "authentication"
    PASSWORD = "password"
    SESSION = "session"
    RISK = "risk"
    ACCOUNT = "account"
    DEVICE = "device"
    LOGGING = "logging"
    AUDIT = "audit"
    ACCESSIBILITY = "accessibility"
    CONFIGURATION = "configuration"


class PolicyDecisionResult(str, Enum):
    """Possible outcomes of a policy decision."""

    ALLOW = "allow"
    DENY = "deny"
    WARN = "warn"
    MONITOR = "monitor"
    IGNORE = "ignore"
    REVIEW = "review"
    UNKNOWN = "unknown"


@dataclass
class PolicyConfiguration:
    """Runtime configuration for a policy."""

    thresholds: dict[str, Any] = field(default_factory=dict)
    timing: dict[str, Any] = field(default_factory=dict)
    messages: dict[str, str] = field(default_factory=dict)
    logging_enabled: bool = True
    audit_enabled: bool = True
    metrics_enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Serialize the configuration to a plain dictionary."""
        return {
            "thresholds": dict(self.thresholds),
            "timing": dict(self.timing),
            "messages": dict(self.messages),
            "logging_enabled": self.logging_enabled,
            "audit_enabled": self.audit_enabled,
            "metrics_enabled": self.metrics_enabled,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PolicyConfiguration:
        """Deserialize a configuration from a plain dictionary."""
        return cls(
            thresholds=data.get("thresholds", {}),
            timing=data.get("timing", {}),
            messages=data.get("messages", {}),
            logging_enabled=data.get("logging_enabled", True),
            audit_enabled=data.get("audit_enabled", True),
            metrics_enabled=data.get("metrics_enabled", True),
        )


@dataclass
class SecurityPolicy:
    """Represents a single security policy in the system."""

    policy_id: str = ""
    name: str = ""
    description: str = ""
    version: int = 1
    category: PolicyCategory = PolicyCategory.AUTHENTICATION
    priority: int = 100
    status: PolicyStatus = PolicyStatus.DRAFT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    author: str = "system"
    configuration: PolicyConfiguration = field(default_factory=PolicyConfiguration)
    dependencies: list[str] = field(default_factory=list)
    execution_order: int = 0
    risk_weight: float = 1.0
    metadata: dict[str, Any] = field(default_factory=dict)
    supported_event_types: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize the policy to a plain dictionary."""
        return {
            "policy_id": self.policy_id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "category": self.category.value,
            "priority": self.priority,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "author": self.author,
            "configuration": self.configuration.to_dict(),
            "dependencies": list(self.dependencies),
            "execution_order": self.execution_order,
            "risk_weight": self.risk_weight,
            "metadata": dict(self.metadata),
            "supported_event_types": list(self.supported_event_types),
        }

    def is_usable(self) -> bool:
        """Return ``True`` if the policy is in an enabled state."""
        return self.status == PolicyStatus.ENABLED


@dataclass
class PolicyDecision:
    """Records the outcome of evaluating a single policy."""

    decision_id: str = ""
    policy_id: str = ""
    rule_id: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    result: PolicyDecisionResult = PolicyDecisionResult.UNKNOWN
    reason: str = ""
    severity: str = "info"
    risk_score: float = 0.0
    execution_time_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
    correlation_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize the decision to a plain dictionary."""
        return {
            "decision_id": self.decision_id,
            "policy_id": self.policy_id,
            "rule_id": self.rule_id,
            "timestamp": self.timestamp.isoformat(),
            "result": self.result.value,
            "reason": self.reason,
            "severity": self.severity,
            "risk_score": self.risk_score,
            "execution_time_ms": self.execution_time_ms,
            "metadata": dict(self.metadata),
            "correlation_id": self.correlation_id,
        }


# Valid status transitions for policies
VALID_STATUS_TRANSITIONS: dict[PolicyStatus, set[PolicyStatus]] = {
    PolicyStatus.DRAFT: {PolicyStatus.TESTING, PolicyStatus.ENABLED, PolicyStatus.ARCHIVED},
    PolicyStatus.TESTING: {PolicyStatus.ENABLED, PolicyStatus.DRAFT, PolicyStatus.DISABLED},
    PolicyStatus.ENABLED: {PolicyStatus.DISABLED, PolicyStatus.DEPRECATED},
    PolicyStatus.DISABLED: {PolicyStatus.ENABLED, PolicyStatus.ARCHIVED, PolicyStatus.DEPRECATED},
    PolicyStatus.DEPRECATED: {PolicyStatus.ARCHIVED, PolicyStatus.DISABLED},
    PolicyStatus.ARCHIVED: {PolicyStatus.DRAFT},
    PolicyStatus.UNKNOWN: {PolicyStatus.DRAFT, PolicyStatus.DISABLED},
}
