"""Integration test fixtures with real database (SQLite in-memory)."""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.shared.base_model import Base


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def engine():
    eng = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    await eng.dispose()


@pytest.fixture
async def db_session(engine):
    session_factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture
def sample_user_data():
    return {
        "username": "testuser",
        "display_name": "Test User",
        "email": "test@example.com",
        "password_hash": "$argon2id$v=19$m=65536,t=3,p=4$hashed",
        "hash_algorithm": "argon2id",
        "account_status": "active",
        "role": "student",
    }
