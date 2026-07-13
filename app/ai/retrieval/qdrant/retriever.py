"""
Qdrant retriever for the AI Intelligence Layer.

Implements BaseRetriever. Embeds the question, performs
vector similarity search, enriches results with PostgreSQL
chunk data, and returns normalized RetrievedDocuments.
"""
import asyncio
import logging
import time
from functools import partial

from app.ai.retrieval.base import BaseRetriever
from app.ai.retrieval.schemas import (
    RetrievalError,
    RetrievalResult,
    RetrievalStatistics,
    RetrievedDocument,
    RetrievalMetadata,
)
from app.ai.retrieval.qdrant.embeddings import embed_text
from app.ai.retrieval.qdrant.search import semantic_search
from app.ai.router.enums import DataSource
from app.ai.router.schemas import RouteDecision

logger = logging.getLogger(__name__)


class QdrantRetriever(BaseRetriever):
    """
    Semantic search retriever. Embeds the user's question
    and retrieves the most relevant code chunks from Qdrant.
    """

    @property
    def source(self) -> DataSource:
        return DataSource.QDRANT

    async def retrieve(self, route: RouteDecision) -> RetrievalResult:
        start = time.monotonic()
        documents: list[RetrievedDocument] = []
        errors: list[RetrievalError] = []

        try:
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                None,
                partial(self._fetch_sync, route),
            )
            documents.extend(docs)
        except Exception as exc:
            logger.exception("QdrantRetriever error: %s", exc)
            errors.append(
                RetrievalError(
                    source=self.source,
                    message=str(exc),
                    retryable=True,
                )
            )

        elapsed_ms = (time.monotonic() - start) * 1000
        return RetrievalResult(
            documents=documents,
            statistics=RetrievalStatistics(
                total_documents=len(documents),
                sources_used=[self.source],
                retrieval_time_ms=elapsed_ms,
            ),
            errors=errors,
        )

    def _fetch_sync(self, route: RouteDecision) -> list[RetrievedDocument]:
        vector = embed_text(route.question)
        results = semantic_search(vector, limit=6)
        docs: list[RetrievedDocument] = []

        for item in results:
            path = item.get("path", "unknown")
            start_line = item.get("start_line", "?")
            end_line = item.get("end_line", "?")
            text = item.get("text", "")
            score = float(item.get("score", 0.0))

            content = (
                f"File: {path}\n"
                f"Lines: {start_line}–{end_line}\n\n"
                f"{text}"
            )
            docs.append(
                RetrievedDocument(
                    source=self.source,
                    document_type="code_chunk",
                    title=f"{path} (L{start_line}–{end_line})",
                    content=content,
                    metadata=RetrievalMetadata(
                        data={
                            "chunk_id": item.get("id"),
                            "path": path,
                            "start_line": start_line,
                            "end_line": end_line,
                        }
                    ),
                    score=score,
                )
            )
        return docs
