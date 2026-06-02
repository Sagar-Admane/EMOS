from sqlalchemy.orm import Session

from app.repositories.commit_file_repository import CommitFileRepository
from app.models.commit import Commit
from app.models.file import File
class CommitFileIngestion:
    def __init__(self, github_service):
        self.github_service = github_service

    def commit_file_ingestion(self, db: Session, repo_name, repo_id):
        commits = db.query(Commit).filter(Commit.repo_id == repo_id).all()

        relation = 0
        for commit in commits:

            github_commit = (
                self.github_service
                .get_commit(
                    repo_name,
                    commit.sha
                )
            )

            for changed_file in github_commit.files:

                file_row = (
                    db.query(File)
                    .filter(
                        File.repo_id == repo_id,
                        File.path == changed_file.filename
                    )
                    .first()
                )

                if not file_row:
                    continue

                CommitFileRepository.create(
                    db,
                    {
                        "commit_id": commit.id,
                        "file_id": file_row.id,
                        "additions": (
                            changed_file.additions
                        ),
                        "deletions": (
                            changed_file.deletions
                        )
                    }
                )

                relation += 1

        db.commit()

        return relation