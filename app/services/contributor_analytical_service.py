from app.repositories.analytical_contributor import AnalyticsContributor
from app.schemas.contributor_analytics_schema import ContributorAnalyticsSchema

from sqlalchemy.orm import Session

class ContributorAnalyticalService:
    @staticmethod
    def get_top_contributors(db: Session, repo_id: int, limit:int = 10):
        contributors = AnalyticsContributor.get_top_contributor(db, repo_id, limit)

        return [ 
            ContributorAnalyticsSchema(
                username=contributor.username,
                contributions=contributor.contributions
            )

            for contributor in contributors
        ]