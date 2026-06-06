from app.repositories.analytical_file_ownership import FileOwnershipAnalytics
from app.schemas.file_ownership_analytics_schema import FileOwnershipAnalyticsSchema

from sqlalchemy.orm import Session

class FileOwnershipAnalyticsService:

    def get_file_ownership(db:Session, repo_id: int):
        file_owners = FileOwnershipAnalytics.get_file_ownership(db, repo_id)

        # return [
        #     FileOwnershipAnalyticsSchema(
        #         file_path=file_owner.path,
        #         owner=file_owner.owner,
        #         changes=file_owner.changes
        #     )
        #     for file_owner in file_owners
        # ]

        owner_count = {}

        for file_owner in file_owners:
            owner = file_owner.owner

            owner_count[owner] = owner_count.get(owner, 0) + 1


        total_files = sum(owner_count.values())

        result = []

        for owner, count in owner_count.items():

            percentage = round((count/total_files) * 100, 2)

            result.append({
                "owner": owner,
                "owned_files": count,
                "percentage": percentage
            })

        return result