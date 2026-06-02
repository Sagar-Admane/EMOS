from app.repositories.analytics_file import AnalyticsFileRepository

from app.schemas.file_analytics_schema import FileAnalyticsSchema

class FileAnalyticsService:

    @staticmethod
    def get_hotspot_files(db, repo_id: int, limit: int = 10):
        files = AnalyticsFileRepository.get_top_changed_file(db, repo_id, limit)

        return [
            FileAnalyticsSchema(
            file_path=file.path,
            changes=file.changes
        )
            for file in files
        ]
