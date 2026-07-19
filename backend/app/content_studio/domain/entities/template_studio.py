"""Template studio domain entities for the Content Production Studio."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class TemplateType(str, Enum):
    COURSE = "course"
    LESSON = "lesson"
    ASSESSMENT = "assessment"
    LAB = "lab"
    DOC = "doc"
    REPORT = "report"
    A11Y = "a11y"
    CURRICULUM = "curriculum"


@dataclass
class ContentTemplate:
    """A reusable content template with structure and defaults."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    template_type: TemplateType = TemplateType.LESSON
    description: str = ""
    structure: dict = field(default_factory=dict)
    version: int = 1
    author: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    inherit_from: str | None = None

    def update_structure(self, updates: dict) -> None:
        self.structure.update(updates)

    def set_structure_key(self, key: str, value: object) -> None:
        self.structure[key] = value

    def get_structure_key(self, key: str, default: object = None) -> object:
        return self.structure.get(key, default)

    def increment_version(self) -> None:
        self.version += 1

    def set_inheritance(self, parent_template_id: str | None) -> None:
        self.inherit_from = parent_template_id

    def get_required_fields(self) -> list[str]:
        return self.structure.get("required_fields", [])

    def get_default_values(self) -> dict:
        return self.structure.get("defaults", {})

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "template_type": self.template_type.value,
            "description": self.description,
            "structure": self.structure,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
            "inherit_from": self.inherit_from,
        }


@dataclass
class TemplateVersion:
    """Tracks version history of a content template."""

    template_id: str = ""
    version: int = 1
    changes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_change(self, change_description: str) -> None:
        self.changes.append(change_description)

    def get_change_count(self) -> int:
        return len(self.changes)

    def to_dict(self) -> dict:
        return {
            "template_id": self.template_id,
            "version": self.version,
            "changes": list(self.changes),
            "created_at": self.created_at.isoformat(),
            "change_count": self.get_change_count(),
        }


@dataclass
class TemplateInstance:
    """An instance of a content template with customizations applied."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    template_id: str = ""
    customizations: dict = field(default_factory=dict)
    created_by: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def apply_customization(self, key: str, value: object) -> None:
        self.customizations[key] = value

    def remove_customization(self, key: str) -> bool:
        if key in self.customizations:
            del self.customizations[key]
            return True
        return False

    def get_customization(self, key: str, default: object = None) -> object:
        return self.customizations.get(key, default)

    def has_customization(self, key: str) -> bool:
        return key in self.customizations

    def clear_customizations(self) -> None:
        self.customizations.clear()

    def merge_customizations(self, additional: dict) -> None:
        self.customizations.update(additional)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "template_id": self.template_id,
            "customizations": dict(self.customizations),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
        }
