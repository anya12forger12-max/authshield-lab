"""Content Production Studio repository interfaces (abstract base classes)."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Optional


class ICourseDesignRepository(ABC):
    """Interface for course design data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, course_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, course_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, course_id: str) -> bool:
        ...

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        ...

    @abstractmethod
    def get_by_program(self, program_id: str) -> list[Any]:
        ...


class IProgramRepository(ABC):
    """Interface for program data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, program_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, program_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, program_id: str) -> bool:
        ...


class IVirtualLabRepository(ABC):
    """Interface for virtual lab data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, lab_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, lab_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, lab_id: str) -> bool:
        ...

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        ...


class ILabTemplateRepository(ABC):
    """Interface for lab template data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, template_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(self) -> list[Any]:
        ...

    @abstractmethod
    def update(self, template_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, template_id: str) -> bool:
        ...


class IMultimediaAssetRepository(ABC):
    """Interface for multimedia asset data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, asset_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, asset_type: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, asset_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, asset_id: str) -> bool:
        ...

    @abstractmethod
    def search(self, query: str, page: int = 1, per_page: int = 20) -> dict[str, Any]:
        ...


class IAssetCollectionRepository(ABC):
    """Interface for asset collection data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, collection_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(self) -> list[Any]:
        ...

    @abstractmethod
    def update(self, collection_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, collection_id: str) -> bool:
        ...


class IContentTemplateRepository(ABC):
    """Interface for content template data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, template_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, template_type: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, template_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, template_id: str) -> bool:
        ...


class IPublishRequestRepository(ABC):
    """Interface for publish request data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, request_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, request_id: str, data: dict[str, Any]) -> Any | None:
        ...

    @abstractmethod
    def delete(self, request_id: str) -> bool:
        ...

    @abstractmethod
    def get_by_content(self, content_id: str) -> list[Any]:
        ...


class IPublishHistoryRepository(ABC):
    """Interface for publish history data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, history_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_content(self, content_id: str) -> list[Any]:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        ...


class IContentVersionRepository(ABC):
    """Interface for content version data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, version_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_latest(self, content_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all_for_content(self, content_id: str) -> list[Any]:
        ...


class IEditorialReviewRepository(ABC):
    """Interface for editorial review data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, review_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_content(self, content_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20, stage: Optional[str] = None
    ) -> dict[str, Any]:
        ...

    @abstractmethod
    def update(self, review_id: str, data: dict[str, Any]) -> Any | None:
        ...


class IReviewCommentRepository(ABC):
    """Interface for review comment data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_review(self, review_id: str) -> list[Any]:
        ...

    @abstractmethod
    def delete(self, comment_id: str) -> bool:
        ...


class IReviewDecisionRepository(ABC):
    """Interface for review decision data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_review(self, review_id: str) -> list[Any]:
        ...

    @abstractmethod
    def get_latest(self, review_id: str) -> Any | None:
        ...


class IA11yCheckRepository(ABC):
    """Interface for accessibility check data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_report(self, report_id: str) -> list[Any]:
        ...


class IA11yValidationReportRepository(ABC):
    """Interface for accessibility validation report persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, report_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_content(self, content_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_all(
        self, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        ...


class IA11yRemediationRepository(ABC):
    """Interface for accessibility remediation data persistence."""

    @abstractmethod
    def create(self, data: dict[str, Any]) -> Any:
        ...

    @abstractmethod
    def get_by_id(self, remediation_id: str) -> Any | None:
        ...

    @abstractmethod
    def get_by_report(self, report_id: str) -> list[Any]:
        ...

    @abstractmethod
    def get_open(self) -> list[Any]:
        ...

    @abstractmethod
    def update(self, remediation_id: str, data: dict[str, Any]) -> Any | None:
        ...
