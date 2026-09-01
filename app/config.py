from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EnterpriseOps Copilot"

    milvus_uri: str = "http://localhost:19530"
    milvus_db: str = "enterpriseops"
    milvus_collection: str = "knowledge_chunks"

    embed_api_key: str = ""
    embed_base_url: str = ""
    embed_model_name: str = ""
    embed_dim: int = 1024
    embed_batch_size: int = 10

    chat_api_key: str = ""
    chat_base_url: str = ""
    chat_model_name: str = ""

    chunk_size: int = 400
    chunk_overlap: int = 80
    top_k: int = 5

    database_url: str = "sqlite:///./enterpriseops.db"

    enable_redis: bool = False
    redis_url: str = "redis://127.0.0.1:6379/0"
    cache_ttl_seconds: int = 60


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings():
    return Settings()


settings = get_settings()
