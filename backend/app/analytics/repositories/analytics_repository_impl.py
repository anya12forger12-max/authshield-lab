"""In-memory repository implementations for analytics entities."""

from __future__ import annotations

import copy
from typing import Optional

from ..domain.interfaces import (
    IActionPlanItemRepository,
    IActionPlanRepository,
    IAnalyticsDashboardRepository,
    IAssessmentOutcomeRepository,
    IContentHealthDashboardRepository,
    IContentHealthRepository,
    IContentUsageRepository,
    ICourseCompletionRepository,
    ICurriculumCoverageRepository,
    ICurriculumEvaluationRepository,
    IExecutiveSummaryRepository,
    IEvaluationRecommendationRepository,
    IImprovementInitiativeRepository,
    IImprovementReportRepository,
    ILearningProgressRepository,
    IMaintenanceScheduleRepository,
    IProgramEvaluationRepository,
    IQualityDashboardRepository,
)
from ..domain.entities.analytics import (
    AssessmentOutcome,
    ContentUsage,
    CurriculumCoverage,
    EducationalAnalyticsDashboard,
    LearningProgress,
    CourseCompletion,
)
from ..domain.entities.learning_quality import LearningQualityDashboard
from ..domain.entities.curriculum_evaluation import (
    CurriculumEvaluationResult,
    EvaluationRecommendation,
)
from ..domain.entities.content_health import (
    ContentHealthDashboard,
    ContentHealthItem,
    MaintenanceSchedule,
)
from ..domain.entities.program_evaluation import ExecutiveSummary, ProgramEvaluation
from ..domain.entities.continuous_improvement import (
    ActionPlan,
    ActionPlanItem,
    ImprovementInitiative,
    ImprovementReport,
)


def _paginate(items: list, page: int, per_page: int) -> dict:
    """Helper to paginate an in-memory list."""
    total = len(items)
    start = (page - 1) * per_page
    end = start + per_page
    pages = max(1, (total + per_page - 1) // per_page) if per_page > 0 else 1
    return {
        "items": [copy.deepcopy(i) for i in items[start:end]],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": pages,
    }


class InMemoryAnalyticsDashboardRepository(IAnalyticsDashboardRepository):
    """In-memory store for EducationalAnalyticsDashboard entities."""

    def __init__(self) -> None:
        self._store: dict[str, EducationalAnalyticsDashboard] = {}

    async def create(self, dashboard: EducationalAnalyticsDashboard) -> EducationalAnalyticsDashboard:
        self._store[dashboard.id] = copy.deepcopy(dashboard)
        return self._store[dashboard.id]

    async def get_by_id(self, dashboard_id: str) -> Optional[EducationalAnalyticsDashboard]:
        item = self._store.get(dashboard_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)

    async def get_latest(self) -> Optional[EducationalAnalyticsDashboard]:
        if not self._store:
            return None
        latest = max(self._store.values(), key=lambda d: d.generated_at)
        return copy.deepcopy(latest)

    async def delete(self, dashboard_id: str) -> bool:
        if dashboard_id in self._store:
            del self._store[dashboard_id]
            return True
        return False


class InMemoryLearningProgressRepository(ILearningProgressRepository):
    """In-memory store for LearningProgress entities."""

    def __init__(self) -> None:
        self._store: dict[str, LearningProgress] = {}

    async def create(self, progress: LearningProgress) -> LearningProgress:
        self._store[progress.learner_id] = copy.deepcopy(progress)
        return self._store[progress.learner_id]

    async def get_by_learner_id(self, learner_id: str) -> Optional[LearningProgress]:
        item = self._store.get(learner_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[LearningProgress]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, learner_id: str, data: dict) -> Optional[LearningProgress]:
        item = self._store.get(learner_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryCourseCompletionRepository(ICourseCompletionRepository):
    """In-memory store for CourseCompletion entities."""

    def __init__(self) -> None:
        self._store: dict[str, CourseCompletion] = {}

    async def create(self, completion: CourseCompletion) -> CourseCompletion:
        self._store[completion.course_id] = copy.deepcopy(completion)
        return self._store[completion.course_id]

    async def get_by_course_id(self, course_id: str) -> Optional[CourseCompletion]:
        item = self._store.get(course_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[CourseCompletion]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, course_id: str, data: dict) -> Optional[CourseCompletion]:
        item = self._store.get(course_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryAssessmentOutcomeRepository(IAssessmentOutcomeRepository):
    """In-memory store for AssessmentOutcome entities."""

    def __init__(self) -> None:
        self._store: dict[str, AssessmentOutcome] = {}

    async def create(self, outcome: AssessmentOutcome) -> AssessmentOutcome:
        self._store[outcome.assessment_id] = copy.deepcopy(outcome)
        return self._store[outcome.assessment_id]

    async def get_by_assessment_id(self, assessment_id: str) -> Optional[AssessmentOutcome]:
        item = self._store.get(assessment_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[AssessmentOutcome]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, assessment_id: str, data: dict) -> Optional[AssessmentOutcome]:
        item = self._store.get(assessment_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryCurriculumCoverageRepository(ICurriculumCoverageRepository):
    """In-memory store for CurriculumCoverage entities."""

    def __init__(self) -> None:
        self._store: dict[str, CurriculumCoverage] = {}

    async def create(self, coverage: CurriculumCoverage) -> CurriculumCoverage:
        self._store[coverage.framework_id] = copy.deepcopy(coverage)
        return self._store[coverage.framework_id]

    async def get_by_framework_id(self, framework_id: str) -> Optional[CurriculumCoverage]:
        item = self._store.get(framework_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[CurriculumCoverage]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, framework_id: str, data: dict) -> Optional[CurriculumCoverage]:
        item = self._store.get(framework_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryContentUsageRepository(IContentUsageRepository):
    """In-memory store for ContentUsage entities."""

    def __init__(self) -> None:
        self._store: dict[str, ContentUsage] = {}

    async def create(self, usage: ContentUsage) -> ContentUsage:
        self._store[usage.content_id] = copy.deepcopy(usage)
        return self._store[usage.content_id]

    async def get_by_content_id(self, content_id: str) -> Optional[ContentUsage]:
        item = self._store.get(content_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[ContentUsage]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, content_id: str, data: dict) -> Optional[ContentUsage]:
        item = self._store.get(content_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryQualityDashboardRepository(IQualityDashboardRepository):
    """In-memory store for LearningQualityDashboard entities."""

    def __init__(self) -> None:
        self._store: dict[str, LearningQualityDashboard] = {}

    async def create(self, dashboard: LearningQualityDashboard) -> LearningQualityDashboard:
        self._store[dashboard.id] = copy.deepcopy(dashboard)
        return self._store[dashboard.id]

    async def get_by_id(self, dashboard_id: str) -> Optional[LearningQualityDashboard]:
        item = self._store.get(dashboard_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)

    async def get_latest(self) -> Optional[LearningQualityDashboard]:
        if not self._store:
            return None
        latest = max(self._store.values(), key=lambda d: d.generated_at)
        return copy.deepcopy(latest)


class InMemoryCurriculumEvaluationRepository(ICurriculumEvaluationRepository):
    """In-memory store for CurriculumEvaluationResult entities."""

    def __init__(self) -> None:
        self._store: dict[str, CurriculumEvaluationResult] = {}

    async def create(self, result: CurriculumEvaluationResult) -> CurriculumEvaluationResult:
        self._store[result.id] = copy.deepcopy(result)
        return self._store[result.id]

    async def get_by_id(self, evaluation_id: str) -> Optional[CurriculumEvaluationResult]:
        item = self._store.get(evaluation_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)


class InMemoryEvaluationRecommendationRepository(IEvaluationRecommendationRepository):
    """In-memory store for EvaluationRecommendation entities."""

    def __init__(self) -> None:
        self._store: dict[str, EvaluationRecommendation] = {}

    async def create(self, rec: EvaluationRecommendation) -> EvaluationRecommendation:
        self._store[rec.id] = copy.deepcopy(rec)
        return self._store[rec.id]

    async def get_by_id(self, rec_id: str) -> Optional[EvaluationRecommendation]:
        item = self._store.get(rec_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[EvaluationRecommendation]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, rec_id: str, data: dict) -> Optional[EvaluationRecommendation]:
        item = self._store.get(rec_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryContentHealthRepository(IContentHealthRepository):
    """In-memory store for ContentHealthItem entities."""

    def __init__(self) -> None:
        self._store: dict[str, ContentHealthItem] = {}

    async def create(self, item: ContentHealthItem) -> ContentHealthItem:
        self._store[item.id] = copy.deepcopy(item)
        return self._store[item.id]

    async def get_by_id(self, item_id: str) -> Optional[ContentHealthItem]:
        item = self._store.get(item_id)
        return copy.deepcopy(item) if item else None

    async def get_by_content_id(self, content_id: str) -> Optional[ContentHealthItem]:
        for item in self._store.values():
            if item.content_id == content_id:
                return copy.deepcopy(item)
        return None

    async def get_all(self) -> list[ContentHealthItem]:
        return [copy.deepcopy(v) for v in self._store.values()]

    async def update(self, item_id: str, data: dict) -> Optional[ContentHealthItem]:
        item = self._store.get(item_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)

    async def delete(self, item_id: str) -> bool:
        if item_id in self._store:
            del self._store[item_id]
            return True
        return False


class InMemoryContentHealthDashboardRepository(IContentHealthDashboardRepository):
    """In-memory store for ContentHealthDashboard entities."""

    def __init__(self) -> None:
        self._store: dict[str, ContentHealthDashboard] = {}

    async def create(self, dashboard: ContentHealthDashboard) -> ContentHealthDashboard:
        self._store[dashboard.id] = copy.deepcopy(dashboard)
        return self._store[dashboard.id]

    async def get_by_id(self, dashboard_id: str) -> Optional[ContentHealthDashboard]:
        item = self._store.get(dashboard_id)
        return copy.deepcopy(item) if item else None

    async def get_latest(self) -> Optional[ContentHealthDashboard]:
        if not self._store:
            return None
        latest = max(self._store.values(), key=lambda d: d.generated_at)
        return copy.deepcopy(latest)


class InMemoryMaintenanceScheduleRepository(IMaintenanceScheduleRepository):
    """In-memory store for MaintenanceSchedule entities."""

    def __init__(self) -> None:
        self._store: dict[str, MaintenanceSchedule] = {}

    async def create(self, schedule: MaintenanceSchedule) -> MaintenanceSchedule:
        self._store[schedule.id] = copy.deepcopy(schedule)
        return self._store[schedule.id]

    async def get_by_id(self, schedule_id: str) -> Optional[MaintenanceSchedule]:
        item = self._store.get(schedule_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self) -> list[MaintenanceSchedule]:
        return [copy.deepcopy(v) for v in self._store.values()]


class InMemoryProgramEvaluationRepository(IProgramEvaluationRepository):
    """In-memory store for ProgramEvaluation entities."""

    def __init__(self) -> None:
        self._store: dict[str, ProgramEvaluation] = {}

    async def create(self, evaluation: ProgramEvaluation) -> ProgramEvaluation:
        self._store[evaluation.id] = copy.deepcopy(evaluation)
        return self._store[evaluation.id]

    async def get_by_id(self, evaluation_id: str) -> Optional[ProgramEvaluation]:
        item = self._store.get(evaluation_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)


class InMemoryExecutiveSummaryRepository(IExecutiveSummaryRepository):
    """In-memory store for ExecutiveSummary entities."""

    def __init__(self) -> None:
        self._store: list[ExecutiveSummary] = []

    async def create(self, summary: ExecutiveSummary) -> ExecutiveSummary:
        self._store.append(copy.deepcopy(summary))
        return self._store[-1]

    async def get_latest(self) -> Optional[ExecutiveSummary]:
        if not self._store:
            return None
        latest = max(self._store, key=lambda s: s.generated_at)
        return copy.deepcopy(latest)

    async def get_all(self) -> list[ExecutiveSummary]:
        return [copy.deepcopy(v) for v in self._store]


class InMemoryActionPlanRepository(IActionPlanRepository):
    """In-memory store for ActionPlan entities."""

    def __init__(self) -> None:
        self._store: dict[str, ActionPlan] = {}

    async def create(self, plan: ActionPlan) -> ActionPlan:
        self._store[plan.id] = copy.deepcopy(plan)
        return self._store[plan.id]

    async def get_by_id(self, plan_id: str) -> Optional[ActionPlan]:
        item = self._store.get(plan_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)

    async def update(self, plan_id: str, data: dict) -> Optional[ActionPlan]:
        item = self._store.get(plan_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryActionPlanItemRepository(IActionPlanItemRepository):
    """In-memory store for ActionPlanItem entities."""

    def __init__(self) -> None:
        self._store: dict[str, ActionPlanItem] = {}

    async def create(self, item: ActionPlanItem) -> ActionPlanItem:
        self._store[item.id] = copy.deepcopy(item)
        return self._store[item.id]

    async def get_by_id(self, item_id: str) -> Optional[ActionPlanItem]:
        item = self._store.get(item_id)
        return copy.deepcopy(item) if item else None

    async def get_by_plan_id(self, plan_id: str) -> list[ActionPlanItem]:
        return [
            copy.deepcopy(v) for v in self._store.values() if v.plan_id == plan_id
        ]

    async def update(self, item_id: str, data: dict) -> Optional[ActionPlanItem]:
        item = self._store.get(item_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryImprovementInitiativeRepository(IImprovementInitiativeRepository):
    """In-memory store for ImprovementInitiative entities."""

    def __init__(self) -> None:
        self._store: dict[str, ImprovementInitiative] = {}

    async def create(self, initiative: ImprovementInitiative) -> ImprovementInitiative:
        self._store[initiative.id] = copy.deepcopy(initiative)
        return self._store[initiative.id]

    async def get_by_id(self, initiative_id: str) -> Optional[ImprovementInitiative]:
        item = self._store.get(initiative_id)
        return copy.deepcopy(item) if item else None

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)

    async def update(self, initiative_id: str, data: dict) -> Optional[ImprovementInitiative]:
        item = self._store.get(initiative_id)
        if item is None:
            return None
        for key, value in data.items():
            if hasattr(item, key):
                setattr(item, key, value)
        return copy.deepcopy(item)


class InMemoryImprovementReportRepository(IImprovementReportRepository):
    """In-memory store for ImprovementReport entities."""

    def __init__(self) -> None:
        self._store: dict[str, ImprovementReport] = {}

    async def create(self, report: ImprovementReport) -> ImprovementReport:
        self._store[report.id] = copy.deepcopy(report)
        return self._store[report.id]

    async def get_by_id(self, report_id: str) -> Optional[ImprovementReport]:
        item = self._store.get(report_id)
        return copy.deepcopy(item) if item else None

    async def get_by_initiative_id(self, initiative_id: str) -> list[ImprovementReport]:
        return [
            copy.deepcopy(v)
            for v in self._store.values()
            if v.initiative_id == initiative_id
        ]

    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        return _paginate(list(self._store.values()), page, per_page)
