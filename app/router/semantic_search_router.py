from fastapi import APIRouter, Request
from app.services.qdrant_sematinc_search_service import SemanticSearchService

router = APIRouter()

@router.post("/semantic-search")
async def search(request: Request):
    body = await request.json()

    try:
        text = body.get("query")
        semantic_search = SemanticSearchService()

        semantic_search.search(text)

    except Exception as exec:
        print(exec)