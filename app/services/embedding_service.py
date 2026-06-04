from sentence_transformers import SentenceTransformer

class EmbeddingService:

    def __init__(self):
        self.model = SentenceTransformer(
            "BAAI/bge-small-en-v1.5"
        )

    def embedd(self, text: str):
        return self.model.encode(
            text,
            normalize_embeddings=True
        ).tolist()