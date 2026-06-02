from app.models.file import File
from app.models.commitFile import CommitFile
from app.models.commit import Commit
from sqlalchemy.orm import Session
from sqlalchemy import func

class FileOwnershipAnalytics:

    @staticmethod
    def get_file_ownership(db: Session, repo_id):
        return db.query(
            File.path,
            Commit.author_name.label("owner"),
            func.count(CommitFile.id).label("changes")
        ).join(CommitFile, CommitFile.file_id == File.id).join(Commit, Commit.id == CommitFile.commit_id).filter(File.repo_id == repo_id).group_by(File.path, Commit.author_name).all()
    