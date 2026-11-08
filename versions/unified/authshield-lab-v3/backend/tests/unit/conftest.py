"""Shared test fixtures for unit tests."""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timezone

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def mock_session():
    return AsyncMock()

@pytest.fixture
def mock_event_bus():
    bus = AsyncMock()
    bus.publish = AsyncMock()
    bus.subscribe = MagicMock()
    return bus

@pytest.fixture
def mock_user_repository():
    repo = AsyncMock()
    repo.get_by_username = AsyncMock(return_value=None)
    repo.get_by_id = AsyncMock(return_value=None)
    repo.exists_by_username = AsyncMock(return_value=False)
    repo.exists_by_email = AsyncMock(return_value=False)
    repo.create = AsyncMock()
    repo.update = AsyncMock()
    repo.search = AsyncMock(return_value={"items": [], "total": 0, "page": 1, "per_page": 20, "pages": 0})
    return repo

@pytest.fixture
def mock_session_repository():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_active_by_user = AsyncMock(return_value=[])
    repo.update = AsyncMock()
    repo.delete = AsyncMock()
    repo.delete_expired = AsyncMock(return_value=0)
    repo.delete_all_user_sessions = AsyncMock(return_value=0)
    return repo

@pytest.fixture
def mock_audit_repository():
    repo = AsyncMock()
    repo.create = AsyncMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_user = AsyncMock(return_value={"items": [], "total": 0, "page": 1, "per_page": 50, "pages": 0})
    repo.search = AsyncMock(return_value={"items": [], "total": 0, "page": 1, "per_page": 50, "pages": 0})
    return repo

@pytest.fixture
def mock_password_hasher():
    hasher = MagicMock()
    hasher.hash_password.return_value = "$argon2id$v=19$m=65536,t=3,p=4$hashed_password"
    hasher.verify_password.return_value = True
    hasher.get_algorithm_info.return_value = {"name": "Argon2id", "type": "Memory-hard"}
    hasher.get_recommended_algorithm.return_value = "argon2id"
    hasher.get_supported_algorithms.return_value = ["argon2id", "bcrypt", "pbkdf2_sha256"]
    return hasher

@pytest.fixture
def mock_performance_monitor():
    monitor = MagicMock()
    monitor.start_timer = MagicMock()
    monitor.stop_timer = MagicMock(return_value=MagicMock(duration_ms=1.5, success=True))
    monitor.record_metric = MagicMock()
    return monitor
