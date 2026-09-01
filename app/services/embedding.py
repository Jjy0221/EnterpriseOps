from functools import lru_cache
from langchain_openai import OpenAIEmbeddings
from app.config import settings


@lru_cache
def get_embedding_model():
    if not settings.embed_api_key:
        raise RuntimeError("请先在 .env 配置 EMBED_API_KEY")

    return OpenAIEmbeddings(
        model=settings.embed_model_name,
        api_key=settings.embed_api_key,
        base_url=settings.embed_base_url,
        dimensions=settings.embed_dim,
        check_embedding_ctx_length=False,
        chunk_size=settings.embed_batch_size,
        model_kwargs={"encoding_format" : "float",},
    )
