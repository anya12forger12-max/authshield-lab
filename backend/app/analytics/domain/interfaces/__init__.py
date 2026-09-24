"""Abstract repository interfaces for analytics entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.analytics import (
    AssessmentOutcome,
    ContentUsage,
    CourseCompletion,
    CurriculumCoverage,
    EducationalAnalyticsDashboard,
    FilterOptions,
    LearningProgress,
)
from ..entities.content_health import (
    ContentHealthDashboard,
    ContentHealthItem,
    MaintenanceSchedule,
)
from ..entities.continuous_improvement import (
    ActionPlan,
    ActionPlanItem,
    HistoricalComparison,
    ImprovementInitiative,
    ImprovementMetric,
    ImprovementReport,
)
from ..entities.curriculum_evaluation import (
    CurriculumEvaluationResult,
    EvaluationRecommendation,
    PrerequisiteGap,
    TopicAnalysis,
)
from ..entities.learning_quality import (
    LearningQualityDashboard,
    LongitudinalComparison,
    QualityIndicator,
)
from ..entities.program_evaluation import ExecutiveSummary, ProgramEvaluation


class IAnalyticsDashboardRepository(ABC):
    """Interface for educational analytics dashboard persistence."""

    @abstractmethod
    async def create(
        self, dashboard: EducationalAnalyticsDashboard
    ) -> EducationalAnalyticsDashboard: ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> EducationalAnalyticsDashboard | None: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...

    @abstractmethod
    async def get_latest(self) -> EducationalAnalyticsDashboard | None: ...

    @abstractmethod
    async def delete(self, dashboard_id: str) -> bool: ...


class ILearningProgressRepository(ABC):
    """Interface for learning progress persistence."""

    @abstractmethod
    async def create(self, progress: LearningProgress) -> LearningProgress: ...

    @abstractmethod
    async def get_by_learner_id(self, learner_id: str) -> LearningProgress | None: ...

    @abstractmethod
    async def get_all(self) -> list[LearningProgress]: ...

    @abstractmethod
    async def update(self, learner_id: str, data: dict) -> LearningProgress | None: ...


class ICourseCompletionRepository(ABC):
    """Interface for course completion persistence."""

    @abstractmethod
    async def create(self, completion: CourseCompletion) -> CourseCompletion: ...

    @abstractmethod
    async def get_by_course_id(self, course_id: str) -> CourseCompletion | None: ...

    @abstractmethod
    async def get_all(self) -> list[CourseCompletion]: ...

    @abstractmethod
    async def update(self, course_id: str, data: dict) -> CourseCompletion | None: ...


class IAssessmentOutcomeRepository(ABC):
    """Interface for assessment outcome persistence."""

    @abstractmethod
    async def create(self, outcome: AssessmentOutcome) -> AssessmentOutcome: ...

    @abstractmethod
    async def get_by_assessment_id(self, assessment_id: str) -> AssessmentOutcome | None: ...

    @abstractmethod
    async def get_all(self) -> list[AssessmentOutcome]: ...

    @abstractmethod
    async def update(self, assessment_id: str, data: dict) -> AssessmentOutcome | None: ...


class ICurriculumCoverageRepository(ABC):
    """Interface for curriculum coverage persistence."""

    @abstractmethod
    async def create(self, coverage: CurriculumCoverage) -> CurriculumCoverage: ...

    @abstractmethod
    async def get_by_framework_id(self, framework_id: str) -> CurriculumCoverage | None: ...

    @abstractmethod
    async def get_all(self) -> list[CurriculumCoverage]: ...

    @abstractmethod
    async def update(self, framework_id: str, data: dict) -> CurriculumCoverage | None: ...


class IContentUsageRepository(ABC):
    """Interface for content usage persistence."""

    @abstractmethod
    async def create(self, usage: ContentUsage) -> ContentUsage: ...

    @abstractmethod
    async def get_by_content_id(self, content_id: str) -> ContentUsage | None: ...

    @abstractmethod
    async def get_all(self) -> list[ContentUsage]: ...

    @abstractmethod
    async def update(self, content_id: str, data: dict) -> ContentUsage | None: ...


class IQualityDashboardRepository(ABC):
    """Interface for learning quality dashboard persistence."""

    @abstractmethod
    async def create(self, dashboard: LearningQualityDashboard) -> LearningQualityDashboard: ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> LearningQualityDashboard | None: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...

    @abstractmethod
    async def get_latest(self) -> LearningQualityDashboard | None: ...


class ICurriculumEvaluationRepository(ABC):
    """Interface for curriculum evaluation persistence."""

    @abstractmethod
    async def create(self, result: CurriculumEvaluationResult) -> CurriculumEvaluationResult: ...

    @abstractmethod
    async def get_by_id(self, evaluation_id: str) -> CurriculumEvaluationResult | None: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...


class IEvaluationRecommendationRepository(ABC):
    """Interface for evaluation recommendation persistence."""

    @abstractmethod
    async def create(self, rec: EvaluationRecommendation) -> EvaluationRecommendation: ...

    @abstractmethod
    async def get_by_id(self, rec_id: str) -> EvaluationRecommendation | None: ...

    @abstractmethod
    async def get_all(self) -> list[EvaluationRecommendation]: ...

    @abstractmethod
    async def update(self, rec_id: str, data: dict) -> EvaluationRecommendation | None: ...


class IContentHealthRepository(ABC):
    """Interface for content health item persistence."""

    @abstractmethod
    async def create(self, item: ContentHealthItem) -> ContentHealthItem: ...

    @abstractmethod
    async def get_by_id(self, item_id: str) -> ContentHealthItem | None: ...

    @abstractmethod
    async def get_by_content_id(self, content_id: str) -> ContentHealthItem | None: ...

    @abstractmethod
    async def get_all(self) -> list[ContentHealthItem]: ...

    @abstractmethod
    async def update(self, item_id: str, data: dict) -> ContentHealthItem | None: ...

    @abstractmethod
    async def delete(self, item_id: str) -> bool: ...


class IContentHealthDashboardRepository(ABC):
    """Interface for content health dashboard persistence."""

    @abstractmethod
    async def create(self, dashboard: ContentHealthDashboard) -> ContentHealthDashboard: ...

    @abstractmethod
    async def get_by_id(self, dashboard_id: str) -> ContentHealthDashboard | None: ...

    @abstractmethod
    async def get_latest(self) -> ContentHealthDashboard | None: ...


class IMaintenanceScheduleRepository(ABC):
    """Interface for maintenance schedule persistence."""

    @abstractmethod
    async def create(self, schedule: MaintenanceSchedule) -> MaintenanceSchedule: ...

    @abstractmethod
    async def get_by_id(self, schedule_id: str) -> MaintenanceSchedule | None: ...

    @abstractmethod
    async def get_all(self) -> list[MaintenanceSchedule]: ...


class IProgramEvaluationRepository(ABC):
    """Interface for program evaluation persistence."""

    @abstractmethod
    async def create(self, evaluation: ProgramEvaluation) -> ProgramEvaluation: ...

    @abstractmethod
    async def get_by_id(self, evaluation_id: str) -> ProgramEvaluation | None: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...


class IExecutiveSummaryRepository(ABC):
    """Interface for executive summary persistence."""

    @abstractmethod
    async def create(self, summary: ExecutiveSummary) -> ExecutiveSummary: ...

    @abstractmethod
    async def get_latest(self) -> ExecutiveSummary | None: ...

    @abstractmethod
    async def get_all(self) -> list[ExecutiveSummary]: ...


class IActionPlanRepository(ABC):
    """Interface for action plan persistence."""

    @abstractmethod
    async def create(self, plan: ActionPlan) -> ActionPlan: ...

    @abstractmethod
    async def get_by_id(self, plan_id: str) -> ActionPlan | None: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...

    @abstractmethod
    async def update(self, plan_id: str, data: dict) -> ActionPlan | None: ...


class IActionPlanItemRepository(ABC):
    """Interface for action plan item persistence."""

    @abstractmethod
    async def create(self, item: ActionPlanItem) -> ActionPlanItem: ...

    @abstractmethod
    async def get_by_id(self, item_id: str) -> ActionPlanItem | None: ...

    @abstractmethod
    async def get_by_plan_id(self, plan_id: str) -> list[ActionPlanItem]: ...

    @abstractmethod
    async def update(self, item_id: str, data: dict) -> ActionPlanItem | None: ...


class IImprovementInitiativeRepository(ABC):
    """Interface for improvement initiative persistence."""

    @abstractmethod
    async def create(self, initiative: ImprovementInitiative) -> ImprovementInitiative: ...

    @abstractmethod
    async def get_by_id(self, initiative_id: str) -> ImprovementInitiative | None: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...

    @abstractmethod
    async def update(self, initiative_id: str, data: dict) -> ImprovementInitiative | None: ...


class IImprovementReportRepository(ABC):
    """Interface for improvement report persistence."""

    @abstractmethod
    async def create(self, report: ImprovementReport) -> ImprovementReport: ...

    @abstractmethod
    async def get_by_id(self, report_id: str) -> ImprovementReport | None: ...

    @abstractmethod
    async def get_by_initiative_id(self, initiative_id: str) -> list[ImprovementReport]: ...

    @abstractmethod
    async def get_all(self, page: int = 1, per_page: int = 20) -> dict: ...
