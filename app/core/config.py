from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    database_url: str = Field(validation_alias="DATABASE_URL")
    github_client: str = Field(validation_alias="GITHUB_CLIENT_ID")
    github_secret: str = Field(validation_alias="GITHUB_CLIENT_SECRET")

    github_token: str = Field(validation_alias="GITHUB_TOKEN")

    api_key: str = Field(validation_alias="GEMINI_API_KEY")

settings = Settings()