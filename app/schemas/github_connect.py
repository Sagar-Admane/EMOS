from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ConnectRepoRequest(BaseModel):
    repo_full_name: str  # e.g. "sagar-admane/StockSync"


class ConnectRepoResponse(BaseModel):
    repo_id: int
    full_name: str
    status: str
    qdrant_collection: Optional[str] = None
    connected_at: datetime

    class Config:
        from_attributes = True


class RepoStatusResponse(BaseModel):
    repo_id: int
    full_name: str
    owner: str
    status: str
    qdrant_collection: Optional[str] = None
    error_message: Optional[str] = None
    connected_at: datetime
    indexed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RepoListItem(BaseModel):
    repo_id: int
    full_name: str
    owner: str
    description: Optional[str] = None
    visibility: str
    status: str
    qdrant_collection: Optional[str] = None
    connected_at: datetime
    indexed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
