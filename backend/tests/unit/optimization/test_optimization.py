"""Tests for optimization entities and services — PerformanceMetric, StartupMetrics, FeatureFlag, BenchmarkResult, PerformanceService."""

from __future__ import annotations

from unittest.mock import MagicMock

from app.optimization.domain.entities.optimization import (
    BenchmarkResult,
    BenchmarkStatus,
    FeatureFlag,
    PerformanceMetric,
    StartupMetrics,
)


class TestPerformanceMetric:
    def test_defaults(self):
        m = PerformanceMetric()
        assert m.value == 0.0
        assert m.passed is True

    def test_evaluate_passes(self):
        m = PerformanceMetric(name="response_time", value=50.0, threshold=100.0)
        assert m.evaluate() is True

    def test_evaluate_fails(self):
        m = PerformanceMetric(name="latency", value=150.0, threshold=100.0)
        assert m.evaluate() is False


class TestStartupMetrics:
    def test_defaults(self):
        m = StartupMetrics()
        assert m.total_ms == 0.0

    def test_calculate_total(self):
        m = StartupMetrics(app_start_ms=100.0, db_init_ms=50.0)
        m.module_load_ms = {"auth": 30.0}
        m.plugin_load_ms = {"plug": 20.0}
        total = m.calculate_total()
        assert total == 200.0

    def test_slowest_module(self):
        m = StartupMetrics(module_load_ms={"a": 10, "b": 50, "c": 30})
        name, val = m.slowest_module()
        assert name == "b"
        assert val == 50

    def test_slowest_plugin_empty(self):
        m = StartupMetrics()
        name, val = m.slowest_plugin()
        assert name == ""


class TestFeatureFlag:
    def test_default_values(self):
        f = FeatureFlag()
        assert f.enabled is False
        assert f.default_value is False

    def test_toggle(self):
        f = FeatureFlag()
        f.activate()
        assert f.is_active() is True
        f.deactivate()
        assert f.is_active() is False

    def test_toggle_returns_new_state(self):
        f = FeatureFlag()
        assert f.toggle() is True
        assert f.toggle() is False

    def test_custom_flag(self):
        f = FeatureFlag(name="beta_search", enabled=True, category="search")
        assert f.name == "beta_search"
        assert f.enabled is True


class TestBenchmarkResult:
    def test_defaults(self):
        b = BenchmarkResult()
        assert b.value == 0.0
        assert b.passed is True

    def test_compare_to_baseline_regression(self):
        b = BenchmarkResult(name="speed", value=120.0, threshold=100.0, baseline_value=100.0)
        status = b.compare_to_baseline()
        assert status == BenchmarkStatus.REGRESSION.value
        assert b.passed is False

    def test_compare_improvement(self):
        b = BenchmarkResult(name="speed", value=80.0, baseline_value=100.0)
        status = b.compare_to_baseline()
        assert status == BenchmarkStatus.IMPROVEMENT.value
        assert b.passed is True

    def test_compare_stable(self):
        b = BenchmarkResult(name="speed", value=102.0, baseline_value=100.0)
        status = b.compare_to_baseline()
        assert status == BenchmarkStatus.PASS.value

    def test_compare_baseline_zero(self):
        b = BenchmarkResult(value=200.0, baseline_value=0)
        status = b.compare_to_baseline()
        assert status == BenchmarkStatus.PASS.value


class TestPerformanceService:
    def test_collect_metric(self):
        from app.optimization.services.performance_service import PerformanceService
        metric_repo = MagicMock()
        metric_repo.create = MagicMock(return_value={
            "id": "m1", "name": "cpu", "category": "system",
            "value": 45.0, "unit": "%", "threshold": 0.0, "passed": True,
        })
        benchmark_repo = MagicMock()
        dashboard_repo = MagicMock()
        service = PerformanceService(metric_repo, benchmark_repo, dashboard_repo)
        result = service.collect_metric({"name": "cpu", "value": 45.0, "unit": "%", "category": "system"})
        assert result["name"] == "cpu"

    def test_get_metrics_by_category(self):
        from app.optimization.services.performance_service import PerformanceService
        metric_repo = MagicMock()
        metric_repo.get_by_category = MagicMock(return_value=[{"name": "cpu", "category": "system"}])
        benchmark_repo = MagicMock()
        dashboard_repo = MagicMock()
        service = PerformanceService(metric_repo, benchmark_repo, dashboard_repo)
        result = service.get_metrics_by_category("system")
        assert len(result) == 1

    def test_list_metrics(self):
        from app.optimization.services.performance_service import PerformanceService
        metric_repo = MagicMock()
        metric_repo.get_all = MagicMock(return_value={"items": [], "total": 0})
        benchmark_repo = MagicMock()
        dashboard_repo = MagicMock()
        service = PerformanceService(metric_repo, benchmark_repo, dashboard_repo)
        result = service.list_metrics()
        assert result["total"] == 0

    def test_get_metric(self):
        from app.optimization.services.performance_service import PerformanceService
        metric_repo = MagicMock()
        metric_repo.get_by_id = MagicMock(return_value={"id": "m1", "name": "memory"})
        benchmark_repo = MagicMock()
        dashboard_repo = MagicMock()
        service = PerformanceService(metric_repo, benchmark_repo, dashboard_repo)
        result = service.get_metric("m1")
        assert result["name"] == "memory"

    def test_get_metric_none(self):
        from app.optimization.services.performance_service import PerformanceService
        metric_repo = MagicMock()
        metric_repo.get_by_id = MagicMock(return_value=None)
        benchmark_repo = MagicMock()
        dashboard_repo = MagicMock()
        service = PerformanceService(metric_repo, benchmark_repo, dashboard_repo)
        result = service.get_metric("missing")
        assert result is None
