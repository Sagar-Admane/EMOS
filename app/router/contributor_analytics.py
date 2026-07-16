from fastapi import APIRouter
from app.db.session import SessionLocal

from app.services.contributor_analytical_service import ContributorAnalyticalService

router = APIRouter()

@router.get("/repositories/{repo_id}/contributors/top")
def get_top_contributors(repo_id: int):
    db = SessionLocal()
    try:
        return ContributorAnalyticalService.get_top_contributors(db, repo_id, 10)
    finally:
        db.close()