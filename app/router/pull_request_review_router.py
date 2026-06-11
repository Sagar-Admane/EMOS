from fastapi import APIRouter

from app.db.session import SessionLocal

from app.core.config import settings
from app.services.github_service import GithubService
from app.services.pull_request_review_service import PullRequestReviewService

from app.models.repository import Repository

router = APIRouter()

token = settings.github_token

github_service = GithubService(token)
db = SessionLocal()

@router.get("/prs-review-service")
def ingest():
    pr_req_review_service = PullRequestReviewService(github_service)

    repos = db.query(Repository).all()

    for repo in repos:
        pr_req_review_service.ingest_reviews(db, repo.id, repo.github_repo_id)

    
