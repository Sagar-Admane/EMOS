from app.repositories.repository_repository import RepositoryRepository

from app.repositories.analytical_repository import AnalyticsRepository

from app.schemas.repository_schema import RepositoryResponseSchema

class RepositoryResponseService:

    @staticmethod
    def get_summary(db, repo_id: int):
        repository = RepositoryRepository.get_by_id(db, repo_id)

        if not repository:
            raise ValueError("Repository not found")

        return RepositoryResponseSchema(
            repository_id=repository.id,
            repository_name=repository.name,
            owner=repository.owner,
            total_commits=AnalyticsRepository.count_commit(db, repo_id),
            total_pull_requests=AnalyticsRepository.count_pull_requests(db, repo_id),
            total_contributors=AnalyticsRepository.count_contributors(db, repo_id),
            total_branches=AnalyticsRepository.count_branches(db, repo_id),
            total_files=AnalyticsRepository.count_files(db, repo_id)
        )