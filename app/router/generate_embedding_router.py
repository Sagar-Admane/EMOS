from fastapi import APIRouter
from app.db.session import SessionLocal
from app.services.embedding_ingestion_service import EmbeddingIngestionService
router = APIRouter()

@router.get("/generate-code-chunk")
def generate_embedding():
    db = SessionLocal()

    embedding_service = EmbeddingIngestionService()
    response = embedding_service.generate_embedding(db)

    return response

