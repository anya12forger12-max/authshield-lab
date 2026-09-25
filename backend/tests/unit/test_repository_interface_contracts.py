"""Regression tests for repository interface/impl contract drift.

Every service and route in these paths calls a concrete in-memory repository
method. `mypy --strict` surfaced several calls to methods that existed on
neither the abstract interface nor the concrete implementation, so the call
site raised `AttributeError` at runtime while the whole 877-test suite stayed
green: the existing unit tests inject `MagicMock()` repositories, and a
`MagicMock` fabricates *any* attribute on demand, so a method that does not
exist in production still "works" in tests.

These tests therefore use the REAL in-memory repositories rather than mocks,
so a missing method is a hard failure instead of a silently-passing mock.
"""

from __future__ import annotations

import pytest

from app.certification.domain.entities.sustainability import APIStabilityReport
from app.certification.repositories.certification_repository_impl import (
    InMemoryAPIStabilityRepository,
)
from app.lms.repositories.lms_repository_impl import InMemoryCompetencyRepository
from app.lms.services.competency_service import CompetencyService
from app.optimization.domain.interfaces.optimization_interfaces import (
    IDiagnosticTraceRepository,
    IReleaseRepository,
)
from app.optimization.repositories.optimization_repository_impl import (
    InMemoryDiagnosticTraceRepository,
    InMemoryReleaseRepository,
)
from app.optimization.services.observability_extended_service import (
    ObservabilityExtendedService,
)
from app.quality.domain.entities.accessibility_a11y import A11yScorecard
from app.quality.domain.entities.performance import Benchmark
from app.quality.domain.interfaces.repositories import (
    A11yScorecardRepository,
    BenchmarkRepository,
)
from app.quality.repositories.quality_repository_impl import (
    InMemoryA11yScorecardRepository,
    InMemoryBenchmarkHistoryRepository,
    InMemoryBenchmarkRepository,
    InMemoryPerformanceReportRepository,
)
from app.quality.services.performance_service import PerformanceService

# ---------------------------------------------------------------------------
# LMS competency progress creation (the repository had no create method)
# ---------------------------------------------------------------------------


class TestCompetencyProgressContract:
    def test_start_competency_creates_progress_for_new_learner(self):
        """Regression: starting a competency with no existing progress raised
        AttributeError because `create_competency_progress` did not exist.

        The old code worked around the missing method with
        `update_progress("", {}) or create_competency_progress(...)`, but no
        record is ever keyed by the empty string, so the first call always
        returned None and the `or` always fell through to the missing method.
        """
        repo = InMemoryCompetencyRepository()
        service = CompetencyService(repo)

        progress = service.start_competency("learner-1", "comp-1")

        assert progress["learner_id"] == "learner-1"
        assert progress["competency_id"] == "comp-1"
        assert progress["status"] == "in_progress"
        assert progress["id"]

    def test_created_progress_is_retrievable(self):
        repo = InMemoryCompetencyRepository()
        service = CompetencyService(repo)

        service.start_competency("learner-1", "comp-1")
        stored = service.get_learner_progress("learner-1", "comp-1")

        assert len(stored) == 1
        assert stored[0]["status"] == "in_progress"

    def test_start_competency_advances_existing_not_started_progress(self):
        repo = InMemoryCompetencyRepository()
        service = CompetencyService(repo)
        existing = repo.create_progress(
            {"learner_id": "learner-2", "competency_id": "comp-1", "status": "not_started"}
        )

        progress = service.start_competency("learner-2", "comp-1")

        assert progress["id"] == existing["id"]
        assert progress["status"] == "in_progress"
        assert len(service.get_learner_progress("learner-2", "comp-1")) == 1

    def test_start_competency_rejects_already_started_progress(self):
        repo = InMemoryCompetencyRepository()
        service = CompetencyService(repo)
        repo.create_progress(
            {"learner_id": "learner-3", "competency_id": "comp-1", "status": "in_progress"}
        )

        with pytest.raises(ValueError, match="already has competency"):
            service.start_competency("learner-3", "comp-1")

    def test_progress_ids_are_unique(self):
        repo = InMemoryCompetencyRepository()
        first = repo.create_progress({"learner_id": "l", "competency_id": "c"})
        second = repo.create_progress({"learner_id": "l", "competency_id": "c"})

        assert first["id"] != second["id"]


# ---------------------------------------------------------------------------
# Quality benchmark listing (the repository had no find-all method)
# ---------------------------------------------------------------------------


class TestBenchmarkRepositoryContract:
    def _service(self) -> tuple[PerformanceService, InMemoryBenchmarkRepository]:
        repo = InMemoryBenchmarkRepository()
        service = PerformanceService(
            repo,
            InMemoryPerformanceReportRepository(),
            InMemoryBenchmarkHistoryRepository(),
        )
        return service, repo

    def test_get_benchmarks_without_name_returns_every_benchmark(self):
        """Regression: `get_benchmarks(None)` called `find_all()`, which the
        interface and `InMemoryBenchmarkRepository` both lacked."""
        service, repo = self._service()
        repo.save(Benchmark(name="latency", category="perf", value=12.0))
        repo.save(Benchmark(name="throughput", category="perf", value=900.0))

        result = service.get_benchmarks()

        assert {b.name for b in result} == {"latency", "throughput"}

    def test_get_benchmarks_with_name_filters(self):
        service, repo = self._service()
        repo.save(Benchmark(name="latency", category="perf", value=12.0))
        repo.save(Benchmark(name="throughput", category="perf", value=900.0))

        result = service.get_benchmarks("latency")

        assert [b.name for b in result] == ["latency"]

    def test_get_benchmarks_on_empty_repository_is_empty(self):
        service, _repo = self._service()

        assert service.get_benchmarks() == []

    def test_repository_satisfies_abstract_contract(self):
        assert issubclass(InMemoryBenchmarkRepository, BenchmarkRepository)


# ---------------------------------------------------------------------------
# Quality a11y scorecard listing, backing the scorecards GET route
# ---------------------------------------------------------------------------


class TestA11yScorecardRepositoryContract:
    def test_find_all_returns_every_scorecard(self):
        repo = InMemoryA11yScorecardRepository()
        repo.save(A11yScorecard(category="contrast", score=92.0))
        repo.save(A11yScorecard(category="labels", score=88.0))

        result = repo.find_all()

        assert {s.category for s in result} == {"contrast", "labels"}

    def test_find_all_on_empty_repository_is_empty(self):
        assert InMemoryA11yScorecardRepository().find_all() == []

    def test_list_scorecards_route_returns_saved_scorecards(self):
        """Regression: the GET /a11y/scorecards handler called `find_all()` on
        the concrete repo, which did not define it -> AttributeError (HTTP 500)."""
        from app.quality.api import quality_routes

        repo = quality_routes._a11y_scorecard_repo
        assert isinstance(repo, A11yScorecardRepository)

        scorecard = A11yScorecard(category="contrast", score=95.0)
        repo.save(scorecard)

        result = quality_routes.list_scorecards()

        assert scorecard.id in {s.id for s in result}


# ---------------------------------------------------------------------------
# Optimization diagnostic trace span persistence (no update method existed)
# ---------------------------------------------------------------------------


class TestDiagnosticTraceRepositoryContract:
    def _service(self) -> tuple[ObservabilityExtendedService, InMemoryDiagnosticTraceRepository]:
        repo = InMemoryDiagnosticTraceRepository()
        return ObservabilityExtendedService(repo), repo

    def test_add_span_persists_spans_and_total_duration(self):
        """Regression: `add_span_to_trace` called `update()`, which the interface
        and `InMemoryDiagnosticTraceRepository` both lacked -> AttributeError."""
        service, _repo = self._service()
        trace = service.create_trace({"name": "login-flow", "spans": []})

        updated = service.add_span_to_trace(
            trace["id"],
            {"name": "db-query", "start_ms": 10.0, "end_ms": 42.5, "module": "db"},
        )

        assert updated is not None
        assert "db-query" in updated["spans_json"]
        assert updated["total_duration_ms"] == pytest.approx(32.5)

    def test_add_span_accumulates_across_calls(self):
        service, _repo = self._service()
        trace = service.create_trace({"name": "flow", "spans": []})

        service.add_span_to_trace(trace["id"], {"name": "first", "start_ms": 0.0, "end_ms": 5.0})
        updated = service.add_span_to_trace(
            trace["id"], {"name": "second", "start_ms": 5.0, "end_ms": 9.0}
        )

        assert updated is not None
        assert "first" in updated["spans_json"]
        assert "second" in updated["spans_json"]
        assert updated["total_duration_ms"] == pytest.approx(9.0)

    def test_add_span_to_missing_trace_returns_none(self):
        service, _repo = self._service()

        assert service.add_span_to_trace("does-not-exist", {"name": "x"}) is None

    def test_update_of_missing_trace_returns_none(self):
        repo = InMemoryDiagnosticTraceRepository()

        assert repo.update("does-not-exist", {"total_duration_ms": 1.0}) is None

    def test_update_ignores_unmanaged_fields(self):
        repo = InMemoryDiagnosticTraceRepository()
        trace = repo.create({"name": "t"})

        updated = repo.update(trace["id"], {"spans_json": "[]", "name": "hijacked"})

        assert updated is not None
        assert updated["name"] == "t"
        assert updated["spans_json"] == "[]"

    def test_repository_satisfies_abstract_contract(self):
        assert issubclass(InMemoryDiagnosticTraceRepository, IDiagnosticTraceRepository)


# ---------------------------------------------------------------------------
# Optimization release approval updates (missing from the interface)
# ---------------------------------------------------------------------------


class TestReleaseApprovalContract:
    def test_update_approval_mutates_only_managed_fields(self):
        repo = InMemoryReleaseRepository()
        approval = repo.create_approval({"status": "pending", "reviewer": "alice"})

        updated = repo.update_approval(approval["id"], {"approved": True, "reviewer": "mallory"})

        assert updated is not None
        assert updated["approved"] is True
        assert updated["reviewer"] == "alice"

    def test_update_approval_of_missing_approval_returns_none(self):
        assert InMemoryReleaseRepository().update_approval("nope", {"approved": True}) is None

    def test_repository_satisfies_abstract_contract(self):
        assert issubclass(InMemoryReleaseRepository, IReleaseRepository)


# ---------------------------------------------------------------------------
# Certification API stability reports (interface now uses the concrete type)
# ---------------------------------------------------------------------------


class TestAPIStabilityRepositoryContract:
    def test_save_then_find_by_version(self):
        repo = InMemoryAPIStabilityRepository()
        report = APIStabilityReport(version="1.0.0", endpoints=10)

        saved = repo.save(report)

        assert saved is report
        assert repo.find_by_version("1.0.0") is report

    def test_find_latest_returns_highest_version(self):
        repo = InMemoryAPIStabilityRepository()
        repo.save(APIStabilityReport(version="1.0.0", endpoints=10))
        latest = repo.save(APIStabilityReport(version="1.2.0", endpoints=12))

        assert repo.find_latest() is latest

    def test_find_latest_on_empty_repository_is_none(self):
        assert InMemoryAPIStabilityRepository().find_latest() is None
