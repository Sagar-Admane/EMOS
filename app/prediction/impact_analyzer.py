"""
Change Impact Analyzer Module — Phase 6.2.
Simulates modifications to a component to determine affected files, APIs, services, and tests.
"""
from __future__ import annotations

import logging
from typing import Any

from app.prediction.models import DependencyGraph
from app.ai.agent.working_memory import WorkingMemory

logger = logging.getLogger(__name__)


class ImpactAnalyzer:
    """
    Simulates modifications to files or functions to identify direct and indirect impacts.
    """

    def analyze_impact(
        self,
        dep_graph: DependencyGraph,
        working_memory: WorkingMemory
    ) -> dict[str, Any]:
        """
        Simulate impact using the DependencyGraph and Service/API maps extracted from Working Memory.
        """
        logger.info("[ImpactAnalyzer] Analyzing change impact for root: '%s'", dep_graph.root)

        # 1. Gather all affected files (including dependents and root file if it's a file)
        # dependents are the files/functions that depend on the root
        affected_entities = set([dep_graph.root] + dep_graph.dependents)

        # 2. Extract service-to-file and API-handler mappings from working memory
        service_file_map: dict[str, str] = {}  # file_path -> service_name
        api_handler_map: dict[str, list[str]] = {}  # handler_file -> list of API formatted strings

        for step in working_memory.steps:
            raw_res = step.get("raw_result")
            if not raw_res or not hasattr(raw_res, "documents"):
                continue

            for doc in raw_res.documents:
                doc_type = getattr(doc, "document_type", "")
                data = getattr(doc.metadata, "data", {}) if hasattr(doc, "metadata") else {}
                if not data:
                    continue

                # Parse Services
                if doc_type == "services" and "services" in data:
                    for s in data["services"]:
                        service_name = s.get("service")
                        files = s.get("files", [])
                        for f in files:
                            if service_name:
                                service_file_map[f] = service_name

                # Parse API Endpoints
                elif doc_type == "api_endpoints" and "endpoints" in data:
                    for e in data["endpoints"]:
                        method = e.get("method", "GET")
                        path = e.get("endpoint", "")
                        handler = e.get("handler_file", "")
                        if path and handler:
                            api_str = f"{method} {path}"
                            api_handler_map.setdefault(handler, []).append(api_str)

        # 3. Compute impact mappings
        affected_files: list[str] = []
        affected_services: set[str] = set()
        affected_apis: list[str] = []
        affected_tests: list[str] = []

        for entity in sorted(affected_entities):
            # Check if this entity is a file path
            is_file = "/" in entity or "." in entity or entity.endswith(".py")
            
            if is_file:
                affected_files.append(entity)
                
                # Check for owning service
                service = service_file_map.get(entity)
                if service:
                    affected_services.add(service)

                # Check for handlers
                apis = api_handler_map.get(entity, [])
                affected_apis.extend(apis)

                # Check for test files
                if "test" in entity.lower() or "tests" in entity.lower():
                    affected_tests.append(entity)
            else:
                # If it's a function, we add it to affected_files if it belongs to a known file context
                # and check if we can resolve its file from database, or treat it as a code entity
                pass

        # Deduplicate results
        affected_apis = sorted(list(set(affected_apis)))
        affected_tests = sorted(list(set(affected_tests)))
        affected_services_list = sorted(list(affected_services))

        return {
            "root": dep_graph.root,
            "affected_files": affected_files,
            "affected_services": affected_services_list,
            "affected_apis": affected_apis,
            "affected_tests": affected_tests,
            "total_files": len(affected_files),
            "total_services": len(affected_services_list),
            "total_apis": len(affected_apis),
            "total_tests": len(affected_tests)
        }
