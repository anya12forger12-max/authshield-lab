"""Device management service implementation."""

from __future__ import annotations

import uuid
from typing import Any, Optional
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...shared.exceptions import NotFoundError, ValidationError
from ...shared.logging_config import get_logger, log_audit_event
from ...shared.events.event_bus import EventBus, DomainEvent
from ...config.constants import MODULE_USERS
from ..domain.interfaces.device_service import IDeviceService
from ..domain.events.identity_events import DeviceRegisteredEvent, DeviceRemovedEvent

logger = get_logger(MODULE_USERS)

# In-memory device store since no Device model table exists yet.
# In production this would use a proper DeviceRepository.
_devices: dict[str, dict[str, Any]] = {}


class DeviceService(IDeviceService):
    """Concrete implementation of trusted device management.

    Parameters
    ----------
    event_bus:
        In-process event bus for publishing domain events.
    """

    def __init__(self, event_bus: Optional[EventBus] = None) -> None:
        self._event_bus = event_bus

    async def _publish_event(self, event: DomainEvent) -> None:
        if self._event_bus is not None:
            await self._event_bus.publish(event)

    async def register_device(self, user_id: str, device_data: dict[str, Any]) -> Optional[dict]:
        """Register a new device for a user."""
        device_name = device_data.get("device_name", "")
        if not device_name:
            raise ValidationError("Device name is required.", detail={"field": "device_name"})

        device_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)

        device: dict[str, Any] = {
            "device_id": device_id,
            "user_id": user_id,
            "device_name": device_name,
            "device_type": device_data.get("device_type", "unknown"),
            "platform": device_data.get("platform", "unknown"),
            "is_active": True,
            "is_trusted": device_data.get("is_trusted", False),
            "last_seen": now.isoformat(),
            "registered_at": now.isoformat(),
        }

        _devices[device_id] = device

        event = DeviceRegisteredEvent(
            user_id=user_id,
            device_id=device_id,
            correlation_id=user_id,
            metadata={"device_name": device_name},
        )
        await self._publish_event(event)

        log_audit_event(
            "DEVICE_REGISTERED",
            user_id=user_id,
            action="REGISTER",
            resource=f"device:{device_id}",
            logger=logger,
        )

        return device

    async def get_device(self, device_id: str) -> Optional[dict]:
        """Retrieve a device by ID."""
        device = _devices.get(device_id)
        if device is None:
            return None
        return dict(device)

    async def get_user_devices(self, user_id: str) -> list[dict]:
        """Return all devices registered to a user."""
        return [
            dict(d) for d in _devices.values()
            if d.get("user_id") == user_id
        ]

    async def update_device(self, device_id: str, data: dict[str, Any]) -> Optional[dict]:
        """Update device metadata."""
        device = _devices.get(device_id)
        if device is None:
            raise NotFoundError(f"Device {device_id} not found.")

        allowed_keys = {"device_name", "device_type", "platform", "is_trusted"}
        for key, value in data.items():
            if key in allowed_keys:
                device[key] = value

        device["last_seen"] = datetime.now(timezone.utc).isoformat()
        return dict(device)

    async def remove_device(self, device_id: str) -> bool:
        """Remove a device registration."""
        device = _devices.pop(device_id, None)
        if device is None:
            raise NotFoundError(f"Device {device_id} not found.")

        event = DeviceRemovedEvent(
            user_id=device.get("user_id", ""),
            device_id=device_id,
            correlation_id=device.get("user_id", ""),
        )
        await self._publish_event(event)

        log_audit_event(
            "DEVICE_REMOVED",
            user_id=device.get("user_id", ""),
            action="REMOVE",
            resource=f"device:{device_id}",
            logger=logger,
        )

        return True

    async def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device without removing it."""
        device = _devices.get(device_id)
        if device is None:
            raise NotFoundError(f"Device {device_id} not found.")

        device["is_active"] = False
        device["last_seen"] = datetime.now(timezone.utc).isoformat()

        log_audit_event(
            "DEVICE_DEACTIVATED",
            user_id=device.get("user_id", ""),
            action="DEACTIVATE",
            resource=f"device:{device_id}",
            logger=logger,
        )

        return True
