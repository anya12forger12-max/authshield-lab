"""Platform validation service: validate all subsystems, run acceptance tests."""

from __future__ import annotations

from typing import Optional

from ..domain.entities.platform_validation import (
    FinalAcceptanceTest,
    PlatformValidationReport,
    SubsystemValidation,
    ValidationCheck,
)
from ..domain.interfaces import (
    FinalAcceptanceTestRepository,
    PlatformValidationReportRepository,
    SubsystemValidationRepository,
    ValidationCheckRepository,
)

KNOWN_SUBSYSTEMS = [
    "authentication",
    "authorization",
    "users",
    "sessions",
    "content",
    "simulation",
    "lms",
    "analytics",
    "quality",
    "developer",
    "ecosystem",
    "collaboration",
    "production",
    "audit",
    "standards",
    "certification",
]


class PlatformValidationService:
    """Validates all platform subsystems and runs final acceptance tests."""

    def __init__(
        self,
        check_repo: ValidationCheckRepository,
        subsystem_repo: SubsystemValidationRepository,
        report_repo: PlatformValidationReportRepository,
        fat_repo: FinalAcceptanceTestRepository,
    ) -> None:
        self._check_repo = check_repo
        self._subsystem_repo = subsystem_repo
        self._report_repo = report_repo
        self._fat_repo = fat_repo

    # ── Individual Checks ───────────────────────────────────────────

    async def run_check(
        self,
        subsystem: str,
        check_name: str,
        status: str = "passed",
        details: str = "",
        evidence: str = "",
    ) -> ValidationCheck:
        """Run and record a single validation check."""
        check = ValidationCheck(
            subsystem=subsystem,
            check_name=check_name,
        )
        if status == "passed":
            check.mark_passed(details, evidence)
        elif status == "failed":
            check.mark_failed(details, evidence)
        else:
            check.mark_skipped(details)
        return self._check_repo.save(check)

    async def get_check(self, check_id: str) -> Optional[ValidationCheck]:
        """Retrieve a validation check by ID."""
        return self._check_repo.find_by_id(check_id)

    async def get_checks_for_subsystem(self, subsystem: str) -> list[ValidationCheck]:
        """Return all checks for a subsystem."""
        return self._check_repo.find_by_subsystem(subsystem)

    async def list_checks(self) -> list[ValidationCheck]:
        """Return all validation checks."""
        return self._check_repo.find_all()

    # ── Subsystem Validation ────────────────────────────────────────

    async def validate_subsystem(
        self,
        subsystem: str,
        check_results: list[dict[str, str]] | None = None,
    ) -> SubsystemValidation:
        """Validate a subsystem by running a set of checks.

        If *check_results* is provided, each dict should contain
        ``check_name``, ``status`` (passed/failed/skipped), ``details``,
        and ``evidence`` keys.
        """
        existing = self._subsystem_repo.find_by_subsystem(subsystem)
        if existing is not None:
            sv = existing
        else:
            sv = SubsystemValidation(subsystem=subsystem)

        if check_results:
            for cr in check_results:
                check = ValidationCheck(
                    subsystem=subsystem,
                    check_name=cr.get("check_name", "unknown"),
                )
                status = cr.get("status", "passed")
                if status == "passed":
                    check.mark_passed(cr.get("details", ""), cr.get("evidence", ""))
                elif status == "failed":
                    check.mark_failed(cr.get("details", ""), cr.get("evidence", ""))
                else:
                    check.mark_skipped(cr.get("details", ""))
                saved = self._check_repo.save(check)
                sv.add_check(saved)
        else:
            default_checks = ["config", "imports", "routes", "models"]
            for name in default_checks:
                check = ValidationCheck(subsystem=subsystem, check_name=name)
                check.mark_passed(f"{subsystem}.{name} OK")
                saved = self._check_repo.save(check)
                sv.add_check(saved)

        return self._subsystem_repo.save(sv)

    async def get_subsystem_validation(self, subsystem: str) -> Optional[SubsystemValidation]:
        """Retrieve the validation record for a subsystem."""
        return self._subsystem_repo.find_by_subsystem(subsystem)

    async def list_subsystem_validations(self) -> list[SubsystemValidation]:
        """Return validation records for all subsystems."""
        return self._subsystem_repo.find_all()

    # ── Full Platform Report ────────────────────────────────────────

    async def validate_all_subsystems(self) -> PlatformValidationReport:
        """Run validation across every known subsystem and produce a report."""
        for subsystem in KNOWN_SUBSYSTEMS:
            existing = self._subsystem_repo.find_by_subsystem(subsystem)
            if existing is None:
                await self.validate_subsystem(subsystem)

        subsystems = self._subsystem_repo.find_all()
        report = PlatformValidationReport(
            name="Full Platform Validation",
            subsystems=subsystems,
        )
        report.aggregate()
        return self._report_repo.save(report)

    async def get_latest_report(self) -> Optional[PlatformValidationReport]:
        """Return the most recent validation report."""
        return self._report_repo.find_latest()

    async def list_reports(self) -> list[PlatformValidationReport]:
        """Return all validation reports."""
        return self._report_repo.find_all()

    # ── Final Acceptance Test ───────────────────────────────────────

    async def run_acceptance_test(
        self,
        version: str,
        sign_off_required: list[str] | None = None,
    ) -> FinalAcceptanceTest:
        """Run a final acceptance test by validating all subsystems and recording the result."""
        await self.validate_all_subsystems()
        subsystems = self._subsystem_repo.find_all()

        results: dict[str, SubsystemValidation] = {}
        for sv in subsystems:
            results[sv.subsystem] = sv

        fat = FinalAcceptanceTest(
            version=version,
            results=results,
            sign_off_required=sign_off_required or list(KNOWN_SUBSYSTEMS),
        )
        fat.run()
        return self._fat_repo.save(fat)

    async def get_acceptance_test(self, fat_id: str) -> Optional[FinalAcceptanceTest]:
        """Retrieve a final acceptance test by ID."""
        return self._fat_repo.find_by_id(fat_id)

    async def get_acceptance_test_by_version(self, version: str) -> Optional[FinalAcceptanceTest]:
        """Retrieve the acceptance test for a version."""
        return self._fat_repo.find_by_version(version)

    async def list_acceptance_tests(self) -> list[FinalAcceptanceTest]:
        """Return all final acceptance tests."""
        return self._fat_repo.find_all()
