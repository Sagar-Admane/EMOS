from sqlalchemy.orm import Session
from app.models.commit import Commit

class CommitRepository:

    @staticmethod
    def get_by_sha(db: Session, sha: str):
        return db.query(Commit).filter(Commit.sha==sha).first()

    @staticmethod
    def create(db: Session, data: dict):
        existing = CommitRepository.get_by_sha(db, data["sha"])

        if existing:
            return existing
        
        commit = Commit(**data)
        db.add(commit)
        db.commit()
        db.refresh(commit)

        return commit