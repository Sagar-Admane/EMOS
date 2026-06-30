from sqlalchemy.orm import Session
from app.models.file import File
from app.utils.text_extension import TEXT_EXTENSIONS
from app.repositories.codeFileRepository import CodeFileRepository
from app.models.repository import Repository

class CodeFileIngestionService:

    def __init__(self, github_service):
        self.github_service = github_service

    def ingest(self, db: Session, repo_id: int, limit: int = 20):
        files = db.query(File).filter(File.repo_id == repo_id).limit(limit).all()
        repo = db.query(Repository).filter(Repository.id == repo_id).first()
        repo_name = repo.full_name

        for file in files:

            extension = "."+file.extension.lower()

            if extension not in TEXT_EXTENSIONS:
                continue
            
            try:
                content = self.github_service.get_file_content(repo_name, file.path)

                if content is None:
                    content = ""
            
                CodeFileRepository.create(db, {
                    "file_id": file.id,
                    "language": file.extension,
                    "content": content   
                })


            except Exception as exec:
                print(exec)
                
        return {"message": "data saved successfully"}