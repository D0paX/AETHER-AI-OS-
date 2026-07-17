import time
from typing import TYPE_CHECKING

import structlog

from ...core.config import get_config
from ...llm._models import Message, ModelTier
from ...llm.router import LLMRouter
from ..models import ConsolidationReport, MemorySource, MemoryType
from .extractor import FactExtractor

if TYPE_CHECKING:
    from ..api import MemoryAPI

logger = structlog.get_logger(__name__)


class ConsolidationPipeline:
    """Orchestrates memory consolidation at the end of a session."""

    def __init__(self) -> None:
        self._extractor = FactExtractor()

    async def run(
        self, session_id: str, llm_router: LLMRouter, memory_api: "MemoryAPI"
    ) -> ConsolidationReport:
        start_time = time.perf_counter()

        messages = await memory_api.get_conversation_messages(session_id)

        min_messages = get_config().memory.consolidation_min_messages
        if len(messages) < min_messages:
            return ConsolidationReport(
                session_id=session_id,
                memories_created=0,
                facts_extracted=0,
                duration_ms=int((time.perf_counter() - start_time) * 1000),
                llm_cost_usd=0.0,
                skipped=True,
                skip_reason="insufficient_messages",
            )

        transcript = "\n".join([f"{m.role}: {m.content}" for m in messages])
        summary_prompt = "Summarize the following conversation concisely."
        msgs = [
            Message(role="system", content=summary_prompt),
            Message(role="user", content=transcript),
        ]

        try:
            summary_response = await llm_router.complete(messages=msgs, tier=ModelTier.LOCAL)
            session_summary = summary_response.content
        except Exception as e:
            logger.error("Failed to summarize session", error=str(e))
            return ConsolidationReport(
                session_id=session_id,
                memories_created=0,
                facts_extracted=0,
                duration_ms=int((time.perf_counter() - start_time) * 1000),
                llm_cost_usd=0.0,
                skipped=True,
                skip_reason="summarization_failed",
            )

        facts = await self._extractor.extract_facts(session_summary, llm_router)

        memories_created = 0
        for fact in facts:
            await memory_api.remember(
                content=fact,
                memory_type=MemoryType.FACT,
                importance=0.6,
                session_id=session_id,
                source=MemorySource.CONVERSATION,
            )
            memories_created += 1

        await memory_api.remember(
            content=session_summary,
            memory_type=MemoryType.EPISODE,
            importance=0.5,
            session_id=session_id,
            source=MemorySource.CONVERSATION,
        )
        memories_created += 1

        # Event emission via the LLM router's event bus since it's connected
        if hasattr(llm_router, "_event_bus") and llm_router._event_bus:
            await memory_api._event_bus.emit(
                "memory.consolidation.completed", {"session_id": session_id, "facts": len(facts)}
            )

        duration = int((time.perf_counter() - start_time) * 1000)

        return ConsolidationReport(
            session_id=session_id,
            memories_created=memories_created,
            facts_extracted=len(facts),
            duration_ms=duration,
            llm_cost_usd=0.0,
            skipped=False,
            skip_reason=None,
        )
