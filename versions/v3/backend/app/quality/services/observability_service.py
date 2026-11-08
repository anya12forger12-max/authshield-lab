from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.observability import (
    ApplicationMetric,
    CacheStats,
    CpuUsage,
    DatabaseStats,
    MemoryUsage,
    ObservabilitySnapshot,
    PluginStatus,
)
from app.quality.domain.interfaces.repositories import (
    ApplicationMetricRepository,
    ObservabilitySnapshotRepository,
)


class ObservabilityService:
    def __init__(
        self,
        metric_repo: ApplicationMetricRepository,
        snapshot_repo: ObservabilitySnapshotRepository,
    ) -> None:
        self._metric_repo = metric_repo
        self._snapshot_repo = snapshot_repo

    def collect_metric(self, metric: ApplicationMetric) -> ApplicationMetric:
        metric.timestamp = datetime.now(timezone.utc)
        return self._metric_repo.save(metric)

    def get_metrics(self, name: str | None = None) -> list[ApplicationMetric]:
        if name:
            return self._metric_repo.find_by_name(name)
        return self._metric_repo.find_all()

    def get_memory_usage(self, used_mb: float, available_mb: float, peak_mb: float) -> MemoryUsage:
        total = used_mb + available_mb
        percentage = (used_mb / total * 100.0) if total > 0 else 0.0
        return MemoryUsage(
            used_mb=used_mb,
            available_mb=available_mb,
            percentage=percentage,
            peak_mb=peak_mb,
        )

    def get_cpu_usage(self, percentage: float, cores: int, load_average: list[float]) -> CpuUsage:
        return CpuUsage(
            percentage=percentage,
            cores=cores,
            load_average=load_average,
        )

    def get_database_stats(
        self,
        total_size_mb: float,
        table_count: int,
        record_counts: dict[str, int],
        query_time_avg_ms: float,
    ) -> DatabaseStats:
        return DatabaseStats(
            total_size_mb=total_size_mb,
            table_count=table_count,
            record_counts=record_counts,
            query_time_avg_ms=query_time_avg_ms,
        )

    def get_cache_stats(self, hits: int, misses: int, size: int, max_size: int) -> CacheStats:
        total = hits + misses
        hit_rate = (hits / total * 100.0) if total > 0 else 0.0
        return CacheStats(
            hits=hits,
            misses=misses,
            hit_rate=hit_rate,
            size=size,
            max_size=max_size,
        )

    def generate_snapshot(
        self,
        memory: MemoryUsage,
        cpu: CpuUsage,
        database: DatabaseStats,
        cache: CacheStats,
        plugins: list[PluginStatus],
        startup_time_ms: float,
        active_sessions: int,
    ) -> ObservabilitySnapshot:
        snapshot = ObservabilitySnapshot(
            memory=memory,
            cpu=cpu,
            database=database,
            cache=cache,
            plugins=plugins,
            startup_time_ms=startup_time_ms,
            active_sessions=active_sessions,
            captured_at=datetime.now(timezone.utc),
        )
        return self._snapshot_repo.save(snapshot)

    def get_latest_snapshot(self) -> ObservabilitySnapshot | None:
        return self._snapshot_repo.find_latest()
