"""Portfolio domain entities for the LMS module."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional


class PortfolioItemType(str, Enum):
    """Type of portfolio item."""

    CERTIFICATE = "certificate"
    PROJECT = "project"
    ASSESSMENT = "assessment"
    REFLECTION = "reflection"
    BADGE = "badge"


@dataclass
class PortfolioCategory:
    """A category for organizing portfolio items."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
        }


@dataclass
class PortfolioItem:
    """A single artifact within a learner's portfolio."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    portfolio_id: str = ""
    title: str = ""
    description: str = ""
    item_type: PortfolioItemType = PortfolioItemType.PROJECT
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)

    def update_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value

    def remove_metadata(self, key: str) -> bool:
        try:
            del self.metadata[key]
            return True
        except KeyError:
            return False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "portfolio_id": self.portfolio_id,
            "title": self.title,
            "description": self.description,
            "item_type": self.item_type.value,
            "created_at": self.created_at.isoformat(),
            "metadata": dict(self.metadata),
        }


@dataclass
class CompetencyEvidence:
    """Links a portfolio item to a competency as evidence of achievement."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    item_id: str = ""
    competency_id: str = ""
    description: str = ""
    date_earned: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "item_id": self.item_id,
            "competency_id": self.competency_id,
            "description": self.description,
            "date_earned": self.date_earned.isoformat(),
        }


@dataclass
class Portfolio:
    """A learner's collection of artifacts and achievements."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = ""
    title: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    _items: list[PortfolioItem] = field(default_factory=list, repr=False)

    @property
    def item_count(self) -> int:
        return len(self._items)

    def add_item(self, item: PortfolioItem) -> None:
        """Add an item to the portfolio."""
        item.portfolio_id = self.id
        self._items.append(item)
        self.updated_at = datetime.now(timezone.utc)

    def remove_item(self, item_id: str) -> bool:
        """Remove an item by ID. Returns ``True`` if found and removed."""
        for i, item in enumerate(self._items):
            if item.id == item_id:
                self._items.pop(i)
                self.updated_at = datetime.now(timezone.utc)
                return True
        return False

    def get_item(self, item_id: str) -> Optional[PortfolioItem]:
        for item in self._items:
            if item.id == item_id:
                return item
        return None

    def get_items_by_type(self, item_type: PortfolioItemType) -> list[PortfolioItem]:
        return [i for i in self._items if i.item_type == item_type]

    def get_all_items(self) -> list[PortfolioItem]:
        return list(self._items)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "learner_id": self.learner_id,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "item_count": self.item_count,
            "items": [i.to_dict() for i in self._items],
        }
