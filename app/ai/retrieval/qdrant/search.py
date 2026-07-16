"""
Vector search helper for the AI Qdrant retrieval layer.

Thin wrapper around QdrantService + CodeChunkRepository to
return enriched search results with file paths and line info.
"""
import logging
from typing import Any

from app.services.qdrant_service import QdrantService
from app.repositories.code_chunk_repository import CodeChunkRepository
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

_qdrant_service: QdrantService | None = None


def get_qdrant_service() -> QdrantService:
    """Return a singleton QdrantService (lazy init)."""
    global _qdrant_service
    if _qdrant_service is None:
        _qdrant_service = QdrantService()
    return _qdrant_service


def semantic_search(
    vector: list[float],
    limit: int = 5,
    repo_id: int | None = None,
) -> list[dict[str, Any]]:
    """
    Perform a vector similarity search in Qdrant and enrich
    results with chunk text and file paths from PostgreSQL.

    Returns a list of dicts with keys:
        id, score, text, path, start_line, end_line
    """
    service = get_qdrant_service()
    collection_name = f"repo_{repo_id}" if repo_id is not None else "test_code_chunks"
    
    try:
        raw_points = service.search(vector, limit=limit, collection_name=collection_name)
    except Exception as exc:
        logger.warning("Qdrant search failed for collection '%s': %s", collection_name, exc)
        return []

    raw_points = sorted(raw_points, key=lambda p: p.score, reverse=True)

    db = SessionLocal()
    enriched: list[dict[str, Any]] = []
    try:
        for point in raw_points:
            chunk_text = CodeChunkRepository.get_by_id(db, point.id)
            if chunk_text is None:
                continue
            row = CodeChunkRepository.get_chunk_with_file(db, point.id)
            if row is None:
                continue
            # get_chunk_with_file returns a SQLAlchemy Row: (CodeChunk, path)
            file_path = row.path if hasattr(row, "path") else (row[1] if len(row) > 1 else "unknown")
            enriched.append(
                {
                    "id": point.id,
                    "score": point.score,
                    "text": chunk_text,
                    "path": file_path,
                    "start_line": point.payload.get("start_line") if point.payload else None,
                    "end_line": point.payload.get("end_line") if point.payload else None,
                }
            )
    finally:
        db.close()

    return enriched
