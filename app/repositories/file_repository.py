from app.models.file import File
from sqlalchemy.orm import Session
class FileRepository:

    @staticmethod
    def get_by_path(db: Session, repo_id, path):
        return db.query(File).filter(File.repo_id == repo_id, File.path == path).first()

    @staticmethod
    def create(db, data):
        existing = FileRepository.get_by_path(db, data["repo_id"], data["path"])
        if existing:
            return existing
        
        file = File(**data)

        db.add(file)

        return file
    
    @staticmethod
    def get_by_repo_id(db: Session,repo_id: int):
        
        return db.query(File).filter(File.repo_id == repo_id).all()
        