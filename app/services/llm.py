from functools import lru_cache
from langchain_openai import ChatOpenAI
from app.config import settings


@lru_cache
def get_chat_model():
    if not settings.chat_api_key:
        raise RuntimeError("请先在 .env 配置 CHAT_API_KEY")

    return ChatOpenAI(
        model=settings.chat_model_name,
        api_key=settings.chat_api_key,
        base_url=settings.chat_base_url,
        temperature=0.1,
    )
