"""Async SQLAlchemy database setup and session management."""

from __future__ import annotations

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.config.settings import get_settings
from app.shared.base_model import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


async def init_db() -> None:
    """Create the async engine, session factory, and tables.

    Called once during application startup.
    """
    global _engine, _session_factory  # noqa: PLW0603

    settings = get_settings()
    db_url = settings.database.url

    _engine = create_async_engine(
        db_url,
        echo=settings.database.echo,
        pool_pre_ping=True,
    )

    _session_factory = async_sessionmaker(
        bind=_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Dispose the async engine and release connection pool resources.

    Called once during application shutdown.
    """
    global _engine, _session_factory  # noqa: PLW0603

    if _engine is not None:
        await _engine.dispose()
        _engine = None
    _session_factory = None


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an ``AsyncSession``.

    The session is automatically closed when the request handler completes.
    """
    if _session_factory is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() during application startup."
        )

    async with _session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


def get_engine() -> AsyncEngine:
    """Return the current async engine (raises if not initialized)."""
    if _engine is None:
        raise RuntimeError("Database engine not initialized.")
    return _engine


def get_metadata():
    """Return the SQLAlchemy ``MetaData`` from the Base."""
    return Base.metadata
