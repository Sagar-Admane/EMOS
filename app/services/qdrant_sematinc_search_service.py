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

        for result in results:
            print(result.id)
            print(result.score)
            print(result.payload)
            
            text = CodeChunkRepository.get_by_id(db, result.id)
            print("The text is: ", text)



        