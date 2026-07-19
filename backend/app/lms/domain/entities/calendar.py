"""Calendar domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class AcademicEventType(str, Enum):
    """Type of academic event."""

    CLASS = "class"
    EXAM = "exam"
    ASSIGNMENT = "assignment"
    HOLIDAY = "holiday"
    BREAK = "break"
    WORKSHOP = "workshop"


class ImportantDateType(str, Enum):
    """Type of important date."""

    ENROLLMENT_DEADLINE = "enrollment_deadline"
    ADD_DROP_DEADLINE = "add_drop_deadline"
    WITHDRAWAL_DEADLINE = "withdrawal_deadline"
    FINAL_EXAM = "final_exam"
    GRADE_POSTING = "grade_posting"
    REGISTRATION_OPENS = "registration_opens"
    COMMENCEMENT = "commencement"


@dataclass
class AcademicEvent:
    """A single event on the academic calendar."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    event_type: AcademicEventType = AcademicEventType.CLASS
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recurring: bool = False
    recurrence_rule: Optional[str] = None
    description: Optional[str] = None
    color: str = "#3B82F6"

    @property
    def duration_minutes(self) -> float:
        delta = self.end_time - self.start_time
        return max(0.0, delta.total_seconds() / 60.0)

    def conflicts_with(self, other: AcademicEvent) -> bool:
        """Return ``True`` if this event overlaps with another."""
        if self.end_time <= other.start_time:
            return False
        if self.start_time >= other.end_time:
            return False
        return True

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "event_type": self.event_type.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "recurring": self.recurring,
            "recurrence_rule": self.recurrence_rule,
            "description": self.description,
            "color": self.color,
            "duration_minutes": self.duration_minutes,
        }


@dataclass
class AcademicCalendar:
    """A named collection of academic events for a specific period."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    year: int = datetime.now(timezone.utc).year
    events: list[AcademicEvent] = field(default_factory=list)

    def add_event(self, event: AcademicEvent) -> None:
        """Add an event, raising ValueError if it conflicts with an existing one."""
        for existing in self.events:
            if event.conflicts_with(existing):
                raise ValueError(
                    f"Event '{event.title}' conflicts with existing event '{existing.title}'."
                )
        self.events.append(event)

    def remove_event(self, event_id: str) -> bool:
        for i, e in enumerate(self.events):
            if e.id == event_id:
                self.events.pop(i)
                return True
        return False

    def get_event(self, event_id: str) -> Optional[AcademicEvent]:
        for e in self.events:
            if e.id == event_id:
                return e
        return None

    def get_events_by_type(self, event_type: AcademicEventType) -> list[AcademicEvent]:
        return [e for e in self.events if e.event_type == event_type]

    def get_events_in_range(
        self, start: datetime, end: datetime
    ) -> list[AcademicEvent]:
        result: list[AcademicEvent] = []
        for e in self.events:
            if e.start_time >= start and e.start_time <= end:
                result.append(e)
        return result

    def has_conflicts(self, event: AcademicEvent) -> bool:
        return any(event.conflicts_with(e) for e in self.events)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "year": self.year,
            "events": [e.to_dict() for e in self.events],
        }


@dataclass
class Term:
    """An academic term (semester, quarter, etc.)."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    start_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    breaks: list[AcademicEvent] = field(default_factory=list)

    @property
    def duration_days(self) -> float:
        delta = self.end_date - self.start_date
        return max(0.0, delta.total_seconds() / 86400.0)

    def add_break(self, break_event: AcademicEvent) -> None:
        if break_event.event_type != AcademicEventType.BREAK:
            raise ValueError("Break events must have event_type BREAK.")
        self.breaks.append(break_event)

    def is_during_break(self, date: datetime) -> bool:
        for b in self.breaks:
            if b.start_time <= date <= b.end_time:
                return True
        return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "duration_days": self.duration_days,
            "breaks": [b.to_dict() for b in self.breaks],
        }


@dataclass
class ImportantDate:
    """A flagged date of significance within the academic calendar."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    date_type: ImportantDateType = ImportantDateType.ENROLLMENT_DEADLINE
    description: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "date": self.date.isoformat(),
            "date_type": self.date_type.value,
            "description": self.description,
        }
