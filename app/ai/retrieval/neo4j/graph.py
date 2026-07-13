"""
Read-only Neo4j graph query helpers for the AI retrieval layer.

Wraps Neo4JClient for read-only graph traversals.
Never writes — no MERGE, CREATE, or SET calls here.
"""
import logging
from typing import Any

from app.graph.neo4j_client import Neo4JClient
from app.ai.retrieval.neo4j import queries as Q

logger = logging.getLogger(__name__)


class AIGraphRepository:
    """
    Read-only graph query executor for the AI pipeline.
    Reuses the existing Neo4JClient infrastructure.
    """

    def __init__(self) -> None:
        self._client = Neo4JClient()

    def _run(self, query: str, params: dict | None = None) -> list[dict[str, Any]]:
        """Execute a Cypher query and return a list of plain dicts."""
        try:
            raw_results = self._client.execute_query(query, params or {})
            return [dict(record) for record in raw_results]
        except Exception as exc:
            logger.warning("Neo4j query failed: %s", exc)
            return []

    # ------------------------------------------------------------------ #
    # PR Reviewer
    # ------------------------------------------------------------------ #

    def find_pr_reviewers(self, pr_number: int) -> list[dict]:
        """Find engineers who reviewed a specific PR by its number."""
        return self._run(
            Q.FIND_PR_REVIEWERS,
            {"pr_number": pr_number},
        )

    def find_all_pr_reviews(self, limit: int = 20) -> list[dict]:
        """Find all PR reviews across the graph."""
        return self._run(
            Q.FIND_ALL_PR_REVIEWS_FOR_REPO,
            {"limit": limit},
        )

    # ------------------------------------------------------------------ #
    # Ownership
    # ------------------------------------------------------------------ #

    def find_file_owners(self, path_fragment: str) -> list[dict]:
        """Find engineers who own files matching a path fragment."""
        return self._run(
            Q.FIND_FILE_OWNERS,
            {"path_fragment": path_fragment},
        )

    def find_active_engineers_on_file(
        self,
        path_fragment: str,
        limit: int = 10,
    ) -> list[dict]:
        """Find engineers who have modified files matching a path fragment."""
        return self._run(
            Q.FIND_MOST_ACTIVE_ENGINEERS_ON_FILE,
            {"path_fragment": path_fragment, "limit": limit},
        )

    def find_engineer_owned_files(self, username: str) -> list[dict]:
        """Find files owned by a specific engineer."""
        return self._run(
            Q.FIND_ENGINEER_OWNED_FILES,
            {"username": username},
        )

    def find_engineer_modified_files(self, username: str, limit: int = 20) -> list[dict]:
        """Find files modified by a specific engineer."""
        return self._run(
            Q.FIND_ENGINEER_MODIFIED_FILES,
            {"username": username, "limit": limit},
        )

    def find_all_engineers(self) -> list[dict]:
        """Return all engineers in the graph."""
        return self._run(Q.FIND_ALL_ENGINEERS)

    def find_engineer_pr_activity(self, username: str, limit: int = 10) -> list[dict]:
        """Return PR activity (created + reviewed) for an engineer."""
        return self._run(
            Q.FIND_ENGINEER_PR_ACTIVITY,
            {"username": username, "limit": limit},
        )

    # ------------------------------------------------------------------ #
    # Dependency / Architecture
    # ------------------------------------------------------------------ #

    def find_file_imports(self, path_fragment: str, limit: int = 20) -> list[dict]:
        """Find what files a given file imports."""
        return self._run(
            Q.FIND_FILE_IMPORTS,
            {"path_fragment": path_fragment, "limit": limit},
        )

    def find_reverse_imports(self, path_fragment: str, limit: int = 20) -> list[dict]:
        """Find what files import a given file (reverse dependency)."""
        return self._run(
            Q.FIND_REVERSE_IMPORTS,
            {"path_fragment": path_fragment, "limit": limit},
        )

    def find_database_usages(self, db_name: str = "") -> list[dict]:
        """Find files that use a specific database or all databases."""
        if db_name:
            return self._run(
                Q.FIND_DATABASE_USAGES,
                {"db_name": db_name},
            )
        return self._run(Q.FIND_ALL_DATABASE_USAGES)

    def find_all_services(self) -> list[dict]:
        """Return all services and their associated files."""
        return self._run(Q.FIND_ALL_SERVICES)

    def find_service_files(self, service_name: str) -> list[dict]:
        """Find files belonging to a specific service."""
        return self._run(
            Q.FIND_SERVICE_FILES,
            {"service_name": service_name},
        )

    def find_api_endpoints(self, limit: int = 30) -> list[dict]:
        """Return all API endpoints and their handler files."""
        return self._run(
            Q.FIND_API_ENDPOINTS,
            {"limit": limit},
        )

    def find_function_calls(self, file_id: int, limit: int = 20) -> list[dict]:
        """Return the function call graph for a specific file."""
        return self._run(
            Q.FIND_FUNCTION_CALLS,
            {"file_id": file_id, "limit": limit},
        )
