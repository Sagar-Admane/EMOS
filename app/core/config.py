from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = Field(validation_alias="DATABASE_URL")
    github_client: Optional[str] = Field(validation_alias="GITHUB_CLIENT_ID")
    github_secret: Optional[str] = Field(validation_alias="GITHUB_CLIENT_SECRET")

    github_token: str = Field(validation_alias="GITHUB_TOKEN")

    api_key: str = Field(validation_alias="GEMINI_API_KEY")

    neo4j_uri: str = Field(validation_alias="NEO4J_URI")
    neo4j_username: str = Field(validation_alias="NEO4J_USERNAME")
    neo4j_password: str = Field(validation_alias="NEO4J_PASSWORD")

    qdrant_host: str = Field(validation_alias="QDRANT_HOST")
    qdrant_api: str = Field(validate_alias="QDRANT_API_KEY")

settings = Settings()