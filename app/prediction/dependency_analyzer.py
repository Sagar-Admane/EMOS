"""
Dependency Analyzer Module — Phase 6.1.
Parses graph relationships from Working Memory, builds dependency trees,
limits depth, and runs cycle detection.
"""
from __future__ import annotations

import logging
from typing import Any

from app.prediction.models import DependencyGraph
from app.ai.agent.working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class DependencyAnalyzer:
    """
    Analyzes dependency relationships of files and functions from Working Memory.
    Performs loop/cycle detection and returns a standardized DependencyGraph object.
    """

    def analyze(
        self,
        working_memory: WorkingMemory,
        entity: str,
        level: str = "auto",
        max_depth: int = 5
    ) -> DependencyGraph:
        """
        Build the DependencyGraph for a target file or function.
        - Parses imports, reverse imports, and function calls from working memory results.
        - Executes depth-limited DFS cycle detection.
        """
        logger.info("[DependencyAnalyzer] Starting analysis for: '%s' (level=%s, max_depth=%d)", entity, level, max_depth)

        # 1. Build adjacency graphs from raw data in Working Memory
        imports_adj: dict[str, set[str]] = {}
        reverse_imports_adj: dict[str, set[str]] = {}
        calls_adj: dict[str, set[str]] = {}
        reverse_calls_adj: dict[str, set[str]] = {}

        for step in working_memory.steps:
            raw_res = step.get("raw_result")
            if not raw_res or not hasattr(raw_res, "documents"):
                continue

            for doc in raw_res.documents:
                doc_type = getattr(doc, "document_type", "")
                data = getattr(doc.metadata, "data", {}) if hasattr(doc, "metadata") else {}
                if not data:
                    continue

                # Parse file imports
                if doc_type == "imports" and "imports" in data:
                    for relation in data["imports"]:
                        src = relation.get("source")
                        dep = relation.get("dependency")
                        if src and dep:
                            imports_adj.setdefault(src, set()).add(dep)

                # Parse reverse file imports
                elif doc_type == "reverse_imports" and "reverse_imports" in data:
                    for relation in data["reverse_imports"]:
                        importer = relation.get("importer")
                        dep = relation.get("dependency")
                        if importer and dep:
                            reverse_imports_adj.setdefault(dep, set()).add(importer)
                            # Also represent the forward relationship for completeness
                            imports_adj.setdefault(importer, set()).add(dep)

                # Parse function calls
                elif doc_type == "function_calls" and "calls" in data:
                    for relation in data["calls"]:
                        caller = relation.get("caller")
                        callee = relation.get("callee")
                        if caller and callee:
                            calls_adj.setdefault(caller, set()).add(callee)
                            reverse_calls_adj.setdefault(callee, set()).add(caller)

        # 2. Determine granularity level
        # If "auto", inspect adjacency lists to see if entity is a file or a function
        selected_level = level
        if selected_level == "auto":
            # Files typically contain "/" or "." or match file keys
            if "/" in entity or "." in entity or entity in imports_adj or entity in reverse_imports_adj:
                selected_level = "file"
            else:
                selected_level = "function"
        logger.debug("[DependencyAnalyzer] Selected analysis level: %s", selected_level)

        # 3. Choose target graphs based on level
        if selected_level == "function":
            forward_adj = calls_adj
            backward_adj = reverse_calls_adj
        else:
            forward_adj = imports_adj
            backward_adj = reverse_imports_adj

        # 4. Resolve Direct Dependencies
        direct_deps = sorted(list(forward_adj.get(entity, set())))

        # 5. Resolve Direct Dependents
        direct_dependents = sorted(list(backward_adj.get(entity, set())))

        # 6. DFS for Transitive (Indirect) Dependencies & Cycle Detection
        visited_nodes: set[str] = set()
        recursion_stack: list[str] = []
        indirect_deps: list[str] = []
        cycles: list[list[str]] = []

        self._dfs(
            node=entity,
            adj=forward_adj,
            visited=visited_nodes,
            rec_stack=recursion_stack,
            depth=1,
            max_depth=max_depth,
            indirect_deps=indirect_deps,
            cycles=cycles
        )

        # Clean up: direct dependencies should not be duplicated in indirect list
        indirect_deps = [d for d in indirect_deps if d != entity and d not in direct_deps]

        # 7. Trace ordered chains
        chain_list = [entity] + indirect_deps

        return DependencyGraph(
            root=entity,
            direct_dependencies=direct_deps,
            indirect_dependencies=indirect_deps,
            dependents=direct_dependents,
            call_chain=chain_list if selected_level == "function" else [],
            import_chain=chain_list if selected_level == "file" else [],
            cycles=cycles
        )

    def _dfs(
        self,
        node: str,
        adj: dict[str, set[str]],
        visited: set[str],
        rec_stack: list[str],
        depth: int,
        max_depth: int,
        indirect_deps: list[str],
        cycles: list[list[str]]
    ) -> None:
        """DFS traversal mapping paths and detecting cycles."""
        if depth > max_depth:
            return

        rec_stack.append(node)
        visited.add(node)

        neighbors = adj.get(node, set())
        for neighbor in sorted(neighbors):
            if neighbor in rec_stack:
                # Cycle detected
                cycle_start = rec_stack.index(neighbor)
                cycle_path = rec_stack[cycle_start:] + [neighbor]
                if cycle_path not in cycles:
                    cycles.append(cycle_path)
            else:
                if neighbor not in visited:
                    indirect_deps.append(neighbor)
                    self._dfs(
                        neighbor, adj, visited, rec_stack,
                        depth + 1, max_depth, indirect_deps, cycles
                    )

        rec_stack.pop()
