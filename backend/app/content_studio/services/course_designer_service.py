"""Course designer service — full hierarchy CRUD for programs, courses, units, modules."""

from __future__ import annotations

import logging
from typing import Any, Optional

from ..domain.entities.course_designer import (
    CourseDesign,
    CourseStatus,
    ModuleDesign,
    Program,
    ProgramStatus,
    UnitDesign,
)
from ..domain.events.content_studio_events import CourseDesigned
from ..domain.interfaces.content_studio_interfaces import (
    ICourseDesignRepository,
    IProgramRepository,
)

logger = logging.getLogger(__name__)


class CourseDesignerService:
    """Service for managing program and course design hierarchies."""

    def __init__(
        self,
        program_repo: IProgramRepository,
        course_repo: ICourseDesignRepository,
    ) -> None:
        self._program_repo = program_repo
        self._course_repo = course_repo

    def create_program(self, data: dict[str, Any]) -> dict[str, Any]:
        program = Program(
            name=data.get("name", ""),
            description=data.get("description", ""),
            department=data.get("department", ""),
            status=ProgramStatus(data.get("status", "draft")),
        )
        result = self._program_repo.create({
            "id": program.id,
            "name": program.name,
            "description": program.description,
            "department": program.department,
            "status": program.status.value,
            "version": program.version,
            "courses": program.courses,
        })
        logger.info("program_created", extra={"program_id": result["id"]})
        return result

    def get_program(self, program_id: str) -> Optional[dict[str, Any]]:
        return self._program_repo.get_by_id(program_id)

    def list_programs(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        return self._program_repo.get_all(page=page, per_page=per_page, status=status)

    def update_program(self, program_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        existing = self._program_repo.get_by_id(program_id)
        if not existing:
            raise ValueError(f"Program '{program_id}' not found.")
        return self._program_repo.update(program_id, data)

    def delete_program(self, program_id: str) -> bool:
        if not self._program_repo.get_by_id(program_id):
            raise ValueError(f"Program '{program_id}' not found.")
        return self._program_repo.delete(program_id)

    def update_program_status(self, program_id: str, status: str) -> Optional[dict[str, Any]]:
        valid_statuses = {s.value for s in ProgramStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        return self._program_repo.update(program_id, {"status": status})

    def create_course(self, data: dict[str, Any]) -> dict[str, Any]:
        program_id = data.get("program_id", "")
        if program_id and not self._program_repo.get_by_id(program_id):
            raise ValueError(f"Program '{program_id}' not found.")

        course = CourseDesign(
            program_id=program_id,
            name=data.get("name", ""),
            description=data.get("description", ""),
            created_by=data.get("created_by", ""),
            status=CourseStatus(data.get("status", "draft")),
        )
        result = self._course_repo.create({
            "id": course.id,
            "program_id": course.program_id,
            "name": course.name,
            "description": course.description,
            "learning_objectives": course.learning_objectives,
            "estimated_hours": course.estimated_hours,
            "competencies": course.competencies,
            "prerequisites": course.prerequisites,
            "a11y_notes": course.a11y_notes,
            "localization_status": course.localization_status,
            "version": course.version,
            "status": course.status.value,
            "created_by": course.created_by,
        })

        if program_id:
            program = self._program_repo.get_by_id(program_id)
            if program:
                courses = program.get("courses", [])
                courses.append(course.id)
                self._program_repo.update(program_id, {"courses": courses})

        event = CourseDesigned(
            course_id=course.id,
            course_name=course.name,
            program_id=program_id,
            created_by=course.created_by,
        )
        logger.info("course_created", extra={"course_id": result["id"], "event_id": event.event_id})
        return result

    def get_course(self, course_id: str) -> Optional[dict[str, Any]]:
        return self._course_repo.get_by_id(course_id)

    def list_courses(
        self, page: int = 1, per_page: int = 20, status: Optional[str] = None
    ) -> dict[str, Any]:
        return self._course_repo.get_all(page=page, per_page=per_page, status=status)

    def update_course(self, course_id: str, data: dict[str, Any]) -> Optional[dict[str, Any]]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")
        data["version"] = existing.get("version", 1) + 1
        return self._course_repo.update(course_id, data)

    def delete_course(self, course_id: str) -> bool:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")
        program_id = existing.get("program_id", "")
        if program_id:
            program = self._program_repo.get_by_id(program_id)
            if program:
                courses = [c for c in program.get("courses", []) if c != course_id]
                self._program_repo.update(program_id, {"courses": courses})
        return self._course_repo.delete(course_id)

    def update_course_status(self, course_id: str, status: str) -> Optional[dict[str, Any]]:
        valid_statuses = {s.value for s in CourseStatus}
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {valid_statuses}")
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")
        return self._course_repo.update(course_id, {"status": status})

    def add_unit_to_course(self, course_id: str, unit_data: dict[str, Any]) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        unit = UnitDesign(
            course_id=course_id,
            name=unit_data.get("name", ""),
        )
        units = existing.get("units", [])
        unit_dict = {
            "id": unit.id,
            "course_id": unit.course_id,
            "name": unit.name,
            "modules": [],
            "order": len(units),
        }
        units.append(unit_dict)
        self._course_repo.update(course_id, {"units": units})
        logger.info("unit_added", extra={"course_id": course_id, "unit_id": unit.id})
        return unit_dict

    def add_module_to_unit(
        self, course_id: str, unit_id: str, module_data: dict[str, Any]
    ) -> dict[str, Any]:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")

        units = existing.get("units", [])
        target_unit = None
        for unit in units:
            if unit["id"] == unit_id:
                target_unit = unit
                break
        if target_unit is None:
            raise ValueError(f"Unit '{unit_id}' not found in course '{course_id}'.")

        module = ModuleDesign(unit_id=unit_id, name=module_data.get("name", ""))
        modules = target_unit.get("modules", [])
        module_dict = {
            "id": module.id,
            "unit_id": module.unit_id,
            "name": module.name,
            "lessons": [],
            "order": len(modules),
        }
        modules.append(module_dict)
        self._course_repo.update(course_id, {"units": units})
        logger.info("module_added", extra={"course_id": course_id, "unit_id": unit_id, "module_id": module.id})
        return module_dict

    def get_course_hierarchy(self, course_id: str) -> dict[str, Any]:
        course = self._course_repo.get_by_id(course_id)
        if not course:
            raise ValueError(f"Course '{course_id}' not found.")
        return course

    def search_courses(
        self, query: str, page: int = 1, per_page: int = 20
    ) -> dict[str, Any]:
        return self._course_repo.search(query, page=page, per_page=per_page)

    def get_courses_by_program(self, program_id: str) -> list[dict[str, Any]]:
        return self._course_repo.get_by_program(program_id)

    def recalculate_hours(self, course_id: str) -> float:
        existing = self._course_repo.get_by_id(course_id)
        if not existing:
            raise ValueError(f"Course '{course_id}' not found.")
        units = existing.get("units", [])
        total_minutes = 0
        for unit in units:
            for module in unit.get("modules", []):
                for lesson in module.get("lessons", []):
                    total_minutes += lesson.get("estimated_minutes", 30)
        hours = round(total_minutes / 60.0, 2)
        self._course_repo.update(course_id, {"estimated_hours": hours})
        return hours
