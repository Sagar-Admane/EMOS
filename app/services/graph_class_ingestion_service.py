from app.graph.graph_repository import GraphRepository
from app.graph.class_extractor import ClassExtractor

from app.models.codeFile import CodeFile

from sqlalchemy.orm import Session

class GraphClassIngestionService:

    def __init__(self):
        self.graph_repo = GraphRepository()

    def ingest_files(self, db: Session, file_id: int):

        codefile = db.query(CodeFile).filter(CodeFile.id == file_id).first()

        if not codefile:
            return
        
        class_name = ClassExtractor.extract_classes(codefile.content, codefile.language)

        if not class_name:
            return

        self.graph_repo.create_class_node(class_name, file_id)

        self.graph_repo.file_class_relation(class_name, file_id)

