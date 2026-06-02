from app.repositories.analytical_file_ownership import FileOwnershipAnalytics
from app.schemas.file_ownership_analytics_schema import FileOwnershipAnalyticsSchema

from sqlalchemy.orm import Session

class FileOwnershipAnalyticsService:

    def get_file_ownership(db:Session, repo_id: int):
        file_owners = FileOwnershipAnalytics.get_file_ownership(db, repo_id)

        return [
            FileOwnershipAnalyticsSchema(
                file_path=file_owner.path,
                owner=file_owner.owner,
                changes=file_owner.changes
            )
            for file_owner in file_owners
        ]