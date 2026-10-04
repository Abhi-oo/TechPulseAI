from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "TechPulse AI"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    BACKEND_HOST: str = "0.0.0.0"
    BACKEND_PORT: int = 8000

    # Supabase / DB Configuration
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # AI Configuration
    GEMINI_API_KEY: Optional[str] = None

    # Pipeline Security
    PIPELINE_SECRET_KEY: str = "dev-secret-change-me"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
