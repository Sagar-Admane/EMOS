"""
ContextBuilder — Phase 4.3.

Transforms a RetrievalResult into an LLM-ready ContextPackage
by running: Knowledge Fusion → Ranking → Compression → Citation building.
"""
from __future__ import annotations

import logging

from app.ai.retrieval.schemas import RetrievalResult, RetrievedDocument
from app.ai.context.merger import DocumentMerger
from app.ai.context.ranker import DocumentRanker
from app.ai.context.compressor import ContextCompressor
from app.ai.context.schemas import Citation, ContextMetadata, ContextPackage
from app.ai.router.enums import Intent

logger = logging.getLogger(__name__)


class ContextBuilder:
    """
    Orchestrates the 4-step context assembly pipeline:
    1. Knowledge Fusion (merge + dedup across sources)
    2. Ranking (score documents by relevance)
    3. Compression (truncate to fit token budget)
    4. Citation building (produce numbered references)

    Outputs a ContextPackage ready for consumption by a Skill.
    """

    def __init__(
        self,
        merger: DocumentMerger | None = None,
        ranker: DocumentRanker | None = None,
        compressor: ContextCompressor | None = None,
    ) -> None:
        self._merger = merger or DocumentMerger()
        self._ranker = ranker or DocumentRanker()
        self._compressor = compressor or ContextCompressor()

    def build(
        self,
        retrieval_result: RetrievalResult,
        intent: Intent | None = None,
        question: str = "",
    ) -> ContextPackage:
        """
        Build a ContextPackage from a RetrievalResult.
        """
        raw_docs = retrieval_result.documents
        total_before = len(raw_docs)

        if not raw_docs:
            logger.warning("ContextBuilder received 0 documents — returning empty package.")
            return ContextPackage(
                summary="No relevant information was found for this question.",
                metadata=ContextMetadata(
                    total_documents_before_compression=0,
                    total_documents_after_compression=0,
                ),
            )

        # Step 1: Knowledge Fusion
        fused = self._merger.fuse(raw_docs)

        # Step 2: Rank
        ranked = self._ranker.rank(fused, intent=intent)

        # Step 3: Compress
        compressed, compression_applied = self._compressor.compress(ranked)

        # Step 4: Build citations + final document dicts
        citations: list[Citation] = []
        doc_dicts: list[dict] = []

        for i, doc in enumerate(compressed, start=1):
            citations.append(
                Citation(
                    index=i,
                    title=doc.title,
                    source=doc.source,
                    document_type=doc.document_type,
                    score=doc.score,
                )
            )
            doc_dicts.append(
                {
                    "index": i,
                    "title": doc.title,
                    "source": doc.source.value,
                    "document_type": doc.document_type,
                    "content": doc.content,
                    "score": doc.score,
                }
            )

        # Build summary
        summary = self._build_summary(
            question=question,
            documents=compressed,
            sources_used=retrieval_result.statistics.sources_used,
        )

        total_text = " ".join(d["content"] for d in doc_dicts)
        estimated_tokens = self._compressor.estimate_tokens(total_text)

        metadata = ContextMetadata(
            total_documents_before_compression=total_before,
            total_documents_after_compression=len(compressed),
            estimated_tokens=estimated_tokens,
            sources_used=list(retrieval_result.statistics.sources_used),
            compression_applied=compression_applied,
            fusion_applied=len(fused) < total_before,
        )

        logger.info(
            "Context built: %d → %d docs | ~%d tokens | compression=%s",
            total_before,
            len(compressed),
            estimated_tokens,
            compression_applied,
        )

        return ContextPackage(
            summary=summary,
            documents=doc_dicts,
            citations=citations,
            metadata=metadata,
        )

    @staticmethod
    def _build_summary(
        question: str,
        documents: list[RetrievedDocument],
        sources_used: list,
    ) -> str:
        source_names = ", ".join(sorted({s.value for s in sources_used}))
        doc_types = sorted({d.document_type for d in documents})
        return (
            f"Context for: '{question}'\n"
            f"Sources: {source_names}\n"
            f"Document types: {', '.join(doc_types)}\n"
            f"Total documents: {len(documents)}"
        )
