from google import genai
from google.genai import types

from app.services.qdrant_sematinc_search_service import SemanticSearchService
from app.services.prompt_builder import PromptBuilder
from app.core.config import settings

class TalkToLLM:

    def __init__(self):
        self.client = genai.Client(api_key=settings.api_key)

    def chat(self,query: str):
        
        qdrant_service = SemanticSearchService()

        chunks: list = qdrant_service.search(query)

        prompt = PromptBuilder.build(query, chunks)

        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0,
                top_p=0.60,
                top_k=20
            )
        )

        return response.text