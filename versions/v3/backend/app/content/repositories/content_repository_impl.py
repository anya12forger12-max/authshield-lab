"""In-memory repository implementations for the Content domain."""

from __future__ import annotations

import copy
from typing import Optional

from ..domain.entities.content import Course, Lesson, Quiz, MediaAsset, KnowledgeNode
from ..domain.interfaces.content_repository import (
    CourseRepository,
    LessonRepository,
    QuizRepository,
    MediaRepository,
    KnowledgeNodeRepository,
)


class InMemoryCourseRepository(CourseRepository):
    """Dict-backed in-memory course repository."""

    def __init__(self) -> None:
        self._store: dict[str, Course] = {}

    async def find_by_id(self, course_id: str) -> Optional[Course]:
        course = self._store.get(course_id)
        return copy.deepcopy(course) if course is not None else None

    async def find_all(self, offset: int = 0, limit: int = 20) -> list[Course]:
        items = list(self._store.values())
        return [copy.deepcopy(c) for c in items[offset : offset + limit]]

    async def save(self, course: Course) -> Course:
        self._store[course.id] = copy.deepcopy(course)
        return copy.deepcopy(course)

    async def delete(self, course_id: str) -> bool:
        if course_id in self._store:
            del self._store[course_id]
            return True
        return False

    async def count(self) -> int:
        return len(self._store)

    async def search(self, query: str, filters: dict | None = None) -> list[Course]:
        query_lower = query.lower()
        results: list[Course] = []
        for course in self._store.values():
            if query_lower and query_lower not in course.title.lower() and query_lower not in course.description.lower():
                continue
            if filters:
                if "difficulty" in filters and course.difficulty != filters["difficulty"]:
                    continue
                if "status" in filters and course.status != filters["status"]:
                    continue
                if "tags" in filters and filters["tags"]:
                    tag_set = set(filters["tags"])
                    if not tag_set.intersection(set(course.tags)):
                        continue
            results.append(copy.deepcopy(course))
        return results


class InMemoryLessonRepository(LessonRepository):
    """Dict-backed in-memory lesson repository."""

    def __init__(self) -> None:
        self._store: dict[str, Lesson] = {}

    async def find_by_id(self, lesson_id: str) -> Optional[Lesson]:
        lesson = self._store.get(lesson_id)
        return copy.deepcopy(lesson) if lesson is not None else None

    async def find_by_course(self, course_id: str) -> list[Lesson]:
        lessons = [l for l in self._store.values() if l.course_id == course_id]
        lessons.sort(key=lambda l: l.order)
        return [copy.deepcopy(l) for l in lessons]

    async def save(self, lesson: Lesson) -> Lesson:
        self._store[lesson.id] = copy.deepcopy(lesson)
        return copy.deepcopy(lesson)

    async def delete(self, lesson_id: str) -> bool:
        if lesson_id in self._store:
            del self._store[lesson_id]
            return True
        return False

    async def reorder(self, course_id: str, ordered_ids: list[str]) -> bool:
        for idx, lesson_id in enumerate(ordered_ids):
            lesson = self._store.get(lesson_id)
            if lesson is not None and lesson.course_id == course_id:
                lesson.order = idx
        return True


class InMemoryQuizRepository(QuizRepository):
    """Dict-backed in-memory quiz repository."""

    def __init__(self) -> None:
        self._store: dict[str, Quiz] = {}

    async def find_by_id(self, quiz_id: str) -> Optional[Quiz]:
        quiz = self._store.get(quiz_id)
        return copy.deepcopy(quiz) if quiz is not None else None

    async def find_by_course(self, course_id: str) -> list[Quiz]:
        return [copy.deepcopy(q) for q in self._store.values() if q.course_id == course_id]

    async def save(self, quiz: Quiz) -> Quiz:
        self._store[quiz.id] = copy.deepcopy(quiz)
        return copy.deepcopy(quiz)

    async def delete(self, quiz_id: str) -> bool:
        if quiz_id in self._store:
            del self._store[quiz_id]
            return True
        return False


class InMemoryMediaRepository(MediaRepository):
    """Dict-backed in-memory media asset repository."""

    def __init__(self) -> None:
        self._store: dict[str, MediaAsset] = {}

    async def find_by_id(self, asset_id: str) -> Optional[MediaAsset]:
        asset = self._store.get(asset_id)
        return copy.deepcopy(asset) if asset is not None else None

    async def find_all(self, offset: int = 0, limit: int = 20) -> list[MediaAsset]:
        items = list(self._store.values())
        return [copy.deepcopy(a) for a in items[offset : offset + limit]]

    async def save(self, asset: MediaAsset) -> MediaAsset:
        self._store[asset.id] = copy.deepcopy(asset)
        return copy.deepcopy(asset)

    async def delete(self, asset_id: str) -> bool:
        if asset_id in self._store:
            del self._store[asset_id]
            return True
        return False

    async def search_by_type(self, media_type: str) -> list[MediaAsset]:
        return [copy.deepcopy(a) for a in self._store.values() if a.media_type == media_type]


class InMemoryKnowledgeNodeRepository(KnowledgeNodeRepository):
    """Dict-backed in-memory knowledge node repository."""

    def __init__(self) -> None:
        self._store: dict[str, KnowledgeNode] = {}

    async def find_by_id(self, node_id: str) -> Optional[KnowledgeNode]:
        node = self._store.get(node_id)
        return copy.deepcopy(node) if node is not None else None

    async def find_all(self) -> list[KnowledgeNode]:
        return [copy.deepcopy(n) for n in self._store.values()]

    async def save(self, node: KnowledgeNode) -> KnowledgeNode:
        self._store[node.id] = copy.deepcopy(node)
        return copy.deepcopy(node)

    async def delete(self, node_id: str) -> bool:
        if node_id in self._store:
            del self._store[node_id]
            return True
        return False

    async def find_related(self, node_id: str) -> list[KnowledgeNode]:
        node = self._store.get(node_id)
        if node is None:
            return []
        related: list[KnowledgeNode] = []
        for rid in node.related_nodes:
            rnode = self._store.get(rid)
            if rnode is not None:
                related.append(copy.deepcopy(rnode))
        return related
