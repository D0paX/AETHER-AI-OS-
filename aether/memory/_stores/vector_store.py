import structlog
from qdrant_client import AsyncQdrantClient, models

from ...core.exceptions import InfrastructureError
from ..models import MemoryFilter

logger = structlog.get_logger(__name__)

COLLECTION_NAME = "episodic_memory"


class QdrantMemoryStore:
    """Internal Qdrant vector storage for semantic memory search."""

    def __init__(self, host: str, port: int, grpc_port: int, prefer_grpc: bool = True):
        try:
            self._client = AsyncQdrantClient(
                host=host, port=port, grpc_port=grpc_port, prefer_grpc=prefer_grpc, timeout=10.0
            )
        except Exception as e:
            raise InfrastructureError(f"Failed to connect to Qdrant: {e}")

    async def initialize_collection(self) -> None:
        """Create the collection if it does not exist with 1024 dims and int8 quantization."""
        try:
            exists = await self._client.collection_exists(COLLECTION_NAME)
            if not exists:
                await self._client.create_collection(
                    collection_name=COLLECTION_NAME,
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
                logger.info("Created new Qdrant collection", collection=COLLECTION_NAME)
        except Exception as e:
            raise InfrastructureError(f"Failed to initialize Qdrant collection: {e}")

    def _build_filter(self, filters: MemoryFilter | None) -> models.Filter | None:
        if not filters:
            return None

        must = []
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

    async def upsert(self, memory_id: str, vector: list[float], payload: dict) -> None:
        try:
            await self._client.upsert(
                collection_name=COLLECTION_NAME,
                points=[models.PointStruct(id=memory_id, vector=vector, payload=payload)],
            )
        except Exception as e:
            raise InfrastructureError(f"Failed to upsert to Qdrant: {e}")

    async def search(
        self,
        query_vector: list[float],
        limit: int,
        score_threshold: float,
        filters: MemoryFilter | None,
    ) -> list[tuple[str, float]]:
        try:
            results = await self._client.search(
                collection_name=COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=self._build_filter(filters),
            )
            return [(str(point.id), point.score) for point in results]
        except Exception as e:
            raise InfrastructureError(f"Failed to search Qdrant: {e}")

    async def delete(self, memory_id: str) -> None:
        try:
            await self._client.delete(
                collection_name=COLLECTION_NAME,
                points_selector=models.PointIdsList(points=[memory_id]),
            )
        except Exception as e:
            raise InfrastructureError(f"Failed to delete from Qdrant: {e}")
