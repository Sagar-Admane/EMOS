from app.graph.graph_repository import GraphRepository
from app.models.codeFile import CodeFile
from app.graph.function_extractor import FunctionExtractor

from sqlalchemy.orm import Session

class FunctionGraphIngestionService:

    def __init__(self):
        self.graph_repository = GraphRepository()

    def ingest_file(self, db:Session, file_id: int):

        try:
            code_file = db.query(CodeFile).filter(CodeFile.file_id == file_id).first()

            if not code_file:
                return
            
            print(code_file.content)
            
            functions = FunctionExtractor.extract_functions(code_file.content, code_file.language)

            if len(functions) == 0:
                print("There are no functions")

            for function_name in functions:

                self.graph_repository.create_function_node(file_id, function_name)

                self.graph_repository.file_to_function_relation(file_id, function_name)
        
            print("Node created successfully")

        except Exception as exc:
            print("Exception",exc)