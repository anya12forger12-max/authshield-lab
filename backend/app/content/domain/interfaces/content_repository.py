"""Repository interfaces (ABCs) for the Content domain."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from ..entities.content import Course, Lesson, Quiz, MediaAsset, KnowledgeNode


class CourseRepository(ABC):
    """Abstract interface for course persistence."""

    @abstractmethod
    async def find_by_id(self, course_id: str) -> Optional[Course]:
        ...

    @abstractmethod
    async def find_all(self, offset: int = 0, limit: int = 20) -> list[Course]:
        ...

    @abstractmethod
    async def save(self, course: Course) -> Course:
        ...

    @abstractmethod
    async def delete(self, course_id: str) -> bool:
        ...

    @abstractmethod
    async def count(self) -> int:
        ...

    @abstractmethod
    async def search(self, query: str, filters: dict | None = None) -> list[Course]:
        ...


class LessonRepository(ABC):
    """Abstract interface for lesson persistence."""

    @abstractmethod
    async def find_by_id(self, lesson_id: str) -> Optional[Lesson]:
        ...

    @abstractmethod
    async def find_by_course(self, course_id: str) -> list[Lesson]:
        ...

    @abstractmethod
    async def save(self, lesson: Lesson) -> Lesson:
        ...

    @abstractmethod
    async def delete(self, lesson_id: str) -> bool:
        ...

    @abstractmethod
    async def reorder(self, course_id: str, ordered_ids: list[str]) -> bool:
        ...


class QuizRepository(ABC):
    """Abstract interface for quiz persistence."""

    @abstractmethod
    async def find_by_id(self, quiz_id: str) -> Optional[Quiz]:
        ...

    @abstractmethod
    async def find_by_course(self, course_id: str) -> list[Quiz]:
        ...

    @abstractmethod
    async def save(self, quiz: Quiz) -> Quiz:
        ...

    @abstractmethod
    async def delete(self, quiz_id: str) -> bool:
        ...


class MediaRepository(ABC):
    """Abstract interface for media asset persistence."""

    @abstractmethod
    async def find_by_id(self, asset_id: str) -> Optional[MediaAsset]:
        ...

    @abstractmethod
    async def find_all(self, offset: int = 0, limit: int = 20) -> list[MediaAsset]:
        ...

    @abstractmethod
    async def save(self, asset: MediaAsset) -> MediaAsset:
        ...

    @abstractmethod
    async def delete(self, asset_id: str) -> bool:
        ...

    @abstractmethod
    async def search_by_type(self, media_type: str) -> list[MediaAsset]:
        ...


class KnowledgeNodeRepository(ABC):
    """Abstract interface for knowledge node persistence."""

    @abstractmethod
    async def find_by_id(self, node_id: str) -> Optional[KnowledgeNode]:
        ...

    @abstractmethod
    async def find_all(self) -> list[KnowledgeNode]:
        ...

    @abstractmethod
    async def save(self, node: KnowledgeNode) -> KnowledgeNode:
        ...

    @abstractmethod
    async def delete(self, node_id: str) -> bool:
        ...

    @abstractmethod
    async def find_related(self, node_id: str) -> list[KnowledgeNode]:
        ...
