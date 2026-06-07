from fastapi import APIRouter
from app.core.config import settings
from app.services.github_service import GithubService
from app.services.code_chunk_ingestion import CodeChunkIngestion
from app.db.session import SessionLocal
router = APIRouter()

@router.get("/ingest-code-chunk")
def ingest():
    db = SessionLocal()
    token = settings.github_token
    github_service = GithubService(token)

    service = CodeChunkIngestion(github_service)

    response = service.ingest(db, 20, 100)

    return response

@router.get("/chunk-update-all")
def update_all():
    db = SessionLocal()

    token = settings.github_token
    github_service = GithubService(token)

    service = CodeChunkIngestion(github_service)

    response = service.update_all(db)

    return response