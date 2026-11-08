"""Classroom domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


class ClassroomStatus(str, Enum):
    """Lifecycle status of a classroom."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class SessionStatus(str, Enum):
    """Status of an individual classroom session."""

    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class ClassroomRole(str, Enum):
    """Roles a member can hold within a classroom."""

    INSTRUCTOR = "instructor"
    TEACHING_ASSISTANT = "teaching_assistant"
    LEARNER = "learner"
    OBSERVER = "observer"


class ClassroomMemberStatus(str, Enum):
    """Membership status of a classroom member."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    REMOVED = "removed"


@dataclass
class ClassroomMember:
    """Membership linking a user to a classroom with a specific role."""

    user_id: str = ""
    role: ClassroomRole = ClassroomRole.LEARNER
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: ClassroomMemberStatus = ClassroomMemberStatus.ACTIVE

    @property
    def is_instructor(self) -> bool:
        return self.role == ClassroomRole.INSTRUCTOR

    @property
    def is_active_member(self) -> bool:
        return self.status == ClassroomMemberStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "role": self.role.value,
            "joined_at": self.joined_at.isoformat(),
            "status": self.status.value,
        }


@dataclass
class ClassroomSession:
    """An individual scheduled session within a classroom."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    classroom_id: str = ""
    title: str = ""
    start_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    end_time: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: SessionStatus = SessionStatus.SCHEDULED
    notes: Optional[str] = None

    @property
    def duration_minutes(self) -> float:
        delta = self.end_time - self.start_time
        return max(0.0, delta.total_seconds() / 60.0)

    def start(self) -> None:
        self.status = SessionStatus.IN_PROGRESS

    def complete(self, notes: Optional[str] = None) -> None:
        self.status = SessionStatus.COMPLETED
        if notes:
            self.notes = notes

    def cancel(self, reason: Optional[str] = None) -> None:
        self.status = SessionStatus.CANCELLED
        if reason:
            self.notes = reason

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "classroom_id": self.classroom_id,
            "title": self.title,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "status": self.status.value,
            "notes": self.notes,
            "duration_minutes": self.duration_minutes,
        }


@dataclass
class Classroom:
    """Root aggregate representing a teaching classroom."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    capacity: int = 30
    instructor_id: str = ""
    status: ClassroomStatus = ClassroomStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _members: list[ClassroomMember] = field(default_factory=list, repr=False)

    @property
    def is_full(self) -> bool:
        """Return ``True`` when active enrollment has reached capacity."""
        return len(self.active_members) >= self.capacity

    @property
    def active_members(self) -> list[ClassroomMember]:
        return [m for m in self._members if m.is_active_member]

    @property
    def member_count(self) -> int:
        return len(self.active_members)

    @property
    def available_seats(self) -> int:
        return max(0, self.capacity - self.member_count)

    def add_member(
        self,
        user_id: str,
        role: ClassroomRole = ClassroomRole.LEARNER,
    ) -> ClassroomMember:
        """Add a member to the classroom.

        Raises
        ------
        ValueError
            If the classroom is full or the user is already an active member.
        """
        for existing in self._members:
            if existing.user_id == user_id and existing.is_active_member:
                raise ValueError(f"User '{user_id}' is already an active member of this classroom.")

        if self.is_full:
            raise ValueError(
                f"Classroom '{self.name}' has reached its capacity of {self.capacity}."
            )

        member = ClassroomMember(
            user_id=user_id,
            role=role,
            joined_at=datetime.now(timezone.utc),
            status=ClassroomMemberStatus.ACTIVE,
        )
        self._members.append(member)
        self.updated_at = datetime.now(timezone.utc)
        return member

    def remove_member(self, user_id: str) -> bool:
        """Remove a member from the classroom by marking them inactive.

        Returns
        -------
        bool
            ``True`` if the member was found and removed, ``False`` otherwise.
        """
        for member in self._members:
            if member.user_id == user_id and member.is_active_member:
                member.status = ClassroomMemberStatus.REMOVED
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def get_members(
        self,
        role: Optional[ClassroomRole] = None,
    ) -> list[ClassroomMember]:
        """Return active members, optionally filtered by role."""
        members = self.active_members
        if role is not None:
            members = [m for m in members if m.role == role]
        return list(members)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capacity": self.capacity,
            "instructor_id": self.instructor_id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "member_count": self.member_count,
            "available_seats": self.available_seats,
            "is_full": self.is_full,
            "members": [m.to_dict() for m in self._members],
        }
