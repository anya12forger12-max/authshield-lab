from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.testing import (
    CoverageReport,
    TestCase,
    TestSuite,
)
from app.quality.domain.interfaces.repositories import (
    CoverageReportRepository,
    TestCaseRepository,
    TestSuiteRepository,
)


class TestPlatformService:
    def __init__(
        self,
        test_case_repo: TestCaseRepository,
        suite_repo: TestSuiteRepository,
        coverage_repo: CoverageReportRepository,
    ) -> None:
        self._test_case_repo = test_case_repo
        self._suite_repo = suite_repo
        self._coverage_repo = coverage_repo

    def create_test_case(self, test_case: TestCase) -> TestCase:
        return self._test_case_repo.save(test_case)

    def update_test_case(self, test_case: TestCase) -> TestCase:
        return self._test_case_repo.save(test_case)

    def get_test_case(self, test_id: str) -> TestCase | None:
        return self._test_case_repo.find_by_id(test_id)

    def get_test_cases_by_type(self, test_type: str) -> list[TestCase]:
        return self._test_case_repo.find_by_type(test_type)

    def get_test_cases_by_module(self, module: str) -> list[TestCase]:
        return self._test_case_repo.find_by_module(module)

    def run_suite(self, suite: TestSuite) -> TestSuite:
        passed = 0
        failed = 0
        skipped = 0
        for tc in suite.test_cases:
            if tc.status == "passed":
                passed += 1
            elif tc.status == "failed":
                failed += 1
            else:
                skipped += 1
            self._test_case_repo.save(tc)
        suite.passed = passed
        suite.failed = failed
        suite.skipped = skipped
        suite.total = len(suite.test_cases)
        suite.run_at = datetime.now(timezone.utc)
        return self._suite_repo.save(suite)

    def create_suite(self, suite: TestSuite) -> TestSuite:
        return self._suite_repo.save(suite)

    def get_suite(self, suite_id: str) -> TestSuite | None:
        return self._suite_repo.find_by_id(suite_id)

    def get_all_suites(self) -> list[TestSuite]:
        return self._suite_repo.find_all()

    def track_coverage(self, report: CoverageReport) -> CoverageReport:
        if report.total_statements > 0:
            report.percentage = (report.covered_statements / report.total_statements) * 100.0
        report.generated_at = datetime.now(timezone.utc)
        return self._coverage_repo.save(report)

    def get_latest_coverage(self) -> CoverageReport | None:
        return self._coverage_repo.find_latest()
