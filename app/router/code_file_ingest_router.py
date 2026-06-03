from fastapi import APIRouter
from app.db.session import SessionLocal
from app.services.code_file_ingestion_service import CodeFileIngestionService
from app.services.github_service import GithubService
from app.core.config import settings
router = APIRouter()

@router.get("/repositories/{repo_id}/code-file-ingest")
def ingest(repo_id: int):
    db = SessionLocal()
    token = settings.github_token
    github_service = GithubService(token)

    service = CodeFileIngestionService(github_service)

    return service.ingest(db, repo_id)
