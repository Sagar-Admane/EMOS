from sqlalchemy.orm import Session

from app.models.pull_request import PullRequest

class PullRequestRepository:

    @staticmethod
    def get_by_static_id(db: Session, github_pr_id: int):
        return db.query(PullRequest).filter(PullRequest.github_pr_id==github_pr_id).first()

    @staticmethod
    def create(db: Session, data: dict):
        existing = PullRequestRepository.get_by_static_id(db, data["github_pr_id"])

        if existing:
            return existing
        
        pr = PullRequest(**data)

        db.add(pr)
        db.commit()
        db.refresh(pr)

        return pr