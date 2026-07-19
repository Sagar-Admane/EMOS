from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct
)
from app.core.config import settings

DEFAULT_COLLECTION = "test_code_chunks"
VECTOR_SIZE = 384


class QdrantService:

    def __init__(self):

        qdrant_host = settings.qdrant_host
        qdrant_api = settings.qdrant_api

        if qdrant_host:
            self.client = QdrantClient(
                host=qdrant_host,
                api_key=qdrant_api
            )
        else:
            self.client = QdrantClient(
                host="localhost",
                port=6333
            )


    def collection_exists(self, collection_name: str) -> bool:
        try:
            existing = self.client.get_collections().collections
            return any(c.name == collection_name for c in existing)
        except Exception:
            return False

    def create_collection(self, collection_name: str = DEFAULT_COLLECTION):
        if self.collection_exists(collection_name):
            print(f"[QdrantService] Collection '{collection_name}' already exists, skipping.")
            return

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=VECTOR_SIZE,
                distance=Distance.COSINE
            )
        )
        print(f"[QdrantService] Created collection '{collection_name}'.")

    def delete_collection(self, collection_name: str):
        if self.collection_exists(collection_name):
            self.client.delete_collection(collection_name)
            print(f"[QdrantService] Deleted collection '{collection_name}'.")

    def upsert_chunk(self, chunk_id: int, vector: list, payload: dict,
                     collection_name: str = DEFAULT_COLLECTION):
        self.client.upsert(
            collection_name=collection_name,
            points=[
                PointStruct(
                    id=chunk_id,
                    vector=vector,
                    payload=payload
                )
            ]
        )

    def search(self, vector: list, limit=5, collection_name: str = DEFAULT_COLLECTION):
        results = self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_vectors=True
        ).points

        return results