"""
ResultMerger — merges multiple RetrievalResults from different
sources into a single deduplicated, score-sorted RetrievalResult.
"""
import logging
from app.ai.retrieval.schemas import (
    RetrievalError,
    RetrievalResult,
    RetrievalStatistics,
    RetrievedDocument,
)

logger = logging.getLogger(__name__)

# Similarity threshold for deduplication (character overlap ratio).
_DEDUP_SIMILARITY_THRESHOLD = 0.85


class ResultMerger:
    """
    Merges multiple per-source RetrievalResults into one
    deduplicated result ordered by score descending.
    """

    def merge(self, results: list[RetrievalResult]) -> RetrievalResult:
        all_documents: list[RetrievedDocument] = []
        all_errors: list[RetrievalError] = []
        sources_used = set()
        total_time_ms = 0.0

        for result in results:
            all_documents.extend(result.documents)
            all_errors.extend(result.errors)
            sources_used.update(result.statistics.sources_used)
            total_time_ms += result.statistics.retrieval_time_ms

        deduplicated = self._deduplicate(all_documents)
        ranked = sorted(
            deduplicated,
            key=lambda d: d.score if d.score is not None else 0.0,
            reverse=True,
        )

        return RetrievalResult(
            documents=ranked,
            statistics=RetrievalStatistics(
                total_documents=len(ranked),
                sources_used=list(sources_used),
                retrieval_time_ms=total_time_ms,
            ),
            errors=all_errors,
        )

    def _deduplicate(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """
        Remove near-duplicate documents based on content similarity.
        Keeps the document with the higher score when a near-duplicate
        is found.
        """
        unique: list[RetrievedDocument] = []
        seen_titles: set[str] = set()

        for doc in documents:
            # Exact title deduplication
            if doc.title in seen_titles:
                continue

            # Content similarity check against already accepted docs
            if self._is_duplicate(doc, unique):
                continue

            unique.append(doc)
            seen_titles.add(doc.title)

        return unique

    @staticmethod
    def _is_duplicate(
        candidate: RetrievedDocument,
        accepted: list[RetrievedDocument],
    ) -> bool:
        """Return True if candidate is too similar to any accepted doc."""
        c_tokens = set(candidate.content.lower().split())
        if not c_tokens:
            return False

        for existing in accepted:
            e_tokens = set(existing.content.lower().split())
            if not e_tokens:
                continue
            intersection = c_tokens & e_tokens
            union = c_tokens | e_tokens
            jaccard = len(intersection) / len(union) if union else 0.0
            if jaccard >= _DEDUP_SIMILARITY_THRESHOLD:
                return True
        return False
