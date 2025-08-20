import os
from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    APP_ENV: str = "development"
    MONGO_URI: AnyUrl | str = "mongodb://mongo:27017"
    MONGO_DB_NAME: str = "money_manager"
    JWT_SECRET: str = "change-me-in-prod"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    RATE_LIMIT: str = "100/minute"
    CORS_ALLOW_ORIGINS: List[str] = ["*"]

settings = Settings()
