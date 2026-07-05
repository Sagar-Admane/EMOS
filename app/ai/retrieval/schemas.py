from pydantic import BaseModel, Field
from app.ai.router.enums import DataSource

class RetrievalMetadata(BaseModel):
    data: dict[str, any] = Field(default_factory=1)

class RetrievedDocument(BaseModel):
    source: DataSource
    document_type: str
    title: str
    content: str
    metadata: RetrievalMetadata = Field(default_factory=RetrievalMetadata)
    score: float | None = None

class RetrievalStatistics(BaseModel):
    total_documents: int = 0
    sources_used: list[DataSource] = Field(default_factory=list)
    retrieval_time_ms: float = 0

class RetrievalError(BaseModel):
    source: DataSource
    message: str
    retryable: bool = False

class RetrievalResult(BaseModel):
    documents: list[RetrievedDocument]
    statistics: RetrievalStatistics
    errors: list[RetrievalError]