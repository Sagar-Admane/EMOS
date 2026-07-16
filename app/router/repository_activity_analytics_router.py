from fastapi import APIRouter
from app.db.session import SessionLocal
from app.services.repository_activity_analytics_service import RepositoryActivityAnalyticsService
router = APIRouter()

@router.get("/repositories/{repo_id}/activity")
def get_repo_activity(repo_id: int):
    db = SessionLocal()
    try:
        return RepositoryActivityAnalyticsService.get_repo_activity(db, repo_id)
    finally:
        db.close()