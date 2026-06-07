from sqlalchemy.orm import Session
from app.models.codeFile import CodeFile
from app.repositories.code_chunk_repository import CodeChunkRepository

import hashlib

class CodeChunkIngestion:
    def __init__(self, github_service):
        self.github_service = github_service

    def ingest(self, db: Session, limit: int, chunk_size: int):

        code_files = db.query(
            CodeFile
        ).limit(limit).all()


        total_chunks = 0

        for code_file in code_files:
            if CodeChunkRepository.exist(db, code_file.id):
                continue

            lines = code_file.content.splitlines()

            for chunk_index, start in enumerate(
                range(0, len(lines), chunk_size)
            ):
                end = start + chunk_size

                chunk_lines = lines[start:end]

                chunk_text = "\n".join(chunk_lines)

                chunk_hash = hashlib.sha256(
                    chunk_text.encode("utf-8")
                ).hexdigest()

                CodeChunkRepository.create(
                    db,
                    {
                        "code_file_id": code_file.id,
                        "code_chunk_index": chunk_index,
                        "chunk_hashed": chunk_hash,
                        "chunk_text": chunk_text,
                        "start_line": start + 1,
                        "end_line": min(end, len(lines))
                    }
                )

                total_chunks += 1

        return {
            "code_file_processed": len(code_files),
            "chunks_created": total_chunks
        }
    
    def update_all(self, db: Session):
        chunks = CodeChunkRepository.get_all(db)

        current_file_id = None
        index = 0

        for chunk in chunks:
            if current_file_id!=chunk.code_file_id:
                current_file_id = chunk.code_file_id
                index = 0
            chunk.code_chunk_index = index
            chunk.chunk_hashed = hashlib.sha256(
                chunk.chunk_text.encode("utf-8")
            ).hexdigest()

            index+=1
        
        CodeChunkRepository.update_all(db, chunks)

        return {"message": "updated_all"}