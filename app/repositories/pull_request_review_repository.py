from sqlalchemy.orm import Session

from app.models.pull_request_reviews import PullRequestReview

class PullRequestReviewRepository:

    @staticmethod
    def exist(db:Session, pull_number: int):
        pr = db.query(PullRequestReview).filter(PullRequestReview.pull_request_id == pull_number).first()
        return pr
        

    @staticmethod
    def create(db: Session, data: dict):
        exists = PullRequestReviewRepository.exist(db, data["pull_request_id"])
        if exists:
            print("Existing...")
            return
        pr_review = PullRequestReview(**data)

        db.add(pr_review)
        db.commit()
        db.refresh(pr_review)