from app.graph.graph_repository import GraphRepository

from sqlalchemy.orm import Session

from app.models.file import File

class GraphFileIngestionService:

    def __init__(self):
        self.graph_repo = GraphRepository()

    def ingest_files(self, db : Session, repo_id):
        files = db.query(File).filter(File.repo_id == repo_id).all()

        for file in files:
            self.graph_repo.create_file_node(file.id, file.path, file.extension)


from app.db.session import SessionLocal
service = GraphFileIngestionService()
db = SessionLocal()

service.ingest_files(db, 4)