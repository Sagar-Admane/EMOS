from google import genai
from app.core.config import settings


class EmbeddingService:

    def __init__(self):
        # Use cloud Gemini client to avoid loading heavy local PyTorch models
        self.client = genai.Client(api_key=settings.api_key)

    def embedd(self, text: str) -> list[float]:
        response = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return response.embeddings[0].values