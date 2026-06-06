from fastapi import APIRouter
from app.services.file_content_ingestion_service import FileContentIngestionService
from app.db.session import SessionLocal
from app.core.config import settings
from app.services.github_service import GithubService

router = APIRouter()


@router.get("/ingest-content/{repo_id}")
def file_content_ingestion(repo_id):
    token = settings.github_token
    github_service = GithubService(token)
    db = SessionLocal()

    return FileContentIngestionService.file_content_ingestion(db, repo_id, github_service)