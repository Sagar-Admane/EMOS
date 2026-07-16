from fastapi import APIRouter, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.core.config import settings

from app.models.repository import Repository
from app.models.connected_repo import ConnectedRepo

from app.schemas.github_connect import (
    ConnectRepoRequest,
    ConnectRepoResponse,
    RepoStatusResponse,
    RepoListItem,
)

from app.services.github_service import GithubService
from app.services.repository_ingestion_service import RepositoryIngestion
from app.services.full_ingestion_pipeline import run_full_ingestion

router = APIRouter(prefix="/github", tags=["GitHub Connect"])


def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/connect", response_model=ConnectRepoResponse, status_code=202)
def connect_repository(body: ConnectRepoRequest, background_tasks: BackgroundTasks):
    """
    Connect a public GitHub repository.
    Validates the repo, stores metadata, then launches the full ingestion
    pipeline (PostgreSQL + Qdrant + Neo4j) as a background task.
    Returns immediately with status = 'indexing'.
    """
    db: Session = SessionLocal()

    try:
        token = settings.github_token
        github_service = GithubService(token)

        # ── 1. Fetch from GitHub API ──────────────────────────────────────────
        try:
            gh_repo = github_service.get_repository(body.repo_full_name)
        except Exception:
            raise HTTPException(
                status_code=404,
                detail=f"Repository '{body.repo_full_name}' not found on GitHub."
            )

        # ── 2. Block private repos ────────────────────────────────────────────
        if gh_repo.private:
            raise HTTPException(
                status_code=403,
                detail="Private repositories are not supported. Only public repos can be connected."
            )

        # ── 3. Upsert into PostgreSQL repositories table ──────────────────────
        ingestion = RepositoryIngestion(github_service)
        repo_record: Repository = ingestion.ingest_repository(db, body.repo_full_name)

        repo_id = repo_record.id
        qdrant_collection = f"repo_{repo_id}"

        # ── 4. Create / update ConnectedRepo status record ───────────────────
        connected = db.query(ConnectedRepo).filter(
            ConnectedRepo.repo_id == repo_id
        ).first()

        if connected:
            # Re-trigger ingestion if previously failed or already done
            connected.status = "indexing"
            connected.error_message = None
            connected.qdrant_collection = qdrant_collection
            from datetime import datetime
            connected.connected_at = datetime.utcnow()
            connected.indexed_at = None
        else:
            connected = ConnectedRepo(
                repo_id=repo_id,
                status="indexing",
                qdrant_collection=qdrant_collection,
            )
            db.add(connected)

        db.commit()
        db.refresh(connected)

        # ── 5. Launch background pipeline ─────────────────────────────────────
        background_tasks.add_task(
            run_full_ingestion,
            repo_id=repo_id,
            repo_full_name=body.repo_full_name,
            qdrant_collection=qdrant_collection,
        )

        return ConnectRepoResponse(
            repo_id=repo_id,
            full_name=repo_record.full_name,
            status="indexing",
            qdrant_collection=qdrant_collection,
            connected_at=connected.connected_at,
        )

    finally:
        db.close()


@router.get("/repos", response_model=list[RepoListItem])
def list_connected_repos():
    """Return all connected repositories and their indexing status."""
    db: Session = SessionLocal()
    try:
        rows = (
            db.query(ConnectedRepo, Repository)
            .join(Repository, ConnectedRepo.repo_id == Repository.id)
            .all()
        )

        result = []
        for cr, repo in rows:
            result.append(
                RepoListItem(
                    repo_id=repo.id,
                    full_name=repo.full_name,
                    owner=repo.owner,
                    description=repo.description,
                    visibility=repo.visibility or "public",
                    status=cr.status,
                    qdrant_collection=cr.qdrant_collection,
                    connected_at=cr.connected_at,
                    indexed_at=cr.indexed_at,
                )
            )
        return result
    finally:
        db.close()


@router.get("/repos/{repo_id}/status", response_model=RepoStatusResponse)
def get_repo_status(repo_id: int):
    """Poll the indexing status of a connected repository."""
    db: Session = SessionLocal()
    try:
        cr = db.query(ConnectedRepo).filter(ConnectedRepo.repo_id == repo_id).first()
        if not cr:
            raise HTTPException(status_code=404, detail="Repository not connected.")

        repo = db.query(Repository).filter(Repository.id == repo_id).first()

        return RepoStatusResponse(
            repo_id=repo_id,
            full_name=repo.full_name,
            owner=repo.owner,
            status=cr.status,
            qdrant_collection=cr.qdrant_collection,
            error_message=cr.error_message,
            connected_at=cr.connected_at,
            indexed_at=cr.indexed_at,
        )
    finally:
        db.close()


@router.delete("/repos/{repo_id}", status_code=204)
def disconnect_repo(repo_id: int):
    """
    Disconnect a repository.
    Removes the ConnectedRepo tracking record.
    Does NOT delete PostgreSQL data or Qdrant vectors — those remain intact.
    """
    db: Session = SessionLocal()
    try:
        cr = db.query(ConnectedRepo).filter(ConnectedRepo.repo_id == repo_id).first()
        if not cr:
            raise HTTPException(status_code=404, detail="Repository not connected.")
        db.delete(cr)
        db.commit()
    finally:
        db.close()
