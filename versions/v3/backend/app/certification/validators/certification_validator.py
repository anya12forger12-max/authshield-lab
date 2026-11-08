"""Certification validators: pre-flight checks for certification operations."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone

from ..domain.entities.certification_center import CertificationStatus, PlatformCertification
from ..domain.entities.operations import ModuleInventory
from ..domain.entities.sustainability import DependencyLifecycle
from ..domain.entities.release_engineering import ReleasePlan, ReleasePhase
from ..domain.entities.disaster_recovery import BackupValidation, RestoreTest


@dataclass
class ValidationResult:
    """A single validation outcome."""

    check: str = ""
    passed: bool = True
    message: str = ""


@dataclass
class CertificationValidationReport:
    """Aggregated validator report."""

    valid: bool = True
    checks: list[ValidationResult] = field(default_factory=list)

    def add(self, check: str, passed: bool, message: str = "") -> None:
        """Append a check result."""
        self.checks.append(ValidationResult(check=check, passed=passed, message=message))
        if not passed:
            self.valid = False

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "valid": self.valid,
            "checks": [
                {"check": c.check, "passed": c.passed, "message": c.message}
                for c in self.checks
            ],
        }


class CertificationValidator:
    """Pre-flight validation for certification workflows."""

    def validate_certification_can_start(self, cert: PlatformCertification) -> CertificationValidationReport:
        """Check whether a certification can transition to in_progress."""
        report = CertificationValidationReport()
        if cert.status != CertificationStatus.PENDING:
            report.add(
                "status_check",
                False,
                f"Cannot start certification in '{cert.status.value}' state",
            )
        else:
            report.add("status_check", True, "Certification is in pending state")

        if not cert.name:
            report.add("name_check", False, "Certification name is empty")
        else:
            report.add("name_check", True, "Name is present")

        if not cert.cert_type:
            report.add("type_check", False, "Certification type is not set")
        else:
            report.add("type_check", True, "Type is set")
        return report

    def validate_certification_can_be_approved(
        self,
        cert: PlatformCertification,
        requirements_met: int,
        requirements_total: int,
    ) -> CertificationValidationReport:
        """Check whether a certification meets all criteria for approval."""
        report = CertificationValidationReport()
        if cert.status not in (CertificationStatus.PENDING, CertificationStatus.IN_PROGRESS):
            report.add(
                "status_check",
                False,
                f"Cannot approve certification in '{cert.status.value}' state",
            )
        else:
            report.add("status_check", True, "Status allows approval")

        if requirements_total > 0 and requirements_met < requirements_total:
            report.add(
                "requirements_check",
                False,
                f"Only {requirements_met}/{requirements_total} requirements are met",
            )
        elif requirements_total == 0:
            report.add("requirements_check", False, "No requirements defined")
        else:
            report.add(
                "requirements_check",
                True,
                f"All {requirements_total} requirements are met",
            )

        if not cert.evidence:
            report.add("evidence_check", False, "No evidence has been provided")
        else:
            report.add(
                "evidence_check",
                True,
                f"{len(cert.evidence)} evidence items provided",
            )
        return report

    def validate_module_inventory(self, module: ModuleInventory) -> CertificationValidationReport:
        """Validate that a module inventory entry is complete."""
        report = CertificationValidationReport()
        if not module.name:
            report.add("name_check", False, "Module name is empty")
        else:
            report.add("name_check", True, "Name is present")

        if not module.version:
            report.add("version_check", False, "Module version is empty")
        else:
            report.add("version_check", True, f"Version {module.version}")

        if not module.enabled:
            report.add("enabled_check", False, "Module is disabled")
        else:
            report.add("enabled_check", True, "Module is enabled")
        return report

    def validate_dependency_health(self, dep: DependencyLifecycle) -> CertificationValidationReport:
        """Validate that a dependency is in good health for certification."""
        report = CertificationValidationReport()
        if dep.status.value == "end_of_life":
            report.add(
                "status_check",
                False,
                f"Dependency '{dep.name}' is end-of-life",
            )
        elif dep.status.value == "deprecated":
            report.add(
                "status_check",
                False,
                f"Dependency '{dep.name}' is deprecated",
            )
        else:
            report.add("status_check", True, f"Dependency '{dep.name}' is supported")

        if dep.update_available:
            report.add(
                "update_check",
                False,
                f"Update available: {dep.latest_version}",
            )
        else:
            report.add("update_check", True, "Dependency is up to date")
        return report

    def validate_release_plan(self, plan: ReleasePlan) -> CertificationValidationReport:
        """Validate that a release plan is ready for certification."""
        report = CertificationValidationReport()
        if plan.status in (ReleasePhase.PLANNING, ReleasePhase.DEVELOPMENT):
            report.add(
                "phase_check",
                False,
                f"Release is still in '{plan.status.value}' phase",
            )
        else:
            report.add("phase_check", True, f"Release is in '{plan.status.value}' phase")

        if not plan.version:
            report.add("version_check", False, "Version string is empty")
        else:
            report.add("version_check", True, f"Version {plan.version}")
        return report

    def validate_backup_readiness(self, backups: list[BackupValidation]) -> CertificationValidationReport:
        """Validate that backups are healthy enough for certification."""
        report = CertificationValidationReport()
        if not backups:
            report.add("backup_check", False, "No backups validated")
            return report

        healthy = [b for b in backups if b.is_healthy()]
        if len(healthy) < len(backups):
            report.add(
                "backup_check",
                False,
                f"{len(backups) - len(healthy)}/{len(backups)} backups are unhealthy",
            )
        else:
            report.add("backup_check", True, f"All {len(backups)} backups are healthy")
        return report

    def validate_restore_readiness(self, tests: list[RestoreTest]) -> CertificationValidationReport:
        """Validate that recent restore tests have succeeded."""
        report = CertificationValidationReport()
        if not tests:
            report.add("restore_check", False, "No restore tests have been run")
            return report

        successes = [t for t in tests if t.status == "success"]
        if not successes:
            report.add("restore_check", False, "No successful restore tests")
        else:
            rate = len(successes) / len(tests) * 100.0
            report.add(
                "restore_check",
                rate >= 80.0,
                f"Restore success rate: {rate:.0f}%",
            )
        return report

    def validate_full_certification_readiness(
        self,
        cert: PlatformCertification,
        modules: list[ModuleInventory],
        dependencies: list[DependencyLifecycle],
        backups: list[BackupValidation],
        restore_tests: list[RestoreTest],
        requirements_met: int,
        requirements_total: int,
    ) -> CertificationValidationReport:
        """Run all validators and produce a combined report."""
        combined = CertificationValidationReport()

        start = self.validate_certification_can_start(cert)
        for c in start.checks:
            combined.add(c.check, c.passed, c.message)

        approval = self.validate_certification_can_be_approved(
            cert, requirements_met, requirements_total
        )
        for c in approval.checks:
            combined.add(c.check, c.passed, c.message)

        for mod in modules:
            mod_report = self.validate_module_inventory(mod)
            for c in mod_report.checks:
                combined.add(f"module.{mod.name}.{c.check}", c.passed, c.message)

        for dep in dependencies:
            dep_report = self.validate_dependency_health(dep)
            for c in dep_report.checks:
                combined.add(f"dep.{dep.name}.{c.check}", c.passed, c.message)

        backup_report = self.validate_backup_readiness(backups)
        for c in backup_report.checks:
            combined.add(c.check, c.passed, c.message)

        restore_report = self.validate_restore_readiness(restore_tests)
        for c in restore_report.checks:
            combined.add(c.check, c.passed, c.message)

        return combined
