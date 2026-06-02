from app.repositories.branch_repository import BrachRepository

class BranchIngestionService:
    
    def __init__(self, github_service):
        self.github_service = github_service

    def ingest_branches(self, db, repo_name: str, repo_id: int):
        branches = self.github_service.get_branches(repo_name)

        count = 0

        for branch in branches:

            print("Calling branch repository")

            BrachRepository.create(db,{
                "repo_id": repo_id,
                "name": branch.name
            })

            count += 1

        return count