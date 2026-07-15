"""
Risk Engine Module — Phase 6.3.
Calculates risk scores (0-100) based on dependents, transitives, cycles, bus factors, and change frequency.
"""
from __future__ import annotations

import logging
from typing import Any

from app.prediction.models import DependencyGraph
from app.ai.agent.working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class RiskEngine:
    """
    Computes static and dynamic risk factors for proposed changes.
    """

    def calculate_risk(
        self,
        dep_graph: DependencyGraph,
        working_memory: WorkingMemory
    ) -> dict[str, Any]:
        """
        Calculate risk score (0-100) and risk level (LOW/MEDIUM/HIGH) with justifications.
        """
        logger.info("[RiskEngine] Calculating risk for root: '%s'", dep_graph.root)

        # 1. Base weights from Graph Topology
        # Direct dependents (incoming connections): Higher count = higher risk
        dependent_count = len(dep_graph.dependents)
        dependent_weight = min(40, dependent_count * 8)

        # Indirect dependencies (ripple dependencies)
        indirect_count = len(dep_graph.indirect_dependencies)
        indirect_weight = min(20, indirect_count * 3)

        # Cycles penalty: Circular dependencies make refactoring risky
        cycle_penalty = 15 if dep_graph.cycles else 0

        # 2. Extract Ownership and Modification stats from Working Memory
        unique_owners: set[str] = set()
        total_modifications = 0
        unique_modifiers: set[str] = set()

        for step in working_memory.steps:
            raw_res = step.get("raw_result")
            if not raw_res or not hasattr(raw_res, "documents"):
                continue

            for doc in raw_res.documents:
                doc_type = getattr(doc, "document_type", "")
                data = getattr(doc.metadata, "data", {}) if hasattr(doc, "metadata") else {}
                if not data:
                    continue

                if doc_type == "file_ownership" and "owners" in data:
                    for o in data["owners"]:
                        owner = o.get("owner")
                        if owner:
                            unique_owners.add(owner)

                elif doc_type == "file_activity" and "modifiers" in data:
                    for m in data["modifiers"]:
                        engineer = m.get("engineer")
                        mods = m.get("modifications", 0)
                        if engineer:
                            unique_modifiers.add(engineer)
                        total_modifications += mods

        # 3. Compute Bus Factor and Change frequency penalties
        # Bus Factor (Number of owners/modifiers): Fewer owners/modifiers = higher dependency risk
        bus_factor = len(unique_owners)
        if bus_factor == 0:
            # If no formal owner, check modifiers
            bus_factor = len(unique_modifiers)

        if bus_factor == 0:
            bus_factor_penalty = 25  # Orphaned file
            bus_factor_msg = "Critical: No registered owner or active modifier."
        elif bus_factor == 1:
            bus_factor_penalty = 15  # Single point of failure
            bus_factor_msg = "Warning: Single point of failure (Bus Factor = 1)."
        else:
            bus_factor_penalty = 0
            bus_factor_msg = f"Healthy ownership coverage (Bus Factor = {bus_factor})."

        # Hotspot check (highly modified files)
        frequency_penalty = min(15, (total_modifications // 5) * 5)
        frequency_msg = f"Modified {total_modifications} times recently."

        # 4. Final aggregation
        score = dependent_weight + indirect_weight + cycle_penalty + bus_factor_penalty + frequency_penalty
        score = max(0, min(100, score))

        if score < 35:
            level = "LOW"
        elif score < 70:
            level = "MEDIUM"
        else:
            level = "HIGH"

        # Collect justifications
        justifications = []
        if dependent_count > 0:
            justifications.append(f"Directly affects {dependent_count} files/functions.")
        if indirect_count > 0:
            justifications.append(f"Indirectly cascades to {indirect_count} transitive components.")
        if cycle_penalty > 0:
            justifications.append("Circular dependencies detected along traversal path.")
        justifications.append(bus_factor_msg)
        if total_modifications > 10:
            justifications.append(f"Frequent hotspot: {frequency_msg}")

        return {
            "score": score,
            "level": level,
            "bus_factor": bus_factor,
            "total_modifications": total_modifications,
            "cycles_detected": len(dep_graph.cycles),
            "justifications": justifications
        }
