from sqlalchemy.orm import Session

from app.models.contributor import Contributor

class ContributorRepository:

    @staticmethod
    def get_by_github_ids(db: Session, github_user_id):
        return db.query(Contributor).filter(Contributor.github_user_id == github_user_id).first()

    @staticmethod
    def create(db: Session, data: dict):
        existing = ContributorRepository.get_by_github_ids(db, data["github_user_id"])
        if existing:
            return existing
        
        contributor = Contributor(**data)
        db.add(contributor)
        db.commit()
        db.refresh(contributor)

        return contributor