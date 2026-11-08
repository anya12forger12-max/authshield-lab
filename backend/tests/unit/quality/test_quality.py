"""Tests for quality entities and services — QualityScore, QualityDashboard, TestCase, Benchmark, QualityDashboardService."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.quality.domain.entities.quality import ModuleHealth, QualityDashboard, QualityScore


class TestQualityScore:
    def test_default_values(self):
        s = QualityScore()
        assert s.score == 0.0
        assert s.max_score == 100.0

    def test_custom_score(self):
        s = QualityScore(category="code_quality", score=85.0, meets_threshold=True)
        assert s.score == 85.0
        assert s.meets_threshold is True


class TestQualityDashboard:
    def test_defaults(self):
        d = QualityDashboard()
        assert d.overall_score == 0.0
        assert d.release_readiness is False

    def test_custom_dashboard(self):
        d = QualityDashboard(
            overall_score=88.5,
            test_coverage=90.0,
            code_quality=85.0,
            security_score=95.0,
            release_readiness=True,
        )
        assert d.overall_score == 88.5
        assert d.release_readiness is True


class TestModuleHealth:
    def test_default_values(self):
        m = ModuleHealth()
        assert m.status == "healthy"
        assert m.error_rate == 0.0

    def test_custom_health(self):
        m = ModuleHealth(module_name="auth", status="degraded", error_rate=5.2)
        assert m.module_name == "auth"
        assert m.status == "degraded"


class TestQualityDashboardService:
    def test_add_score(self):
        from app.quality.services.quality_dashboard_service import QualityDashboardService
        score_repo = MagicMock()
        score_repo.save = MagicMock(return_value=QualityScore(category="test", score=90.0))
        dash_repo = MagicMock()
        module_repo = MagicMock()
        service = QualityDashboardService(score_repo, dash_repo, module_repo)
        result = service.add_score(QualityScore(category="test", score=90.0))
        assert result.score == 90.0

    def test_generate_dashboard(self):
        from app.quality.services.quality_dashboard_service import QualityDashboardService
        scores = [
            QualityScore(category="test", score=90.0),
            QualityScore(category="code", score=80.0),
            QualityScore(category="a11y", score=70.0),
        ]
        score_repo = MagicMock()
        score_repo.find_all = MagicMock(return_value=scores)
        dash_repo = MagicMock()
        saved_dashboard = None

        def capture_save(d):
            nonlocal saved_dashboard
            saved_dashboard = d
            return d

        dash_repo.save = MagicMock(side_effect=capture_save)
        module_repo = MagicMock()
        service = QualityDashboardService(score_repo, dash_repo, module_repo)
        result = service.generate_dashboard()
        assert result.test_coverage == 90.0
        assert result.code_quality == 80.0
        assert result.a11y_compliance == 70.0

    def test_get_module_health(self):
        from app.quality.services.quality_dashboard_service import QualityDashboardService
        score_repo = MagicMock()
        dash_repo = MagicMock()
        module_repo = MagicMock()
        module_repo.find_all = MagicMock(return_value=[
            ModuleHealth(module_name="auth", status="healthy"),
        ])
        service = QualityDashboardService(score_repo, dash_repo, module_repo)
        result = service.get_module_health()
        assert len(result) == 1
        assert result[0].module_name == "auth"

    def test_update_module_health(self):
        from app.quality.services.quality_dashboard_service import QualityDashboardService
        score_repo = MagicMock()
        dash_repo = MagicMock()
        module_repo = MagicMock()
        module_repo.save = MagicMock()
        service = QualityDashboardService(score_repo, dash_repo, module_repo)
        mh = ModuleHealth(module_name="api", status="degraded")
        service.update_module_health(mh)
        module_repo.save.assert_called_once()

    def test_get_latest_dashboard(self):
        from app.quality.services.quality_dashboard_service import QualityDashboardService
        score_repo = MagicMock()
        dash_repo = MagicMock()
        dash_repo.find_latest = MagicMock(return_value=QualityDashboard(overall_score=95.0))
        module_repo = MagicMock()
        service = QualityDashboardService(score_repo, dash_repo, module_repo)
        result = service.get_latest_dashboard()
        assert result.overall_score == 95.0

    def test_aggregate_scores(self):
        from app.quality.services.quality_dashboard_service import QualityDashboardService
        score_repo = MagicMock()
        score_repo.find_all = MagicMock(return_value=[
            QualityScore(category="test", score=90.0),
            QualityScore(category="code", score=80.0),
        ])
        dash_repo = MagicMock()
        module_repo = MagicMock()
        service = QualityDashboardService(score_repo, dash_repo, module_repo)
        results = service.aggregate_scores()
        assert len(results) == 2


class TestTestCase:
    """Test the TestCase model from quality domain."""

    def test_create_test_case(self):
        from app.quality.domain.entities.testing import TestCase
        tc = TestCase(name="test_login", test_type="unit", module="auth")
        assert tc.name == "test_login"
        assert tc.test_type == "unit"

    def test_default_values(self):
        from app.quality.domain.entities.testing import TestCase
        tc = TestCase()
        assert tc.status == "not_run"
        assert tc.execution_time_ms == 0


class TestTestPlatformService:
    def test_create_test_case(self):
        from app.quality.services.test_platform_service import TestPlatformService
        from app.quality.domain.entities.testing import TestCase
        repo = MagicMock()
        suite_repo = MagicMock()
        coverage_repo = MagicMock()
        service = TestPlatformService(repo, suite_repo, coverage_repo)
        tc = TestCase(name="test_x")
        service.create_test_case(tc)
        repo.save.assert_called_with(tc)

    def test_get_test_case(self):
        from app.quality.services.test_platform_service import TestPlatformService
        from app.quality.domain.entities.testing import TestCase
        repo = MagicMock()
        repo.find_by_id = MagicMock(return_value=TestCase(name="test_y"))
        suite_repo = MagicMock()
        coverage_repo = MagicMock()
        service = TestPlatformService(repo, suite_repo, coverage_repo)
        result = service.get_test_case("1")
        assert result.name == "test_y"
