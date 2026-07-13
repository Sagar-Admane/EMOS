"""
Knowledge Fusion / Deduplication layer — Phase 4.3.

Merges semantically similar or duplicate documents from
multiple sources before they reach the LLM prompt.
This is the "Knowledge Fusion Layer" recommended in the spec.
"""
from __future__ import annotations

import logging
from collections import defaultdict

from app.ai.retrieval.schemas import RetrievedDocument

logger = logging.getLogger(__name__)

# Jaccard threshold above which two documents are considered duplicates.
_JACCARD_THRESHOLD = 0.75
# Maximum content length for a single merged document (chars).
_MERGE_CONTENT_LIMIT = 2000


class DocumentMerger:
    """
    Resolves conflicts and merges duplicate information from
    PostgreSQL, Neo4j, and Qdrant before prompt preparation.

    Responsibilities:
    - Detect near-duplicate documents (same topic, different source)
    - Merge complementary documents of the same type
    - Enrich entities (e.g., link review info from both SQL and graph)
    - Return a clean, unified list ready for ranking
    """

    def fuse(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """
        Main entry point. Performs knowledge fusion on the document list.
        """
        if not documents:
            return documents

        # Step 1: Group by document_type to find complementary docs
        grouped = self._group_by_type(documents)

        # Step 2: Within each group, merge near-duplicates
        fused: list[RetrievedDocument] = []
        for doc_type, group in grouped.items():
            fused.extend(self._merge_group(doc_type, group))

        # Step 3: Cross-source deduplication (whole-list pass)
        fused = self._cross_source_dedup(fused)

        logger.debug(
            "Knowledge fusion: %d → %d documents",
            len(documents),
            len(fused),
        )
        return fused

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _group_by_type(
        documents: list[RetrievedDocument],
    ) -> dict[str, list[RetrievedDocument]]:
        groups: dict[str, list[RetrievedDocument]] = defaultdict(list)
        for doc in documents:
            groups[doc.document_type].append(doc)
        return dict(groups)

    def _merge_group(
        self,
        doc_type: str,
        group: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """
        For document types where multiple sources provide
        overlapping information (e.g., pr_reviewers from both
        Neo4j and SQL), merge into a single enriched document.
        """
        if len(group) == 1:
            return group

        # For pr_reviews / pr_reviewers — merge complementary content
        if doc_type in {"pr_reviews", "pr_reviewers"}:
            return [self._merge_review_docs(group)]

        # For contributors / engineers — merge into one overview
        if doc_type in {"contributors", "engineers"}:
            return [self._merge_contributor_docs(group)]

        # Default: remove near-duplicates, keep best-scored
        return self._deduplicate_group(group)

    @staticmethod
    def _merge_review_docs(
        group: list[RetrievedDocument],
    ) -> RetrievedDocument:
        """Merge multiple review documents into one enriched document."""
        best = max(group, key=lambda d: d.score or 0.0)
        extra_lines: list[str] = []
        for doc in group:
            if doc is best:
                continue
            # Append any unique lines from secondary sources
            for line in doc.content.splitlines():
                if line and line not in best.content:
                    extra_lines.append(line)

        merged_content = best.content
        if extra_lines:
            merged_content += "\n\nAdditional info:\n" + "\n".join(extra_lines)
        merged_content = merged_content[:_MERGE_CONTENT_LIMIT]

        return best.model_copy(update={"content": merged_content})

    @staticmethod
    def _merge_contributor_docs(
        group: list[RetrievedDocument],
    ) -> RetrievedDocument:
        """Merge contributor/engineer listings into one document."""
        best = max(group, key=lambda d: d.score or 0.0)
        all_lines: list[str] = []
        seen: set[str] = set()
        for doc in group:
            for line in doc.content.splitlines():
                stripped = line.strip()
                if stripped and stripped not in seen:
                    all_lines.append(stripped)
                    seen.add(stripped)
        merged_content = "\n".join(all_lines)[:_MERGE_CONTENT_LIMIT]
        return best.model_copy(update={"content": merged_content})

    def _deduplicate_group(
        self,
        group: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """Remove near-duplicates from a group, keeping highest-scored."""
        sorted_group = sorted(
            group,
            key=lambda d: d.score or 0.0,
            reverse=True,
        )
        unique: list[RetrievedDocument] = []
        for doc in sorted_group:
            if not self._is_near_duplicate(doc, unique):
                unique.append(doc)
        return unique

    @staticmethod
    def _is_near_duplicate(
        candidate: RetrievedDocument,
        accepted: list[RetrievedDocument],
    ) -> bool:
        c_tokens = set(candidate.content.lower().split())
        if not c_tokens:
            return False
        for existing in accepted:
            e_tokens = set(existing.content.lower().split())
            if not e_tokens:
                continue
            intersection = c_tokens & e_tokens
            union = c_tokens | e_tokens
            if union and (len(intersection) / len(union)) >= _JACCARD_THRESHOLD:
                return True
        return False

    def _cross_source_dedup(
        self,
        documents: list[RetrievedDocument],
    ) -> list[RetrievedDocument]:
        """Final pass to remove any remaining near-duplicates across types."""
        unique: list[RetrievedDocument] = []
        for doc in documents:
            if not self._is_near_duplicate(doc, unique):
                unique.append(doc)
        return unique
