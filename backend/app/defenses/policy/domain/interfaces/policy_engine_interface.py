"""Policy engine interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional

from ..entities.policy_entity import PolicyCategory, PolicyDecision, PolicyStatus, SecurityPolicy
from ..entities.rule_entity import SecurityRule


class IPolicyEngine(ABC):
    """Interface for the central policy evaluation engine."""

    @abstractmethod
    async def evaluate(
        self, event_type: str, context: dict[str, Any], correlation_id: str = ""
    ) -> list[PolicyDecision]:
        """Evaluate an event against all applicable policies.

        Parameters
        ----------
        event_type:
            The type of event being evaluated.
        context:
            Contextual data for the evaluation.
        correlation_id:
            Optional correlation ID for distributed tracing.
        """
        ...

    @abstractmethod
    async def register_policy(self, policy: SecurityPolicy) -> bool:
        """Register a new policy with the engine."""
        ...

    @abstractmethod
    async def unregister_policy(self, policy_id: str) -> bool:
        """Remove a policy from the engine."""
        ...

    @abstractmethod
    async def enable_policy(self, policy_id: str) -> bool:
        """Enable a policy."""
        ...

    @abstractmethod
    async def disable_policy(self, policy_id: str) -> bool:
        """Disable a policy."""
        ...

    @abstractmethod
    async def get_policy(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Return a policy by ID, or ``None``."""
        ...

    @abstractmethod
    async def list_policies(
        self,
        category: Optional[PolicyCategory] = None,
        status: Optional[PolicyStatus] = None,
    ) -> list[SecurityPolicy]:
        """Return all policies, optionally filtered."""
        ...

    @abstractmethod
    async def update_policy(
        self, policy_id: str, data: dict[str, Any]
    ) -> Optional[SecurityPolicy]:
        """Update a policy's configuration."""
        ...

    @abstractmethod
    def get_metrics(self) -> dict[str, Any]:
        """Return engine evaluation metrics."""
        ...


class IRuleEngine(ABC):
    """Interface for the rule evaluation engine."""

    @abstractmethod
    async def evaluate_rules(
        self, rules: list[SecurityRule], context: dict[str, Any]
    ) -> list[tuple[SecurityRule, bool, list]]:
        """Evaluate a set of rules against the context.

        Returns a list of ``(rule, all_conditions_met, matching_actions)``
        tuples.
        """
        ...

    @abstractmethod
    async def add_rule(self, rule: SecurityRule) -> bool:
        """Add a rule to the engine."""
        ...

    @abstractmethod
    async def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID."""
        ...

    @abstractmethod
    async def get_rule(self, rule_id: str) -> Optional[SecurityRule]:
        """Return a rule by ID, or ``None``."""
        ...

    @abstractmethod
    async def list_rules(self, active_only: bool = True) -> list[SecurityRule]:
        """Return all rules, optionally filtered to active ones."""
        ...


class IPolicyRegistry(ABC):
    """Interface for the policy registry (storage and lookup)."""

    @abstractmethod
    async def register(self, policy: SecurityPolicy) -> bool:
        """Register a new policy."""
        ...

    @abstractmethod
    async def unregister(self, policy_id: str) -> bool:
        """Remove a policy."""
        ...

    @abstractmethod
    async def get(self, policy_id: str) -> Optional[SecurityPolicy]:
        """Return a policy by ID, or ``None``."""
        ...

    @abstractmethod
    async def get_all(self) -> list[SecurityPolicy]:
        """Return all registered policies."""
        ...

    @abstractmethod
    async def search(
        self,
        query: str,
        category: Optional[PolicyCategory] = None,
    ) -> list[SecurityPolicy]:
        """Search policies by name/description with optional category filter."""
        ...

    @abstractmethod
    async def enable(self, policy_id: str) -> bool:
        """Enable a policy."""
        ...

    @abstractmethod
    async def disable(self, policy_id: str) -> bool:
        """Disable a policy."""
        ...

    @abstractmethod
    async def export_policies(self) -> dict:
        """Export all policies as a serialisable dictionary."""
        ...

    @abstractmethod
    async def import_policies(self, data: dict) -> int:
        """Import policies from a previously exported dictionary.

        Returns the number of policies imported.
        """
        ...
