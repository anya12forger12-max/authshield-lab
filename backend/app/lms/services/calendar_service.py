"""Calendar management service for the LMS module."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from ..domain.events.lms_events import CalendarEventCreated
from ..domain.interfaces.lms_interfaces import ICalendarRepository
from ..validators.lms_validator import validate_calendar_event_data

logger = logging.getLogger(__name__)


class CalendarService:
    """Service for managing academic calendars, events, terms, and important dates."""

    def __init__(self, calendar_repo: ICalendarRepository) -> None:
        self._repo = calendar_repo

    def create_calendar(self, name: str, year: Optional[int] = None) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValueError("Calendar name is required.")
        if year is None:
            year = datetime.now(timezone.utc).year
        return self._repo.create({"name": name.strip(), "year": year})

    def get_calendar(self, calendar_id: str) -> Optional[dict[str, Any]]:
        return self._repo.get_by_id(calendar_id)

    def list_calendars(self) -> list[dict[str, Any]]:
        return self._repo.get_all()

    def update_calendar(
        self, calendar_id: str, data: dict[str, Any]
    ) -> Optional[dict[str, Any]]:
        if not self._repo.get_by_id(calendar_id):
            raise ValueError(f"Calendar '{calendar_id}' not found.")
        return self._repo.update(calendar_id, data)

    def delete_calendar(self, calendar_id: str) -> bool:
        if not self._repo.get_by_id(calendar_id):
            raise ValueError(f"Calendar '{calendar_id}' not found.")
        return self._repo.delete(calendar_id)

    def add_event(self, calendar_id: str, event_data: dict[str, Any]) -> dict[str, Any]:
        calendar = self._repo.get_by_id(calendar_id)
        if not calendar:
            raise ValueError(f"Calendar '{calendar_id}' not found.")

        validation = validate_calendar_event_data(event_data)
        if not validation.is_valid:
            raise ValueError(f"Validation failed: {validation.to_dict()}")

        existing_events = self._repo.get_events(calendar_id)
        start_time = event_data.get("start_time")
        end_time = event_data.get("end_time")
        if start_time and end_time:
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)
            for existing in existing_events:
                ex_start = existing.get("start_time")
                ex_end = existing.get("end_time")
                if isinstance(ex_start, str):
                    ex_start = datetime.fromisoformat(ex_start)
                if isinstance(ex_end, str):
                    ex_end = datetime.fromisoformat(ex_end)
                if start_time < ex_end and end_time > ex_start:
                    raise ValueError(
                        f"Event conflicts with existing event '{existing.get('title', '')}'."
                    )

        event = self._repo.add_event(calendar_id, event_data)
        event_created = CalendarEventCreated(
            calendar_id=calendar_id,
            event_id=event.get("id", ""),
            event_title=event.get("title", ""),
            event_type_detail=event.get("event_type", ""),
        )
        logger.info(
            "calendar_event_created",
            extra={"calendar_id": calendar_id, "event_id": event.get("id"), "event_id_event": event_created.event_id},
        )
        return event

    def get_events(self, calendar_id: str) -> list[dict[str, Any]]:
        if not self._repo.get_by_id(calendar_id):
            raise ValueError(f"Calendar '{calendar_id}' not found.")
        return self._repo.get_events(calendar_id)

    def remove_event(self, calendar_id: str, event_id: str) -> bool:
        if not self._repo.get_by_id(calendar_id):
            raise ValueError(f"Calendar '{calendar_id}' not found.")
        return self._repo.remove_event(calendar_id, event_id)

    def get_events_by_type(
        self, calendar_id: str, event_type: str
    ) -> list[dict[str, Any]]:
        events = self._repo.get_events(calendar_id)
        return [e for e in events if e.get("event_type") == event_type]

    def check_conflicts(
        self, calendar_id: str, start_time: datetime, end_time: datetime
    ) -> list[dict[str, Any]]:
        events = self._repo.get_events(calendar_id)
        conflicts: list[dict[str, Any]] = []
        for e in events:
            ex_start = e.get("start_time")
            ex_end = e.get("end_time")
            if isinstance(ex_start, str):
                ex_start = datetime.fromisoformat(ex_start)
            if isinstance(ex_end, str):
                ex_end = datetime.fromisoformat(ex_end)
            if start_time < ex_end and end_time > ex_start:
                conflicts.append(e)
        return conflicts

    def create_term(self, term_data: dict[str, Any]) -> dict[str, Any]:
        name = term_data.get("name", "")
        if not name or not str(name).strip():
            raise ValueError("Term name is required.")
        start_date = term_data.get("start_date")
        end_date = term_data.get("end_date")
        if not start_date or not end_date:
            raise ValueError("Both start_date and end_date are required.")
        return self._repo.create_term(term_data)

    def list_terms(self) -> list[dict[str, Any]]:
        return self._repo.get_terms()

    def create_important_date(self, data: dict[str, Any]) -> dict[str, Any]:
        title = data.get("title", "")
        if not title or not str(title).strip():
            raise ValueError("Important date title is required.")
        date_val = data.get("date")
        if not date_val:
            raise ValueError("Date is required.")
        return self._repo.create_important_date(data)

    def list_important_dates(self) -> list[dict[str, Any]]:
        return self._repo.get_important_dates()

    def get_upcoming_events(self, calendar_id: str) -> list[dict[str, Any]]:
        now = datetime.now(timezone.utc)
        events = self._repo.get_events(calendar_id)
        upcoming: list[dict[str, Any]] = []
        for e in events:
            start_time = e.get("start_time")
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if start_time and start_time > now:
                upcoming.append(e)
        upcoming.sort(key=lambda e: e.get("start_time", ""))
        return upcoming
