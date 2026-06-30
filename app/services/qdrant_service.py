from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)

class QdrantService:

    def __init__(self):
        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

    def create_collection(self):

        self.client.recreate_collection(
            collection_name="test_code_chunks",
            vectors_config=VectorParams(
                size=384,
                distance=Distance.COSINE
            )
        )

    def upsert_chunk(self, chunk_id: int, vector: list, payload: dict):
        self.client.upsert(
            collection_name="test_code_chunks",
            points = [
                PointStruct(
                    id=chunk_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search(self, vector: list, limit=5):
        results = self.client.query_points(
            collection_name="test_code_chunks",
            query=vector,
            limit=limit,
            with_vectors=True
        ).points
        
        return results