"""
Embedding helper for the AI Qdrant retrieval layer.

Thin wrapper around the existing EmbeddingService to keep
the retrieval layer decoupled from the raw model API.
"""
from app.services.embedding_service import EmbeddingService

_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Return a singleton EmbeddingService (lazy init)."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


def embed_text(text: str) -> list[float]:
    """
    Convert a text string into a normalized embedding vector.
    Delegates to the shared EmbeddingService.
    """
    return get_embedding_service().embedd(text)
