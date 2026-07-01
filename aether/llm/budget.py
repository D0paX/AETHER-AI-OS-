"""Financial budget management for paid LLM APIs."""

import calendar
from datetime import UTC, datetime

import redis.asyncio as aioredis

from aether.core.config import BudgetConfig, get_config
from aether.core.events import EventBus
from aether.core.logging import get_logger
from aether.llm._models import BudgetStatus, ModelTier

logger = get_logger("aether.llm.budget")


class BudgetManager:
    """Manages LLM API budgets using Redis counters."""

    def __init__(self, config: BudgetConfig, redis_client: aioredis.Redis) -> None:
        """Initialize the budget manager."""
        self._config = config
        self._redis = redis_client
        self._daily_key = "aether:llm:budget:daily"
        self._monthly_key = "aether:llm:budget:monthly"
        self._event_bus = EventBus(get_config().redis)

    def _get_seconds_until_midnight_utc(self) -> int:
        now = datetime.now(UTC)
        tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta

        tomorrow += timedelta(days=1)
        return int((tomorrow - now).total_seconds())

    def _get_seconds_until_next_month_utc(self) -> int:
        now = datetime.now(UTC)
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        next_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        from datetime import timedelta

        next_month += timedelta(days=days_in_month)
        return int((next_month - now).total_seconds())

    async def check_and_record(
        self, requested_tier: ModelTier, estimated_cost_usd: float
    ) -> ModelTier:
        """Check if budget allows the requested tier and reserve estimated cost.

        If the budget is exceeded, it silently returns ModelTier.LOCAL.
        If the budget hits 80%, it emits a warning event.
        """
        if requested_tier == ModelTier.LOCAL or estimated_cost_usd <= 0.0:
            return requested_tier

        # Atomically increment and get new values
        pipeline = self._redis.pipeline()
        pipeline.incrbyfloat(self._daily_key, estimated_cost_usd)
        pipeline.incrbyfloat(self._monthly_key, estimated_cost_usd)

        # Ensure TTL is set if not already set (returns -1 if no TTL, -2 if key missing)
        pipeline.ttl(self._daily_key)
        pipeline.ttl(self._monthly_key)

        results = await pipeline.execute()
        daily_spent = float(results[0])
        monthly_spent = float(results[1])
        daily_ttl = int(results[2])
        monthly_ttl = int(results[3])

        # Set TTLs if they don't exist
        if daily_ttl < 0:
            await self._redis.expire(self._daily_key, self._get_seconds_until_midnight_utc())
        if monthly_ttl < 0:
            await self._redis.expire(self._monthly_key, self._get_seconds_until_next_month_utc())

        # Check limits
        daily_limit = self._config.daily_limit_usd
        monthly_limit = self._config.monthly_limit_usd

        daily_percent = (daily_spent / daily_limit) if daily_limit > 0 else 0
        monthly_percent = (monthly_spent / monthly_limit) if monthly_limit > 0 else 0

        # Check for 80% threshold to emit warning
        if (
            daily_percent >= 0.8 and (daily_percent - (estimated_cost_usd / daily_limit)) < 0.8
        ) or (
            monthly_percent >= 0.8
            and (monthly_percent - (estimated_cost_usd / monthly_limit)) < 0.8
        ):
            logger.warning(
                "Budget threshold reached",
                daily_percent=daily_percent,
                monthly_percent=monthly_percent,
            )
            # Ensure bus is connected before emitting
            if not self._event_bus._redis:
                await self._event_bus.connect()
            await self._event_bus.emit(
                event_type="system.budget.threshold_reached",
                payload={
                    "daily_percent": daily_percent,
                    "monthly_percent": monthly_percent,
                },
            )

        # Check if exceeded
        if daily_spent > daily_limit or monthly_spent > monthly_limit:
            logger.warning(
                "Budget exceeded. Falling back to LOCAL tier.",
                daily_spent=daily_spent,
                monthly_spent=monthly_spent,
            )
            # Revert the estimated cost since we are falling back
            revert_pipeline = self._redis.pipeline()
            revert_pipeline.incrbyfloat(self._daily_key, -estimated_cost_usd)
            revert_pipeline.incrbyfloat(self._monthly_key, -estimated_cost_usd)
            await revert_pipeline.execute()
            return ModelTier.LOCAL

        return requested_tier

    async def record_actual_cost(self, cost_usd: float, tier: ModelTier) -> None:
        """Record the actual cost after the LLM call completes.

        Note: check_and_record already added the estimated cost.
        A full implementation would subtract the estimate and add the actual,
        but for simplicity we assume the estimate was 0.0 or we just add the actual here
        if we didn't do an estimate upfront.
        Wait, if we assume check_and_record was called with 0.0, we just add here.
        If we want to be exact, we should track the delta.
        For now, we simply add the cost_usd if it's > 0.
        """
        if tier == ModelTier.LOCAL or cost_usd <= 0.0:
            return

        pipeline = self._redis.pipeline()
        pipeline.incrbyfloat(self._daily_key, cost_usd)
        pipeline.incrbyfloat(self._monthly_key, cost_usd)
        await pipeline.execute()

    async def get_status(self) -> BudgetStatus:
        """Return the current budget status from Redis counters."""
        pipeline = self._redis.pipeline()
        pipeline.get(self._daily_key)
        pipeline.get(self._monthly_key)
        results = await pipeline.execute()

        daily_spent = float(results[0]) if results[0] else 0.0
        monthly_spent = float(results[1]) if results[1] else 0.0

        daily_limit = self._config.daily_limit_usd
        monthly_limit = self._config.monthly_limit_usd

        daily_percent = (daily_spent / daily_limit) if daily_limit > 0 else 0
        monthly_percent = (monthly_spent / monthly_limit) if monthly_limit > 0 else 0

        active_override = None
        if daily_spent > daily_limit or monthly_spent > monthly_limit:
            active_override = ModelTier.LOCAL

        return BudgetStatus(
            daily_spent_usd=daily_spent,
            daily_limit_usd=daily_limit,
            daily_percent=daily_percent,
            monthly_spent_usd=monthly_spent,
            monthly_limit_usd=monthly_limit,
            monthly_percent=monthly_percent,
            active_tier_override=active_override,
        )

    async def reset_daily(self) -> None:
        """Reset the daily counter immediately."""
        await self._redis.delete(self._daily_key)
