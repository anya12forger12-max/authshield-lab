"""Base repository with common CRUD operations."""

from __future__ import annotations

from typing import Any, Generic, Optional, Type, TypeVar

from sqlalchemy import select, func, desc, asc, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..base_model import Base
from ..logging_config import get_logger

ModelType = TypeVar("ModelType", bound=Base)
logger = get_logger(__name__)


class BaseRepository(Generic[ModelType]):
    """Generic async repository that provides standard CRUD operations.

    Subclass this and set ``_model`` to a specific SQLAlchemy mapped class
    to gain type-safe access patterns for that entity.
    """

    def __init__(self, model: Type[ModelType], session: AsyncSession) -> None:
        self._model = model
        self._session = session

    # ------------------------------------------------------------------
    # Create
    # ------------------------------------------------------------------

    async def create(self, data: dict[str, Any]) -> ModelType:
        """Insert a new row and return the persisted instance.

        Parameters
        ----------
        data:
            Mapping of column name -> value for the new row.

        Raises
        ------
        IntegrityError
            Re-raised after a rollback when a unique / FK constraint fails.
        """
        instance = self._model(**data)
        self._session.add(instance)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            logger.warning(
                "integrity_error_on_create",
                model=self._model.__tablename__,
            )
            raise
        return instance  # type: ignore[return-value]

    # ------------------------------------------------------------------
    # Read
    # ------------------------------------------------------------------

    async def get_by_id(self, id: str) -> Optional[ModelType]:
        """Return the entity with the given primary key, or ``None``."""
        stmt = select(self._model).where(self._model.id == id)  # type: ignore[attr-defined]
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        order_by: str = "created_at",
        descending: bool = True,
    ) -> dict:
        """Return a paginated list of all entities.

        Returns
        -------
        dict
            ``{"items": [...], "total": int, "page": int, "per_page": int,
            "pages": int}``
        """
        # Build ordering column
        col = getattr(self._model, order_by, None)
        if col is None:
            col = self._model.id  # type: ignore[attr-defined]
        order = desc(col) if descending else asc(col)

        # Total count
        count_stmt = select(func.count()).select_from(self._model)
        total_result = await self._session.execute(count_stmt)
        total: int = total_result.scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = select(self._model).order_by(order).offset(offset).limit(per_page)
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    # ------------------------------------------------------------------
    # Update
    # ------------------------------------------------------------------

    async def update(self, id: str, data: dict[str, Any]) -> Optional[ModelType]:
        """Merge *data* into the row identified by *id*.

        Returns the updated instance or ``None`` if no row was found.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return None

        for key, value in data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        self._session.add(instance)
        try:
            await self._session.flush()
        except IntegrityError:
            await self._session.rollback()
            logger.warning(
                "integrity_error_on_update",
                model=self._model.__tablename__,
                entity_id=id,
            )
            raise
        return instance

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    async def delete(self, id: str, hard: bool = False) -> bool:
        """Delete (or soft-delete) the entity with the given *id*.

        Parameters
        ----------
        id:
            Primary key value.
        hard:
            When ``True`` the row is physically removed.  When ``False``
            and the model has ``SoftDeleteMixin``, the row is soft-deleted.

        Returns
        -------
        bool
            ``True`` if a row was affected, ``False`` otherwise.
        """
        instance = await self.get_by_id(id)
        if instance is None:
            return False

        if hard or not hasattr(instance, "is_deleted"):
            await self._session.delete(instance)
        else:
            from datetime import datetime, timezone

            instance.is_deleted = True  # type: ignore[attr-defined]
            instance.deleted_at = datetime.now(timezone.utc)  # type: ignore[attr-defined]
            self._session.add(instance)

        await self._session.flush()
        return True

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    async def count(self, filters: Optional[dict[str, Any]] = None) -> int:
        """Return the row count, optionally filtered by *filters*."""
        stmt = select(func.count()).select_from(self._model)
        if filters:
            stmt = self._apply_filters(stmt, filters)
        result = await self._session.execute(stmt)
        return result.scalar()  # type: ignore[return-value]

    async def exists(self, **kwargs: Any) -> bool:
        """Return ``True`` if at least one row matches the keyword filters."""
        stmt = select(func.count()).select_from(self._model)
        stmt = self._apply_filters(stmt, kwargs)
        result = await self._session.execute(stmt)
        count_val: int = result.scalar()  # type: ignore[assignment]
        return count_val > 0

    async def search(
        self,
        query: str,
        fields: list[str],
        page: int = 1,
        per_page: int = 20,
    ) -> dict:
        """Case-insensitive LIKE search across the given *fields*.

        Returns a paginated result dict with the same shape as ``get_all``.
        """
        conditions = []
        for field_name in fields:
            col = getattr(self._model, field_name, None)
            if col is not None:
                conditions.append(col.ilike(f"%{query}%"))

        if not conditions:
            return {"items": [], "total": 0, "page": page, "per_page": per_page, "pages": 0}

        from sqlalchemy import or_

        stmt = select(self._model).where(or_(*conditions))
        count_stmt = select(func.count()).select_from(self._model).where(or_(*conditions))

        total_result = await self._session.execute(count_stmt)
        total: int = total_result.scalar()  # type: ignore[assignment]

        pages = max(1, (total + per_page - 1) // per_page)
        offset = (page - 1) * per_page

        stmt = stmt.order_by(desc(self._model.created_at)).offset(offset).limit(per_page)  # type: ignore[attr-defined]
        result = await self._session.execute(stmt)
        items = list(result.scalars().all())

        return {
            "items": items,
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": pages,
        }

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _apply_filters(self, stmt: Any, filters: dict[str, Any]) -> Any:
        """Apply equality filters to a SELECT statement."""
        for key, value in filters.items():
            col = getattr(self._model, key, None)
            if col is not None:
                stmt = stmt.where(col == value)
        return stmt
