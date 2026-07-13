"""
Document ranker for the Context Builder phase.

Ranks RetrievedDocuments by a combined score that considers
Qdrant vector similarity, source priority, and document type.
"""
from __future__ import annotations

from app.ai.retrieval.schemas import RetrievedDocument
from app.ai.router.enums import DataSource, Intent

# Source priority weights (higher = more important for context)
_SOURCE_WEIGHTS: dict[DataSource, float] = {
    DataSource.NEO4J: 1.15,
    DataSource.QDRANT: 1.10,
    DataSource.POSTGRES: 1.00,
}

# Document-type priority weights
_TYPE_WEIGHTS: dict[str, float] = {
    "pr_reviewers": 1.20,
    "pr_reviews": 1.15,
    "file_ownership": 1.15,
    "file_activity": 1.10,
    "code_chunk": 1.10,
    "contributors": 1.05,
    "repository_info": 1.05,
    "services": 1.00,
    "api_endpoints": 0.95,
    "pull_request": 0.90,
    "commit": 0.80,
    "file_list": 0.70,
    "engineers": 0.70,
}


class DocumentRanker:
    """
    Scores and sorts RetrievedDocuments by a weighted composite score.
    Can optionally be biased toward certain sources based on intent.
    """

    def rank(
        self,
        documents: list[RetrievedDocument],
        intent: Intent | None = None,
    ) -> list[RetrievedDocument]:
        if not documents:
            return documents

        scored = [
            (doc, self._compute_score(doc, intent))
            for doc in documents
        ]
        scored.sort(key=lambda pair: pair[1], reverse=True)
        return [doc for doc, _ in scored]

    @staticmethod
    def _compute_score(
        doc: RetrievedDocument,
        intent: Intent | None,
    ) -> float:
        base_score = doc.score if doc.score is not None else 0.5

        source_weight = _SOURCE_WEIGHTS.get(doc.source, 1.0)
        type_weight = _TYPE_WEIGHTS.get(doc.document_type, 1.0)

        # Intent-based boost
        intent_boost = 1.0
        if intent == Intent.REVIEW_HISTORY:
            if doc.document_type in {"pr_reviewers", "pr_reviews"}:
                intent_boost = 1.30
        elif intent == Intent.OWNERSHIP:
            if doc.document_type in {"file_ownership", "file_activity", "contributors"}:
                intent_boost = 1.25
        elif intent in {Intent.DEPENDENCY, Intent.ARCHITECTURE}:
            if doc.document_type in {"imports", "reverse_imports", "database_usage", "services"}:
                intent_boost = 1.20
        elif intent == Intent.REPOSITORY_SUMMARY:
            intent_boost = 1.05  # Treat all sources equally for summary

        return base_score * source_weight * type_weight * intent_boost
