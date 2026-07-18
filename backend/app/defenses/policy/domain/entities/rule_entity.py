"""Rule entity for the rule processing engine."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class RuleExecutionMode(str, Enum):
    """Controls how a rule's conditions are evaluated."""

    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    SHORT_CIRCUIT = "short_circuit"


class RuleCondition(str, Enum):
    """Supported comparison operators for rule condition clauses."""

    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    GREATER_THAN = "greater_than"
    LESS_THAN = "less_than"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    IN_LIST = "in_list"
    NOT_IN_LIST = "not_in_list"
    REGEX_MATCH = "regex_match"
    ALWAYS_TRUE = "always_true"


@dataclass
class RuleConditionClause:
    """A single condition within a rule."""

    field_name: str = ""
    operator: RuleCondition = RuleCondition.ALWAYS_TRUE
    value: Any = None

    def evaluate(self, context: dict[str, Any]) -> bool:
        """Evaluate this clause against the supplied context.

        Parameters
        ----------
        context:
            The evaluation context dictionary.  Field values are resolved
            from this dictionary using ``field_name`` as the key.

        Returns
        -------
        bool
            ``True`` if the condition is satisfied.
        """
        if self.operator == RuleCondition.ALWAYS_TRUE:
            return True

        field_value = context.get(self.field_name)

        if self.operator == RuleCondition.EQUALS:
            return field_value == self.value

        if self.operator == RuleCondition.NOT_EQUALS:
            return field_value != self.value

        if self.operator == RuleCondition.GREATER_THAN:
            try:
                return float(field_value or 0) > float(self.value)
            except (TypeError, ValueError):
                return False

        if self.operator == RuleCondition.LESS_THAN:
            try:
                return float(field_value or 0) < float(self.value)
            except (TypeError, ValueError):
                return False

        if self.operator == RuleCondition.CONTAINS:
            if isinstance(field_value, str) and isinstance(self.value, str):
                return self.value in field_value
            if isinstance(field_value, (list, set)):
                return self.value in field_value
            return False

        if self.operator == RuleCondition.NOT_CONTAINS:
            if isinstance(field_value, str) and isinstance(self.value, str):
                return self.value not in field_value
            if isinstance(field_value, (list, set)):
                return self.value not in field_value
            return True

        if self.operator == RuleCondition.IN_LIST:
            if isinstance(self.value, (list, set)):
                return field_value in self.value
            return False

        if self.operator == RuleCondition.NOT_IN_LIST:
            if isinstance(self.value, (list, set)):
                return field_value not in self.value
            return True

        if self.operator == RuleCondition.REGEX_MATCH:
            if isinstance(field_value, str) and isinstance(self.value, str):
                import re
                try:
                    return bool(re.search(self.value, field_value))
                except re.error:
                    return False
            return False

        return False


@dataclass
class RuleAction:
    """An action to execute when a rule matches."""

    action_type: str = ""  # "block", "allow", "warn", "log", "monitor"
    parameters: dict[str, Any] = field(default_factory=dict)
    message: str = ""


@dataclass
class SecurityRule:
    """A configurable security rule with conditions and actions."""

    rule_id: str = ""
    name: str = ""
    description: str = ""
    priority: int = 100
    conditions: list[RuleConditionClause] = field(default_factory=list)
    actions: list[RuleAction] = field(default_factory=list)
    execution_mode: RuleExecutionMode = RuleExecutionMode.SEQUENTIAL
    metadata: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def evaluate(self, context: dict[str, Any]) -> tuple[bool, list[RuleAction]]:
        """Evaluate all conditions against the context.

        Parameters
        ----------
        context:
            The evaluation context dictionary.

        Returns
        -------
        tuple[bool, list[RuleAction]]
            A tuple of ``(all_conditions_met, matching_actions)``.  When
            all conditions are satisfied the returned actions are the
            rule's configured actions; otherwise an empty list is returned.
        """
        if not self.is_active or not self.conditions:
            return False, []

        if self.execution_mode == RuleExecutionMode.SHORT_CIRCUIT:
            for clause in self.conditions:
                if not clause.evaluate(context):
                    return False, []
            return True, list(self.actions)

        # SEQUENTIAL and PARALLEL both check ALL conditions
        all_met = all(clause.evaluate(context) for clause in self.conditions)
        if all_met:
            return True, list(self.actions)
        return False, []

    def to_dict(self) -> dict[str, Any]:
        """Serialize the rule to a plain dictionary."""
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "priority": self.priority,
            "conditions": [
                {
                    "field_name": c.field_name,
                    "operator": c.operator.value,
                    "value": c.value,
                }
                for c in self.conditions
            ],
            "actions": [
                {
                    "action_type": a.action_type,
                    "parameters": dict(a.parameters),
                    "message": a.message,
                }
                for a in self.actions
            ],
            "execution_mode": self.execution_mode.value,
            "metadata": dict(self.metadata),
            "version": self.version,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat(),
        }
