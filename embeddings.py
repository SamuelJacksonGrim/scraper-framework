# embeddings.py
"""
Pluggable text embedder.

Two backends: `local` (sentence-transformers, runs on-device) and `voyage`
(Voyage AI cloud API). All consumers of the scoring pipeline must use the
same backend - vectors from different backends live in different spaces and
cosine similarity across them is meaningless.
"""
from typing import Protocol, runtime_checkable

import numpy as np


@runtime_checkable
class Embedder(Protocol):
    def embed(self, text: str) -> np.ndarray: ...

    @property
    def dim(self) -> int: ...


class LocalSTEmbedder:
    """sentence-transformers on-device embedder. Default: all-MiniLM-L6-v2."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(model_name)

    def embed(self, text: str) -> np.ndarray:
        return self._model.encode(text, convert_to_numpy=True)

    @property
    def dim(self) -> int:
        return self._model.get_sentence_embedding_dimension()


class VoyageEmbedder:
    """Voyage AI cloud embedder. Requires VOYAGE_API_KEY env var."""

    _MODEL_DIMS = {
        "voyage-3": 1024,
        "voyage-3-lite": 512,
        "voyage-large-2": 1536,
    }

    def __init__(self, model: str = "voyage-3"):
        import voyageai
        self._client = voyageai.Client()
        self._model = model
        self._dim = self._MODEL_DIMS.get(model, 1024)

    def embed(self, text: str) -> np.ndarray:
        result = self._client.embed([text], model=self._model)
        return np.array(result.embeddings[0], dtype=np.float32)

    @property
    def dim(self) -> int:
        return self._dim


_cached_embedder = None


def get_embedder() -> Embedder:
    """Factory that reads config.EMBEDDING_BACKEND. Caches the instance."""
    global _cached_embedder
    if _cached_embedder is None:
        from config import EMBEDDING_BACKEND, EMBEDDING_MODEL
        if EMBEDDING_BACKEND == "voyage":
            _cached_embedder = VoyageEmbedder(EMBEDDING_MODEL)
        else:
            _cached_embedder = LocalSTEmbedder(EMBEDDING_MODEL)
    return _cached_embedder


def _reset_cache() -> None:
    """Test helper - clears the cached instance."""
    global _cached_embedder
    _cached_embedder = None
