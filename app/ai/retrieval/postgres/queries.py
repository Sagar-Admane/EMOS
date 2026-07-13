"""
Named query functions for the AI Postgres retrieval layer.

These functions delegate to AIPostgresRepository and return
normalized dicts — no raw SQL is written here.
"""
from sqlalchemy.orm import Session

from app.ai.retrieval.postgres.repository import AIPostgresRepository


def commits_for_repo(
    db: Session,
    repo_id: int,
    limit: int = 20,
) -> list[dict]:
    """Return recent commits for a repository."""
    return AIPostgresRepository.get_commits_for_repo(db, repo_id, limit)


def commits_by_author(
    db: Session,
    repo_id: int,
    author_name: str,
    limit: int = 20,
) -> list[dict]:
    """Return commits filtered by author name (case-insensitive partial match)."""
    return AIPostgresRepository.get_commits_by_author(db, repo_id, author_name, limit)


def contributors_for_repo(
    db: Session,
    repo_id: int,
) -> list[dict]:
    """Return all contributors sorted by contribution count descending."""
    return AIPostgresRepository.get_contributors_for_repo(db, repo_id)


def pull_requests_for_repo(
    db: Session,
    repo_id: int,
    limit: int = 20,
) -> list[dict]:
    """Return recent pull requests for a repository."""
    return AIPostgresRepository.get_pull_requests_for_repo(db, repo_id, limit)


def pull_request_by_number(
    db: Session,
    repo_id: int,
    pr_number: int,
) -> dict | None:
    """Return a single pull request by its repo-relative number."""
    return AIPostgresRepository.get_pull_request_by_number(db, repo_id, pr_number)


def reviews_for_pr(
    db: Session,
    pr_internal_id: int,
) -> list[dict]:
    """Return all reviews for a pull request given its internal DB id."""
    return AIPostgresRepository.get_reviews_for_pr(db, pr_internal_id)


def files_for_repo(
    db: Session,
    repo_id: int,
    limit: int = 50,
) -> list[dict]:
    """Return files tracked for a repository."""
    return AIPostgresRepository.get_files_for_repo(db, repo_id, limit)


def repository_info(
    db: Session,
    repo_id: int,
) -> dict | None:
    """Return summary info about a repository."""
    return AIPostgresRepository.get_repository(db, repo_id)
