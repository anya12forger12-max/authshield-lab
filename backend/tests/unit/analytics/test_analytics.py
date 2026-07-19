"""Tests for analytics entities and services."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.analytics.domain.entities.analytics import LearningProgress
from app.analytics.domain.entities.curriculum_evaluation import (
    CurriculumEvaluationResult,
    EvaluationRecommendation,
    TopicAnalysis,
    PrerequisiteGap,
)
from app.analytics.domain.entities.content_health import (
    ContentHealthDashboard,
    ContentHealthItem,
    MaintenanceSchedule,
    MaintenanceScheduleItem,
)
from app.analytics.domain.entities.learning_quality import (
    LearningQualityDashboard,
    LongitudinalComparison,
    QualityIndicator,
)


class TestLearningProgress:
    def test_defaults(self):
        p = LearningProgress()
        assert p.learner_id == ""
        assert p.competencies_achieved == 0

    def test_custom(self):
        p = LearningProgress(learner_id="u1", courses_enrolled=5, courses_completed=3, avg_score=85.0)
        assert p.learner_id == "u1"
        assert p.courses_enrolled == 5
        assert p.courses_completed == 3


class TestCurriculumEvaluationResult:
    def test_defaults(self):
        r = CurriculumEvaluationResult()
        assert r.assessment_alignment == 0.0
        assert r.review_frequency_days == 30

    def test_custom(self):
        r = CurriculumEvaluationResult(
            curriculum_balance={"math": 50.0, "science": 50.0},
            assessment_alignment=75.0,
            a11y_coverage=80.0,
        )
        assert r.curriculum_balance["math"] == 50.0
        assert r.a11y_coverage == 80.0


class TestEvaluationRecommendation:
    def test_defaults(self):
        r = EvaluationRecommendation()
        assert r.priority == "medium"

    def test_high_priority(self):
        r = EvaluationRecommendation(category="alignment", priority="high", recommendation="Fix alignment")
        assert r.priority == "high"


class TestTopicAnalysis:
    def test_defaults(self):
        t = TopicAnalysis()
        assert t.coverage_pct == 0.0
        assert t.gaps == []


class TestPrerequisiteGap:
    def test_defaults(self):
        g = PrerequisiteGap()
        assert g.severity == "medium"


class TestContentHealthItem:
    def test_defaults(self):
        h = ContentHealthItem()
        assert h.version_status == "current"
        assert h.broken_refs == 0


class TestContentHealthDashboard:
    def test_defaults(self):
        d = ContentHealthDashboard()
        assert d.total_items == 0
        assert d.healthy == 0


class TestMaintenanceSchedule:
    def test_defaults(self):
        s = MaintenanceSchedule()
        assert s.items == []


class TestLearningQualityDashboard:
    def test_defaults(self):
        d = LearningQualityDashboard()
        assert d.completion_rates == 0.0


class TestLongitudinalComparison:
    def test_improving_trend(self):
        c = LongitudinalComparison(term="2026", value=85.0, change_pct=5.0, trend="improving")
        assert c.trend == "improving"


class TestQualityIndicator:
    def test_exceeds_benchmark(self):
        i = QualityIndicator(name="rate", value=90.0, benchmark=80.0, status="exceeds")
        assert i.status == "exceeds"


class TestAnalyticsCenterService:
    @pytest.fixture
    def repos(self):
        return MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()

    @pytest.fixture
    def service(self, repos):
        from app.analytics.services.analytics_center_service import AnalyticsCenterService
        return AnalyticsCenterService(*repos)

    @pytest.mark.asyncio
    async def test_record_learning_progress(self, service, repos):
        progress_repo = repos[1]
        progress_repo.get_by_learner_id = AsyncMock(return_value=None)
        progress_repo.create = AsyncMock(return_value=LearningProgress(learner_id="u1", courses_enrolled=3))
        result = await service.record_learning_progress("u1", courses_enrolled=3)
        assert result.learner_id == "u1"
        assert result.courses_enrolled == 3

    @pytest.mark.asyncio
    async def test_record_course_completion(self, service, repos):
        course_repo = repos[2]
        from app.analytics.domain.entities.analytics import CourseCompletion
        course_repo.get_by_course_id = AsyncMock(return_value=None)
        course_repo.create = AsyncMock(return_value=CourseCompletion(
            course_id="c1", course_name="Course1", enrolled=10, completed=5, completion_rate=50.0
        ))
        result = await service.record_course_completion("c1", course_name="Course1", enrolled=10, completed=5)
        assert result.completion_rate == 50.0

    @pytest.mark.asyncio
    async def test_get_aggregate_metrics(self, service, repos):
        progress_repo, course_repo, assess_repo, _, content_repo = repos[1:6]
        progress_repo.get_all = AsyncMock(return_value=[LearningProgress(learner_id="u1")])
        course_repo.get_all = AsyncMock(return_value=[])
        assess_repo.get_all = AsyncMock(return_value=[])
        content_repo.get_all = AsyncMock(return_value=[])
        result = await service.get_aggregate_metrics()
        assert result["total_learners"] == 1


class TestCurriculumEvaluationService:
    @pytest.mark.asyncio
    async def test_evaluate_curriculum(self):
        from app.analytics.services.curriculum_evaluation_service import CurriculumEvaluationService
        eval_repo = MagicMock()
        eval_repo.create = AsyncMock()
        rec_repo = MagicMock()
        rec_repo.create = AsyncMock()
        service = CurriculumEvaluationService(eval_repo, rec_repo)
        result = await service.evaluate_curriculum(
            topics=["math"], competencies=["comp1"], mapped_competencies=["comp1"]
        )
        assert result.assessment_alignment >= 0

    @pytest.mark.asyncio
    async def test_generate_recommendations(self):
        from app.analytics.services.curriculum_evaluation_service import CurriculumEvaluationService
        eval_repo = MagicMock()
        rec_repo = MagicMock()
        rec_repo.create = AsyncMock()
        service = CurriculumEvaluationService(eval_repo, rec_repo)
        evaluation = CurriculumEvaluationResult(
            assessment_alignment=50.0,
            a11y_coverage=60.0,
            content_freshness=70.0,
            redundant_content=[{"title": "dup"}],
            missing_prerequisites=[{"missing_from": "x", "needed_by": "y"}],
        )
        recs = await service.generate_recommendations(evaluation)
        assert len(recs) >= 5

    @pytest.mark.asyncio
    async def test_analyze_topics(self):
        from app.analytics.services.curriculum_evaluation_service import CurriculumEvaluationService
        eval_repo = MagicMock()
        rec_repo = MagicMock()
        service = CurriculumEvaluationService(eval_repo, rec_repo)
        topics = ["math", "science"]
        result = await service.analyze_topics(topics, [{"title": "math 101", "topic": "math"}])
        assert len(result) == 2
        math_analysis = [r for r in result if r.topic == "math"][0]
        assert math_analysis.coverage_pct > 0


class TestContentHealthService:
    @pytest.mark.asyncio
    async def test_add_content_item(self):
        from app.analytics.services.content_health_service import ContentHealthService
        from app.analytics.domain.entities.content_health import ContentHealthItem
        content_repo = MagicMock()
        content_repo.get_by_content_id = AsyncMock(return_value=None)
        content_repo.create = AsyncMock(return_value=ContentHealthItem(
            content_id="c1", content_type="course", title="Test"
        ))
        service = ContentHealthService(content_repo, MagicMock(), MagicMock())
        result = await service.add_content_item("c1", content_type="course", title="Test")
        assert result.content_id == "c1"

    @pytest.mark.asyncio
    async def test_generate_health_dashboard(self):
        from app.analytics.services.content_health_service import ContentHealthService
        content_repo = MagicMock()
        content_repo.get_all = AsyncMock(return_value=[
            ContentHealthItem(content_id="c1", broken_refs=0, doc_completeness=100.0),
            ContentHealthItem(content_id="c2", broken_refs=5, doc_completeness=50.0),
        ])
        dashboard_repo = MagicMock()
        dashboard_repo.create = AsyncMock()
        service = ContentHealthService(content_repo, dashboard_repo, MagicMock())
        dashboard = await service.generate_health_dashboard()
        assert dashboard.total_items == 2

    @pytest.mark.asyncio
    async def test_get_items_needing_attention(self):
        from app.analytics.services.content_health_service import ContentHealthService
        content_repo = MagicMock()
        content_repo.get_all = AsyncMock(return_value=[
            ContentHealthItem(
                content_id="c1", broken_refs=0, doc_completeness=100.0,
                publication_quality=100.0, dependency_health=100.0,
                a11y_status="compliant", localization_status="complete",
            ),
            ContentHealthItem(content_id="c2", broken_refs=5, doc_completeness=50.0),
        ])
        service = ContentHealthService(content_repo, MagicMock(), MagicMock())
        items = await service.get_items_needing_attention()
        assert len(items) == 1


class TestLearningQualityService:
    @pytest.mark.asyncio
    async def test_generate_dashboard(self):
        from app.analytics.services.learning_quality_service import LearningQualityService
        repo = MagicMock()
        repo.create = AsyncMock()
        service = LearningQualityService(repo)
        result = await service.generate_dashboard(completion_rates=85.0, lab_completion=90.0)
        assert result.completion_rates == 85.0
        assert result.lab_completion == 90.0

    @pytest.mark.asyncio
    async def test_generate_longitudinal_comparisons(self):
        from app.analytics.services.learning_quality_service import LearningQualityService
        repo = MagicMock()
        service = LearningQualityService(repo)
        current = LearningQualityDashboard(completion_rates=85.0, lab_completion=90.0)
        previous = LearningQualityDashboard(completion_rates=80.0, lab_completion=85.0)
        comparisons = await service.generate_longitudinal_comparisons(current, previous)
        assert len(comparisons) > 0

    @pytest.mark.asyncio
    async def test_generate_quality_indicators(self):
        from app.analytics.services.learning_quality_service import LearningQualityService
        repo = MagicMock()
        service = LearningQualityService(repo)
        dashboard = LearningQualityDashboard(completion_rates=90.0, lab_completion=95.0)
        indicators = await service.generate_quality_indicators(dashboard)
        assert len(indicators) == 8
        assert indicators[0].status == "exceeds"

    @pytest.mark.asyncio
    async def test_compute_overall_quality_score(self):
        from app.analytics.services.learning_quality_service import LearningQualityService
        repo = MagicMock()
        service = LearningQualityService(repo)
        dashboard = LearningQualityDashboard(
            completion_rates=100.0, learning_objective_achievement=100.0,
            competency_growth=100.0, lab_completion=100.0,
            portfolio_progress=100.0, certification_progress=100.0,
            reflection_participation=100.0, instructor_review_status=100.0,
        )
        score = await service.compute_overall_quality_score(dashboard)
        assert score == 100.0
