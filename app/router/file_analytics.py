from fastapi import APIRouter
from app.db.session import SessionLocal
router = APIRouter()

from app.services.file_analytics_service import FileAnalyticsService

@router.get("/repositories/{repo_id}/files/hotspot")
def hotspot_file(repo_id: int, limit: int = 10):
    db = SessionLocal()
    try:
        files = FileAnalyticsService.get_hotspot_files(db, repo_id)
        return files
    finally:
        db.close()
