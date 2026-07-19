from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.performance import (
    Benchmark,
    BenchmarkHistory,
    PerformanceReport,
)
from app.quality.domain.interfaces.repositories import (
    BenchmarkHistoryRepository,
    BenchmarkRepository,
    PerformanceReportRepository,
)


class PerformanceService:
    def __init__(
        self,
        benchmark_repo: BenchmarkRepository,
        report_repo: PerformanceReportRepository,
        history_repo: BenchmarkHistoryRepository,
    ) -> None:
        self._benchmark_repo = benchmark_repo
        self._report_repo = report_repo
        self._history_repo = history_repo

    def run_benchmark(self, benchmark: Benchmark) -> Benchmark:
        benchmark.measured_at = datetime.now(timezone.utc)
        benchmark.passed = benchmark.value <= benchmark.threshold
        result = self._benchmark_repo.save(benchmark)
        history = self._history_repo.find_by_benchmark_name(benchmark.name)
        if history:
            history.measurements.append((datetime.now(timezone.utc), benchmark.value))
            history.trend = self._calculate_trend(history.measurements)
            history.regression_detected = self._detect_regression(history.measurements)
            self._history_repo.save(history)
        else:
            new_history = BenchmarkHistory(
                benchmark_name=benchmark.name,
                measurements=[(datetime.now(timezone.utc), benchmark.value)],
                trend="stable",
                regression_detected=False,
            )
            self._history_repo.save(new_history)
        return result

    def _calculate_trend(self, measurements: list[tuple[datetime, float]]) -> str:
        if len(measurements) < 2:
            return "stable"
        recent = measurements[-1][1]
        previous = measurements[-2][1]
        if recent < previous * 0.95:
            return "improving"
        if recent > previous * 1.05:
            return "degrading"
        return "stable"

    def _detect_regression(self, measurements: list[tuple[datetime, float]]) -> bool:
        if len(measurements) < 3:
            return False
        recent_three = [m[1] for m in measurements[-3:]]
        return all(recent_three[i] > recent_three[i + 1] for i in range(len(recent_three) - 1))

    def get_benchmarks(self, name: str | None = None) -> list[Benchmark]:
        if name:
            return self._benchmark_repo.find_by_name(name)
        return self._benchmark_repo.find_all()

    def generate_report(self, name: str, benchmarks: list[Benchmark]) -> PerformanceReport:
        for b in benchmarks:
            self._benchmark_repo.save(b)
        overall = 0.0
        if benchmarks:
            overall = sum(b.value for b in benchmarks) / len(benchmarks)
        report = PerformanceReport(
            name=name,
            benchmarks=benchmarks,
            overall_score=overall,
            generated_at=datetime.now(timezone.utc),
        )
        return self._report_repo.save(report)

    def get_report(self, report_id: str) -> PerformanceReport | None:
        return self._report_repo.find_by_id(report_id)

    def get_all_reports(self) -> list[PerformanceReport]:
        return self._report_repo.find_all()

    def get_history(self, benchmark_name: str) -> BenchmarkHistory | None:
        return self._history_repo.find_by_benchmark_name(benchmark_name)
