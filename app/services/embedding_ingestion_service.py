from sqlalchemy.orm import Session

from app.services.embedding_service import EmbeddingService
from app.services.qdrant_service import QdrantService
from app.models.code_chunk import CodeChunk
from app.models.codeFile import CodeFile
from app.models.file import File


class EmbeddingIngestionService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.qdrant_service = QdrantService()

    def generate_embedding(
        self,
        db: Session,
        repo_id: int,
        collection_name: str,
        limit: int = None  # None = all chunks
    ):
        """
        Embed all code chunks for a given repo and upsert them into Qdrant.
        Fixes the earlier bug where file_path stored language instead of actual path.
        """
        # Join CodeChunk → CodeFile → File to get actual file path
        query = (
            db.query(CodeChunk, CodeFile, File)
            .join(CodeFile, CodeChunk.code_file_id == CodeFile.id)
            .join(File, CodeFile.file_id == File.id)
            .filter(File.repo_id == repo_id)
        )

        if limit:
            query = query.limit(limit)

        rows = query.all()

        embedded_count = 0

        for chunk, code_file, file in rows:
            try:
                vector = self.embedding_service.embedd(chunk.chunk_text)

                self.qdrant_service.upsert_chunk(
                    chunk_id=chunk.id,
                    vector=vector,
                    payload={
                        "chunk_id": chunk.id,
                        "code_file_id": chunk.code_file_id,
                        "repo_id": repo_id,
                        "start_line": chunk.start_line,
                        "end_line": chunk.end_line,
                        "file_path": file.path,           # Fixed: real path not language
                        "language": code_file.language,   # Added: language as separate field
                    },
                    collection_name=collection_name
                )

                embedded_count += 1

            except Exception as exc:
                print(f"[EmbeddingIngestion] Error on chunk {chunk.id}: {exc}")

        return {"chunks_embedded": embedded_count}