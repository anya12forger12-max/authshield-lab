"""Course designer domain entities for the Content Production Studio."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ProgramStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class CourseStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class BlockType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    DIAGRAM = "diagram"
    TABLE = "table"
    CODE_SAMPLE = "code_sample"
    QUESTION = "question"
    REFLECTION = "reflection"
    GLOSSARY_REF = "glossary_ref"
    SIMULATION = "simulation"
    RESOURCE = "resource"


class ActivityType(str, Enum):
    MCQ = "mcq"
    MATCHING = "matching"
    DRAG_DROP = "drag_drop"
    TIMELINE_ORDERING = "timeline_ordering"
    SCENARIO_ANALYSIS = "scenario_analysis"
    LOG_ANALYSIS = "log_analysis"
    POLICY_REVIEW = "policy_review"
    CONFIG_REVIEW = "config_review"
    ARCHITECTURE_REVIEW = "architecture_review"
    REFLECTION = "reflection"


@dataclass
class ContentBlock:
    """A single content block within a lesson."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    block_type: BlockType = BlockType.TEXT
    content: str = ""
    metadata: dict = field(default_factory=dict)
    order: int = 0
    accessible: bool = True
    localized: bool = False

    def mark_accessible(self) -> None:
        self.accessible = True

    def mark_inaccessible(self, reason: str = "") -> None:
        self.accessible = False
        if reason:
            self.metadata["inaccessibility_reason"] = reason

    def mark_localized(self) -> None:
        self.localized = True

    def update_content(self, content: str) -> None:
        self.content = content

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "block_type": self.block_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "order": self.order,
            "accessible": self.accessible,
            "localized": self.localized,
        }


@dataclass
class InteractiveActivity:
    """An interactive learning activity within a lesson."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    activity_type: ActivityType = ActivityType.MCQ
    title: str = ""
    description: str = ""
    content: dict = field(default_factory=dict)
    scoring: dict = field(default_factory=dict)
    order: int = 0

    def update_scoring(self, scoring: dict) -> None:
        self.scoring.update(scoring)

    def get_max_score(self) -> float:
        return self.scoring.get("max_score", 100.0)

    def get_passing_score(self) -> float:
        return self.scoring.get("passing_score", 70.0)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "activity_type": self.activity_type.value,
            "title": self.title,
            "description": self.description,
            "content": self.content,
            "scoring": self.scoring,
            "order": self.order,
        }


@dataclass
class LessonDesign:
    """A lesson within a module, containing content blocks and activities."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    module_id: str = ""
    name: str = ""
    content_blocks: list[ContentBlock] = field(default_factory=list)
    activities: list[InteractiveActivity] = field(default_factory=list)
    estimated_minutes: int = 30
    learning_objectives: list[str] = field(default_factory=list)
    order: int = 0

    def add_content_block(self, block: ContentBlock) -> None:
        block.order = len(self.content_blocks)
        self.content_blocks.append(block)

    def remove_content_block(self, block_id: str) -> bool:
        for i, block in enumerate(self.content_blocks):
            if block.id == block_id:
                self.content_blocks.pop(i)
                self._reorder_blocks()
                return True
        return False

    def add_activity(self, activity: InteractiveActivity) -> None:
        activity.order = len(self.activities)
        self.activities.append(activity)

    def remove_activity(self, activity_id: str) -> bool:
        for i, act in enumerate(self.activities):
            if act.id == activity_id:
                self.activities.pop(i)
                self._reorder_activities()
                return True
        return False

    def get_block_count(self) -> int:
        return len(self.content_blocks)

    def get_activity_count(self) -> int:
        return len(self.activities)

    def calculate_estimated_minutes(self) -> int:
        reading_time = len(self.content_blocks) * 3
        activity_time = len(self.activities) * 10
        return reading_time + activity_time

    def _reorder_blocks(self) -> None:
        for i, block in enumerate(self.content_blocks):
            block.order = i

    def _reorder_activities(self) -> None:
        for i, act in enumerate(self.activities):
            act.order = i

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "module_id": self.module_id,
            "name": self.name,
            "content_blocks": [b.to_dict() for b in self.content_blocks],
            "activities": [a.to_dict() for a in self.activities],
            "estimated_minutes": self.estimated_minutes,
            "learning_objectives": self.learning_objectives,
            "order": self.order,
        }


@dataclass
class ModuleDesign:
    """A module within a unit, containing lessons."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    unit_id: str = ""
    name: str = ""
    lessons: list[LessonDesign] = field(default_factory=list)
    order: int = 0

    def add_lesson(self, lesson: LessonDesign) -> None:
        lesson.module_id = self.id
        lesson.order = len(self.lessons)
        self.lessons.append(lesson)

    def remove_lesson(self, lesson_id: str) -> bool:
        for i, lesson in enumerate(self.lessons):
            if lesson.id == lesson_id:
                self.lessons.pop(i)
                self._reorder_lessons()
                return True
        return False

    def get_lesson_count(self) -> int:
        return len(self.lessons)

    def calculate_total_minutes(self) -> int:
        return sum(lesson.estimated_minutes for lesson in self.lessons)

    def get_all_content_blocks(self) -> list[ContentBlock]:
        blocks: list[ContentBlock] = []
        for lesson in self.lessons:
            blocks.extend(lesson.content_blocks)
        return blocks

    def _reorder_lessons(self) -> None:
        for i, lesson in enumerate(self.lessons):
            lesson.order = i

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "unit_id": self.unit_id,
            "name": self.name,
            "lessons": [l.to_dict() for l in self.lessons],
            "order": self.order,
            "total_minutes": self.calculate_total_minutes(),
        }


@dataclass
class UnitDesign:
    """A unit within a course, containing modules."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    course_id: str = ""
    name: str = ""
    modules: list[ModuleDesign] = field(default_factory=list)
    order: int = 0

    def add_module(self, module: ModuleDesign) -> None:
        module.unit_id = self.id
        module.order = len(self.modules)
        self.modules.append(module)

    def remove_module(self, module_id: str) -> bool:
        for i, module in enumerate(self.modules):
            if module.id == module_id:
                self.modules.pop(i)
                self._reorder_modules()
                return True
        return False

    def get_module_count(self) -> int:
        return len(self.modules)

    def get_total_lessons(self) -> int:
        return sum(module.get_lesson_count() for module in self.modules)

    def calculate_total_minutes(self) -> int:
        return sum(module.calculate_total_minutes() for module in self.modules)

    def _reorder_modules(self) -> None:
        for i, module in enumerate(self.modules):
            module.order = i

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "course_id": self.course_id,
            "name": self.name,
            "modules": [m.to_dict() for m in self.modules],
            "order": self.order,
            "total_lessons": self.get_total_lessons(),
            "total_minutes": self.calculate_total_minutes(),
        }


@dataclass
class CourseDesign:
    """Root aggregate for a course design, containing units."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    program_id: str = ""
    name: str = ""
    description: str = ""
    units: list[UnitDesign] = field(default_factory=list)
    learning_objectives: list[str] = field(default_factory=list)
    estimated_hours: float = 0.0
    competencies: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    a11y_notes: str = ""
    localization_status: str = "pending"
    version: int = 1
    status: CourseStatus = CourseStatus.DRAFT
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_unit(self, unit: UnitDesign) -> None:
        unit.course_id = self.id
        unit.order = len(self.units)
        self.units.append(unit)
        self.updated_at = datetime.now(timezone.utc)

    def remove_unit(self, unit_id: str) -> bool:
        for i, unit in enumerate(self.units):
            if unit.id == unit_id:
                self.units.pop(i)
                self._reorder_units()
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def update_status(self, new_status: CourseStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def increment_version(self) -> None:
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)

    def get_total_modules(self) -> int:
        return sum(unit.get_module_count() for unit in self.units)

    def get_total_lessons(self) -> int:
        return sum(unit.get_total_lessons() for unit in self.units)

    def recalculate_estimated_hours(self) -> float:
        total_minutes = sum(unit.calculate_total_minutes() for unit in self.units)
        self.estimated_hours = round(total_minutes / 60.0, 2)
        return self.estimated_hours

    def add_learning_objective(self, objective: str) -> None:
        if objective not in self.learning_objectives:
            self.learning_objectives.append(objective)
            self.updated_at = datetime.now(timezone.utc)

    def remove_learning_objective(self, objective: str) -> bool:
        if objective in self.learning_objectives:
            self.learning_objectives.remove(objective)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def add_competency(self, competency: str) -> None:
        if competency not in self.competencies:
            self.competencies.append(competency)
            self.updated_at = datetime.now(timezone.utc)

    def add_prerequisite(self, prerequisite: str) -> None:
        if prerequisite not in self.prerequisites:
            self.prerequisites.append(prerequisite)
            self.updated_at = datetime.now(timezone.utc)

    def _reorder_units(self) -> None:
        for i, unit in enumerate(self.units):
            unit.order = i

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "program_id": self.program_id,
            "name": self.name,
            "description": self.description,
            "units": [u.to_dict() for u in self.units],
            "learning_objectives": self.learning_objectives,
            "estimated_hours": self.estimated_hours,
            "competencies": self.competencies,
            "prerequisites": self.prerequisites,
            "a11y_notes": self.a11y_notes,
            "localization_status": self.localization_status,
            "version": self.version,
            "status": self.status.value,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "total_modules": self.get_total_modules(),
            "total_lessons": self.get_total_lessons(),
        }


@dataclass
class Program:
    """A program containing multiple courses."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    department: str = ""
    status: ProgramStatus = ProgramStatus.DRAFT
    version: int = 1
    courses: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_course(self, course_id: str) -> None:
        if course_id not in self.courses:
            self.courses.append(course_id)
            self.updated_at = datetime.now(timezone.utc)

    def remove_course(self, course_id: str) -> bool:
        if course_id in self.courses:
            self.courses.remove(course_id)
            self.updated_at = datetime.now(timezone.utc)
            return True
        return False

    def update_status(self, new_status: ProgramStatus) -> None:
        self.status = new_status
        self.updated_at = datetime.now(timezone.utc)

    def increment_version(self) -> None:
        self.version += 1
        self.updated_at = datetime.now(timezone.utc)

    def get_course_count(self) -> int:
        return len(self.courses)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "department": self.department,
            "status": self.status.value,
            "version": self.version,
            "courses": self.courses,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
