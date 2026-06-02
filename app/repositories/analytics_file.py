from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.file import File
from app.models.commitFile import CommitFile

class AnalyticsFileRepository:
    @staticmethod
    def get_top_changed_file(db: Session, repo_id: int, limit: int = 10):
        return (db.query(
            File.path,
            func.count(CommitFile.id).label("changes")
        )
        .join(
            CommitFile,
            CommitFile.file_id == File.id
        )
        .filter(
            File.repo_id == repo_id
        )
        .group_by(
            File.id,
            File.path
        )
        .order_by(
            func.count(CommitFile.id).desc()
        )
        .limit(limit)
        .all())