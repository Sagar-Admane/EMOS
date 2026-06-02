from pydantic import BaseModel
from datetime import datetime

class RepositoryActivityAnalyticsSchema(BaseModel):
    total_commits: int
    first_commit: datetime | None
    last_commit: datetime | None
    active_days: int
    avg_commit_per_day: float