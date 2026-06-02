from pydantic import BaseModel

class ContributorAnalyticsSchema(BaseModel):
    username: str
    contributions: int