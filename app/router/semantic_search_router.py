from fastapi import APIRouter, Request
from app.services.talk_to_llm import TalkToLLM

router = APIRouter()

@router.post("/semantic-search")
async def search(request: Request):
    body = await request.json()

    try:
        text = body.get("query")
        prompt = TalkToLLM.chat(text)

        return prompt 
    except Exception as exec:
        print(exec)