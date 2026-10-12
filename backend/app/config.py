from __future__ import annotations

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Retail Sales Opportunity Propensity"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    model_dir: str = "backend/models"
    data_dir: str = "backend/data"
    log_level: str = "INFO"
    secret_key: str = "change_me"

    class Config:
        env_file = ".env"


settings = Settings()
