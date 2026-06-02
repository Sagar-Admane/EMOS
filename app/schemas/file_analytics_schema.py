from pydantic import BaseModel

class FileAnalyticsSchema(BaseModel):
    file_path: str
    changes: int