"""Release engineering service: plans, validations, packaging, regression, history."""

from __future__ import annotations

from typing import Any, Optional

from ..domain.entities.release_engineering import (
    PackagingResult,
    RegressionResult,
    ReleaseHistoryEntry,
    ReleasePhase,
    ReleasePlan,
    ReleaseValidation,
)
from ..domain.interfaces import (
    PackagingResultRepository,
    RegressionResultRepository,
    ReleaseHistoryRepository,
    ReleasePlanRepository,
    ReleaseValidationRepository,
)


class ReleaseEngineeringService:
    """Manages release plans, validations, packaging, regression, and history."""

    def __init__(
        self,
        plan_repo: ReleasePlanRepository,
        validation_repo: ReleaseValidationRepository,
        packaging_repo: PackagingResultRepository,
        regression_repo: RegressionResultRepository,
        history_repo: ReleaseHistoryRepository,
    ) -> None:
        self._plan_repo = plan_repo
        self._validation_repo = validation_repo
        self._packaging_repo = packaging_repo
        self._regression_repo = regression_repo
        self._history_repo = history_repo

    # ── Release Plans ───────────────────────────────────────────────

    async def create_plan(
        self,
        version: str,
        code_name: str = "",
        end_date: str = "",
    ) -> ReleasePlan:
        """Create a new release plan in the planning phase."""
        plan = ReleasePlan(
            version=version,
            code_name=code_name,
            end_date=end_date,
        )
        return self._plan_repo.save(plan)

    async def get_plan(self, plan_id: str) -> Optional[ReleasePlan]:
        """Retrieve a release plan by ID."""
        return self._plan_repo.find_by_id(plan_id)

    async def get_plan_by_version(self, version: str) -> Optional[ReleasePlan]:
        """Retrieve a release plan by version string."""
        return self._plan_repo.find_by_version(version)

    async def list_plans(self) -> list[ReleasePlan]:
        """Return all release plans."""
        return self._plan_repo.find_all()

    async def update_plan(self, plan_id: str, data: dict[str, Any]) -> Optional[ReleasePlan]:
        """Update arbitrary fields on a release plan."""
        return self._plan_repo.update(plan_id, data)

    async def advance_plan(self, plan_id: str) -> Optional[ReleasePlan]:
        """Move a release plan to the next lifecycle phase."""
        plan = self._plan_repo.find_by_id(plan_id)
        if plan is None:
            return None
        plan.advance()
        return self._plan_repo.save(plan)

    async def delete_plan(self, plan_id: str) -> bool:
        """Remove a release plan."""
        return self._plan_repo.delete(plan_id)

    # ── Release Validations ─────────────────────────────────────────

    async def create_validation(
        self,
        release_id: str,
        validation_type: str,
    ) -> ReleaseValidation:
        """Create a new validation record for a release."""
        val = ReleaseValidation(
            release_id=release_id,
            validation_type=validation_type,
        )
        return self._validation_repo.save(val)

    async def pass_validation(self, val_id: str, details: str = "") -> Optional[ReleaseValidation]:
        """Mark a validation as passed."""
        val = self._validation_repo.find_by_id(val_id)
        if val is None:
            return None
        val.mark_passed(details)
        return self._validation_repo.save(val)

    async def fail_validation(self, val_id: str, details: str = "") -> Optional[ReleaseValidation]:
        """Mark a validation as failed."""
        val = self._validation_repo.find_by_id(val_id)
        if val is None:
            return None
        val.mark_failed(details)
        return self._validation_repo.save(val)

    async def get_validations_for_release(self, release_id: str) -> list[ReleaseValidation]:
        """Return all validations for a release."""
        return self._validation_repo.find_by_release_id(release_id)

    # ── Packaging ───────────────────────────────────────────────────

    async def create_package(
        self,
        release_id: str,
        platform: str,
        package_type: str = "",
        output_path: str = "",
        checksum: str = "",
    ) -> PackagingResult:
        """Record a packaging result for a release."""
        pkg = PackagingResult(
            release_id=release_id,
            platform=platform,
            package_type=package_type,
            output_path=output_path,
            checksum=checksum,
        )
        return self._packaging_repo.save(pkg)

    async def get_packages_for_release(self, release_id: str) -> list[PackagingResult]:
        """Return all packages built for a release."""
        return self._packaging_repo.find_by_release_id(release_id)

    async def get_package(self, pkg_id: str) -> Optional[PackagingResult]:
        """Retrieve a package result by ID."""
        return self._packaging_repo.find_by_id(pkg_id)

    # ── Regression ──────────────────────────────────────────────────

    async def record_regression(
        self,
        release_id: str,
        tests_run: int = 0,
        passed: int = 0,
        failed: int = 0,
        skipped: int = 0,
        coverage: float = 0.0,
    ) -> RegressionResult:
        """Record the outcome of a regression test run."""
        result = RegressionResult(
            release_id=release_id,
            tests_run=tests_run,
            passed=passed,
            failed=failed,
            skipped=skipped,
            coverage=coverage,
        )
        return self._regression_repo.save(result)

    async def get_regression_results(self, release_id: str) -> list[RegressionResult]:
        """Return all regression results for a release."""
        return self._regression_repo.find_by_release_id(release_id)

    async def get_regression(self, result_id: str) -> Optional[RegressionResult]:
        """Retrieve a regression result by ID."""
        return self._regression_repo.find_by_id(result_id)

    # ── Release History ─────────────────────────────────────────────

    async def record_history(
        self,
        version: str,
        summary: str = "",
        highlights: list[str] | None = None,
        known_issues: list[str] | None = None,
    ) -> ReleaseHistoryEntry:
        """Record a historical release entry."""
        entry = ReleaseHistoryEntry(
            version=version,
            summary=summary,
            highlights=highlights or [],
            known_issues=known_issues or [],
        )
        return self._history_repo.save(entry)

    async def get_history(self, entry_id: str) -> Optional[ReleaseHistoryEntry]:
        """Retrieve a history entry by ID."""
        return self._history_repo.find_by_id(entry_id)

    async def get_history_by_version(self, version: str) -> Optional[ReleaseHistoryEntry]:
        """Retrieve a history entry by version."""
        return self._history_repo.find_by_version(version)

    async def list_history(self) -> list[ReleaseHistoryEntry]:
        """Return all release history entries."""
        return self._history_repo.find_all()

    async def add_highlight(self, entry_id: str, text: str) -> Optional[ReleaseHistoryEntry]:
        """Add a highlight to a history entry."""
        entry = self._history_repo.find_by_id(entry_id)
        if entry is None:
            return None
        entry.add_highlight(text)
        return self._history_repo.save(entry)

    async def add_known_issue(self, entry_id: str, text: str) -> Optional[ReleaseHistoryEntry]:
        """Add a known issue to a history entry."""
        entry = self._history_repo.find_by_id(entry_id)
        if entry is None:
            return None
        entry.add_known_issue(text)
        return self._history_repo.save(entry)
