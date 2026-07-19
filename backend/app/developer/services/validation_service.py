"""Validation service for extensions, templates, packages, and compatibility."""

from __future__ import annotations

from datetime import datetime, timezone

from app.developer.domain.entities.validation import (
    ValidationReport,
    ValidationResult,
    ValidationRule,
)


class ValidationService:
    """Runs validation rules against various target types and produces reports."""

    def __init__(self) -> None:
        self._rules: dict[str, ValidationRule] = {}
        self._results: dict[str, ValidationResult] = {}
        self._reports: dict[str, ValidationReport] = {}

    # -- Rule management -----------------------------------------------------

    def create_rule(
        self,
        name: str,
        rule_type: str = "schema",
        description: str = "",
        severity: str = "error",
        check_fn: str = "",
    ) -> ValidationRule:
        """Create and register a validation rule."""
        rule = ValidationRule(
            name=name,
            rule_type=rule_type,
            description=description,
            severity=severity,
            check_fn=check_fn,
        )
        self._rules[rule.id] = rule
        return rule

    def get_rule(self, rule_id: str) -> ValidationRule | None:
        """Retrieve a rule by ID."""
        return self._rules.get(rule_id)

    def list_rules(self) -> list[ValidationRule]:
        """Return all registered rules."""
        return list(self._rules.values())

    def list_rules_by_type(self, rule_type: str) -> list[ValidationRule]:
        """Return rules filtered by type."""
        return [r for r in self._rules.values() if r.rule_type == rule_type]

    def delete_rule(self, rule_id: str) -> bool:
        """Remove a rule."""
        if rule_id in self._rules:
            del self._rules[rule_id]
            return True
        return False

    # -- Validation execution ------------------------------------------------

    def validate_extension(self, extension_data: dict) -> ValidationReport:
        """Validate extension data against all registered extension rules."""
        target_id = extension_data.get("id", "unknown")
        rules = self.list_rules_by_type("extension")
        if not rules:
            rules = [r for r in self._rules.values() if r.rule_type in ("schema", "extension")]
        return self._run_rules(target_id, "extension", extension_data, rules)

    def validate_template(self, template_data: dict) -> ValidationReport:
        """Validate template data against registered rules."""
        target_id = template_data.get("id", "unknown")
        rules = self.list_rules_by_type("template")
        if not rules:
            rules = [r for r in self._rules.values() if r.rule_type in ("schema", "template")]
        return self._run_rules(target_id, "template", template_data, rules)

    def validate_package(self, package_data: dict) -> ValidationReport:
        """Validate package data against registered rules."""
        target_id = package_data.get("id", "unknown")
        rules = self.list_rules_by_type("package")
        if not rules:
            rules = [r for r in self._rules.values() if r.rule_type in ("schema", "package")]
        return self._run_rules(target_id, "package", package_data, rules)

    def validate_compatibility(
        self,
        source_version: str,
        target_version: str,
        source_type: str = "generic",
    ) -> ValidationReport:
        """Validate version compatibility between source and target."""
        report = ValidationReport(
            name=f"compatibility:{source_type}",
            target_type="compatibility",
            generated_at=datetime.now(timezone.utc),
        )
        source_parts = [int(p) for p in source_version.split(".")]
        target_parts = [int(p) for p in target_version.split(".")]
        major_compatible = source_parts[0] <= target_parts[0]
        result = ValidationResult(
            rule_id="compat-check",
            target_id=f"{source_version}->{target_version}",
            target_type="compatibility",
            passed=major_compatible,
            message=(
                "Major version is compatible"
                if major_compatible
                else "Major version mismatch"
            ),
        )
        report.add_result(result)
        report.compute_score()
        report.compute_overall_status()
        self._reports[report.id] = report
        return report

    def validate_custom(
        self,
        target_id: str,
        target_type: str,
        data: dict,
        rule_ids: list[str] | None = None,
    ) -> ValidationReport:
        """Run a custom set of rules against arbitrary data."""
        if rule_ids is not None:
            rules = [self._rules[rid] for rid in rule_ids if rid in self._rules]
        else:
            rules = list(self._rules.values())
        return self._run_rules(target_id, target_type, data, rules)

    # -- Internal helpers ----------------------------------------------------

    def _run_rules(
        self,
        target_id: str,
        target_type: str,
        data: dict,
        rules: list[ValidationRule],
    ) -> ValidationReport:
        """Execute rules against data and build a report."""
        report = ValidationReport(
            name=f"{target_type}:{target_id}",
            target_type=target_type,
            generated_at=datetime.now(timezone.utc),
        )
        for rule in rules:
            passed = self._evaluate_rule(rule, data)
            result = ValidationResult(
                rule_id=rule.id,
                target_id=target_id,
                target_type=target_type,
                passed=passed,
                message=f"Rule '{rule.name}' {'passed' if passed else 'failed'}",
            )
            report.add_result(result)
            self._results[result.id] = result
        report.compute_score()
        report.compute_overall_status()
        self._reports[report.id] = report
        return report

    def _evaluate_rule(self, rule: ValidationRule, data: dict) -> bool:
        """Evaluate a single rule against data (built-in checks)."""
        check = rule.check_fn
        if check == "has_name":
            return bool(data.get("name"))
        if check == "has_version":
            return bool(data.get("version"))
        if check == "has_author":
            return bool(data.get("author"))
        if check == "has_description":
            return bool(data.get("description"))
        if check == "has_checksum":
            return bool(data.get("checksum"))
        if check == "version_format":
            version = data.get("version", "")
            parts = version.split(".")
            return len(parts) == 3 and all(p.isdigit() for p in parts)
        if check == "non_empty":
            return bool(data)
        if check == "always_pass":
            return True
        if check == "always_fail":
            return False
        return True

    # -- Report management ---------------------------------------------------

    def get_report(self, report_id: str) -> ValidationReport | None:
        """Retrieve a report by ID."""
        return self._reports.get(report_id)

    def list_reports(self) -> list[ValidationReport]:
        """Return all validation reports."""
        return list(self._reports.values())

    def list_reports_by_target(self, target_type: str) -> list[ValidationReport]:
        """Return reports filtered by target type."""
        return [r for r in self._reports.values() if r.target_type == target_type]

    def delete_report(self, report_id: str) -> bool:
        """Remove a report."""
        if report_id in self._reports:
            del self._reports[report_id]
            return True
        return False
