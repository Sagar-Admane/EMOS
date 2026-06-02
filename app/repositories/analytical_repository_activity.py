from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.commit import Commit

class RepositoryActivityAnalytics:
    @staticmethod
    def get_commit_activity(db: Session, repo_id: int):
        return db.query(
            func.count(Commit.id).label("total_commits"),
            func.min(Commit.commit_date).label("first_commit"),
            func.max(Commit.commit_date).label("last_commit")
        ).filter(
            Commit.repo_id == repo_id
        ).first()
    