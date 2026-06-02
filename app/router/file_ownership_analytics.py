from app.services.file_ownership_analytics_service import FileOwnershipAnalyticsService
from fastapi import APIRouter
from app.db.session import SessionLocal
router = APIRouter()

@router.get("/repositories/{repo_id}/files/ownership")
def get_file_owners(repo_id: int):
    try:
        db = SessionLocal()
        return FileOwnershipAnalyticsService.get_file_ownership(db, repo_id)
    finally:
        db.close()
