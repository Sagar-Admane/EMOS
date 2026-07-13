"""
Shared Pydantic schemas for the Context Builder phase.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.ai.router.enums import DataSource


class Citation(BaseModel):
    """Reference to a source document used in the context."""

    index: int
    title: str
    source: DataSource
    document_type: str
    score: float | None = None


class ContextMetadata(BaseModel):
    """Statistics and metadata about the assembled context."""

    total_documents_before_compression: int = 0
    total_documents_after_compression: int = 0
    estimated_tokens: int = 0
    sources_used: list[DataSource] = Field(default_factory=list)
    compression_applied: bool = False
    fusion_applied: bool = False


class ContextPackage(BaseModel):
    """
    The LLM-ready context package produced by the Context Builder.

    Contains:
      - summary:   A short plain-text overview for the LLM system prompt.
      - documents: Ordered, compressed list of relevant text blocks.
      - citations: Numbered source references.
      - metadata:  Stats about the context assembly process.
    """

    summary: str = ""
    documents: list[dict[str, Any]] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    metadata: ContextMetadata = Field(default_factory=ContextMetadata)

    def as_text(self) -> str:
        """
        Render all documents as a single plain-text block
        suitable for LLM context insertion.
        """
        parts: list[str] = []
        for i, doc in enumerate(self.documents, start=1):
            title = doc.get("title", f"Document {i}")
            content = doc.get("content", "")
            source = doc.get("source", "")
            parts.append(
                f"[{i}] {title} (source: {source})\n"
                f"{'-' * 60}\n"
                f"{content}\n"
            )
        return "\n".join(parts)

    def citations_as_text(self) -> str:
        """Render citations as a numbered list."""
        lines = [
            f"[{c.index}] {c.title} — {c.source.value} ({c.document_type})"
            for c in self.citations
        ]
        return "\n".join(lines)
