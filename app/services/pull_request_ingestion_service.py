from app.repositories.pull_request_repository import PullRequestRepository

class PullRequestIngestionService:

    def __init__(self, github_service):
        self.github_service = github_service

    def ingest_pull_requests(self, db, repo_name: str, repo_id: int, limit: int):
        pulls = self.github_service.get_pull_requests(repo_name)

        processed = 0

        for pr in pulls:
            if processed >= limit:
                break

            data = {
                "repo_id": repo_id,
                "github_pr_id": pr.id,
                "number": pr.number,
                "title": pr.title,
                "body": pr.body,
                "state": pr.state,
                "author": (
                    pr.user.login
                    if pr.user
                    else None
                ),
                "merged": pr.merged,
                "created_at": pr.created_at,
                "merged_at": pr.merged_at
            }

            PullRequestRepository.create(
                db,
                data
            )

            processed += 1
        
        return processed