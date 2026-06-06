from app.repositories.file_content_repository import FileContentRepository
from app.repositories.file_repository import FileRepository
from app.repositories.repository_repository import RepositoryRepository

from app.services.github_service import GithubService
from app.core.config import settings
from app.utils.hashing import hash

from sqlalchemy.orm import Session

class FileContentIngestionService:

    def file_content_ingestion(db: Session, repo_id, githubservice: GithubService):
        repo_name = RepositoryRepository.get_by_id(db, repo_id).full_name
        files = FileRepository.get_by_repo_id(db, repo_id)

        for file in files:
            
            existing = FileContentRepository.get_by_file_id(db, file.id)

            if existing:
                continue

            content = githubservice.get_file_content(repo_name, file.path)

            if content is None:
                continue

            hashed_content = hash(content)

            FileContentRepository.create(db, {
                "file_id": file.id,
                "content": content,
                "content_hashed": hashed_content
            })


        return {
            "message": "file content ingested successfully"
        }