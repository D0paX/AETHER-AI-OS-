"""Local embedding service using sentence-transformers."""

import asyncio
import threading
from typing import TYPE_CHECKING

from aether.core.config import EMBEDDING_DIMENSION, get_config
from aether.core.exceptions import ConfigurationError
from aether.core.logging import get_logger
from aether.llm._models import Embedding

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

logger = get_logger("aether.llm.embedding")

# Process-wide cache of loaded models, keyed by (model_name, device). Loading a
# SentenceTransformer re-initializes torch/transformers; doing so more than once
# in a single process is the trigger for the native Windows access-violation
# crash tracked as DEBT-011 (root-caused via DEBT-006). Caching the loaded model
# means it initializes EXACTLY ONCE per (model, device) for the life of the
# process — for every EmbeddingService instance, in tests and in production
# alike. The lock makes the first, concurrent construction safe.
_MODEL_CACHE: dict[tuple[str, str], "SentenceTransformer"] = {}
_MODEL_CACHE_LOCK = threading.Lock()


class EmbeddingService:
    """Service for generating vector embeddings locally."""

    def __init__(self) -> None:
        """Initialize the embedding model locally (reusing a cached load)."""
        config = get_config()
        model_name = config.memory.embedding_model
        device = config.memory.embedding_device

        cache_key = (model_name, device)
        with _MODEL_CACHE_LOCK:
            cached = _MODEL_CACHE.get(cache_key)
            if cached is not None:
                logger.info(
                    "Reusing cached embedding model",
                    model_name=model_name,
                    device=device,
                )
                self._model = cached
            else:
                logger.info(
                    "Loading local embedding model",
                    model_name=model_name,
                    device=device,
                )
                try:
                    from sentence_transformers import SentenceTransformer

                    self._model = SentenceTransformer(model_name, device=device)
                except Exception as e:
                    raise ConfigurationError(
                        f"Failed to load sentence-transformers model '{model_name}': {e}"
                    ) from e
                _MODEL_CACHE[cache_key] = self._model

        # Validate dimensions
        dimensions = self._model.get_sentence_embedding_dimension()
        if dimensions != EMBEDDING_DIMENSION:
            raise ConfigurationError(
                f"Embedding model '{model_name}' produces {dimensions} dimensions, "
                f"but Aether OS requires strictly {EMBEDDING_DIMENSION} dimensions."
            )

        self._model_name = model_name

    def _embed_batch_sync(self, texts: list[str]) -> list[Embedding]:
        """Synchronously generate embeddings for a batch of texts."""
        # Using numpy() ensures we get a list of floats rather than torch tensors
        vectors = self._model.encode(texts, convert_to_numpy=True).tolist()

        return [
            Embedding(vector=vector, text=text, model=self._model_name)
            for vector, text in zip(vectors, texts, strict=True)
        ]

    async def embed(self, text: str) -> Embedding:
        """Asynchronously embed a single string using a thread pool.

        Args:
            text: The text to embed.

        Returns:
            The embedding vector.
        """
        results = await self.embed_batch([text])
        return results[0]

    async def embed_batch(self, texts: list[str]) -> list[Embedding]:
        """Asynchronously embed a batch of strings using a thread pool.

        Args:
            texts: List of texts to embed.

        Returns:
            A list of embeddings.
        """
        if not texts:
            return []

        # Offload the CPU/GPU heavy embedding generation to a background thread
        return await asyncio.to_thread(self._embed_batch_sync, texts)
