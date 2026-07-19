"""Lesson builder service — content blocks, activities, and rich content management."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.course_designer import (
    ActivityType,
    BlockType,
    ContentBlock,
    InteractiveActivity,
)
from ..domain.events.content_studio_events import LessonCreated
from ..domain.interfaces.content_studio_interfaces import ICourseDesignRepository

logger = logging.getLogger(__name__)


class LessonBuilderService:
    """Service for managing content blocks and activities within lessons."""

    def __init__(self, course_repo: ICourseDesignRepository) -> None:
        self._course_repo = course_repo

    def _find_lesson_in_course(
        self, course_data: dict[str, Any], lesson_id: str
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None, dict[str, Any] | None]:
        for unit in course_data.get("units", []):
            for module in unit.get("modules", []):
                for lesson in module.get("lessons", []):
                    if lesson["id"] == lesson_id:
                        return lesson, module, unit
        return None, None, None

    def _save_course_data(self, course_id: str, course_data: dict[str, Any]) -> None:
        self._course_repo.update(course_id, {"units": course_data.get("units", [])})

    def add_lesson_to_module(
        self,
        course_id: str,
        unit_id: str,
        module_id: str,
        lesson_data: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        for unit in existing.get("units", []):
            if unit["id"] == unit_id:
                for module in unit.get("modules", []):
                    if module["id"] == module_id:
                        lesson = {
                            "id": lesson_data.get("id", __import__("uuid").uuid4().hex),
                            "module_id": module_id,
                            "name": lesson_data.get("name", ""),
                            "content_blocks": [],
                            "activities": [],
                            "estimated_minutes": lesson_data.get("estimated_minutes", 30),
                            "learning_objectives": lesson_data.get("learning_objectives", []),
                            "order": len(module.get("lessons", [])),
                        }
                        module.setdefault("lessons", []).append(lesson)
                        self._save_course_data(course_id, existing)

                        event = LessonCreated(
                            lesson_id=lesson["id"],
                            module_id=module_id,
                            lesson_name=lesson["name"],
                        )
                        logger.info("lesson_created", extra={
                            "course_id": course_id,
                            "lesson_id": lesson["id"],
                            "event_id": event.event_id,
                        })
                        return lesson
                raise ValueError(f"Module '{module_id}' not found in unit '{unit_id}'.")
        raise ValueError(f"Unit '{unit_id}' not found in course '{course_id}'.")

    def add_content_block(
        self,
        course_id: str,
        lesson_id: str,
        block_data: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        block = ContentBlock(
            block_type=BlockType(block_data.get("block_type", "text")),
            content=block_data.get("content", ""),
            metadata=block_data.get("metadata", {}),
            accessible=block_data.get("accessible", True),
            localized=block_data.get("localized", False),
        )
        block.order = len(lesson.get("content_blocks", []))
        block_dict = block.to_dict()
        lesson.setdefault("content_blocks", []).append(block_dict)
        self._save_course_data(course_id, existing)
        logger.info("content_block_added", extra={"course_id": course_id, "lesson_id": lesson_id, "block_id": block.id})
        return block_dict

    def update_content_block(
        self,
        course_id: str,
        lesson_id: str,
        block_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        for block in lesson.get("content_blocks", []):
            if block["id"] == block_id:
                for key in ("content", "block_type", "metadata", "accessible", "localized", "order"):
                    if key in data:
                        block[key] = data[key]
                self._save_course_data(course_id, existing)
                return block
        raise ValueError(f"Content block '{block_id}' not found in lesson '{lesson_id}'.")

    def remove_content_block(
        self, course_id: str, lesson_id: str, block_id: str
    ) -> bool:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        blocks = lesson.get("content_blocks", [])
        for i, block in enumerate(blocks):
            if block["id"] == block_id:
                blocks.pop(i)
                for j, b in enumerate(blocks):
                    b["order"] = j
                self._save_course_data(course_id, existing)
                return True
        return False

    def reorder_content_blocks(
        self, course_id: str, lesson_id: str, block_ids: list[str]
    ) -> bool:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        block_map = {b["id"]: b for b in lesson.get("content_blocks", [])}
        reordered: list[dict[str, Any]] = []
        for idx, bid in enumerate(block_ids):
            block = block_map.get(bid)
            if block is None:
                return False
            block["order"] = idx
            reordered.append(block)
        lesson["content_blocks"] = reordered
        self._save_course_data(course_id, existing)
        return True

    def add_activity(
        self,
        course_id: str,
        lesson_id: str,
        activity_data: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        activity = InteractiveActivity(
            activity_type=ActivityType(activity_data.get("activity_type", "mcq")),
            title=activity_data.get("title", ""),
            description=activity_data.get("description", ""),
            content=activity_data.get("content", {}),
            scoring=activity_data.get("scoring", {}),
        )
        activity.order = len(lesson.get("activities", []))
        activity_dict = activity.to_dict()
        lesson.setdefault("activities", []).append(activity_dict)
        self._save_course_data(course_id, existing)
        logger.info("activity_added", extra={"course_id": course_id, "lesson_id": lesson_id, "activity_id": activity.id})
        return activity_dict

    def update_activity(
        self,
        course_id: str,
        lesson_id: str,
        activity_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        for activity in lesson.get("activities", []):
            if activity["id"] == activity_id:
                for key in ("title", "description", "content", "scoring", "activity_type", "order"):
                    if key in data:
                        activity[key] = data[key]
                self._save_course_data(course_id, existing)
                return activity
        raise ValueError(f"Activity '{activity_id}' not found in lesson '{lesson_id}'.")

    def remove_activity(
        self, course_id: str, lesson_id: str, activity_id: str
    ) -> bool:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, _, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        activities = lesson.get("activities", [])
        for i, act in enumerate(activities):
            if act["id"] == activity_id:
                activities.pop(i)
                for j, a in enumerate(activities):
                    a["order"] = j
                self._save_course_data(course_id, existing)
                return True
        return False

    def get_lesson(self, course_id: str, lesson_id: str) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, module, unit = self._find_lesson_in_course(existing, lesson_id)
        if not lesson:
            raise ValueError(f"Lesson '{lesson_id}' not found.")
        return lesson

    def delete_lesson(self, course_id: str, lesson_id: str) -> bool:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        for unit in existing.get("units", []):
            for module in unit.get("modules", []):
                lessons = module.get("lessons", [])
                for i, lesson in enumerate(lessons):
                    if lesson["id"] == lesson_id:
                        lessons.pop(i)
                        for j, l in enumerate(lessons):
                            l["order"] = j
                        self._save_course_data(course_id, existing)
                        return True
        return False

    def duplicate_lesson(
        self, course_id: str, lesson_id: str, new_name: str = ""
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        lesson, module, _ = self._find_lesson_in_course(existing, lesson_id)
        if not lesson or module is None:
            raise ValueError(f"Lesson '{lesson_id}' not found.")

        import copy
        import uuid as _uuid
        new_lesson = copy.deepcopy(lesson)
        new_lesson["id"] = str(_uuid.uuid4())
        new_lesson["name"] = new_name or f"{lesson.get('name', '')} (Copy)"
        new_lesson["order"] = len(module.get("lessons", []))
        for block in new_lesson.get("content_blocks", []):
            block["id"] = str(_uuid.uuid4())
        for act in new_lesson.get("activities", []):
            act["id"] = str(_uuid.uuid4())
        module.setdefault("lessons", []).append(new_lesson)
        self._save_course_data(course_id, existing)
        return new_lesson
