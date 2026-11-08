from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.diagnostics import (
    DiagnosticBundle,
    DiagnosticCategory,
    DiagnosticCheck,
)
from app.quality.domain.interfaces.repositories import (
    DiagnosticBundleRepository,
    DiagnosticCheckRepository,
)


class DiagnosticsService:
    def __init__(
        self,
        check_repo: DiagnosticCheckRepository,
        bundle_repo: DiagnosticBundleRepository,
    ) -> None:
        self._check_repo = check_repo
        self._bundle_repo = bundle_repo

    def run_check(self, check: DiagnosticCheck) -> DiagnosticCheck:
        check.checked_at = datetime.now(timezone.utc)
        return self._check_repo.save(check)

    def get_checks_by_category(self, category: str) -> list[DiagnosticCheck]:
        return self._check_repo.find_by_category(category)

    def generate_bundle(
        self,
        name: str,
        checks: list[DiagnosticCheck],
        platform: str,
        version: str,
        includes_sensitive: bool = False,
    ) -> DiagnosticBundle:
        for c in checks:
            self._check_repo.save(c)
        overall = "pass"
        for c in checks:
            if c.status == "fail":
                overall = "fail"
                break
            if c.status == "warning" and overall == "pass":
                overall = "warning"
        bundle = DiagnosticBundle(
            name=name,
            checks=checks,
            overall_status=overall,
            platform=platform,
            version=version,
            includes_sensitive=includes_sensitive,
            generated_at=datetime.now(timezone.utc),
        )
        return self._bundle_repo.save(bundle)

    def get_bundle(self, bundle_id: str) -> DiagnosticBundle | None:
        return self._bundle_repo.find_by_id(bundle_id)

    def get_all_bundles(self) -> list[DiagnosticBundle]:
        return self._bundle_repo.find_all()

    def categorize_results(self, checks: list[DiagnosticCheck]) -> list[DiagnosticCategory]:
        cat_map: dict[str, dict] = {}
        for c in checks:
            if c.category not in cat_map:
                cat_map[c.category] = {"name": c.category, "description": "", "checks_count": 0, "passed": 0, "failed": 0, "warnings": 0}
            cat_map[c.category]["checks_count"] += 1
            if c.status == "pass":
                cat_map[c.category]["passed"] += 1
            elif c.status == "fail":
                cat_map[c.category]["failed"] += 1
            elif c.status == "warning":
                cat_map[c.category]["warnings"] += 1
        return [DiagnosticCategory(**v) for v in cat_map.values()]
