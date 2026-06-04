from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams,
    Distance
)

class QdrantService:

    def __init__(self):
        self.client = QdrantClient(
            host="localhost",
            port=6333
        )

    def create_collection(self):

        self.client.recreate_collection(
            collection_name="code_chunks",
            vectors_config=VectorParams(
                size=768,
                distance=Distance.COSINE
            )
        )