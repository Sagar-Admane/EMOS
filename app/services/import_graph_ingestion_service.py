from sqlalchemy.orm import Session
from app.graph.graph_repository import GraphRepository

from app.graph.import_extractor import ImportExtractor
from app.graph.path_resolver import PathResolver

from app.models.file import File
from app.models.codeFile import CodeFile


class ImportGraphIngestionServive:
    def __init__(self):
        self.graph_repository = GraphRepository()

    def ingest_imports(self, db:Session, file_id: int):
        current_file = db.query(File).filter(File.id==file_id).first()

        if not current_file:
            return
        
        print(current_file.path)
        
        code_file = db.query(CodeFile).filter(CodeFile.file_id == file_id).first()

        if not code_file:
            return

        imports = ImportExtractor.extract_imports(code_file.content, code_file.language)


        if not imports:
            return
        
        print("Imports are: ", imports)
        
        for import_path in imports:

            if not (import_path.startswith("./") or import_path.startswith("../")):
                continue

            resolved_path = PathResolver.resolve_imports(current_file.path, import_path)

            imported_path=db.query(File).filter(File.path == resolved_path).first()

            if not imported_path:
                continue

            print("Imported path: ", resolved_path)

            self.graph_repository.create_file_import_relationship(
                source_file_id=current_file.id,
                dest_file_id=imported_path.id
            )

