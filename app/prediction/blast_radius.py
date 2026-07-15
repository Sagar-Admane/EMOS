"""
Blast Radius Analyzer Module — Phase 6.4.
Traverses dependencies to model downstream cascading change trees and estimate scope.
"""
from __future__ import annotations

import logging
from typing import Any

from app.prediction.models import DependencyGraph

logger = logging.getLogger(__name__)


class BlastRadiusAnalyzer:
    """
    Models change propagation trees and estimates indirect scope of modifications.
    """

    def build_change_tree(self, dep_graph: DependencyGraph) -> dict[str, Any]:
        """
        Build a hierarchically structured dictionary representing the change blast radius.
        """
        logger.info("[BlastRadiusAnalyzer] Building change tree for root: '%s'", dep_graph.root)

        # Build immediate children from direct dependents
        direct_children = []
        for dep in sorted(dep_graph.dependents):
            # For this simple tree representation, indirect dependents branch off direct ones
            direct_children.append({
                "name": dep,
                "type": "dependent",
                "children": []
            })

        # Append transitive ones under indirect or flat branches
        indirect_children = []
        for ind in sorted(dep_graph.indirect_dependencies):
            indirect_children.append({
                "name": ind,
                "type": "transitive_dependent",
                "children": []
            })

        # If we have direct dependents, we can represent indirect ones under them
        # (or flatly as secondary radius dependents)
        tree = {
            "name": dep_graph.root,
            "type": "root",
            "children": direct_children + indirect_children
        }
        return tree

    def estimate_scope(self, dep_graph: DependencyGraph) -> dict[str, Any]:
        """
        Estimate the size, depth, and volume of the blast radius.
        """
        direct_count = len(dep_graph.dependents)
        indirect_count = len(dep_graph.indirect_dependencies)
        total_scope_count = direct_count + indirect_count

        # Estimate scope classification
        if total_scope_count == 0:
            classification = "ISOLATED"
        elif total_scope_count <= 2:
            classification = "CONTAINED"
        elif total_scope_count <= 6:
            classification = "SIGNIFICANT"
        else:
            classification = "SYSTEMIC"

        return {
            "root": dep_graph.root,
            "direct_impact_count": direct_count,
            "indirect_impact_count": indirect_count,
            "total_impact_count": total_scope_count,
            "scope_classification": classification
        }
