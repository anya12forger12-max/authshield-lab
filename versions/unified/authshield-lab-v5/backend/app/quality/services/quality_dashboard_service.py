from __future__ import annotations

from datetime import datetime, timezone

from app.quality.domain.entities.quality import ModuleHealth, QualityDashboard, QualityScore
from app.quality.domain.interfaces.repositories import (
    ModuleHealthRepository,
    QualityDashboardRepository,
    QualityScoreRepository,
)


class QualityDashboardService:
    def __init__(
        self,
        score_repo: QualityScoreRepository,
        dashboard_repo: QualityDashboardRepository,
        module_health_repo: ModuleHealthRepository,
    ) -> None:
        self._score_repo = score_repo
        self._dashboard_repo = dashboard_repo
        self._module_health_repo = module_health_repo

    def aggregate_scores(self) -> list[QualityScore]:
        return self._score_repo.find_all()

    def generate_dashboard(self) -> QualityDashboard:
        scores = self._score_repo.find_all()
        overall = 0.0
        count = len(scores)
        dash = QualityDashboard()
        if count > 0:
            overall = sum(s.score for s in scores) / count
        dash.overall_score = overall
        for s in scores:
            cat = s.category.lower()
            if "test" in cat:
                dash.test_coverage = s.score
            elif "code" in cat:
                dash.code_quality = s.score
            elif "a11y" in cat or "access" in cat:
                dash.a11y_compliance = s.score
            elif "doc" in cat:
                dash.doc_coverage = s.score
            elif "perf" in cat:
                dash.performance_score = s.score
            elif "security" in cat:
                dash.security_score = s.score
            elif "local" in cat:
                dash.localization_coverage = s.score
            elif "release" in cat:
                dash.release_readiness = s.score >= 80.0
        dash.generated_at = datetime.now(timezone.utc)
        return self._dashboard_repo.save(dash)

    def get_module_health(self) -> list[ModuleHealth]:
        return self._module_health_repo.find_all()

    def update_module_health(self, health: ModuleHealth) -> ModuleHealth:
        return self._module_health_repo.save(health)

    def get_latest_dashboard(self) -> QualityDashboard | None:
        return self._dashboard_repo.find_latest()

    def add_score(self, score: QualityScore) -> QualityScore:
        return self._score_repo.save(score)
