"""
Neo4j retriever for the AI Intelligence Layer.

Implements BaseRetriever. Uses AIGraphRepository to run
read-only Cypher queries and maps results into
normalized RetrievedDocument objects.
"""
import asyncio
import logging
import re
import time
from functools import partial

from app.ai.retrieval.base import BaseRetriever
from app.ai.retrieval.schemas import (
    RetrievalError,
    RetrievalResult,
    RetrievalStatistics,
    RetrievedDocument,
    RetrievalMetadata,
)
from app.ai.retrieval.neo4j.graph import AIGraphRepository
from app.ai.router.enums import DataSource, Intent
from app.ai.router.schemas import RouteDecision

logger = logging.getLogger(__name__)


class Neo4jRetriever(BaseRetriever):
    """
    Retrieves engineering information from Neo4j using
    read-only graph traversals based on the RouteDecision.
    """

    def __init__(self) -> None:
        self._graph = AIGraphRepository()

    @property
    def source(self) -> DataSource:
        return DataSource.NEO4J

    async def retrieve(self, route: RouteDecision) -> RetrievalResult:
        start = time.monotonic()
        documents: list[RetrievedDocument] = []
        errors: list[RetrievalError] = []

        try:
            loop = asyncio.get_event_loop()
            docs = await loop.run_in_executor(
                None,
                partial(self._fetch_sync, route),
            )
            documents.extend(docs)
        except Exception as exc:
            logger.exception("Neo4jRetriever error: %s", exc)
            errors.append(
                RetrievalError(
                    source=self.source,
                    message=str(exc),
                    retryable=True,
                )
            )

        elapsed_ms = (time.monotonic() - start) * 1000
        return RetrievalResult(
            documents=documents,
            statistics=RetrievalStatistics(
                total_documents=len(documents),
                sources_used=[self.source],
                retrieval_time_ms=elapsed_ms,
            ),
            errors=errors,
        )

    # ------------------------------------------------------------------ #
    # Internal sync dispatcher
    # ------------------------------------------------------------------ #

    def _fetch_sync(self, route: RouteDecision) -> list[RetrievedDocument]:
        intent = route.intent
        docs: list[RetrievedDocument] = []

        if intent in {Intent.REVIEW_HISTORY, Intent.PR_ANALYSIS}:
            pr_number = self._extract_pr_number(route.question)
            if pr_number is not None:
                docs.extend(self._fetch_pr_reviewers(pr_number))
            else:
                docs.extend(self._fetch_all_pr_reviews())

        if intent in {Intent.OWNERSHIP, Intent.ARCHITECTURE, Intent.REPOSITORY_SUMMARY}:
            path_fragment = self._extract_path_fragment(route)
            if path_fragment:
                docs.extend(self._fetch_ownership_for_path(path_fragment))
            else:
                docs.extend(self._fetch_all_engineers())

        if intent in {Intent.DEPENDENCY, Intent.ARCHITECTURE}:
            path_fragment = self._extract_path_fragment(route)
            docs.extend(self._fetch_dependencies(route.question, path_fragment))
            docs.extend(self._fetch_services())
            docs.extend(self._fetch_api_endpoints())

        if intent == Intent.REPOSITORY_SUMMARY:
            docs.extend(self._fetch_services())
            docs.extend(self._fetch_api_endpoints())
            docs.extend(self._fetch_database_usages())

        if intent == Intent.MIXED:
            docs.extend(self._fetch_all_engineers())
            docs.extend(self._fetch_services())

        return docs

    # ------------------------------------------------------------------ #
    # Fetchers
    # ------------------------------------------------------------------ #

    def _fetch_pr_reviewers(self, pr_number: int) -> list[RetrievedDocument]:
        results = self._graph.find_pr_reviewers(pr_number)
        if not results:
            return []
        reviewers = [r.get("reviewer", "unknown") for r in results]
        pr_title = results[0].get("pr_title", f"PR #{pr_number}") if results else f"PR #{pr_number}"
        content = (
            f"Reviewers for PR #{pr_number} – {pr_title}:\n"
            + "\n".join(f"- {r}" for r in reviewers)
        )
        return [
            RetrievedDocument(
                source=self.source,
                document_type="pr_reviewers",
                title=f"Graph: Reviewers for PR #{pr_number}",
                content=content,
                metadata=RetrievalMetadata(data={"pr_number": pr_number, "reviewers": results}),
                score=1.0,
            )
        ]

    def _fetch_all_pr_reviews(self, limit: int = 15) -> list[RetrievedDocument]:
        results = self._graph.find_all_pr_reviews(limit)
        if not results:
            return []
        lines = [
            f"- {r.get('reviewer')} reviewed PR #{r.get('pr_number')} – {r.get('pr_title', '')}"
            for r in results
        ]
        content = "Recent PR Reviews:\n" + "\n".join(lines)
        return [
            RetrievedDocument(
                source=self.source,
                document_type="pr_reviews",
                title="Graph: Recent PR Reviews",
                content=content,
                metadata=RetrievalMetadata(data={"reviews": results}),
                score=0.7,
            )
        ]

    def _fetch_ownership_for_path(self, path_fragment: str) -> list[RetrievedDocument]:
        owners = self._graph.find_file_owners(path_fragment)
        modifiers = self._graph.find_active_engineers_on_file(path_fragment)
        docs = []
        if owners:
            lines = [f"- {o.get('owner')} owns {o.get('file_path')}" for o in owners]
            content = f"File Owners for '{path_fragment}':\n" + "\n".join(lines)
            docs.append(
                RetrievedDocument(
                    source=self.source,
                    document_type="file_ownership",
                    title=f"Graph: Ownership of '{path_fragment}'",
                    content=content,
                    metadata=RetrievalMetadata(data={"owners": owners}),
                    score=0.95,
                )
            )
        if modifiers:
            lines = [
                f"- {m.get('engineer')} ({m.get('modifications')} modifications)"
                for m in modifiers
            ]
            content = f"Most Active Engineers on '{path_fragment}':\n" + "\n".join(lines)
            docs.append(
                RetrievedDocument(
                    source=self.source,
                    document_type="file_activity",
                    title=f"Graph: Active Engineers on '{path_fragment}'",
                    content=content,
                    metadata=RetrievalMetadata(data={"modifiers": modifiers}),
                    score=0.9,
                )
            )
        return docs

    def _fetch_all_engineers(self) -> list[RetrievedDocument]:
        engineers = self._graph.find_all_engineers()
        if not engineers:
            return []
        lines = [f"- {e.get('username')}" for e in engineers]
        content = "Engineers in Graph:\n" + "\n".join(lines)
        return [
            RetrievedDocument(
                source=self.source,
                document_type="engineers",
                title="Graph: All Engineers",
                content=content,
                metadata=RetrievalMetadata(data={"engineers": engineers}),
                score=0.6,
            )
        ]

    def _fetch_dependencies(
        self,
        question: str,
        path_fragment: str | None,
    ) -> list[RetrievedDocument]:
        docs = []
        if path_fragment:
            imports = self._graph.find_file_imports(path_fragment)
            rev_imports = self._graph.find_reverse_imports(path_fragment)
            if imports:
                lines = [f"- {r.get('source')} → {r.get('dependency')}" for r in imports]
                docs.append(
                    RetrievedDocument(
                        source=self.source,
                        document_type="imports",
                        title=f"Graph: Imports from '{path_fragment}'",
                        content="File Imports:\n" + "\n".join(lines),
                        metadata=RetrievalMetadata(data={"imports": imports}),
                        score=0.9,
                    )
                )
            if rev_imports:
                lines = [f"- {r.get('importer')} imports {r.get('dependency')}" for r in rev_imports]
                docs.append(
                    RetrievedDocument(
                        source=self.source,
                        document_type="reverse_imports",
                        title=f"Graph: What imports '{path_fragment}'",
                        content="Reverse Dependencies:\n" + "\n".join(lines),
                        metadata=RetrievalMetadata(data={"reverse_imports": rev_imports}),
                        score=0.85,
                    )
                )

        # Database usage
        db_match = re.search(
            r"\b(redis|postgres|mongodb|mysql|elasticsearch|sqlite)\b",
            question,
            re.IGNORECASE,
        )
        db_name = db_match.group(1) if db_match else ""
        db_usages = self._graph.find_database_usages(db_name)
        if db_usages:
            label = f"'{db_name}'" if db_name else "all databases"
            lines = [f"- {r.get('file_path')} uses {r.get('database')}" for r in db_usages]
            docs.append(
                RetrievedDocument(
                    source=self.source,
                    document_type="database_usage",
                    title=f"Graph: Database Usage ({label})",
                    content=f"Database Dependencies ({label}):\n" + "\n".join(lines),
                    metadata=RetrievalMetadata(data={"usages": db_usages}),
                    score=0.88,
                )
            )
        return docs

    def _fetch_services(self) -> list[RetrievedDocument]:
        services = self._graph.find_all_services()
        if not services:
            return []
        lines = [
            f"- {s.get('service')} ({s.get('file_count')} files)"
            for s in services
        ]
        return [
            RetrievedDocument(
                source=self.source,
                document_type="services",
                title="Graph: Services Architecture",
                content="Services:\n" + "\n".join(lines),
                metadata=RetrievalMetadata(data={"services": services}),
                score=0.8,
            )
        ]

    def _fetch_api_endpoints(self) -> list[RetrievedDocument]:
        endpoints = self._graph.find_api_endpoints()
        if not endpoints:
            return []
        lines = [
            f"- {e.get('method')} {e.get('endpoint')} → {e.get('handler_file')}"
            for e in endpoints
        ]
        return [
            RetrievedDocument(
                source=self.source,
                document_type="api_endpoints",
                title="Graph: API Endpoints",
                content="API Endpoints:\n" + "\n".join(lines),
                metadata=RetrievalMetadata(data={"endpoints": endpoints}),
                score=0.75,
            )
        ]

    def _fetch_database_usages(self) -> list[RetrievedDocument]:
        usages = self._graph.find_database_usages()
        if not usages:
            return []
        lines = [f"- {u.get('file_path')} uses {u.get('database')}" for u in usages]
        return [
            RetrievedDocument(
                source=self.source,
                document_type="database_usage",
                title="Graph: All Database Usages",
                content="Database Usages:\n" + "\n".join(lines),
                metadata=RetrievalMetadata(data={"usages": usages}),
                score=0.7,
            )
        ]

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_pr_number(question: str) -> int | None:
        match = re.search(r"(?:pr|pull request)\s*#?(\d+)", question, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r"#(\d+)", question)
        if match:
            return int(match.group(1))
        return None

    @staticmethod
    def _extract_path_fragment(route: RouteDecision) -> str | None:
        for entity in route.entities:
            if entity.typing in {"file", "module", "service", "path"}:
                return str(entity.value)
        if route.filters and route.filters.file:
            return route.filters.file
        return None
