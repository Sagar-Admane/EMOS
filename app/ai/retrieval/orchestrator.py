"""
RetrievalOrchestrator — Phase 4.2 orchestration layer.

Receives a RouteDecision, fans out to the appropriate
retrievers in parallel, and merges results.
"""
import asyncio
import logging
import time

from app.ai.retrieval.base import BaseRetriever
from app.ai.retrieval.merger import ResultMerger
from app.ai.retrieval.schemas import RetrievalResult
from app.ai.retrieval.postgres.retriever import PostgresRetriever
from app.ai.retrieval.neo4j.retriever import Neo4jRetriever
from app.ai.retrieval.qdrant.retriever import QdrantRetriever
from app.ai.router.schemas import RouteDecision

logger = logging.getLogger(__name__)


class RetrievalOrchestrator:
    """
    Fans the RouteDecision out to all applicable retrievers
    concurrently, then merges and deduplicates the results.

    The orchestrator never knows about SQL, Cypher, or embeddings —
    it only coordinates BaseRetriever implementations.
    """

    def __init__(
        self,
        retrievers: list[BaseRetriever] | None = None,
        merger: ResultMerger | None = None,
    ) -> None:
        self._retrievers: list[BaseRetriever] = retrievers or [
            PostgresRetriever(),
            Neo4jRetriever(),
            QdrantRetriever(),
        ]
        self._merger = merger or ResultMerger()

    async def retrieve(self, route: RouteDecision) -> RetrievalResult:
        """
        Execute retrieval for the given RouteDecision.

        1. Filter retrievers to those that support the route.
        2. Run them concurrently via asyncio.gather.
        3. Merge all results with the ResultMerger.
        """
        start = time.monotonic()

        applicable = [r for r in self._retrievers if r.supports(route)]

        if not applicable:
            logger.warning(
                "No retrievers matched sources %s — returning empty result.",
                route.required_sources,
            )
            from app.ai.retrieval.schemas import RetrievalStatistics
            return RetrievalResult(
                statistics=RetrievalStatistics(
                    retrieval_time_ms=(time.monotonic() - start) * 1000
                )
            )

        logger.info(
            "Dispatching to %d retriever(s): %s",
            len(applicable),
            [type(r).__name__ for r in applicable],
        )

        partial_results: list[RetrievalResult] = await asyncio.gather(
            *[r.retrieve(route) for r in applicable],
            return_exceptions=False,
        )

        merged = self._merger.merge(list(partial_results))

        elapsed_ms = (time.monotonic() - start) * 1000
        logger.info(
            "Retrieval complete: %d documents in %.1f ms",
            merged.statistics.total_documents,
            elapsed_ms,
        )
        return merged
