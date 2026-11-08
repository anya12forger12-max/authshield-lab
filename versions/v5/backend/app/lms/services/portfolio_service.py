"""Portfolio management service for the LMS module."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.events.lms_events import PortfolioItemAdded
from ..domain.interfaces.lms_interfaces import IPortfolioRepository
from ..validators.lms_validator import validate_portfolio_data, validate_portfolio_item_data

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for managing learner portfolios and portfolio items."""

    def __init__(self, portfolio_repo: IPortfolioRepository) -> None:
        self._repo = portfolio_repo

    def create_portfolio(self, data: dict[str, Any]) -> dict[str, Any]:
        validation = validate_portfolio_data(data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        existing = self._repo.get_by_learner(data["learner_id"])
        if existing:
            raise ValueError(f"Learner '{data['learner_id']}' already has a portfolio.")

        return self._repo.create(data)

    def get_portfolio(self, portfolio_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(portfolio_id)

    def get_portfolio_by_learner(self, learner_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_learner(learner_id)

    def list_portfolios(self) -> list[dict[str, Any]]:
        return self._repo.get_all()

    def update_portfolio(
        self, portfolio_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        if not self._repo.get_by_id(portfolio_id):
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")
        return self._repo.update(portfolio_id, data)

    def delete_portfolio(self, portfolio_id: str) -> bool:
        if not self._repo.get_by_id(portfolio_id):
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")
        return self._repo.delete(portfolio_id)

    def add_item(self, portfolio_id: str, item_data: dict[str, Any]) -> dict[str, Any]:
        portfolio = self._repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")

        validation = validate_portfolio_item_data(item_data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        item = self._repo.add_item(portfolio_id, item_data)

        event = PortfolioItemAdded(
            portfolio_id=portfolio_id,
            item_id=item.get("id", ""),
            learner_id=portfolio.get("learner_id", ""),
            item_type=item_data.get("item_type", "project"),
        )
        logger.info(
            "portfolio_item_added",
            extra={"portfolio_id": portfolio_id, "item_id": item.get("id"), "event_id": event.event_id},
        )
        return item

    def get_items(self, portfolio_id: str) -> list[dict[str, Any]]:
        if not self._repo.get_by_id(portfolio_id):
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")
        return self._repo.get_items(portfolio_id)

    def remove_item(self, portfolio_id: str, item_id: str) -> bool:
        portfolio = self._repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")
        return self._repo.remove_item(portfolio_id, item_id)

    def add_evidence(
        self, item_id: str, evidence_data: dict[str, Any]
    ) -> dict[str, Any]:
        if not evidence_data.get("competency_id"):
            raise ValueError("Competency ID is required for evidence.")
        if not evidence_data.get("description"):
            raise ValueError("Evidence description is required.")
        return self._repo.add_evidence(item_id, evidence_data)

    def get_evidence(self, item_id: str) -> list[dict[str, Any]]:
        return self._repo.get_evidence(item_id)

    def get_portfolio_summary(self, portfolio_id: str) -> dict[str, Any]:
        portfolio = self._repo.get_by_id(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")

        items = self._repo.get_items(portfolio_id)
        type_counts: dict[str, int] = {}
        for item in items:
            t = item.get("item_type", "unknown")
            type_counts[t] = type_counts.get(t, 0) + 1

        return {
            "portfolio_id": portfolio_id,
            "learner_id": portfolio.get("learner_id", ""),
            "title": portfolio.get("title", ""),
            "total_items": len(items),
            "item_type_counts": type_counts,
            "created_at": portfolio.get("created_at", ""),
            "updated_at": portfolio.get("updated_at", ""),
        }

    def update_item_metadata(
        self, portfolio_id: str, item_id: str, key: str, value: Any
    ) -> Optional[dict[str, Any]]:
        if not self._repo.get_by_id(portfolio_id):
            raise ValueError(f"Portfolio '{portfolio_id}' not found.")
        if not key:
            raise ValueError("Metadata key cannot be empty.")
        items = self._repo.get_items(portfolio_id)
        for item in items:
            if item.get("id") == item_id:
                metadata = item.get("metadata", {})
                metadata[key] = value
                item["metadata"] = metadata
                return item
        raise ValueError(f"Item '{item_id}' not found in portfolio.")
