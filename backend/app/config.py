from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    app_name: str = "AI Interview Intelligence Platform"
    app_version: str = "1.0.0"
    debug: bool = False
    database_url: str
    # database_url: str = "postgresql://postgres:admin123@localhost:5432/interview-platform"
    allowed_origins: list[str] = ["http://localhost:3000"]
    max_upload_size_mb: int = 10
    upload_dir: str = "uploads"
    embedding_model: str = "all-MiniLM-L6-v2"
    similarity_threshold: float = 0.5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
