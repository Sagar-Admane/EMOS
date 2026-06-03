from pydantic import BaseModel

class CodeFile(BaseModel):
    file_id: int
    content: str
    language: str