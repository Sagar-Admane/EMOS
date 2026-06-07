from sqlalchemy.orm import Session
from app.models.code_chunk import CodeChunk
from app.models.file import File
from app.models.codeFile import CodeFile

class CodeChunkRepository:
    @staticmethod

    def create(db : Session, data: dict):
        codeChunkData = CodeChunk(**data)
        db.add(codeChunkData)
        db.commit()
        db.refresh(codeChunkData)

        return codeChunkData

    @staticmethod
    def exist(db: Session, code_file_id):
        return db.query(CodeChunk).filter(CodeChunk.code_file_id == code_file_id).first()
    
    @staticmethod
    def get_by_id(db: Session, code_chunk_id):
        codechunk = db.query(CodeChunk).filter(CodeChunk.id == code_chunk_id).first()
        return codechunk.chunk_text;

    @staticmethod
    def get_all(db:Session):
        return db.query(CodeChunk).order_by(CodeChunk.code_file_id, CodeChunk.start_line).all()

    @staticmethod
    def update_all(db: Session, chunks):
        db.bulk_save_objects(chunks)
        db.commit()

    @staticmethod
    def get_chunk_with_file(
        db: Session,
        chunk_id: int
    ):
        return (
            db.query(
                CodeChunk,
                File.path.label("path")
            )
            .join(
                CodeFile,
                CodeChunk.code_file_id == CodeFile.id
            )
            .join(
                File,
                CodeFile.file_id == File.id
            )
            .filter(
                CodeChunk.id == chunk_id
            )
            .first()
        )