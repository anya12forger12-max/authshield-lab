"""Device management service interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Any


class IDeviceService(ABC):
    """Interface for trusted device management operations."""

    @abstractmethod
    async def register_device(self, user_id: str, device_data: dict[str, Any]) -> Optional[dict]:
        """Register a new device for a user."""
        ...

    @abstractmethod
    async def get_device(self, device_id: str) -> Optional[dict]:
        """Retrieve a device by ID."""
        ...

    @abstractmethod
    async def get_user_devices(self, user_id: str) -> list[dict]:
        """Return all devices registered to a user."""
        ...

    @abstractmethod
    async def update_device(self, device_id: str, data: dict[str, Any]) -> Optional[dict]:
        """Update device metadata."""
        ...

    @abstractmethod
    async def remove_device(self, device_id: str) -> bool:
        """Remove a device registration."""
        ...

    @abstractmethod
    async def deactivate_device(self, device_id: str) -> bool:
        """Deactivate a device without removing it."""
        ...
