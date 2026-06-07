from app.services.qdrant_service import QdrantService
from app.services.embedding_service import EmbeddingService
from app.repositories.code_chunk_repository import CodeChunkRepository
from app.db.session import SessionLocal

class SemanticSearchService:

    def __init__(self):
        self.qdrantService = QdrantService()
        self.embeddingService = EmbeddingService()

    def search(self, text: str):

        db = SessionLocal()
        vector = self.embeddingService.embedd(text)
        results = self.qdrantService.search(vector)

        results = sorted(results, key = lambda x:x.score, reverse=True)

        search_answers = []

        for result in results:
            print(result.id)
            print(result.score)
            print(result.payload)
            
            payload = result.payload

            text = CodeChunkRepository.get_by_id(db, result.id)
            if text is None:
                continue
            path = CodeChunkRepository.get_chunk_with_file(db, result.id).path
            print("The text is: ", text)
            print("PAth is: ", path)

            search_answers.append({
                "id": result.id,
                "score": result.score,
                "text": text,
                "path": path,
                "start_line": payload.get("start_line"),
                "end_line": payload.get("end_line")
            })

        return search_answers