"""Classroom management service for the LMS module."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.entities.classroom import Classroom, ClassroomRole, ClassroomSession, SessionStatus
from ..domain.events.lms_events import ClassroomCreated, ClassroomUpdated
from ..domain.interfaces.lms_interfaces import IClassroomRepository
from ..validators.lms_validator import validate_classroom_capacity, validate_classroom_data

logger = logging.getLogger(__name__)


class ClassroomService:
    """Service for managing classrooms, sessions, and members."""

    def __init__(self, classroom_repo: IClassroomRepository) -> None:
        self._repo = classroom_repo

    def create_classroom(self, data: dict[str, Any]) -> dict[str, Any]:
        validation = validate_classroom_data(data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        classroom = self._repo.create(data)
        event = ClassroomCreated(
            classroom_id=classroom["id"],
            classroom_name=classroom.get("name", ""),
            instructor_id=classroom.get("instructor_id", ""),
        )
        logger.info("classroom_created", extra={"classroom_id": classroom["id"], "event_id": event.event_id})
        return classroom

    def get_classroom(self, classroom_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(classroom_id)

    def list_classrooms(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        return self._repo.get_all(page=page, per_page=per_page, status=status)

    def update_classroom(self, classroom_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        existing = self._repo.get_by_id(classroom_id)
        if not existing:
            raise ValueError(f"Classroom '{classroom_id}' not found.")

        merged = {**existing, **data}
        validation = validate_classroom_data(merged)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        updated = self._repo.update(classroom_id, data)
        if updated:
            event = ClassroomUpdated(
                classroom_id=classroom_id,
                classroom_name=updated.get("name", ""),
                changes=data,
            )
            logger.info("classroom_updated", extra={"classroom_id": classroom_id, "event_id": event.event_id})
        return updated

    def delete_classroom(self, classroom_id: str) -> bool:
        if not self._repo.get_by_id(classroom_id):
            raise ValueError(f"Classroom '{classroom_id}' not found.")
        return self._repo.delete(classroom_id)

    def search_classrooms(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._repo.search(query, page=page, per_page=per_page)

    def add_member(
        self,
        classroom_id: str,
        user_id: str,
        role: str = "learner",
    ) -> dict[str, Any]:
        classroom = self._repo.get_by_id(classroom_id)
        if not classroom:
            raise ValueError(f"Classroom '{classroom_id}' not found.")

        if classroom.get("status") != "active":
            raise ValueError(f"Cannot add member to a classroom in '{classroom.get('status')}' status.")

        existing_members = self._repo.get_members(classroom_id)
        member_user_ids = [m["user_id"] for m in existing_members if m["status"] == "active"]
        if user_id in member_user_ids:
            raise ValueError(f"User '{user_id}' is already an active member of this classroom.")

        capacity_validation = validate_classroom_capacity(
            len(existing_members), classroom.get("capacity", 30), add_count=1
        )
        if not capacity_validation.is_valid:
            raise ValueError(f"Capacity validation failed: {capacity_validation.to_dict()}")

        member = self._repo.add_member(classroom_id, {
            "user_id": user_id,
            "role": role,
            "status": "active",
        })
        logger.info("classroom_member_added", extra={"classroom_id": classroom_id, "user_id": user_id, "role": role})
        return member

    def remove_member(self, classroom_id: str, user_id: str) -> bool:
        classroom = self._repo.get_by_id(classroom_id)
        if not classroom:
            raise ValueError(f"Classroom '{classroom_id}' not found.")
        result = self._repo.remove_member(classroom_id, user_id)
        if result:
            logger.info("classroom_member_removed", extra={"classroom_id": classroom_id, "user_id": user_id})
        return result

    def get_members(self, classroom_id: str) -> list[dict[str, Any]]:
        classroom = self._repo.get_by_id(classroom_id)
        if not classroom:
            raise ValueError(f"Classroom '{classroom_id}' not found.")
        return self._repo.get_members(classroom_id)

    def get_members_by_role(self, classroom_id: str, role: str) -> list[dict[str, Any]]:
        members = self._get_members(classroom_id)
        return [m for m in members if m.get("role") == role]

    def _get_members(self, classroom_id: str) -> list[dict[str, Any]]:
        return self._repo.get_members(classroom_id)

    def update_classroom_status(self, classroom_id: str, status: str) -> Optional[dict[str, Any]]:
        valid_statuses = {"active", "inactive", "archived"}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        return self._repo.update(classroom_id, {"status": status})
