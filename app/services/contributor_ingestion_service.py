from app.repositories.contributor_repository import ContributorRepository

class ContributorIngestionService:
    def __init__(self, github_service):
        self.github_service = github_service

    def contributor_ingestion(self, db, repo_name, repo_id):
        contributors = self.github_service.get_contributors(repo_name)

        count = 0

        for contributor in contributors:

            ContributorRepository.create(
                db,
                {
                    "repo_id": repo_id,
                    "github_user_id": contributor.id,
                    "username": contributor.login,
                    "contributions": contributor.contributions
                }
            )

            count+=1

        return count