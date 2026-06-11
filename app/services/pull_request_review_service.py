from app.repositories.pull_request_review_repository import PullRequestReviewRepository

from sqlalchemy.orm import Session

from app.services.github_service import GithubService

from app.models.pull_request import PullRequest

class PullRequestReviewService:

    def __init__(self, github_service: GithubService):
        self.github_service = github_service

    def ingest_reviews(self, db: Session, repo_id: int, github_repo_id: int):

        print("Pr ingesting....")
        pull_requests = db.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()

        if len(pull_requests) == 0:
            print("issfurfiewfiewfjej")
            return

        for pr in pull_requests:
            pr_reviews = self.github_service.get_pr_reviews(github_repo_id, pr.number)

            if not pr_reviews:
                print("No pr existed")
                return

            for pr_review in pr_reviews:
                data = {
                    "pull_request_id": pr.id,
                    "reviewer_username": pr_review.user.login,
                    "state": pr_review.state,
                    "submitted_at": pr_review.submitted_at 
                }
                PullRequestReviewRepository.create(db, data)