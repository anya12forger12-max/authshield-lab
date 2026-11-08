"""Device repository with user-device tracking helpers."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select, func, desc, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.device import Device
from ..logging_config import get_logger
from .base_repository import BaseRepository

logger = get_logger(__name__)


class DeviceRepository(BaseRepository[Device]):
    """Async repository for :class:`Device` entities."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(Device, session)

    # ------------------------------------------------------------------
    # Lookups
    # ------------------------------------------------------------------

    async def get_by_device_id(self, device_id: str) -> Device | None:
        """Return the device matching *device_id*, or ``None``."""
        stmt = select(Device).where(Device.device_id == device_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_devices(self, user_id: str) -> list[Device]:
        """Return all devices (active and inactive) for *user_id*."""
        stmt = (
            select(Device)
            .where(Device.user_id == user_id)
            .order_by(desc(Device.last_seen))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def get_active_devices(self, user_id: str) -> list[Device]:
        """Return only active devices for *user_id*."""
        stmt = (
            select(Device)
            .where(Device.user_id == user_id, Device.is_active == True)  # noqa: E712
            .order_by(desc(Device.last_seen))
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    # ------------------------------------------------------------------
    # State transitions
    # ------------------------------------------------------------------

    async def update_last_seen(self, device_id: str) -> Device | None:
        """Bump ``last_seen`` to now for the given device.

        Returns the updated device or ``None`` if not found.
        """
        stmt = select(Device).where(Device.device_id == device_id)
        result = await self._session.execute(stmt)
        device = result.scalar_one_or_none()
        if device is None:
            return None

        device.last_seen = datetime.now(timezone.utc)
        self._session.add(device)
        await self._session.flush()
        return device

    async def deactivate_device(self, device_id: str) -> bool:
        """Set ``is_active`` to ``False`` for the given device.

        Returns ``True`` if a row was affected.
        """
        stmt = (
            update(Device)
            .where(Device.device_id == device_id)
            .values(is_active=False)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        count = result.rowcount  # type: ignore[attr-defined]
        if count > 0:
            logger.info("device_deactivated", device_id=device_id)
        return count > 0  # type: ignore[return-value]
