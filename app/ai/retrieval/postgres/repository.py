"""
AI-side read-only PostgreSQL repository adapter.

Wraps existing domain repositories to return plain dicts
suitable for document normalization. Never writes data.
"""
from sqlalchemy.orm import Session

from app.repositories.commit_repository import CommitRepository
from app.repositories.contributor_repository import ContributorRepository
from app.repositories.file_repository import FileRepository
from app.repositories.pull_request_repository import PullRequestRepository
from app.repositories.pull_request_review_repository import PullRequestReviewRepository
from app.repositories.repository_repository import RepositoryRepository
from app.models.commit import Commit
from app.models.contributor import Contributor
from app.models.file import File
from app.models.pull_request import PullRequest
from app.models.pull_request_reviews import PullRequestReview
from app.models.repository import Repository


class AIPostgresRepository:
    """
    Read-only adapter layer used by the AI retrieval pipeline.
    Translates domain ORM objects into plain dicts without
    duplicating any existing query logic.
    """

    # ------------------------------------------------------------------ #
    # Repository
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_repository(db: Session, repo_id: int) -> dict | None:
        repo: Repository | None = RepositoryRepository.get_by_id(db, repo_id)
        if repo is None:
            return None
        return {
            "id": repo.id,
            "name": repo.name,
            "full_name": repo.full_name,
            "owner": repo.owner,
            "description": repo.description,
            "default_branch": repo.default_branch,
            "visibility": repo.visibility,
        }

    # ------------------------------------------------------------------ #
    # Commits
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_commits_for_repo(
        db: Session,
        repo_id: int,
        limit: int = 20,
    ) -> list[dict]:
        commits: list[Commit] = (
            db.query(Commit)
            .filter(Commit.repo_id == repo_id)
            .order_by(Commit.commit_date.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "sha": c.sha,
                "message": c.message,
                "author_name": c.author_name,
                "author_email": c.author_email,
                "commit_date": str(c.commit_date) if c.commit_date else None,
                "url": c.github_commit_url,
            }
            for c in commits
        ]

    @staticmethod
    def get_commits_by_author(
        db: Session,
        repo_id: int,
        author_name: str,
        limit: int = 20,
    ) -> list[dict]:
        commits: list[Commit] = (
            db.query(Commit)
            .filter(Commit.repo_id == repo_id, Commit.author_name.ilike(f"%{author_name}%"))
            .order_by(Commit.commit_date.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "sha": c.sha,
                "message": c.message,
                "author_name": c.author_name,
                "commit_date": str(c.commit_date) if c.commit_date else None,
            }
            for c in commits
        ]

    # ------------------------------------------------------------------ #
    # Contributors
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_contributors_for_repo(
        db: Session,
        repo_id: int,
    ) -> list[dict]:
        contributors: list[Contributor] = (
            db.query(Contributor)
            .filter(Contributor.repo_id == repo_id)
            .order_by(Contributor.contributions.desc())
            .all()
        )
        return [
            {
                "username": c.username,
                "github_user_id": c.github_user_id,
                "contributions": c.contributions,
            }
            for c in contributors
        ]

    # ------------------------------------------------------------------ #
    # Pull Requests
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_pull_requests_for_repo(
        db: Session,
        repo_id: int,
        limit: int = 20,
    ) -> list[dict]:
        prs: list[PullRequest] = (
            db.query(PullRequest)
            .filter(PullRequest.repo_id == repo_id)
            .order_by(PullRequest.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": pr.id,
                "number": pr.number,
                "title": pr.title,
                "state": pr.state,
                "author": pr.author,
                "merged": pr.merged,
                "created_at": str(pr.created_at) if pr.created_at else None,
                "merged_at": str(pr.merged_at) if pr.merged_at else None,
            }
            for pr in prs
        ]

    @staticmethod
    def get_pull_request_by_number(
        db: Session,
        repo_id: int,
        pr_number: int,
    ) -> dict | None:
        pr: PullRequest | None = (
            db.query(PullRequest)
            .filter(PullRequest.repo_id == repo_id, PullRequest.number == pr_number)
            .first()
        )
        if pr is None:
            return None
        return {
            "id": pr.id,
            "number": pr.number,
            "title": pr.title,
            "body": pr.body,
            "state": pr.state,
            "author": pr.author,
            "merged": pr.merged,
            "created_at": str(pr.created_at) if pr.created_at else None,
            "merged_at": str(pr.merged_at) if pr.merged_at else None,
        }

    # ------------------------------------------------------------------ #
    # Pull Request Reviews
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_reviews_for_pr(
        db: Session,
        pr_internal_id: int,
    ) -> list[dict]:
        reviews: list[PullRequestReview] = (
            db.query(PullRequestReview)
            .filter(PullRequestReview.pull_request_id == pr_internal_id)
            .all()
        )
        return [
            {
                "reviewer_username": r.reviewer_username,
                "state": r.state,
                "submitted_at": str(r.submitted_at) if r.submitted_at else None,
            }
            for r in reviews
        ]

    # ------------------------------------------------------------------ #
    # Files
    # ------------------------------------------------------------------ #

    @staticmethod
    def get_files_for_repo(
        db: Session,
        repo_id: int,
        limit: int = 50,
    ) -> list[dict]:
        files: list[File] = (
            db.query(File)
            .filter(File.repo_id == repo_id)
            .limit(limit)
            .all()
        )
        return [
            {
                "id": f.id,
                "path": f.path,
                "extension": f.extension,
                "size": f.size,
            }
            for f in files
        ]
