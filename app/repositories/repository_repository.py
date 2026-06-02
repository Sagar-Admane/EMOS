from sqlalchemy.orm import Session
from app.models.repository import Repository

class RepositoryRepository(Repository):

    @staticmethod
    def get_by_full_name(db: Session, full_name: str):
        return db.query(Repository).filter(Repository.full_name==full_name).first()

    @staticmethod
    def create(db: Session, data: dict):

        existing = RepositoryRepository.get_by_full_name(db, data["full_name"])
        if existing:
            return existing
        repo = Repository(**data)

        db.add(repo)
        db.commit()
        db.refresh(repo)
        
        return repo
    
    @staticmethod
    def get_by_id(db: Session, repo_id: int):
        return db.query(Repository).filter(Repository.id == repo_id).first()