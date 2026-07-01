import json

import structlog

from ...llm._models import Message, ModelTier
from ...llm.router import LLMRouter

logger = structlog.get_logger(__name__)


class FactExtractor:
    """Internal module to extract facts using the local LLM."""

    async def extract_facts(self, session_summary: str, llm_router: LLMRouter) -> list[str]:
        prompt = (
            "Extract atomic facts from this conversation summary. "
            "Return a JSON array of strings. Each string is one atomic fact. "
            "Only return the JSON array, nothing else."
        )
        messages = [
            Message(role="system", content=prompt),
            Message(role="user", content=session_summary),
        ]

        try:
            response = await llm_router.complete(messages=messages, tier=ModelTier.LOCAL)
            content = response.content.strip()

            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()

            facts = json.loads(content)
            if isinstance(facts, list):
                facts = [str(f) for f in facts]
                return facts[:20]
            return []
        except Exception as e:
            logger.warning("Fact extraction failed or JSON parsing failed", error=str(e))
            return []
