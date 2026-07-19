"""Template management service for projects, courses, assessments, and policies."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


class _TemplateRecord:
    """Internal template storage object."""

    def __init__(
        self,
        id: str,
        name: str,
        template_type: str,
        description: str,
        content: dict,
        category: str,
        version: str,
        author: str,
        created_at: datetime,
    ) -> None:
        self.id = id
        self.name = name
        self.template_type = template_type
        self.description = description
        self.content = content
        self.category = category
        self.version = version
        self.author = author
        self.created_at = created_at

    def to_dict(self) -> dict:
        """Serialize to a plain dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "template_type": self.template_type,
            "description": self.description,
            "content": dict(self.content),
            "category": self.category,
            "version": self.version,
            "author": self.author,
            "created_at": self.created_at.isoformat(),
        }


class TemplateService:
    """CRUD operations for project, course, assessment, and policy templates."""

    def __init__(self) -> None:
        self._templates: dict[str, _TemplateRecord] = {}

    def create(
        self,
        name: str,
        template_type: str = "project",
        description: str = "",
        content: dict | None = None,
        category: str = "general",
        version: str = "1.0.0",
        author: str = "",
    ) -> _TemplateRecord:
        """Create a new template."""
        record = _TemplateRecord(
            id=str(uuid.uuid4()),
            name=name,
            template_type=template_type,
            description=description,
            content=content if content is not None else {},
            category=category,
            version=version,
            author=author,
            created_at=datetime.now(timezone.utc),
        )
        self._templates[record.id] = record
        return record

    def get(self, template_id: str) -> _TemplateRecord | None:
        """Retrieve a template by ID."""
        return self._templates.get(template_id)

    def list_all(self) -> list[_TemplateRecord]:
        """Return all templates."""
        return list(self._templates.values())

    def list_by_type(self, template_type: str) -> list[_TemplateRecord]:
        """Return templates filtered by type."""
        return [t for t in self._templates.values() if t.template_type == template_type]

    def list_by_category(self, category: str) -> list[_TemplateRecord]:
        """Return templates filtered by category."""
        return [t for t in self._templates.values() if t.category == category]

    def search(self, query: str) -> list[_TemplateRecord]:
        """Search templates by name or description."""
        q = query.lower()
        return [
            t
            for t in self._templates.values()
            if q in t.name.lower() or q in t.description.lower()
        ]

    def update(
        self,
        template_id: str,
        name: str | None = None,
        description: str | None = None,
        content: dict | None = None,
        category: str | None = None,
        version: str | None = None,
        author: str | None = None,
    ) -> _TemplateRecord | None:
        """Update mutable fields on a template."""
        record = self._templates.get(template_id)
        if record is None:
            return None
        if name is not None:
            record.name = name
        if description is not None:
            record.description = description
        if content is not None:
            record.content = dict(content)
        if category is not None:
            record.category = category
        if version is not None:
            record.version = version
        if author is not None:
            record.author = author
        return record

    def delete(self, template_id: str) -> bool:
        """Delete a template."""
        if template_id in self._templates:
            del self._templates[template_id]
            return True
        return False

    def duplicate(self, template_id: str, new_name: str | None = None) -> _TemplateRecord | None:
        """Create a copy of an existing template."""
        original = self._templates.get(template_id)
        if original is None:
            return None
        copy = _TemplateRecord(
            id=str(uuid.uuid4()),
            name=new_name or f"{original.name} (copy)",
            template_type=original.template_type,
            description=original.description,
            content=dict(original.content),
            category=original.category,
            version=original.version,
            author=original.author,
            created_at=datetime.now(timezone.utc),
        )
        self._templates[copy.id] = copy
        return copy

    def count(self) -> int:
        """Return the total number of templates."""
        return len(self._templates)

    def list_project_templates(self) -> list[_TemplateRecord]:
        """Return templates of type 'project'."""
        return self.list_by_type("project")

    def list_course_templates(self) -> list[_TemplateRecord]:
        """Return templates of type 'course'."""
        return self.list_by_type("course")

    def list_assessment_templates(self) -> list[_TemplateRecord]:
        """Return templates of type 'assessment'."""
        return self.list_by_type("assessment")

    def list_policy_templates(self) -> list[_TemplateRecord]:
        """Return templates of type 'policy'."""
        return self.list_by_type("policy")
