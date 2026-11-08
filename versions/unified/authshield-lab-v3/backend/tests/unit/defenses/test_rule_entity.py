"""Tests for SecurityRule and RuleConditionClause evaluation."""

import pytest
from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class RuleConditionClause:
    field_name: str = ""
    operator: str = "eq"
    value: Any = None

    def evaluate(self, context: dict) -> bool:
        actual = context.get(self.field_name)
        if actual is None:
            return False
        if self.operator == "eq":
            return actual == self.value
        elif self.operator == "neq":
            return actual != self.value
        elif self.operator == "gt":
            return actual > self.value
        elif self.operator == "gte":
            return actual >= self.value
        elif self.operator == "lt":
            return actual < self.value
        elif self.operator == "lte":
            return actual <= self.value
        elif self.operator == "contains":
            return self.value in actual
        elif self.operator == "in":
            return actual in self.value
        return False


@dataclass
class SecurityRule:
    rule_id: str = ""
    name: str = ""
    description: str = ""
    conditions: list[RuleConditionClause] = field(default_factory=list)
    action: str = "deny"
    priority: int = 0
    enabled: bool = True

    def evaluate(self, context: dict) -> bool:
        if not self.enabled:
            return True
        return all(c.evaluate(context) for c in self.conditions)

    def to_dict(self) -> dict:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "action": self.action,
            "priority": self.priority,
            "enabled": self.enabled,
            "condition_count": len(self.conditions),
        }


class TestRuleConditionClauseEq:
    def test_eq_match(self):
        clause = RuleConditionClause(field_name="status", operator="eq", value="active")
        assert clause.evaluate({"status": "active"}) is True

    def test_eq_no_match(self):
        clause = RuleConditionClause(field_name="status", operator="eq", value="active")
        assert clause.evaluate({"status": "locked"}) is False

    def test_eq_missing_field(self):
        clause = RuleConditionClause(field_name="missing", operator="eq", value="x")
        assert clause.evaluate({}) is False


class TestRuleConditionClauseComparison:
    def test_gt(self):
        clause = RuleConditionClause(field_name="count", operator="gt", value=5)
        assert clause.evaluate({"count": 10}) is True
        assert clause.evaluate({"count": 5}) is False

    def test_gte(self):
        clause = RuleConditionClause(field_name="count", operator="gte", value=5)
        assert clause.evaluate({"count": 5}) is True
        assert clause.evaluate({"count": 4}) is False

    def test_lt(self):
        clause = RuleConditionClause(field_name="count", operator="lt", value=5)
        assert clause.evaluate({"count": 3}) is True
        assert clause.evaluate({"count": 5}) is False

    def test_lte(self):
        clause = RuleConditionClause(field_name="count", operator="lte", value=5)
        assert clause.evaluate({"count": 5}) is True
        assert clause.evaluate({"count": 6}) is False

    def test_neq(self):
        clause = RuleConditionClause(field_name="status", operator="neq", value="locked")
        assert clause.evaluate({"status": "active"}) is True
        assert clause.evaluate({"status": "locked"}) is False


class TestRuleConditionClauseContainsAndIn:
    def test_contains(self):
        clause = RuleConditionClause(field_name="tags", operator="contains", value="admin")
        assert clause.evaluate({"tags": ["admin", "user"]}) is True
        assert clause.evaluate({"tags": ["user"]}) is False

    def test_in_operator(self):
        clause = RuleConditionClause(field_name="role", operator="in", value=["admin", "superadmin"])
        assert clause.evaluate({"role": "admin"}) is True
        assert clause.evaluate({"role": "user"}) is False


class TestSecurityRule:
    def test_no_conditions_always_matches(self):
        rule = SecurityRule(rule_id="r1", name="no-conditions")
        assert rule.evaluate({"anything": "goes"}) is True

    def test_all_conditions_must_match(self):
        rule = SecurityRule(
            conditions=[
                RuleConditionClause(field_name="role", operator="eq", value="admin"),
                RuleConditionClause(field_name="status", operator="eq", value="active"),
            ]
        )
        assert rule.evaluate({"role": "admin", "status": "active"}) is True
        assert rule.evaluate({"role": "admin", "status": "locked"}) is False

    def test_disabled_rule_always_matches(self):
        rule = SecurityRule(
            enabled=False,
            conditions=[RuleConditionClause(field_name="x", operator="eq", value="y")],
        )
        assert rule.evaluate({}) is True

    def test_to_dict(self):
        rule = SecurityRule(
            rule_id="r1",
            name="rate-limit",
            action="deny",
            priority=10,
            conditions=[RuleConditionClause(field_name="count", operator="gt", value=100)],
        )
        d = rule.to_dict()
        assert d["rule_id"] == "r1"
        assert d["name"] == "rate-limit"
        assert d["action"] == "deny"
        assert d["condition_count"] == 1
