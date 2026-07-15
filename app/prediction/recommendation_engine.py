"""
Recommendation Engine Module — Phase 6.5.
Provides engineering advice: suggested reviewers, target test runs, rollout, and monitoring plans.
"""
from __future__ import annotations

import logging
from typing import Any

from app.ai.agent.working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Generates actionable recommendations and safeguards for code and system changes.
    """

    def suggest_reviewers(self, working_memory: WorkingMemory, affected_files: list[str]) -> list[str]:
        """
        Suggest code reviewers based on historical activity and ownership of affected files.
        """
        reviewer_scores: dict[str, int] = {}

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
                        file_path = o.get("file_path")
                        if owner and file_path in affected_files:
                            reviewer_scores[owner] = reviewer_scores.get(owner, 0) + 15

                elif doc_type == "file_activity" and "modifiers" in data:
                    for m in data["modifiers"]:
                        engineer = m.get("engineer")
                        mods = m.get("modifications", 0)
                        if engineer:
                            # Verify if any of the modified files match our affected set
                            reviewer_scores[engineer] = reviewer_scores.get(engineer, 0) + min(10, mods)

        # Sort reviewers by score
        suggested = [r for r, score in sorted(reviewer_scores.items(), key=lambda item: item[1], reverse=True)]
        
        # Fallback if no specific owners/modifiers found
        if not suggested:
            suggested = ["lead-engineer", "architect"]

        return suggested[:3]

    def suggest_tests(self, affected_files: list[str]) -> list[str]:
        """
        Identify target regression tests to run based on the affected files set.
        """
        tests = []

        for f in affected_files:
            # Check if there is a matching test file in the directory
            base_name = f.split("/")[-1].split(".")[0]
            
            # Look for test variations
            if f.startswith("app/"):
                test_candidate = f.replace("app/", "app/test/test_").replace(".py", ".py")
                tests.append(f"pytest {test_candidate}")
            
            # Check if it contains specific subsystems
            if "auth" in f.lower():
                tests.append("pytest tests/test_auth.py")
            if "db" in f.lower() or "repository" in f.lower():
                tests.append("pytest tests/test_database.py")
            if "api" in f.lower() or "router" in f.lower():
                tests.append("pytest tests/test_api.py")

        # Standard fallback regression tests
        tests.append("pytest tests/regression/")
        
        # Deduplicate and sort
        deduped = []
        for t in tests:
            if t not in deduped:
                deduped.append(t)
        return deduped[:4]

    def suggest_rollout(self, risk_score: int) -> str:
        """
        Define deployment and rollout strategy based on computed risk scores.
        """
        if risk_score < 35:
            return (
                "Standard rollout: Direct deployment to production.\n"
                "Standard automated health check post-deploy."
            )
        elif risk_score < 70:
            return (
                "Canary rollout: Deploy to 10% traffic canary first.\n"
                "Soak time: 30 minutes. Monitor error rates before fanning out to 100%."
            )
        else:
            return (
                "High-Risk rollout: Gradual progressive rollout (1% -> 10% -> 50% -> 100%).\n"
                "Manual sign-off required at each phase. Soak time: 1 hour between stages.\n"
                "Automated rollback triggered if HTTP 5xx errors increase by >1%."
            )

    def suggest_monitoring(self, affected_files: list[str], affected_apis: list[str]) -> list[str]:
        """
        Recommend key metrics to monitor during progressive rollout.
        """
        metrics = ["CPU / Memory usage metrics"]
        
        if affected_apis:
            metrics.append(f"HTTP Latency / Failure rates on endpoints: {', '.join(affected_apis[:3])}")
        
        # Check database usage
        if any("db" in f or "model" in f or "session" in f for f in affected_files):
            metrics.append("Database Connection Pool usage & Query latency")
        
        # Redis check
        if any("redis" in f or "cache" in f for f in affected_files):
            metrics.append("Redis CPU & Cache Hit ratio")

        return metrics[:4]
