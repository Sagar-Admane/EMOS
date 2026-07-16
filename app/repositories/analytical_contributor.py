from app.models.contributor import Contributor
from app.models.commit import Commit
from sqlalchemy import func
from sqlalchemy.orm import Session


class AnalyticsContributor:

    @staticmethod
    def get_top_contributor(db: Session, repo_id: int, limit: int = 10):
        # 1. Try to fetch from the explicit contributors table
        contributors = (
            db.query(Contributor)
            .filter(Contributor.repo_id == repo_id)
            .order_by(Contributor.contributions.desc())
            .limit(limit)
            .all()
        )
        if contributors:
            return contributors

        # 2. Fallback: Aggregate and group commits by author
        results = (
            db.query(
                Commit.author_name,
                func.count(Commit.id).label("contributions")
            )
            .filter(Commit.repo_id == repo_id)
            .group_by(Commit.author_name)
            .order_by(func.count(Commit.id).desc())
            .limit(limit)
            .all()
        )

        class PseudoContributor:
            def __init__(self, username, contributions):
                self.username = username
                self.contributions = contributions

        return [
            PseudoContributor(row.author_name, row.contributions)
            for row in results
        ]