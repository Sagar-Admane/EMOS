from app.repositories.analytical_repository_activity import RepositoryActivityAnalytics
from sqlalchemy.orm import Session

from app.schemas.repository_activity_analytics_schema import RepositoryActivityAnalyticsSchema

class RepositoryActivityAnalyticsService:
    def get_repo_activity(db: Session, repo_id: int):
        activity = RepositoryActivityAnalytics.get_commit_activity(db, repo_id)

        active_days = (activity.last_commit - activity.first_commit).days
        if active_days!=0:
            avg_commit_per_day = activity.total_commits/active_days
        else:
            avg_commit_per_day = 0
            
        return RepositoryActivityAnalyticsSchema(
            total_commits=activity.total_commits,
            first_commit=activity.first_commit,
            last_commit=activity.last_commit,
            active_days=active_days,
            avg_commit_per_day=avg_commit_per_day
        )
        