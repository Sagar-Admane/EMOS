"""
Read-only Neo4j graph query helpers for the AI retrieval layer.
All repository-based queries now accept and enforce a repo_id scope filter.
"""
import logging
from typing import Any

from app.graph.neo4j_client import Neo4JClient
from app.ai.retrieval.neo4j import queries as Q

logger = logging.getLogger(__name__)


class AIGraphRepository:
    """
    Read-only graph query executor for the AI pipeline.
    Scopes queries to a specific connected repository ID.
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

    def find_file_owners(self, path_fragment: str, repo_id: int) -> list[dict]:
        """Find engineers who own files matching a path fragment inside a repo."""
        return self._run(
            Q.FIND_FILE_OWNERS,
            {"path_fragment": path_fragment, "repo_id": repo_id},
        )

    def find_active_engineers_on_file(
        self,
        path_fragment: str,
        repo_id: int,
        limit: int = 10,
    ) -> list[dict]:
        """Find engineers who have modified files matching a path fragment inside a repo."""
        return self._run(
            Q.FIND_MOST_ACTIVE_ENGINEERS_ON_FILE,
            {"path_fragment": path_fragment, "repo_id": repo_id, "limit": limit},
        )

    def find_engineer_owned_files(self, username: str, repo_id: int) -> list[dict]:
        """Find files owned by a specific engineer inside a repo."""
        return self._run(
            Q.FIND_ENGINEER_OWNED_FILES,
            {"username": username, "repo_id": repo_id},
        )

    def find_engineer_modified_files(self, username: str, repo_id: int, limit: int = 20) -> list[dict]:
        """Find files modified by a specific engineer inside a repo."""
        return self._run(
            Q.FIND_ENGINEER_MODIFIED_FILES,
            {"username": username, "repo_id": repo_id, "limit": limit},
        )

    def find_all_engineers(self, repo_id: int) -> list[dict]:
        """Return all active engineers for a given repository."""
        return self._run(
            Q.FIND_ALL_ENGINEERS,
            {"repo_id": repo_id}
        )

    def find_engineer_pr_activity(self, username: str, limit: int = 10) -> list[dict]:
        """Return PR activity (created + reviewed) for an engineer."""
        return self._run(
            Q.FIND_ENGINEER_PR_ACTIVITY,
            {"username": username, "limit": limit},
        )

    # ------------------------------------------------------------------ #
    # Dependency / Architecture
    # ------------------------------------------------------------------ #

    def find_file_imports(self, path_fragment: str, repo_id: int, limit: int = 20) -> list[dict]:
        """Find what files a given file imports inside a repo."""
        return self._run(
            Q.FIND_FILE_IMPORTS,
            {"path_fragment": path_fragment, "repo_id": repo_id, "limit": limit},
        )

    def find_reverse_imports(self, path_fragment: str, repo_id: int, limit: int = 20) -> list[dict]:
        """Find what files import a given file (reverse dependency) inside a repo."""
        return self._run(
            Q.FIND_REVERSE_IMPORTS,
            {"path_fragment": path_fragment, "repo_id": repo_id, "limit": limit},
        )

    def find_database_usages(self, repo_id: int, db_name: str = "") -> list[dict]:
        """Find files that use a specific database or all databases inside a repo."""
        if db_name:
            return self._run(
                Q.FIND_DATABASE_USAGES,
                {"db_name": db_name, "repo_id": repo_id},
            )
        return self._run(
            Q.FIND_ALL_DATABASE_USAGES,
            {"repo_id": repo_id}
        )

    def find_all_services(self, repo_id: int) -> list[dict]:
        """Return all services and their associated files inside a repo."""
        return self._run(
            Q.FIND_ALL_SERVICES,
            {"repo_id": repo_id}
        )

    def find_service_files(self, service_name: str, repo_id: int) -> list[dict]:
        """Find files belonging to a specific service inside a repo."""
        return self._run(
            Q.FIND_SERVICE_FILES,
            {"service_name": service_name, "repo_id": repo_id},
        )

    def find_api_endpoints(self, repo_id: int, limit: int = 30) -> list[dict]:
        """Return all API endpoints and their handler files inside a repo."""
        return self._run(
            Q.FIND_API_ENDPOINTS,
            {"repo_id": repo_id, "limit": limit},
        )

    def find_function_calls(self, file_id: int, limit: int = 20) -> list[dict]:
        """Return the function call graph for a specific file."""
        return self._run(
            Q.FIND_FUNCTION_CALLS,
            {"file_id": file_id, "limit": limit},
        )
