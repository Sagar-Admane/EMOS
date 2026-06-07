from fastapi import APIRouter, Request
from app.services.talk_to_llm import TalkToLLM
from fastapi.responses import PlainTextResponse

router = APIRouter()

@router.post("/semantic-search")
async def search(request: Request):
    body = await request.json()

    try:
        text = body.get("query")
        talk_to_llm_service = TalkToLLM()
        response = talk_to_llm_service.chat(text)

        return PlainTextResponse(response) 
    except Exception as exec:
        print(exec)