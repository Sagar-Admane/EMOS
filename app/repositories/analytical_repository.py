from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.commit import Commit
from app.models.pull_request import PullRequest
from app.models.contributor import Contributor
from app.models.file import File
from app.models.branch import Branch

from sqlalchemy.orm import Session

class AnalyticsRepository:

    @staticmethod
    def count_commit(db:Session, repo_id: int):
        return db.query(func.count(Commit.id)).filter(Commit.repo_id == repo_id).scalar()

    @staticmethod
    def count_pull_requests(db: Session, repo_id):
        return db.query(func.count(PullRequest.id)).filter(PullRequest.repo_id == repo_id).scalar()
    
    @staticmethod
    def count_contributors(db: Session, repo_id):
        return db.query(func.count(Contributor.id)).filter(Contributor.repo_id == repo_id).scalar()
    
    @staticmethod
    def count_files(db: Session, repo_id):
        return db.query(func.count(File.id)).filter(File.repo_id == repo_id).scalar()
    
    @staticmethod
    def count_branches(db: Session, repo_id):
        return db.query(func.count(Branch.id)).filter(Branch.repo_id == repo_id).scalar()