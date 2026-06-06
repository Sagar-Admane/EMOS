from sqlalchemy.orm import Session
from app.models.code_chunk import CodeChunk

class CodeChunkRepository:
    @staticmethod

    def create(db : Session, data: dict):
        exists = CodeChunkRepository.exist(db, data["code_file_id"])
        if exists:
            return exists
        codeChunkData = CodeChunk(**data)
        db.add(codeChunkData)
        db.commit()
        db.refresh(codeChunkData)

        return codeChunkData

    def exist(db: Session, code_file_id):
        return db.query(CodeChunk).filter(CodeChunk.code_file_id == code_file_id).first()
    
    def get_by_id(db: Session, code_chunk_id):
        codechunk = db.query(CodeChunk).filter(CodeChunk.id == code_chunk_id).first()
        return codechunk.chunk_text;