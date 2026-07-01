import inspect

from aether.memory.api import MemoryAPI
from aether.memory.models import (
    ConsolidationReport,
    ContextPackage,
    MemoryRecord,
    MemoryType,
)


def test_memory_api_has_remember_method():
    assert hasattr(MemoryAPI, "remember")


def test_remember_signature_matches_spec():
    sig = inspect.signature(MemoryAPI.remember)
    assert "content" in sig.parameters
    assert "memory_type" in sig.parameters
    assert "importance" in sig.parameters
    assert "metadata" in sig.parameters
    assert "session_id" in sig.parameters
    assert "source" in sig.parameters
    assert sig.return_annotation == str


def test_memory_api_has_recall_method():
    assert hasattr(MemoryAPI, "recall")


def test_recall_signature_matches_spec():
    sig = inspect.signature(MemoryAPI.recall)
    assert "query" in sig.parameters
    assert "k" in sig.parameters
    assert "filters" in sig.parameters
    assert "token_budget" in sig.parameters
    assert sig.return_annotation == ContextPackage


def test_memory_api_has_forget_method():
    assert hasattr(MemoryAPI, "forget")
    sig = inspect.signature(MemoryAPI.forget)
    assert "memory_id" in sig.parameters
    assert "reason" in sig.parameters
    assert sig.return_annotation == bool


def test_memory_api_has_consolidate_method():
    assert hasattr(MemoryAPI, "consolidate")
    sig = inspect.signature(MemoryAPI.consolidate)
    assert "session_id" in sig.parameters
    assert sig.return_annotation == ConsolidationReport


def test_memory_api_has_search_method():
    assert hasattr(MemoryAPI, "search")
    sig = inspect.signature(MemoryAPI.search)
    assert "query" in sig.parameters
    assert "memory_type" in sig.parameters
    assert "limit" in sig.parameters
    assert "min_importance" in sig.parameters
    assert sig.return_annotation == list[MemoryRecord]


def test_memory_record_is_frozen():
    assert MemoryRecord.model_config.get("frozen") is True


def test_context_package_has_formatted_context_field():
    assert "formatted_context" in ContextPackage.model_fields


def test_memory_type_has_four_values():
    values = [m.value for m in MemoryType]
    assert "FACT" in values
    assert "EPISODE" in values
    assert "SKILL" in values
    assert "PREFERENCE" in values
    assert len(values) == 4
