from app.services.qdrant_sematinc_search_service import SemanticSearchService
from app.services.prompt_builder import PromptBuilder

class TalkToLLM:

    def chat(query: str):
        
        qdrant_service = SemanticSearchService()

        chunks: list = qdrant_service.search(query)

        prompt = PromptBuilder.build(query, chunks)

        return prompt