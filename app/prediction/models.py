"""
Pydantic schemas and data transfer objects for the Prediction Intelligence Layer.
"""
from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class DependencyGraph(BaseModel):
    """
    Standardized dependency representation mapping direct/indirect dependencies,
    dependents, traces, and circular loop cycles.
    """
    root: str
    direct_dependencies: list[str] = Field(default_factory=list)
    indirect_dependencies: list[str] = Field(default_factory=list)
    dependents: list[str] = Field(default_factory=list)
    call_chain: list[str] = Field(default_factory=list)
    import_chain: list[str] = Field(default_factory=list)
    cycles: list[list[str]] = Field(default_factory=list)
