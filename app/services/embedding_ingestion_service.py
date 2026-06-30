from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.models.code_chunk import CodeChunk
from app.models.codeFile import CodeFile
from sqlalchemy.orm import Session
class EmbeddingIngestionService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def generate_embedding(self, db: Session, limit: int = 100):

        chunks = db.query(CodeChunk).limit(limit).all()

        embedded_count = 0

        for chunk in chunks:
            vector = self.embedding_service.embedd(chunk.chunk_text)

            path = db.query(CodeFile).filter(CodeFile.id == chunk.code_file_id).first().language

            self.qdrant_service.upsert_chunk(
                chunk_id=chunk.id,
                vector=vector,
                payload = {
                    "chunk_id": chunk.id,
                    "code_file_id": chunk.code_file_id,
                    "start_line": chunk.start_line,
                    "end_line": chunk.end_line,
                    "file_path": path
                }
            )

            embedded_count+=1

        return {
            "chunks_processed": embedded_count
        }