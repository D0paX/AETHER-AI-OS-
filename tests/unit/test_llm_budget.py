"""Unit tests for the financial budget manager."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from aether.core.config import BudgetConfig
from aether.llm._models import ModelTier
from aether.llm.budget import BudgetManager


@pytest.fixture
def budget_manager() -> BudgetManager:
    config = BudgetConfig(daily_limit_usd=1.0, monthly_limit_usd=10.0)
    mock_redis = MagicMock()

    # Mock pipeline for check_and_record
    mock_pipeline = MagicMock()
    mock_redis.expire = AsyncMock()
    # incrbyfloat daily, incrbyfloat monthly, ttl daily, ttl monthly
    mock_pipeline.execute = AsyncMock(return_value=[0.1, 0.1, 86400, 2592000])  # type: ignore
    mock_redis.pipeline.return_value = mock_pipeline

    manager = BudgetManager(config, mock_redis)
    # Mock the internal event bus to prevent real Redis connections during tests
    manager._event_bus = AsyncMock()
    return manager


@pytest.mark.asyncio
async def test_budget_tracks_spend_in_redis(budget_manager: BudgetManager) -> None:
    # Set up pipeline specifically for record_actual_cost
    mock_pipeline = MagicMock()
    mock_pipeline.execute = AsyncMock()
    budget_manager._redis.pipeline.return_value = mock_pipeline  # type: ignore

    await budget_manager.record_actual_cost(0.5, ModelTier.PREMIUM)

    # Verify incrbyfloat was called for daily and monthly keys
    mock_pipeline.incrbyfloat.assert_any_call("aether:llm:budget:daily", 0.5)
    mock_pipeline.incrbyfloat.assert_any_call("aether:llm:budget:monthly", 0.5)
    mock_pipeline.execute.assert_called_once()


@pytest.mark.asyncio
async def test_daily_budget_resets_key_with_ttl(budget_manager: BudgetManager) -> None:
    # Setup ttl return of -1 (no ttl)
    mock_pipeline = MagicMock()
    mock_pipeline.execute = AsyncMock(return_value=[0.1, 0.1, -1, -1])
    budget_manager._redis.pipeline.return_value = mock_pipeline

    await budget_manager.check_and_record(ModelTier.PREMIUM, 0.1)

    # Should have called expire for daily and monthly since TTL was < 0
    assert budget_manager._redis.expire.call_count == 2  # type: ignore
    args, _ = budget_manager._redis.expire.call_args_list[0]  # type: ignore
    assert args[0] == "aether:llm:budget:daily"
    assert isinstance(args[1], int)


@pytest.mark.asyncio
async def test_local_tier_not_counted_against_budget(budget_manager: BudgetManager) -> None:
    tier = await budget_manager.check_and_record(ModelTier.LOCAL, 100.0)
    assert tier == ModelTier.LOCAL
    # Pipeline shouldn't even be created for LOCAL
    budget_manager._redis.pipeline.assert_not_called()  # type: ignore


@pytest.mark.asyncio
async def test_exceeded_budget_returns_local_tier_silently(budget_manager: BudgetManager) -> None:
    mock_pipeline = MagicMock()
    # Spent 5.0 on a 1.0 limit
    mock_pipeline.execute = AsyncMock(return_value=[5.0, 5.0, 86400, 2592000])  # type: ignore
    budget_manager._redis.pipeline.return_value = mock_pipeline  # type: ignore

    tier = await budget_manager.check_and_record(ModelTier.PREMIUM, 0.5)
    assert tier == ModelTier.LOCAL


@pytest.mark.asyncio
async def test_get_status_returns_budget_status_type(budget_manager: BudgetManager) -> None:
    mock_pipeline = MagicMock()
    mock_pipeline.execute = AsyncMock(return_value=[0.5, 2.5])  # type: ignore
    budget_manager._redis.pipeline.return_value = mock_pipeline  # type: ignore

    status = await budget_manager.get_status()

    assert status.daily_spent_usd == 0.5
    assert status.daily_limit_usd == 1.0
    assert status.daily_percent == 0.5
    assert status.monthly_spent_usd == 2.5
    assert status.active_tier_override is None
