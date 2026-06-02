from pydantic import BaseModel

class RepositoryResponseSchema(BaseModel):
    repository_id: int
    repository_name: str
    owner: str
    total_commits: int
    total_pull_requests: int
    total_contributors: int
    total_branches: int
    total_files: int