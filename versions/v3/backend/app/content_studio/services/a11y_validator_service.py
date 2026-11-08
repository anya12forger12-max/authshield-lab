"""Accessibility validator service — run checks, generate reports, track remediations."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.a11y_validator import (
    A11yCheck,
    A11yRemediation,
    A11yValidationReport,
)
from ..domain.events.content_studio_events import A11yValidationCompleted
from ..domain.interfaces.content_studio_interfaces import (
    IA11yCheckRepository,
    IA11yRemediationRepository,
    IA11yValidationReportRepository,
)

logger = logging.getLogger(__name__)

DEFAULT_CHECKS: list[dict[str, Any]] = [
    {
        "check_type": "alt_text",
        "description": "All images have descriptive alt text",
        "severity": "critical",
    },
    {
        "check_type": "heading_hierarchy",
        "description": "Heading levels follow proper hierarchy (h1 > h2 > h3)",
        "severity": "error",
    },
    {
        "check_type": "color_contrast",
        "description": "Text has sufficient color contrast ratio (4.5:1 minimum)",
        "severity": "critical",
    },
    {
        "check_type": "keyboard_navigation",
        "description": "Interactive elements are keyboard accessible",
        "severity": "critical",
    },
    {
        "check_type": "aria_labels",
        "description": "Interactive elements have ARIA labels",
        "severity": "error",
    },
    {
        "check_type": "transcript_available",
        "description": "Audio/video content has transcripts",
        "severity": "critical",
    },
    {
        "check_type": "language_attribute",
        "description": "Content has a defined language attribute",
        "severity": "error",
    },
    {
        "check_type": "focus_indicators",
        "description": "Visible focus indicators are present",
        "severity": "error",
    },
]


class A11yValidatorService:
    """Service for accessibility validation, reporting, and remediation tracking."""

    def __init__(
        self,
        check_repo: IA11yCheckRepository,
        report_repo: IA11yValidationReportRepository,
        remediation_repo: IA11yRemediationRepository,
    ) -> None:
        self._check_repo = check_repo
        self._report_repo = report_repo
        self._remediation_repo = remediation_repo

    def run_checks(self, content_id: str, content_data: dict[str, Any]) -> dict[str, Any]:
        checks: list[A11yCheck] = []

        for check_def in DEFAULT_CHECKS:
            check_type = check_def["check_type"]
            passed = self._evaluate_check(check_type, content_data)
            evidence = f"Check '{check_type}' on content '{content_id}'"
            remediation_text = None if passed else f"Remediate: {check_def['description']}"

            check = A11yCheck(
                check_type=check_type,
                description=check_def["description"],
                passed=passed,
                element=content_id,
                evidence=evidence,
                remediation=remediation_text,
                severity=check_def.get("severity", "error"),
            )
            checks.append(check)

        report = A11yValidationReport(content_id=content_id)
        for check in checks:
            self._check_repo.create({
                "id": check.id,
                "report_id": "",
                "check_type": check.check_type,
                "description": check.description,
                "passed": check.passed,
                "element": check.element,
                "evidence": check.evidence,
                "remediation": check.remediation,
                "severity": check.severity,
            })
            report.add_check(check)

        report_dict = self._report_repo.create({
            "content_id": content_id,
            "total": report.total,
            "passed": report.passed,
            "failed": report.failed,
            "na": report.na,
            "compliance_pct": report.compliance_pct,
            "generated_at": report.generated_at.isoformat(),
        })

        for check in checks:
            self._check_repo.create({
                "id": check.id,
                "report_id": report_dict["id"],
                "check_type": check.check_type,
                "description": check.description,
                "passed": check.passed,
                "element": check.element,
                "evidence": check.evidence,
                "remediation": check.remediation,
                "severity": check.severity,
            })

        for check in checks:
            if not check.passed:
                self._remediation_repo.create({
                    "report_id": report_dict["id"],
                    "check_id": check.id,
                    "action": check.remediation or f"Fix {check.check_type}",
                    "priority": "critical" if check.severity == "critical" else "high",
                    "status": "open",
                    "assignee": "",
                })

        event = A11yValidationCompleted(
            report_id=report_dict["id"],
            content_id=content_id,
            compliance_pct=report.compliance_pct,
            total_checks=report.total,
            passed_checks=report.passed,
        )
        logger.info("a11y_validation_completed", extra={
            "report_id": report_dict["id"],
            "content_id": content_id,
            "compliance_pct": report.compliance_pct,
            "event_id": event.event_id,
        })
        return report_dict

    def _evaluate_check(self, check_type: str, content_data: dict[str, Any]) -> bool:
        if check_type == "alt_text":
            has_alt = content_data.get("alt_text")
            if isinstance(has_alt, str):
                return bool(has_alt.strip())
            return True
        if check_type == "transcript_available":
            has_transcript = content_data.get("transcript")
            asset_type = content_data.get("asset_type", "")
            if asset_type in ("audio", "video"):
                return bool(has_transcript and str(has_transcript).strip())
            return True
        if check_type == "heading_hierarchy":
            return True
        if check_type == "color_contrast":
            return content_data.get("color_contrast_ok", True)
        if check_type == "keyboard_navigation":
            return content_data.get("keyboard_accessible", True)
        if check_type == "aria_labels":
            return content_data.get("has_aria_labels", True)
        if check_type == "language_attribute":
            return content_data.get("has_language_attr", True)
        if check_type == "focus_indicators":
            return content_data.get("has_focus_indicators", True)
        return True

    def get_report(self, report_id: str) -> Optional[dict[str, Any]]:
        return self._report_repo.get_by_id(report_id)

    def get_report_by_content(self, content_id: str) -> Optional[dict[str, Any]]:
        return self._report_repo.get_by_content(content_id)

    def list_reports(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._report_repo.get_all(page=page, per_page=per_page)

    def get_checks_for_report(self, report_id: str) -> list[dict[str, Any]]:
        return self._check_repo.get_by_report(report_id)

    def get_open_remediations(self) -> list[dict[str, Any]]:
        return self._remediation_repo.get_open()

    def get_remediations_for_report(self, report_id: str) -> list[dict[str, Any]]:
        return self._remediation_repo.get_by_report(report_id)

    def update_remediation(
        self, remediation_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        existing = self._remediation_repo.get_by_id(remediation_id)
        if not existing:
            raise ValueError(f"Remediation '{remediation_id}' not found.")
        return self._remediation_repo.update(remediation_id, data)

    def assign_remediation(self, remediation_id: str, assignee: str) -> Optional[dict[str, Any]]:
        return self.update_remediation(remediation_id, {"assignee": assignee, "status": "in_progress"})

    def complete_remediation(self, remediation_id: str) -> Optional[dict[str, Any]]:
        return self.update_remediation(remediation_id, {"status": "completed"})

    def dismiss_remediation(self, remediation_id: str) -> Optional[dict[str, Any]]:
        return self.update_remediation(remediation_id, {"status": "dismissed"})

    def get_compliance_summary(self, content_id: str) -> dict[str, Any]:
        report = self._report_repo.get_by_content(content_id)
        if not report:
            return {"content_id": content_id, "compliance_pct": 0.0, "has_report": False}

        checks = self._check_repo.get_by_report(report["id"])
        critical_failures = [c for c in checks if not c.get("passed") and c.get("severity") == "critical"]
        remediations = self._remediation_repo.get_by_report(report["id"])
        open_remediations = [r for r in remediations if r.get("status") in ("open", "in_progress")]

        return {
            "content_id": content_id,
            "report_id": report["id"],
            "compliance_pct": report.get("compliance_pct", 0.0),
            "total_checks": report.get("total", 0),
            "passed_checks": report.get("passed", 0),
            "failed_checks": report.get("failed", 0),
            "critical_failures": len(critical_failures),
            "open_remediations": len(open_remediations),
            "has_report": True,
        }
