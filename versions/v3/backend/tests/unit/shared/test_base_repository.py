"""Tests for BaseRepository methods."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.repositories.base_repository import BaseRepository


class FakeModel(TimestampMixin, UUIDPrimaryKeyMixin, Base):
    __tablename__ = "fake_test_table"
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


@pytest.fixture
def mock_session():
    return AsyncMock()


@pytest.fixture
def repository(mock_session):
    return BaseRepository(FakeModel, mock_session)


class TestRepositoryInit:
    def test_stores_model_and_session(self, mock_session):
        repo = BaseRepository(FakeModel, mock_session)
        assert repo._model is FakeModel
        assert repo._session is mock_session


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_flushes(self, repository, mock_session):
        await repository.create({"name": "test"})
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_returns_instance(self, repository, mock_session):
        instance = await repository.create({"name": "test"})
        assert instance is not None
        assert isinstance(instance, FakeModel)


class TestGetById:
    @pytest.mark.asyncio
    async def test_get_by_id_executes_query(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        result = await repository.get_by_id("test-id")
        assert result is None
        mock_session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_by_id_returns_instance(self, repository, mock_session):
        expected = MagicMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = expected
        mock_session.execute.return_value = mock_result
        result = await repository.get_by_id("test-id")
        assert result is expected


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_returns_false_when_not_found(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        result = await repository.delete("test-id")
        assert result is False

    @pytest.mark.asyncio
    async def test_soft_delete_sets_is_deleted(self, repository, mock_session):
        instance = MagicMock(spec=FakeModel)
        instance.is_deleted = False
        instance.deleted_at = None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = instance
        mock_session.execute.return_value = mock_result
        result = await repository.delete("test-id", hard=False)
        assert result is True
        assert instance.is_deleted is True

    @pytest.mark.asyncio
    async def test_hard_delete_removes(self, repository, mock_session):
        instance = MagicMock(spec=FakeModel)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = instance
        mock_session.execute.return_value = mock_result
        result = await repository.delete("test-id", hard=True)
        assert result is True
        mock_session.delete.assert_called_once_with(instance)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_returns_none_when_not_found(self, repository, mock_session):
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        result = await repository.update("test-id", {"name": "new"})
        assert result is None

    @pytest.mark.asyncio
    async def test_update_merges_data(self, repository, mock_session):
        instance = MagicMock(spec=FakeModel)
        instance.name = "old"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = instance
        mock_session.execute.return_value = mock_result
        result = await repository.update("test-id", {"name": "new"})
        assert instance.name == "new"
        mock_session.add.assert_called_once()
