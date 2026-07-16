from app.graph.graph_repository import GraphRepository

from sqlalchemy.orm import Session

from app.models.codeFile import CodeFile

from app.graph.api_extractor import APIExtractor
from app.models.file import File

class GraphAPIIngestion:

    def __init__(self):
        self.graph_repo = GraphRepository()

    def ingest_files(self, db:Session, file_id: int):

        codefiles = db.query(CodeFile).filter(CodeFile.file_id == file_id).first()
        file = db.query(File).filter(File.id == file_id).first()

        if not codefiles:
            return

        apis = APIExtractor.extract_apis(codefiles.content)

        for api in apis:

            self.graph_repo.create_api_node(path=api["path"], method=api["method"])
            self.graph_repo.create_api_funtion_relation(api["path"], api["method"], file_id, file.path)
