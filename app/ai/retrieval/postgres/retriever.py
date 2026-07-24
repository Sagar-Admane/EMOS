"""
PostgreSQL retriever for the AI Intelligence Layer.

Implements BaseRetriever. Maps domain objects from the existing
repository layer into normalized RetrievedDocument objects.
Never writes SQL directly — delegates to queries.py.
"""
import asyncio
import logging
import re
import time
from functools import partial

from sqlalchemy.orm import Session

from app.ai.retrieval.base import BaseRetriever
from app.ai.retrieval.schemas import (
    RetrievalError,
    RetrievalResult,
    RetrievalStatistics,
    RetrievedDocument,
    RetrievalMetadata,
)
from app.ai.retrieval import postgres as pg_queries
from app.ai.router.enums import DataSource, Intent
from app.ai.router.schemas import RouteDecision
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)


class PostgresRetriever(BaseRetriever):
    """
    Retrieves engineering information from PostgreSQL by
    translating a RouteDecision into the appropriate queries.
    """

    @property
    def source(self) -> DataSource:
        return DataSource.POSTGRES

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
            logger.exception("PostgresRetriever error: %s", exc)
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
    # Internal sync helpers (run in executor to keep async pipeline clean)
    # ------------------------------------------------------------------ #

    def _fetch_sync(self, route: RouteDecision) -> list[RetrievedDocument]:
        db: Session = SessionLocal()
        try:
            return self._dispatch(db, route)
        finally:
            db.close()

    def _dispatch(
        self,
        db: Session,
        route: RouteDecision,
    ) -> list[RetrievedDocument]:
        """Route to the appropriate query based on intent."""
        intent = route.intent
        repo_id: int | None = self._extract_repo_id(route)
        docs: list[RetrievedDocument] = []

        if intent == Intent.REVIEW_HISTORY or intent == Intent.PR_ANALYSIS:
            docs.extend(self._fetch_pr_and_reviews(db, route, repo_id))

        if intent in {Intent.OWNERSHIP, Intent.COMMIT_HISTORY, Intent.REPOSITORY_SUMMARY}:
            docs.extend(self._fetch_commits(db, repo_id))
            docs.extend(self._fetch_contributors(db, repo_id))

        if intent == Intent.REPOSITORY_SUMMARY:
            docs.extend(self._fetch_repo_info(db, repo_id))
            docs.extend(self._fetch_pull_requests(db, repo_id))
            docs.extend(self._fetch_files(db, repo_id))

        if intent == Intent.MIXED:
            docs.extend(self._fetch_repo_info(db, repo_id))
            docs.extend(self._fetch_commits(db, repo_id))
            docs.extend(self._fetch_contributors(db, repo_id))
            docs.extend(self._fetch_files(db, repo_id))

        return docs

    # ------------------------------------------------------------------ #
    # Fetchers → produce RetrievedDocument
    # ------------------------------------------------------------------ #

    def _fetch_repo_info(
        self,
        db: Session,
        repo_id: int | None,
    ) -> list[RetrievedDocument]:
        if repo_id is None:
            return []
        info = pg_queries.repository_info(db, repo_id)
        if info is None:
            return []
        content = (
            f"Repository: {info['full_name']}\n"
            f"Owner: {info['owner']}\n"
            f"Description: {info.get('description') or 'N/A'}\n"
            f"Default Branch: {info.get('default_branch') or 'main'}\n"
            f"Visibility: {info.get('visibility') or 'unknown'}"
        )
        return [
            RetrievedDocument(
                source=self.source,
                document_type="repository_info",
                title=f"Repository: {info['full_name']}",
                content=content,
                metadata=RetrievalMetadata(data=info),
                score=1.0,
            )
        ]

    def _fetch_commits(
        self,
        db: Session,
        repo_id: int | None,
        limit: int = 15,
    ) -> list[RetrievedDocument]:
        if repo_id is None:
            return []
        commits = pg_queries.commits_for_repo(db, repo_id, limit)
        docs = []
        for c in commits:
            content = (
                f"SHA: {c['sha']}\n"
                f"Author: {c['author_name']} <{c.get('author_email', '')}>\n"
                f"Date: {c.get('commit_date', 'unknown')}\n"
                f"Message: {c['message']}"
            )
            docs.append(
                RetrievedDocument(
                    source=self.source,
                    document_type="commit",
                    title=f"Commit {c['sha'][:8]} by {c['author_name']}",
                    content=content,
                    metadata=RetrievalMetadata(data=c),
                    score=0.7,
                )
            )
        return docs

    def _fetch_contributors(
        self,
        db: Session,
        repo_id: int | None,
    ) -> list[RetrievedDocument]:
        if repo_id is None:
            return []
        contributors = pg_queries.contributors_for_repo(db, repo_id)
        if not contributors:
            return []
        lines = [
            f"- {c['username']} ({c['contributions']} contributions)"
            for c in contributors
        ]
        content = "Top Contributors:\n" + "\n".join(lines)
        return [
            RetrievedDocument(
                source=self.source,
                document_type="contributors",
                title="Repository Contributors",
                content=content,
                metadata=RetrievalMetadata(
                    data={"contributors": contributors}
                ),
                score=0.85,
            )
        ]

    def _fetch_pull_requests(
        self,
        db: Session,
        repo_id: int | None,
        limit: int = 10,
    ) -> list[RetrievedDocument]:
        if repo_id is None:
            return []
        prs = pg_queries.pull_requests_for_repo(db, repo_id, limit)
        docs = []
        for pr in prs:
            content = (
                f"PR #{pr['number']}: {pr['title']}\n"
                f"Author: {pr.get('author', 'unknown')}\n"
                f"State: {pr['state']} | Merged: {pr['merged']}\n"
                f"Created: {pr.get('created_at', 'unknown')}"
            )
            docs.append(
                RetrievedDocument(
                    source=self.source,
                    document_type="pull_request",
                    title=f"PR #{pr['number']}: {pr['title'][:60]}",
                    content=content,
                    metadata=RetrievalMetadata(data=pr),
                    score=0.75,
                )
            )
        return docs

    def _fetch_pr_and_reviews(
        self,
        db: Session,
        route: RouteDecision,
        repo_id: int | None,
    ) -> list[RetrievedDocument]:
        docs: list[RetrievedDocument] = []

        # Try to extract a PR number from the question
        pr_number = self._extract_pr_number(route.question)

        if pr_number is not None and repo_id is not None:
            pr_dict = pg_queries.pull_request_by_number(db, repo_id, pr_number)
            if pr_dict:
                reviews = pg_queries.reviews_for_pr(db, pr_dict["id"])

                pr_content = (
                    f"PR #{pr_dict['number']}: {pr_dict['title']}\n"
                    f"Author: {pr_dict.get('author', 'unknown')}\n"
                    f"State: {pr_dict['state']} | Merged: {pr_dict['merged']}\n"
                    f"Body: {(pr_dict.get('body') or '')[:300]}"
                )
                docs.append(
                    RetrievedDocument(
                        source=self.source,
                        document_type="pull_request",
                        title=f"PR #{pr_dict['number']}: {pr_dict['title'][:60]}",
                        content=pr_content,
                        metadata=RetrievalMetadata(data=pr_dict),
                        score=1.0,
                    )
                )

                if reviews:
                    lines = [
                        f"- {r['reviewer_username']} ({r['state']}) at {r.get('submitted_at', 'unknown')}"
                        for r in reviews
                    ]
                    review_content = (
                        f"Reviews for PR #{pr_dict['number']} – {pr_dict['title']}:\n"
                        + "\n".join(lines)
                    )
                    docs.append(
                        RetrievedDocument(
                            source=self.source,
                            document_type="pr_reviews",
                            title=f"Reviews for PR #{pr_dict['number']}",
                            content=review_content,
                            metadata=RetrievalMetadata(
                                data={"pr": pr_dict, "reviews": reviews}
                            ),
                            score=1.0,
                        )
                    )

        elif repo_id is not None:
            # No specific PR — return recent PRs
            docs.extend(self._fetch_pull_requests(db, repo_id))

        return docs

    def _fetch_files(
        self,
        db: Session,
        repo_id: int | None,
    ) -> list[RetrievedDocument]:
        if repo_id is None:
            return []
        files = pg_queries.files_for_repo(db, repo_id, limit=200)
        if not files:
            return []

        # Calculate extension distribution
        ext_counts = {}
        for f in files:
            ext = f.get('extension', '') or 'no extension'
            ext_counts[ext] = ext_counts.get(ext, 0) + 1

        sorted_exts = sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)
        ext_summary = ", ".join(f"{ext}: {count} files" for ext, count in sorted_exts)

        lines = [f"- {f['path']} ({f.get('extension', '')})" for f in files[:50]]
        content = f"Language / Extension Summary: {ext_summary}\n\nRepository File List (Sample):\n" + "\n".join(lines)
        return [
            RetrievedDocument(
                source=self.source,
                document_type="file_list",
                title="Repository File Tree and Language Breakdown",
                content=content,
                metadata=RetrievalMetadata(data={"files": files, "extension_counts": ext_counts}),
                score=0.9,
            )
        ]

    # ------------------------------------------------------------------ #
    # Utilities
    # ------------------------------------------------------------------ #

    @staticmethod
    def _extract_repo_id(route: RouteDecision) -> int | None:
        """
        Extract repo_id from route filters or entities.
        Falls back gracefully if not present.
        """
        if hasattr(route, "filters") and route.filters:
            raw = getattr(route.filters, "repository", None)
            if raw and str(raw).isdigit():
                return int(raw)
        # Also check entities
        for entity in route.entities:
            if entity.typing == "repo_id":
                try:
                    return int(entity.value)
                except (ValueError, TypeError):
                    pass
        return None

    @staticmethod
    def _extract_pr_number(question: str) -> int | None:
        """Extract a PR number like #43 or PR 43 from the question."""
        match = re.search(r"(?:pr|pull request)\s*#?(\d+)", question, re.IGNORECASE)
        if match:
            return int(match.group(1))
        match = re.search(r"#(\d+)", question)
        if match:
            return int(match.group(1))
        return None
