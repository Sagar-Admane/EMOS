from app.models.contributor import Contributor

from sqlalchemy.orm import Session

class AnalyticsContributor:

    @staticmethod
    def get_top_contributor(db: Session, repo_id: int, limit: int = 10):
        return db.query(Contributor).filter(Contributor.repo_id == repo_id).order_by(Contributor.contributions.desc()).limit(limit).all()
    