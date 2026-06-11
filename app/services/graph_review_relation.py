from app.graph.graph_repository import GraphRepository
from sqlalchemy.orm import Session
from app.models.pull_request_reviews import PullRequestReview
from app.core.config import settings
from app.services.github_service import GithubService
class GraphReviewRelation:

    def __init__(self):
        self.graph_repo = GraphRepository()

    def create_relation(self, db: Session, pr_id: int):
        token = settings.github_token
        github_service = GithubService(token)
        pr_reviews = db.query(PullRequestReview).all()
        for pr_review in pr_reviews:
            user = pr_review.reviewer_username
            github_user_id = github_service.get_user(user).id
            self.graph_repo.create_engineer_nodes(github_user_id, user)
            self.graph_repo.create_engineer_pr_reviews_relation(pr_review.pull_request_id, user)

from app.db.session import SessionLocal

from app.models.pull_request import PullRequest

service = GraphReviewRelation()
db = SessionLocal()

prs = db.query(PullRequest).all()

for pr in prs:
    service.create_relation(db, pr.id)
