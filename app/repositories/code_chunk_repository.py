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