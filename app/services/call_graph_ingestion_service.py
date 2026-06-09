from app.graph.graph_repository import GraphRepository
from app.models.codeFile import CodeFile
from sqlalchemy.orm import Session
from app.graph.call_extractor import CallExtractor

class CallGraphIngestionService:

    def __init__(self):
        self.graph_repository = GraphRepository()

    def ingest_file(self, db:Session, file_id: int):
        codefile = db.query(CodeFile).filter(CodeFile.file_id == file_id).first()

        if not codefile:
            return


        calls = CallExtractor.extract_calls(codefile.content)

        for caller, callees in calls.items():

            for callee in callees:
                self.graph_repository.create_function_call_relation(caller_name=caller, callee_name=callee, file_id=file_id)

from app.db.session import SessionLocal

service = CallGraphIngestionService()
db = SessionLocal()
service.ingest_file(db, 3055)