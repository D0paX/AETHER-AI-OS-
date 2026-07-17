from typing import Any

import structlog
from qdrant_client import AsyncQdrantClient, models

from ...core.exceptions import InfrastructureError
from ..models import MemoryFilter

logger = structlog.get_logger(__name__)

# Default production collection name. The active collection is per-instance
# (self._collection_name), so tests can be redirected to a disposable test
# collection without touching production (M2.1.7 Part 2).
COLLECTION_NAME = "episodic_memory"


class QdrantMemoryStore:
    """Internal Qdrant vector storage for semantic memory search."""

    def __init__(
        self,
        host: str,
        port: int,
        grpc_port: int,
        prefer_grpc: bool = True,
        # 10, not 10.0: the annotation and AsyncQdrantClient both specify int.
        # Same 10-second timeout; the float literal was simply a typo.
        timeout: int | None = 10,
        collection_name: str = COLLECTION_NAME,
    ):
        self._collection_name = collection_name
        try:
            self._client = AsyncQdrantClient(
                host=host, port=port, grpc_port=grpc_port, prefer_grpc=prefer_grpc, timeout=timeout
            )
        except Exception as e:
            raise InfrastructureError(f"Failed to connect to Qdrant: {e}") from e

    async def initialize_collection(self) -> None:
        """Create the collection if it does not exist with 1024 dims and int8 quantization."""
        try:
            exists = await self._client.collection_exists(self._collection_name)
            if not exists:
                await self._client.create_collection(
                    collection_name=self._collection_name,
                    vectors_config=models.VectorParams(
                        size=1024,
                        distance=models.Distance.COSINE,
                    ),
                    quantization_config=models.ScalarQuantization(
                        scalar=models.ScalarQuantizationConfig(
                            type=models.ScalarType.INT8, quantile=0.99, always_ram=True
                        )
                    ),
                )
                logger.info("Created new Qdrant collection", collection=self._collection_name)
        except Exception as e:
            raise InfrastructureError(f"Failed to initialize Qdrant collection: {e}") from e

    def _build_filter(self, filters: MemoryFilter | None) -> models.Filter | None:
        if not filters:
            return None

        must: list[models.Condition] = []
        if filters.memory_types:
            must.append(
                models.FieldCondition(
                    key="memory_type",
                    match=models.MatchAny(any=[mt.value for mt in filters.memory_types]),
                )
            )
        if filters.source:
            must.append(
                models.FieldCondition(
                    key="source", match=models.MatchValue(value=filters.source.value)
                )
            )
        if filters.min_importance > 0:
            must.append(
                models.FieldCondition(
                    key="importance", range=models.Range(gte=filters.min_importance)
                )
            )
        if filters.min_confidence > 0:
            must.append(
                models.FieldCondition(
                    key="confidence", range=models.Range(gte=filters.min_confidence)
                )
            )

        if not must:
            return None

        return models.Filter(must=must)

    async def upsert(self, memory_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        try:
            await self._client.upsert(
                collection_name=self._collection_name,
                points=[models.PointStruct(id=memory_id, vector=vector, payload=payload)],
            )
        except Exception as e:
            raise InfrastructureError(f"Failed to upsert to Qdrant: {e}") from e

    async def search(
        self,
        query_vector: list[float],
        limit: int,
        score_threshold: float,
        filters: MemoryFilter | None,
    ) -> list[tuple[str, float]]:
        try:
            response = await self._client.query_points(
                collection_name=self._collection_name,
                query=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=self._build_filter(filters),
            )
            return [(str(point.id), point.score) for point in response.points]
        except Exception as e:
            raise InfrastructureError(f"Failed to search Qdrant: {e}") from e

    async def delete(self, memory_id: str) -> None:
        try:
            await self._client.delete(
                collection_name=self._collection_name,
                points_selector=models.PointIdsList(points=[memory_id]),
            )
        except Exception as e:
            raise InfrastructureError(f"Failed to delete from Qdrant: {e}") from e
