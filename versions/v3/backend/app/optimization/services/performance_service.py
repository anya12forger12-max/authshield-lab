"""Performance metrics service — collect, benchmark, dashboard, regressions."""

from __future__ import annotations

import logging
import statistics
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.optimization import (
    BenchmarkHistory,
    BenchmarkResult,
    MemorySnapshot,
    OptimizationDashboard,
    PerformanceMetric,
    RenderingMetrics,
    SearchMetrics,
    StartupMetrics,
    StorageMetrics,
)
from ..domain.events.optimization_events import (
    BenchmarkCompleted,
    OptimizationDashboardGenerated,
)
from ..domain.interfaces.optimization_interfaces import (
    IBenchmarkRepository,
    IDashboardRepository,
    IPerformanceMetricRepository,
)

logger = logging.getLogger(__name__)


class PerformanceService:
    """Collects metrics, runs benchmarks, and generates dashboards."""

    def __init__(
        self,
        metric_repo: IPerformanceMetricRepository,
        benchmark_repo: IBenchmarkRepository,
        dashboard_repo: IDashboardRepository,
    ) -> None:
        self._metric_repo = metric_repo
        self._benchmark_repo = benchmark_repo
        self._dashboard_repo = dashboard_repo
        self._benchmark_history: dict[str, BenchmarkHistory] = {}

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def collect_metric(self, data: dict[str, Any]) -> dict[str, Any]:
        """Collect a new performance metric."""
        metric = PerformanceMetric(
            name=data.get("name", ""),
            category=data.get("category", ""),
            value=float(data.get("value", 0.0)),
            unit=data.get("unit", ""),
            threshold=float(data.get("threshold", 0.0)),
        )
        metric.evaluate()
        result = self._metric_repo.create(metric.to_dict())
        logger.info("metric_collected", extra={"metric_id": result["id"], "name": metric.name})
        return result

    def get_metric(self, metric_id: str) -> Optional[dict[str, Any]]:
        return self._metric_repo.get_by_id(metric_id)

    def list_metrics(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._metric_repo.get_all(page=page, per_page=per_page, category=category)

    def delete_metric(self, metric_id: str) -> bool:
        return self._metric_repo.delete(metric_id)

    def get_metrics_by_category(self, category: str) -> list[dict[str, Any]]:
        return self._metric_repo.get_by_category(category)

    # ------------------------------------------------------------------
    # Benchmarks
    # ------------------------------------------------------------------

    def run_benchmark(self, data: dict[str, Any]) -> dict[str, Any]:
        """Run a benchmark and record the result."""
        result = BenchmarkResult(
            name=data.get("name", ""),
            category=data.get("category", ""),
            value=float(data.get("value", 0.0)),
            unit=data.get("unit", ""),
            threshold=float(data.get("threshold", 0.0)),
            baseline_value=float(data.get("baseline_value", 0.0)),
        )
        status = result.compare_to_baseline()
        if result.threshold > 0:
            result.passed = result.value <= result.threshold and status != "regression"

        stored = self._benchmark_repo.create(result.to_dict())

        history = self._benchmark_history.setdefault(
            result.name, BenchmarkHistory(name=result.name)
        )
        history.add_measurement(result.value, result.measured_at)

        event = BenchmarkCompleted(
            benchmark_id=stored["id"],
            benchmark_name=result.name,
            category=result.category,
            value=result.value,
            passed=result.passed,
        )
        logger.info(
            "benchmark_completed",
            extra={"benchmark_id": stored["id"], "name": result.name, "event_id": event.event_id},
        )
        return stored

    def list_benchmarks(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._benchmark_repo.get_all(page=page, per_page=per_page, category=category)

    def get_benchmark_history(self, name: str) -> dict[str, Any]:
        """Return trend data for a named benchmark."""
        history = self._benchmark_history.get(name)
        if history is None:
            history = BenchmarkHistory(name=name)
        return history.to_dict()

    def detect_regressions(self) -> list[dict[str, Any]]:
        """Return all benchmarks with regression detected."""
        regressions = []
        for name, history in self._benchmark_history.items():
            if history.regression_detected:
                regressions.append(history.to_dict())
        return regressions

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def generate_dashboard(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Build and persist an optimization dashboard snapshot."""
        data = data or {}
        startup = StartupMetrics(
            app_start_ms=float(data.get("app_start_ms", 0.0)),
            db_init_ms=float(data.get("db_init_ms", 0.0)),
            module_load_ms=data.get("module_load_ms", {}),
            plugin_load_ms=data.get("plugin_load_ms", {}),
        )
        startup.calculate_total()

        memory = MemorySnapshot(
            used_mb=float(data.get("memory_used_mb", 0.0)),
            available_mb=float(data.get("memory_available_mb", 0.0)),
            peak_mb=float(data.get("memory_peak_mb", 0.0)),
            gc_collections=int(data.get("gc_collections", 0)),
        )

        storage = StorageMetrics(
            total_mb=float(data.get("storage_total_mb", 0.0)),
            used_mb=float(data.get("storage_used_mb", 0.0)),
            by_module=data.get("storage_by_module", {}),
            backup_mb=float(data.get("backup_mb", 0.0)),
            archive_mb=float(data.get("archive_mb", 0.0)),
        )

        search = SearchMetrics(
            query_count=int(data.get("search_query_count", 0)),
            avg_response_ms=float(data.get("search_avg_response_ms", 0.0)),
            cache_hit_rate=float(data.get("search_cache_hit_rate", 0.0)),
            index_size=int(data.get("search_index_size", 0)),
        )

        rendering = RenderingMetrics(
            avg_render_ms=float(data.get("avg_render_ms", 0.0)),
            paint_time_ms=float(data.get("paint_time_ms", 0.0)),
            interactive_time_ms=float(data.get("interactive_time_ms", 0.0)),
            frame_rate=float(data.get("frame_rate", 0.0)),
        )

        dashboard = OptimizationDashboard(
            startup=startup,
            memory=memory,
            storage=storage,
            search=search,
            rendering=rendering,
            module_load_times=data.get("module_load_times", {}),
            plugin_performance=data.get("plugin_performance", {}),
        )

        stored = self._dashboard_repo.create(dashboard.to_dict())

        event = OptimizationDashboardGenerated(
            dashboard_id=stored["id"],
            overall_health=dashboard.overall_health(),
        )
        logger.info(
            "dashboard_generated",
            extra={"dashboard_id": stored["id"], "event_id": event.event_id},
        )
        return stored

    def get_dashboard(self, dashboard_id: str) -> Optional[dict[str, Any]]:
        return self._dashboard_repo.get_by_id(dashboard_id)

    def get_latest_dashboard(self) -> Optional[dict[str, Any]]:
        return self._dashboard_repo.get_latest()

    def list_dashboards(self, limit: int = 10) -> list[dict[str, Any]]:
        return self._dashboard_repo.get_all(limit=limit)

    def delete_dashboard(self, dashboard_id: str) -> bool:
        return self._dashboard_repo.delete(dashboard_id)
