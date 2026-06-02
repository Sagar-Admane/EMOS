from app.models.repository import Repository
from app.repositories.repository_repository import RepositoryRepository

class RepositoryIngestion(RepositoryRepository):

    def __init__(self, github_service):
        self.github_service = github_service

    def ingest_repository(self, db, repo_name:str):
        github_repo = (self.github_service.get_repository(repo_name))

        data = {
            "github_repo_id": github_repo.id,
            "name": github_repo.name,
            "full_name": github_repo.full_name,
            "owner": github_repo.owner.login,
            "description": github_repo.description,
            "default_branch": github_repo.default_branch,
            "visibility": (
                "private"
                if github_repo.private
                else "public"
            )
        }

        return RepositoryRepository.create(
            db,
            data
        )