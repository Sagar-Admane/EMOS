from pydantic import BaseModel

class FileOwnershipAnalyticsSchema(BaseModel):
    file_path: str
    owner: str
    changes: int