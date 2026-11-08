"""Abstract repository interfaces for analytics entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.analytics import (
    AssessmentOutcome,
    ContentUsage,
    CurriculumCoverage,
    EducationalAnalyticsDashboard,
    FilterOptions,
    LearningProgress,
    CourseCompletion,
)
from ..entities.learning_quality import (
    LearningQualityDashboard,
    LongitudinalComparison,
    QualityIndicator,
)
from ..entities.curriculum_evaluation import (
    CurriculumEvaluationResult,
    EvaluationRecommendation,
    PrerequisiteGap,
    TopicAnalysis,
)
from ..entities.content_health import (
    ContentHealthDashboard,
    ContentHealthItem,
    MaintenanceSchedule,
)
from ..entities.program_evaluation import ExecutiveSummary, ProgramEvaluation
from ..entities.continuous_improvement import (
    ActionPlan,
    ActionPlanItem,
    HistoricalComparison,
    ImprovementInitiative,
    ImprovementMetric,
    ImprovementReport,
)


class IAnalyticsDashboardRepository(ABC):
    """Interface for educational analytics dashboard persistence."""

    @abstractmethod
    async def create(self, dashboard: EducationalAnalyticsDashboard) -> EducationalAnalyticsDashboard:
        ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> Optional[EducationalAnalyticsDashboard]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def get_latest(self) -> Optional[EducationalAnalyticsDashboard]:
        ...

    @abstractmethod
    async def delete(self, dashboard_id: str) -> bool:
        ...


class ILearningProgressRepository(ABC):
    """Interface for learning progress persistence."""

    @abstractmethod
    async def create(self, progress: LearningProgress) -> LearningProgress:
        ...

    @abstractmethod
    async def get_by_learner_id(self, learner_id: str) -> Optional[LearningProgress]:
        ...

    @abstractmethod
    async def get_all(self) -> list[LearningProgress]:
        ...

    @abstractmethod
    async def update(self, learner_id: str, data: dict) -> Optional[LearningProgress]:
        ...


class ICourseCompletionRepository(ABC):
    """Interface for course completion persistence."""

    @abstractmethod
    async def create(self, completion: CourseCompletion) -> CourseCompletion:
        ...

    @abstractmethod
    async def get_by_course_id(self, course_id: str) -> Optional[CourseCompletion]:
        ...

    @abstractmethod
    async def get_all(self) -> list[CourseCompletion]:
        ...

    @abstractmethod
    async def update(self, course_id: str, data: dict) -> Optional[CourseCompletion]:
        ...


class IAssessmentOutcomeRepository(ABC):
    """Interface for assessment outcome persistence."""

    @abstractmethod
    async def create(self, outcome: AssessmentOutcome) -> AssessmentOutcome:
        ...

    @abstractmethod
    async def get_by_assessment_id(self, assessment_id: str) -> Optional[AssessmentOutcome]:
        ...

    @abstractmethod
    async def get_all(self) -> list[AssessmentOutcome]:
        ...

    @abstractmethod
    async def update(self, assessment_id: str, data: dict) -> Optional[AssessmentOutcome]:
        ...


class ICurriculumCoverageRepository(ABC):
    """Interface for curriculum coverage persistence."""

    @abstractmethod
    async def create(self, coverage: CurriculumCoverage) -> CurriculumCoverage:
        ...

    @abstractmethod
    async def get_by_framework_id(self, framework_id: str) -> Optional[CurriculumCoverage]:
        ...

    @abstractmethod
    async def get_all(self) -> list[CurriculumCoverage]:
        ...

    @abstractmethod
    async def update(self, framework_id: str, data: dict) -> Optional[CurriculumCoverage]:
        ...


class IContentUsageRepository(ABC):
    """Interface for content usage persistence."""

    @abstractmethod
    async def create(self, usage: ContentUsage) -> ContentUsage:
        ...

    @abstractmethod
    async def get_by_content_id(self, content_id: str) -> Optional[ContentUsage]:
        ...

    @abstractmethod
    async def get_all(self) -> list[ContentUsage]:
        ...

    @abstractmethod
    async def update(self, content_id: str, data: dict) -> Optional[ContentUsage]:
        ...


class IQualityDashboardRepository(ABC):
    """Interface for learning quality dashboard persistence."""

    @abstractmethod
    async def create(self, dashboard: LearningQualityDashboard) -> LearningQualityDashboard:
        ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> Optional[LearningQualityDashboard]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def get_latest(self) -> Optional[LearningQualityDashboard]:
        ...


class ICurriculumEvaluationRepository(ABC):
    """Interface for curriculum evaluation persistence."""

    @abstractmethod
    async def create(self, result: CurriculumEvaluationResult) -> CurriculumEvaluationResult:
        ...

    @abstractmethod
    async def get_by_id(self, evaluation_id: str) -> Optional[CurriculumEvaluationResult]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...


class IEvaluationRecommendationRepository(ABC):
    """Interface for evaluation recommendation persistence."""

    @abstractmethod
    async def create(self, rec: EvaluationRecommendation) -> EvaluationRecommendation:
        ...

    @abstractmethod
    async def get_by_id(self, rec_id: str) -> Optional[EvaluationRecommendation]:
        ...

    @abstractmethod
    async def get_all(self) -> list[EvaluationRecommendation]:
        ...

    @abstractmethod
    async def update(self, rec_id: str, data: dict) -> Optional[EvaluationRecommendation]:
        ...


class IContentHealthRepository(ABC):
    """Interface for content health item persistence."""

    @abstractmethod
    async def create(self, item: ContentHealthItem) -> ContentHealthItem:
        ...

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[ContentHealthItem]:
        ...

    @abstractmethod
    async def get_by_content_id(self, content_id: str) -> Optional[ContentHealthItem]:
        ...

    @abstractmethod
    async def get_all(self) -> list[ContentHealthItem]:
        ...

    @abstractmethod
    async def update(self, item_id: str, data: dict) -> Optional[ContentHealthItem]:
        ...

    @abstractmethod
    async def delete(self, item_id: str) -> bool:
        ...


class IContentHealthDashboardRepository(ABC):
    """Interface for content health dashboard persistence."""

    @abstractmethod
    async def create(self, dashboard: ContentHealthDashboard) -> ContentHealthDashboard:
        ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> Optional[ContentHealthDashboard]:
        ...

    @abstractmethod
    async def get_latest(self) -> Optional[ContentHealthDashboard]:
        ...


class IMaintenanceScheduleRepository(ABC):
    """Interface for maintenance schedule persistence."""

    @abstractmethod
    async def create(self, schedule: MaintenanceSchedule) -> MaintenanceSchedule:
        ...

    @abstractmethod
    async def get_by_id(self, schedule_id: str) -> Optional[MaintenanceSchedule]:
        ...

    @abstractmethod
    async def get_all(self) -> list[MaintenanceSchedule]:
        ...


class IProgramEvaluationRepository(ABC):
    """Interface for program evaluation persistence."""

    @abstractmethod
    async def create(self, evaluation: ProgramEvaluation) -> ProgramEvaluation:
        ...

    @abstractmethod
    async def get_by_id(self, evaluation_id: str) -> Optional[ProgramEvaluation]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...


class IExecutiveSummaryRepository(ABC):
    """Interface for executive summary persistence."""

    @abstractmethod
    async def create(self, summary: ExecutiveSummary) -> ExecutiveSummary:
        ...

    @abstractmethod
    async def get_latest(self) -> Optional[ExecutiveSummary]:
        ...

    @abstractmethod
    async def get_all(self) -> list[ExecutiveSummary]:
        ...


class IActionPlanRepository(ABC):
    """Interface for action plan persistence."""

    @abstractmethod
    async def create(self, plan: ActionPlan) -> ActionPlan:
        ...

    @abstractmethod
    async def get_by_id(self, plan_id: str) -> Optional[ActionPlan]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def update(self, plan_id: str, data: dict) -> Optional[ActionPlan]:
        ...


class IActionPlanItemRepository(ABC):
    """Interface for action plan item persistence."""

    @abstractmethod
    async def create(self, item: ActionPlanItem) -> ActionPlanItem:
        ...

    @abstractmethod
    async def get_by_id(self, item_id: str) -> Optional[ActionPlanItem]:
        ...

    @abstractmethod
    async def get_by_plan_id(self, plan_id: str) -> list[ActionPlanItem]:
        ...

    @abstractmethod
    async def update(self, item_id: str, data: dict) -> Optional[ActionPlanItem]:
        ...


class IImprovementInitiativeRepository(ABC):
    """Interface for improvement initiative persistence."""

    @abstractmethod
    async def create(self, initiative: ImprovementInitiative) -> ImprovementInitiative:
        ...

    @abstractmethod
    async def get_by_id(self, initiative_id: str) -> Optional[ImprovementInitiative]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...

    @abstractmethod
    async def update(self, initiative_id: str, data: dict) -> Optional[ImprovementInitiative]:
        ...


class IImprovementReportRepository(ABC):
    """Interface for improvement report persistence."""

    @abstractmethod
    async def create(self, report: ImprovementReport) -> ImprovementReport:
        ...

    @abstractmethod
    async def get_by_id(self, report_id: str) -> Optional[ImprovementReport]:
        ...

    @abstractmethod
    async def get_by_initiative_id(self, initiative_id: str) -> list[ImprovementReport]:
        ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict:
        ...
