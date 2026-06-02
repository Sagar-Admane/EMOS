from fastapi import APIRouter
from app.db.session import SessionLocal
from app.services.repository_response_service import RepositoryResponseService

router = APIRouter()

@router.get("/repositories/{repo_id}/summary")
def repository_summary(repo_id: int):
    db = SessionLocal()
    try:
        return RepositoryResponseService.get_summary(db, repo_id)
    finally:
        db.close()