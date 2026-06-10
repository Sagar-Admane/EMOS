from app.graph.graph_repository import GraphRepository
from app.graph.database_extractor import DatabaseExtractor

from app.models.codeFile import CodeFile

from sqlalchemy.orm import Session

class GraphDatabaseIngestionService:

    def __init__(self):
        self.graphRepository = GraphRepository()

    def ingest_files(self, db: Session, file_id: int):
        code_file = db.query(CodeFile).filter(CodeFile.file_id == file_id).first()

        if not code_file:
            return
        
        database = DatabaseExtractor.extract_database(code_file.content)

        if not database:
            return
        
        self.graphRepository.create_database_node(database)

        self.graphRepository.create_file_database_relation(file_id, database)

from app.db.session import SessionLocal

from app.models.file import File

service = GraphDatabaseIngestionService()
db = SessionLocal()

files = db.query(File).all()

for file in files:
    service.ingest_files(db, file.id)

