from app.graph.graph_repository import GraphRepository
from app.graph.service_extractor import ServiceExtractor

from app.models.file import File

from sqlalchemy.orm import Session

class GraphServiceIngestionService:

    def __init__(self):
        self.graph_repo = GraphRepository()

    def ingest_services(self, db: Session, file_id):
        
        file = db.query(File).filter(File.id == file_id).first()
        if not file:
            return
        
        path = file.path

        if not path:
            return

        service_name = ServiceExtractor.extract_service(path)
        if not service_name:
            return
        self.graph_repo.create_service_node(service_name)
        self.graph_repo.create_service_file_relation(service_name, file_id)

from app.db.session import SessionLocal

from app.models.file import File

service = GraphServiceIngestionService()
db = SessionLocal()

files = db.query(File).all()

for file in files:
    service.ingest_services(db, file.id)