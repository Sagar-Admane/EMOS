from app.repositories.commit_repository import (
    CommitRepository
)


class CommitIngestionService:

    def __init__(
        self,
        github_service
    ):
        self.github_service = github_service

    def ingest_commits(
        self,
        db,
        repo_name,
        repo_id,
        limit=20
    ):
        commits = (
            self.github_service
            .get_commit(repo_name)
        )

        count = 0

        for commit in commits:

            if count >= limit:
                break

            data = {
                "repo_id": repo_id,
                "sha": commit.sha,
                "message": commit.commit.message,
                "author_name": (
                    commit.commit.author.name
                    if commit.commit.author
                    else "Unknown"
                ),
                "author_email": (
                    commit.commit.author.email
                    if commit.commit.author
                    else None
                ),
                "commit_date": (
                    commit.commit.author.date
                    if commit.commit.author
                    else None
                ),
                "parent_sha": (
                    commit.parents[0].sha
                    if commit.parents
                    else None
                )
            }

            CommitRepository.create(
                db,
                data
            )

            count += 1

        return count