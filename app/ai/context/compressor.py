"""
Content compressor for the Context Builder phase.

Truncates document content to stay within the token budget,
preserving the most important information at the top of each document.
"""
from __future__ import annotations

import logging

from app.ai.retrieval.schemas import RetrievedDocument

logger = logging.getLogger(__name__)

# Default maximum characters per document (rough ~512 tokens)
_DEFAULT_MAX_CHARS_PER_DOC = 2048

# Default maximum total characters for the whole context
_DEFAULT_MAX_TOTAL_CHARS = 16384


class ContextCompressor:
    """
    Truncates RetrievedDocument content to stay within a
    token budget. Uses a character-based approximation
    (4 chars ≈ 1 token) since tiktoken is not installed.
    """

    def __init__(
        self,
        max_chars_per_doc: int = _DEFAULT_MAX_CHARS_PER_DOC,
        max_total_chars: int = _DEFAULT_MAX_TOTAL_CHARS,
    ) -> None:
        self._max_per_doc = max_chars_per_doc
        self._max_total = max_total_chars

    def compress(
        self,
        documents: list[RetrievedDocument],
    ) -> tuple[list[RetrievedDocument], bool]:
        """
        Compress the document list to fit within the total char budget.

        Returns:
            (compressed_documents, compression_applied)
        """
        compressed: list[RetrievedDocument] = []
        total_chars = 0
        compression_applied = False

        for doc in documents:
            content = doc.content

            # Per-document truncation
            if len(content) > self._max_per_doc:
                content = content[: self._max_per_doc] + "\n... [truncated]"
                compression_applied = True

            # Total budget check
            remaining = self._max_total - total_chars
            if remaining <= 0:
                logger.debug(
                    "Total context budget exhausted — dropping remaining docs."
                )
                break

            if len(content) > remaining:
                content = content[:remaining] + "\n... [truncated]"
                compression_applied = True

            total_chars += len(content)
            compressed.append(doc.model_copy(update={"content": content}))

        return compressed, compression_applied

    @staticmethod
    def estimate_tokens(text: str) -> int:
        """Rough token estimate: 4 chars ≈ 1 token."""
        return max(1, len(text) // 4)
