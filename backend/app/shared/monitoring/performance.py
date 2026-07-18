"""Offline performance monitoring — no telemetry."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional
from contextlib import asynccontextmanager


@dataclass
class PerformanceMetric:
    """A single recorded metric data point."""

    name: str
    value: float
    unit: str = "ms"
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TimingResult:
    """Result returned after stopping a named timer."""

    operation: str
    duration_ms: float
    success: bool = True
    metadata: dict[str, Any] = field(default_factory=dict)


class PerformanceMonitor:
    """Offline performance monitoring — no telemetry.

    Collects in-memory metrics (timers, counters, ad-hoc data points) and
    provides aggregate queries.  Designed for local development / debugging
    and does **not** ship data externally.
    """

    def __init__(self, max_metrics: int = 5000) -> None:
        self._metrics: list[PerformanceMetric] = []
        self._timers: dict[str, float] = {}
        self._counters: dict[str, int] = {}
        self._max_metrics: int = max_metrics

    # ------------------------------------------------------------------
    # Timers
    # ------------------------------------------------------------------

    def start_timer(self, name: str) -> None:
        """Start a named timer.

        If *name* is already running, the previous start time is silently
        overwritten.
        """
        self._timers[name] = time.perf_counter()

    def stop_timer(self, name: str) -> TimingResult:
        """Stop a named timer and record the elapsed time.

        Returns a :class:`TimingResult` with ``duration_ms``.  If the
        timer was never started the result carries ``duration_ms=0`` and
        ``success=False``.
        """
        start = self._timers.pop(name, None)
        if start is None:
            return TimingResult(operation=name, duration_ms=0.0, success=False)

        duration_ms = (time.perf_counter() - start) * 1000
        self._append_metric(
            PerformanceMetric(name=name, value=duration_ms, unit="ms")
        )
        return TimingResult(operation=name, duration_ms=duration_ms, success=True)

    @asynccontextmanager
    async def track(self, operation: str):
        """Async context-manager that times the enclosed block.

        Usage::

            async with monitor.track("db.query"):
                await db.execute(...)
        """
        self.start_timer(operation)
        try:
            yield
            self.stop_timer(operation)
        except Exception:
            self.stop_timer(operation)
            raise

    # ------------------------------------------------------------------
    # Ad-hoc metrics
    # ------------------------------------------------------------------

    def record_metric(
        self, name: str, value: float, unit: str = "ms", **metadata: Any
    ) -> None:
        """Record an arbitrary metric data point."""
        self._append_metric(
            PerformanceMetric(name=name, value=value, unit=unit, metadata=metadata)
        )

    # ------------------------------------------------------------------
    # Counters
    # ------------------------------------------------------------------

    def increment_counter(self, name: str, amount: int = 1) -> None:
        """Increment a named counter by *amount*."""
        self._counters[name] = self._counters.get(name, 0) + amount

    def get_counter(self, name: str) -> int:
        """Return the current value of a named counter (0 if never set)."""
        return self._counters.get(name, 0)

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_metrics(
        self, name: Optional[str] = None, limit: int = 100
    ) -> list[PerformanceMetric]:
        """Return recorded metrics, optionally filtered by name.

        Parameters
        ----------
        name:
            If provided, only metrics matching this name are returned.
        limit:
            Maximum number of metrics to return (most recent first).
        """
        metrics = self._metrics
        if name is not None:
            metrics = [m for m in metrics if m.name == name]
        return list(reversed(metrics[-limit:]))

    def get_average(self, name: str) -> Optional[float]:
        """Return the arithmetic mean of all values for *name*, or ``None``."""
        values = [m.value for m in self._metrics if m.name == name]
        if not values:
            return None
        return sum(values) / len(values)

    def get_summary(self) -> dict[str, Any]:
        """Return an aggregate summary of all collected metrics and counters."""
        names: dict[str, list[float]] = {}
        for m in self._metrics:
            names.setdefault(m.name, []).append(m.value)

        summary: dict[str, Any] = {}
        for name, values in sorted(names.items()):
            summary[name] = {
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
            }

        summary["counters"] = dict(self._counters)
        return summary

    def clear(self) -> None:
        """Discard all collected metrics, timers, and counters."""
        self._metrics.clear()
        self._timers.clear()
        self._counters.clear()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _append_metric(self, metric: PerformanceMetric) -> None:
        """Append a metric, evicting the oldest if the buffer is full."""
        self._metrics.append(metric)
        if len(self._metrics) > self._max_metrics:
            excess = len(self._metrics) - self._max_metrics
            self._metrics = self._metrics[excess:]


# ------------------------------------------------------------------
# Module-level singleton
# ------------------------------------------------------------------

_monitor: Optional[PerformanceMonitor] = None


def get_performance_monitor() -> PerformanceMonitor:
    """Return the global :class:`PerformanceMonitor`, creating it lazily."""
    global _monitor  # noqa: PLW0603
    if _monitor is None:
        _monitor = PerformanceMonitor()
    return _monitor
