"""Optimization domain entities — performance metrics, benchmarks, and dashboards."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


@dataclass
class PerformanceMetric:
    """A single collected performance measurement."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    value: float = 0.0
    unit: str = ""
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    threshold: float = 0.0
    passed: bool = True

    def evaluate(self) -> bool:
        """Check whether the metric value passes its threshold."""
        self.passed = self.value <= self.threshold if self.threshold > 0 else True
        return self.passed

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "value": self.value,
            "unit": self.unit,
            "timestamp": self.timestamp.isoformat(),
            "threshold": self.threshold,
            "passed": self.passed,
        }


@dataclass
class StartupMetrics:
    """Timing data collected during application startup."""

    app_start_ms: float = 0.0
    db_init_ms: float = 0.0
    module_load_ms: dict[str, float] = field(default_factory=dict)
    plugin_load_ms: dict[str, float] = field(default_factory=dict)
    total_ms: float = 0.0

    def calculate_total(self) -> float:
        """Sum all startup timing components."""
        self.total_ms = (
            self.app_start_ms
            + self.db_init_ms
            + sum(self.module_load_ms.values())
            + sum(self.plugin_load_ms.values())
        )
        return self.total_ms

    def slowest_module(self) -> tuple[str, float]:
        """Return the module with the highest load time."""
        if not self.module_load_ms:
            return ("", 0.0)
        name = max(self.module_load_ms, key=self.module_load_ms.get)  # type: ignore[arg-type]
        return (name, self.module_load_ms[name])

    def slowest_plugin(self) -> tuple[str, float]:
        """Return the plugin with the highest load time."""
        if not self.plugin_load_ms:
            return ("", 0.0)
        name = max(self.plugin_load_ms, key=self.plugin_load_ms.get)  # type: ignore[arg-type]
        return (name, self.plugin_load_ms[name])

    def to_dict(self) -> dict:
        return {
            "app_start_ms": self.app_start_ms,
            "db_init_ms": self.db_init_ms,
            "module_load_ms": dict(self.module_load_ms),
            "plugin_load_ms": dict(self.plugin_load_ms),
            "total_ms": self.total_ms,
        }


@dataclass
class MemorySnapshot:
    """Point-in-time memory usage data."""

    used_mb: float = 0.0
    available_mb: float = 0.0
    peak_mb: float = 0.0
    gc_collections: int = 0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def usage_ratio(self) -> float:
        """Return used / (used + available) as a fraction (0-1)."""
        total = self.used_mb + self.available_mb
        if total == 0:
            return 0.0
        return self.used_mb / total

    def is_pressure(self, threshold: float = 0.85) -> bool:
        """Return True if memory usage exceeds the threshold."""
        return self.usage_ratio() > threshold

    def to_dict(self) -> dict:
        return {
            "used_mb": self.used_mb,
            "available_mb": self.available_mb,
            "peak_mb": self.peak_mb,
            "gc_collections": self.gc_collections,
            "timestamp": self.timestamp.isoformat(),
            "usage_ratio": round(self.usage_ratio(), 4),
        }


@dataclass
class StorageMetrics:
    """Disk / storage usage broken down by area."""

    total_mb: float = 0.0
    used_mb: float = 0.0
    by_module: dict[str, float] = field(default_factory=dict)
    backup_mb: float = 0.0
    archive_mb: float = 0.0

    def free_mb(self) -> float:
        """Return the free space in megabytes."""
        return max(0.0, self.total_mb - self.used_mb)

    def usage_ratio(self) -> float:
        """Return used / total as a fraction (0-1)."""
        if self.total_mb == 0:
            return 0.0
        return self.used_mb / self.total_mb

    def top_module(self) -> tuple[str, float]:
        """Return the module consuming the most storage."""
        if not self.by_module:
            return ("", 0.0)
        name = max(self.by_module, key=self.by_module.get)  # type: ignore[arg-type]
        return (name, self.by_module[name])

    def to_dict(self) -> dict:
        return {
            "total_mb": self.total_mb,
            "used_mb": self.used_mb,
            "by_module": dict(self.by_module),
            "backup_mb": self.backup_mb,
            "archive_mb": self.archive_mb,
            "free_mb": self.free_mb(),
        }


@dataclass
class SearchMetrics:
    """Search engine performance metrics."""

    query_count: int = 0
    avg_response_ms: float = 0.0
    cache_hit_rate: float = 0.0
    index_size: int = 0

    def cache_efficiency_grade(self) -> str:
        """Return a letter grade for cache performance."""
        if self.cache_hit_rate >= 0.9:
            return "A"
        if self.cache_hit_rate >= 0.75:
            return "B"
        if self.cache_hit_rate >= 0.6:
            return "C"
        if self.cache_hit_rate >= 0.4:
            return "D"
        return "F"

    def to_dict(self) -> dict:
        return {
            "query_count": self.query_count,
            "avg_response_ms": self.avg_response_ms,
            "cache_hit_rate": self.cache_hit_rate,
            "index_size": self.index_size,
            "cache_efficiency_grade": self.cache_efficiency_grade(),
        }


@dataclass
class RenderingMetrics:
    """Frontend rendering performance metrics."""

    avg_render_ms: float = 0.0
    paint_time_ms: float = 0.0
    interactive_time_ms: float = 0.0
    frame_rate: float = 0.0

    def performance_score(self) -> float:
        """Return a 0-100 score based on rendering metrics."""
        score = 100.0
        if self.avg_render_ms > 16.0:
            score -= min(30.0, (self.avg_render_ms - 16.0) * 2)
        if self.paint_time_ms > 100.0:
            score -= min(20.0, (self.paint_time_ms - 100.0) * 0.2)
        if self.interactive_time_ms > 3000.0:
            score -= min(25.0, (self.interactive_time_ms - 3000.0) * 0.005)
        if self.frame_rate < 60.0 and self.frame_rate > 0:
            score -= min(25.0, (60.0 - self.frame_rate) * 2)
        return max(0.0, min(100.0, score))

    def to_dict(self) -> dict:
        return {
            "avg_render_ms": self.avg_render_ms,
            "paint_time_ms": self.paint_time_ms,
            "interactive_time_ms": self.interactive_time_ms,
            "frame_rate": self.frame_rate,
            "performance_score": round(self.performance_score(), 2),
        }


@dataclass
class OptimizationDashboard:
    """Aggregated optimization dashboard snapshot."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    startup: StartupMetrics = field(default_factory=StartupMetrics)
    memory: MemorySnapshot = field(default_factory=MemorySnapshot)
    storage: StorageMetrics = field(default_factory=StorageMetrics)
    search: SearchMetrics = field(default_factory=SearchMetrics)
    rendering: RenderingMetrics = field(default_factory=RenderingMetrics)
    module_load_times: dict[str, float] = field(default_factory=dict)
    plugin_performance: dict[str, float] = field(default_factory=dict)
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def overall_health(self) -> str:
        """Return a health label based on the collected metrics."""
        issues = 0
        if self.memory.is_pressure():
            issues += 1
        if self.storage.usage_ratio() > 0.9:
            issues += 1
        if self.search.cache_hit_rate < 0.5 and self.search.query_count > 0:
            issues += 1
        if self.rendering.performance_score() < 50.0:
            issues += 1
        if self.startup.total_ms > 5000.0:
            issues += 1
        if issues == 0:
            return "healthy"
        if issues <= 2:
            return "degraded"
        return "critical"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "startup": self.startup.to_dict(),
            "memory": self.memory.to_dict(),
            "storage": self.storage.to_dict(),
            "search": self.search.to_dict(),
            "rendering": self.rendering.to_dict(),
            "module_load_times": dict(self.module_load_times),
            "plugin_performance": dict(self.plugin_performance),
            "generated_at": self.generated_at.isoformat(),
            "overall_health": self.overall_health(),
        }


class BenchmarkStatus(str, Enum):
    """Status of a benchmark comparison."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"
    REGRESSION = "regression"
    IMPROVEMENT = "improvement"


@dataclass
class BenchmarkResult:
    """Result of a single benchmark test."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    category: str = ""
    value: float = 0.0
    unit: str = ""
    threshold: float = 0.0
    passed: bool = True
    baseline_value: float = 0.0
    regression_pct: float = 0.0
    measured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def compare_to_baseline(self) -> str:
        """Compare current value to baseline and classify."""
        if self.baseline_value == 0:
            return BenchmarkStatus.PASS.value
        self.regression_pct = ((self.value - self.baseline_value) / self.baseline_value) * 100.0
        if self.regression_pct > 10.0:
            self.passed = False
            return BenchmarkStatus.REGRESSION.value
        if self.regression_pct < -10.0:
            return BenchmarkStatus.IMPROVEMENT.value
        return BenchmarkStatus.PASS.value

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "value": self.value,
            "unit": self.unit,
            "threshold": self.threshold,
            "passed": self.passed,
            "baseline_value": self.baseline_value,
            "regression_pct": round(self.regression_pct, 2),
            "measured_at": self.measured_at.isoformat(),
        }


@dataclass
class BenchmarkHistory:
    """Historical trend data for a named benchmark."""

    name: str = ""
    measurements: list[dict] = field(default_factory=list)
    trend: str = "stable"
    regression_detected: bool = False

    def add_measurement(self, value: float, timestamp: datetime) -> None:
        """Record a new measurement and recalculate trend."""
        self.measurements.append({
            "value": value,
            "timestamp": timestamp.isoformat(),
        })
        self._recalculate_trend()

    def _recalculate_trend(self) -> None:
        """Determine trend direction from recent measurements."""
        if len(self.measurements) < 2:
            self.trend = "stable"
            self.regression_detected = False
            return
        recent = [m["value"] for m in self.measurements[-5:]]
        older = [m["value"] for m in self.measurements[:-5]] if len(self.measurements) > 5 else recent[:1]
        avg_recent = sum(recent) / len(recent)
        avg_older = sum(older) / len(older) if older else avg_recent
        diff_pct = ((avg_recent - avg_older) / avg_older * 100.0) if avg_older != 0 else 0.0
        if diff_pct > 10.0:
            self.trend = "regressing"
            self.regression_detected = True
        elif diff_pct < -10.0:
            self.trend = "improving"
            self.regression_detected = False
        else:
            self.trend = "stable"
            self.regression_detected = False

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "measurements": list(self.measurements),
            "trend": self.trend,
            "regression_detected": self.regression_detected,
        }


@dataclass
class CompatibilityResult:
    """Result of testing a single component on a single platform."""

    platform: str = ""
    component: str = ""
    status: str = "skip"
    details: str = ""
    tested_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "platform": self.platform,
            "component": self.component,
            "status": self.status,
            "details": self.details,
            "tested_at": self.tested_at.isoformat(),
        }


@dataclass
class CompatibilityReport:
    """Aggregated cross-platform compatibility report."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    results: list[CompatibilityResult] = field(default_factory=list)
    platforms: list[str] = field(default_factory=list)
    overall_status: str = "pending"
    generated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def evaluate(self) -> str:
        """Determine overall status from individual results."""
        if not self.results:
            self.overall_status = "no_data"
            return self.overall_status
        statuses = [r.status for r in self.results]
        if all(s == "pass" for s in statuses):
            self.overall_status = "pass"
        elif any(s == "fail" for s in statuses):
            self.overall_status = "fail"
        else:
            self.overall_status = "partial"
        return self.overall_status

    def results_by_platform(self, platform: str) -> list[CompatibilityResult]:
        """Filter results for a specific platform."""
        return [r for r in self.results if r.platform == platform]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "results": [r.to_dict() for r in self.results],
            "platforms": list(self.platforms),
            "overall_status": self.overall_status,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class FeatureFlag:
    """A feature flag for gradual rollout."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    enabled: bool = False
    category: str = ""
    default_value: bool = False
    rollout_date: str = ""
    removal_date: str = ""

    def toggle(self) -> bool:
        """Toggle the enabled state and return the new value."""
        self.enabled = not self.enabled
        return self.enabled

    def is_active(self) -> bool:
        """Return True if the flag is currently enabled."""
        return self.enabled

    def activate(self) -> None:
        """Force-enable the flag."""
        self.enabled = True

    def deactivate(self) -> None:
        """Force-disable the flag."""
        self.enabled = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "enabled": self.enabled,
            "category": self.category,
            "default_value": self.default_value,
            "rollout_date": self.rollout_date,
            "removal_date": self.removal_date,
        }


@dataclass
class ConfigProfile:
    """A named configuration profile for target audiences."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    target_audience: str = ""
    settings: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = "1.0"

    def get_setting(self, key: str, default: object = None) -> object:
        """Retrieve a single setting value."""
        return self.settings.get(key, default)

    def update_setting(self, key: str, value: object) -> None:
        """Add or update a setting."""
        self.settings[key] = value

    def remove_setting(self, key: str) -> bool:
        """Remove a setting. Return True if the key existed."""
        if key in self.settings:
            del self.settings[key]
            return True
        return False

    def merge_settings(self, overrides: dict) -> None:
        """Merge additional settings into this profile."""
        self.settings.update(overrides)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "target_audience": self.target_audience,
            "settings": dict(self.settings),
            "created_at": self.created_at.isoformat(),
            "version": self.version,
        }


@dataclass
class TraceSpan:
    """A single span within a diagnostic trace."""

    name: str = ""
    start_ms: float = 0.0
    end_ms: float = 0.0
    module: str = ""
    details: dict = field(default_factory=dict)

    def duration_ms(self) -> float:
        """Return the span duration in milliseconds."""
        return max(0.0, self.end_ms - self.start_ms)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "module": self.module,
            "details": dict(self.details),
            "duration_ms": round(self.duration_ms(), 3),
        }


@dataclass
class DiagnosticTrace:
    """A collection of trace spans representing a complete diagnostic capture."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    spans: list[TraceSpan] = field(default_factory=list)
    total_duration_ms: float = 0.0
    captured_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_span(self, span: TraceSpan) -> None:
        """Append a span and recalculate total duration."""
        self.spans.append(span)
        self._recalculate_duration()

    def _recalculate_duration(self) -> None:
        """Compute total duration from all spans."""
        if not self.spans:
            self.total_duration_ms = 0.0
            return
        earliest = min(s.start_ms for s in self.spans)
        latest = max(s.end_ms for s in self.spans)
        self.total_duration_ms = max(0.0, latest - earliest)

    def spans_by_module(self, module: str) -> list[TraceSpan]:
        """Filter spans belonging to a specific module."""
        return [s for s in self.spans if s.module == module]

    def slowest_span(self) -> Optional[TraceSpan]:
        """Return the span with the longest duration."""
        if not self.spans:
            return None
        return max(self.spans, key=lambda s: s.duration_ms())

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "spans": [s.to_dict() for s in self.spans],
            "total_duration_ms": round(self.total_duration_ms, 3),
            "captured_at": self.captured_at.isoformat(),
        }
