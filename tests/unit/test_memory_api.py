from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from aether.memory.api import MemoryAPI
from aether.memory.models import ContextPackage, MemoryRecord, MemorySource, MemoryType


@pytest.fixture
def mock_llm_router():
    router = MagicMock()
    router._embedding_service = AsyncMock()
    router._embedding_service.embed.return_value = MagicMock(vector=[0.1, 0.2, 0.3])
    router._event_bus = AsyncMock()
    return router


@pytest.fixture
def mock_sqlite():
    store = AsyncMock()
    store.create_memory.return_value = "00000000-0000-0000-0000-000000000000"
    store.delete_memory.return_value = True
    return store


@pytest.fixture
def mock_qdrant():
    store = AsyncMock()
    return store


@pytest.fixture
def mock_hybrid():
    hybrid = AsyncMock()
    pkg = ContextPackage(
        memories=[],
        total_found=0,
        token_estimate=0,
        formatted_context="",
        retrieval_query="",
        retrieval_duration_ms=0,
    )
    hybrid.search.return_value = pkg
    return hybrid


@pytest.fixture
def memory_api(mock_llm_router, mock_sqlite, mock_qdrant, mock_hybrid):
    api = MemoryAPI(mock_llm_router)
    api._sqlite_store = mock_sqlite
    api._vector_store = mock_qdrant
    api._hybrid = mock_hybrid
    return api


@pytest.mark.asyncio
async def test_remember_stores_to_sqlite(memory_api, mock_sqlite):
    await memory_api.remember("Test memory", MemoryType.FACT, 0.9)
    mock_sqlite.create_memory.assert_called_once()
    assert mock_sqlite.create_memory.call_args.kwargs["content"] == "Test memory"


@pytest.mark.asyncio
async def test_remember_stores_to_qdrant(memory_api, mock_qdrant):
    await memory_api.remember("Test memory", MemoryType.FACT, 0.9)
    mock_qdrant.upsert.assert_called_once()
    assert (
        mock_qdrant.upsert.call_args.kwargs["memory_id"] == "00000000-0000-0000-0000-000000000000"
    )
    assert "payload" in mock_qdrant.upsert.call_args.kwargs


@pytest.mark.asyncio
async def test_remember_returns_uuid_string(memory_api):
    result = await memory_api.remember("Test memory", MemoryType.FACT, 0.9)
    assert isinstance(result, str)
    assert result == "00000000-0000-0000-0000-000000000000"


@pytest.mark.asyncio
async def test_remember_emits_memory_store_created_event(memory_api, mock_llm_router):
    await memory_api.remember("Test memory", MemoryType.FACT, 0.9)
    mock_llm_router._event_bus.publish.assert_called_once()
    assert mock_llm_router._event_bus.publish.call_args.args[0] == "memory.store.created"


@pytest.mark.asyncio
async def test_recall_returns_context_package_type(memory_api):
    result = await memory_api.recall("test query")
    assert isinstance(result, ContextPackage)


@pytest.mark.asyncio
async def test_recall_respects_token_budget(memory_api, mock_hybrid):
    await memory_api.recall("test query", token_budget=100)
    mock_hybrid.search.assert_called_once()
    assert mock_hybrid.search.call_args.kwargs["token_budget"] == 100


@pytest.mark.asyncio
async def test_recall_updates_access_count(memory_api, mock_sqlite, mock_hybrid):
    # Mock return
    record = MemoryRecord(
        id="123",
        content="Test",
        memory_type=MemoryType.FACT,
        importance=0.5,
        confidence=0.9,
        source=MemorySource.CONVERSATION,
        tags=[],
        entities=[],
        created_at=datetime.now(UTC),
        last_accessed_at=datetime.now(UTC),
        access_count=0,
    )
    mock_hybrid.search.return_value = ContextPackage(
        memories=[record],
        total_found=1,
        token_estimate=10,
        formatted_context="",
        retrieval_query="",
        retrieval_duration_ms=0,
    )
    await memory_api.recall("test query")
    mock_sqlite.update_access.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_recall_updates_last_accessed_at(memory_api, mock_sqlite, mock_hybrid):
    # The API calls update_access, which in the SQLite layer updates last_accessed_at
    record = MemoryRecord(
        id="123",
        content="Test",
        memory_type=MemoryType.FACT,
        importance=0.5,
        confidence=0.9,
        source=MemorySource.CONVERSATION,
        tags=[],
        entities=[],
        created_at=datetime.now(UTC),
        last_accessed_at=datetime.now(UTC),
        access_count=0,
    )
    mock_hybrid.search.return_value = ContextPackage(
        memories=[record],
        total_found=1,
        token_estimate=10,
        formatted_context="",
        retrieval_query="",
        retrieval_duration_ms=0,
    )
    await memory_api.recall("test query")
    # In API, we just call update_access which implies last_accessed_at update is tested in SQLite
    mock_sqlite.update_access.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_forget_removes_from_sqlite(memory_api, mock_sqlite):
    await memory_api.forget("123", "Reason")
    mock_sqlite.delete_memory.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_forget_removes_from_qdrant(memory_api, mock_qdrant):
    await memory_api.forget("123", "Reason")
    mock_qdrant.delete.assert_called_once_with("123")


@pytest.mark.asyncio
async def test_forget_requires_reason_parameter(memory_api):
    with pytest.raises(ValueError):
        await memory_api.forget("123", "")


@pytest.mark.asyncio
async def test_forget_emits_memory_store_deleted_event(memory_api, mock_llm_router):
    await memory_api.forget("123", "Reason")
    mock_llm_router._event_bus.publish.assert_called_once()
    assert mock_llm_router._event_bus.publish.call_args.args[0] == "memory.store.deleted"
