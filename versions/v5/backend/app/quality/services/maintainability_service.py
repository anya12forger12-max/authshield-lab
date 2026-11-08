from __future__ import annotations

import math
from datetime import timezone

from app.quality.domain.entities.maintainability import (
    BuildHealth,
    ComplexityMetric,
    DependencyInfo,
    MaintainabilityIndex,
    TechnicalDebtItem,
)
from app.quality.domain.interfaces.repositories import (
    BuildHealthRepository,
    TechnicalDebtItemRepository,
)


class MaintainabilityService:
    def __init__(
        self,
        debt_repo: TechnicalDebtItemRepository,
        build_repo: BuildHealthRepository,
    ) -> None:
        self._debt_repo = debt_repo
        self._build_repo = build_repo

    def calculate_index(self, halstead_volume: float, cyclomatic: int, loc: int) -> MaintainabilityIndex:
        if loc <= 0:
            return MaintainabilityIndex(score=100.0, grade="A")
        raw = 171 - 5.2 * math.log(halstead_volume + 1) - 0.23 * cyclomatic - 16.2 * math.log(loc)
        score = max(0.0, min(100.0, raw))
        if score >= 85:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 50:
            grade = "C"
        elif score >= 30:
            grade = "D"
        else:
            grade = "F"
        return MaintainabilityIndex(score=score, grade=grade)

    def add_debt_item(self, item: TechnicalDebtItem) -> TechnicalDebtItem:
        return self._debt_repo.save(item)

    def get_debt_by_category(self, category: str) -> list[TechnicalDebtItem]:
        return self._debt_repo.find_by_category(category)

    def get_all_debt_items(self) -> list[TechnicalDebtItem]:
        return self._debt_repo.find_all()

    def get_total_estimated_hours(self) -> float:
        return sum(item.estimated_hours for item in self._debt_repo.find_all())

    def analyze_dependency(self, dep: DependencyInfo) -> bool:
        return dep.update_available or dep.vulnerabilities > 0

    def record_build(self, build: BuildHealth) -> BuildHealth:
        return self._build_repo.save(build)

    def get_builds_by_status(self, status: str) -> list[BuildHealth]:
        return self._build_repo.find_by_status(status)

    def get_all_builds(self) -> list[BuildHealth]:
        return self._build_repo.find_all()
