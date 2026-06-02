import os
from app.repositories.file_repository import FileRepository

class FileIngestionService:
    def __init__(self, github_service):
        self.github_service = github_service

    def file_ingestion(self, db, repo_name, repo_id):
        tree = self.github_service.get_repository_tree(repo_name)

        count = 0

        for item in tree:

            if item.type!="blob":
                continue
            path = item.path

            extension = os.path.splitext(path)[1].replace(".","")

            FileRepository.create(db, {
                "repo_id": repo_id,
                "path": path,
                "extension": extension,
                "size" : item.size,
                "last_modified_commit": item.sha
            })

        db.commit()

        return count