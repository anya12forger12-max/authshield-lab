"""Tests for PerformanceMonitor: timers, counters, metrics."""

import pytest
import asyncio
import time

from app.shared.monitoring.performance import (
    PerformanceMonitor,
    PerformanceMetric,
    TimingResult,
    get_performance_monitor,
)


@pytest.fixture
def monitor():
    return PerformanceMonitor()


class TestTimers:
    def test_start_and_stop(self, monitor):
        monitor.start_timer("test_op")
        result = monitor.stop_timer("test_op")
        assert result.success is True
        assert result.duration_ms >= 0
        assert result.operation == "test_op"

    def test_stop_without_start(self, monitor):
        result = monitor.stop_timer("nonexistent")
        assert result.success is False
        assert result.duration_ms == 0.0

    def test_stop_removes_timer(self, monitor):
        monitor.start_timer("op")
        monitor.stop_timer("op")
        result = monitor.stop_timer("op")
        assert result.success is False

    def test_overwrite_timer(self, monitor):
        monitor.start_timer("op")
        monitor.start_timer("op")
        result = monitor.stop_timer("op")
        assert result.success is True


class TestCounters:
    def test_increment_counter(self, monitor):
        monitor.increment_counter("requests")
        assert monitor.get_counter("requests") == 1

    def test_increment_by_amount(self, monitor):
        monitor.increment_counter("requests", 5)
        assert monitor.get_counter("requests") == 5

    def test_multiple_increments(self, monitor):
        monitor.increment_counter("requests")
        monitor.increment_counter("requests")
        monitor.increment_counter("requests")
        assert monitor.get_counter("requests") == 3

    def test_nonexistent_counter(self, monitor):
        assert monitor.get_counter("missing") == 0


class TestMetrics:
    def test_record_metric(self, monitor):
        monitor.record_metric("latency", 15.5, unit="ms")
        metrics = monitor.get_metrics(name="latency")
        assert len(metrics) == 1
        assert metrics[0].value == 15.5

    def test_record_metric_with_metadata(self, monitor):
        monitor.record_metric("latency", 10.0, endpoint="/api/login")
        metrics = monitor.get_metrics(name="latency")
        assert metrics[0].metadata["endpoint"] == "/api/login"

    def test_get_metrics_limit(self, monitor):
        for _ in range(10):
            monitor.record_metric("latency", 1.0)
        metrics = monitor.get_metrics(name="latency", limit=5)
        assert len(metrics) == 5

    def test_get_metrics_by_name(self, monitor):
        monitor.record_metric("latency", 1.0)
        monitor.record_metric("throughput", 100.0)
        metrics = monitor.get_metrics(name="latency")
        assert len(metrics) == 1

    def test_get_average(self, monitor):
        monitor.record_metric("latency", 10.0)
        monitor.record_metric("latency", 20.0)
        avg = monitor.get_average("latency")
        assert avg == 15.0

    def test_get_average_no_data(self, monitor):
        assert monitor.get_average("missing") is None


class TestAsyncTrack:
    @pytest.mark.asyncio
    async def test_track_success(self, monitor):
        async with monitor.track("async_op"):
            await asyncio.sleep(0.01)
        metrics = monitor.get_metrics(name="async_op")
        assert len(metrics) == 1
        assert metrics[0].value >= 0

    @pytest.mark.asyncio
    async def test_track_exception(self, monitor):
        with pytest.raises(ValueError):
            async with monitor.track("failing_op"):
                raise ValueError("test error")
        metrics = monitor.get_metrics(name="failing_op")
        assert len(metrics) == 1


class TestSummary:
    def test_get_summary(self, monitor):
        monitor.record_metric("latency", 10.0)
        monitor.record_metric("latency", 20.0)
        monitor.increment_counter("requests")
        summary = monitor.get_summary()
        assert "latency" in summary
        assert summary["latency"]["count"] == 2
        assert summary["latency"]["min"] == 10.0
        assert summary["latency"]["max"] == 20.0
        assert summary["counters"]["requests"] == 1

    def test_clear(self, monitor):
        monitor.record_metric("latency", 10.0)
        monitor.increment_counter("requests")
        monitor.start_timer("op")
        monitor.clear()
        assert monitor.get_metrics() == []
        assert monitor.get_counter("requests") == 0


class TestMetricEviction:
    def test_max_metrics_evicts_old(self):
        small_monitor = PerformanceMonitor(max_metrics=3)
        for i in range(5):
            small_monitor.record_metric("latency", float(i))
        metrics = small_monitor.get_metrics()
        assert len(metrics) == 3


class TestGetPerformanceMonitor:
    def test_singleton(self):
        m1 = get_performance_monitor()
        m2 = get_performance_monitor()
        assert m1 is m2

    def test_type(self):
        assert isinstance(get_performance_monitor(), PerformanceMonitor)
