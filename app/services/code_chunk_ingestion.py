from sqlalchemy.orm import Session
from app.models.codeFile import CodeFile
from app.repositories.code_chunk_repository import CodeChunkRepository

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

            for start in range(0, len(lines), chunk_size):
                end = start+ chunk_size
                chunk_lines = lines[start:end]

                chunk_text = "\n".join(chunk_lines)

                CodeChunkRepository.create(db, {
                    "code_file_id": code_file.id,
                    "chunk_text": chunk_text,
                    "start_line": start+1,
                    "end_line": min(end, len(lines))
                })

                total_chunks+=1

        return {
            "code_file_processed": len(code_files),
            "chunks_created": total_chunks
        }