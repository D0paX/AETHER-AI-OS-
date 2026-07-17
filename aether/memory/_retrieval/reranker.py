from datetime import UTC, datetime

from ..models import ContextPackage, MemoryRecord


class MemoryReranker:
    """Internal module for scoring and assembling memory context."""

    RERANK_WEIGHTS = {"similarity": 0.6, "recency": 0.3, "importance": 0.1}

    def _calculate_recency_weight(self, created_at: datetime) -> float:
        now = datetime.now(UTC)
        age_days = (now - created_at).days
        if age_days <= 0:
            return 1.0
        elif age_days >= 30:
            return 0.1
        else:
            return 1.0 - (age_days * 0.03)

    def rerank(
        self, candidates: list[tuple[MemoryRecord, float]], token_budget: int
    ) -> list[MemoryRecord]:
        scored_candidates = []
        for record, similarity in candidates:
            # Re-scale importance (assuming it is 0 to 1, default 0.5)
            # Or just use the value directly as per the formula
            recency_weight = self._calculate_recency_weight(record.created_at)

            score = (
                (self.RERANK_WEIGHTS["similarity"] * similarity)
                + (self.RERANK_WEIGHTS["recency"] * recency_weight)
                + (self.RERANK_WEIGHTS["importance"] * record.importance)
            )
            scored_candidates.append((record, score))

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x[1], reverse=True)

        # Assemble list respecting token_budget
        selected_records = []
        current_tokens = 0

        for record, _score in scored_candidates:
            # Token estimate: len(record.content.split()) * 1.3
            token_estimate = int(len(record.content.split()) * 1.3)
            if current_tokens + token_estimate <= token_budget:
                selected_records.append(record)
                current_tokens += token_estimate

        return selected_records

    def assemble_context_package(
        self, ranked: list[MemoryRecord], query: str, token_budget: int, duration_ms: int
    ) -> ContextPackage:
        if not ranked:
            formatted_context = "Relevant context from memory:\n\nNo relevant memory found."
            total_tokens = 0
        else:
            blocks = []
            total_tokens = 0
            for r in ranked:
                blocks.append(f"[{r.memory_type.value}] {r.content}")
                total_tokens += int(len(r.content.split()) * 1.3)

            formatted_context = "Relevant context from memory:\n\n" + "\n---\n".join(blocks)

        return ContextPackage(
            memories=ranked,
            total_found=len(ranked),
            token_estimate=total_tokens,
            formatted_context=formatted_context,
            retrieval_query=query,
            retrieval_duration_ms=duration_ms,
        )
