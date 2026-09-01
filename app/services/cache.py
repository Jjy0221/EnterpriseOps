import hashlib
import json
import redis
from app.config import settings

# 缓存键版本段：fingerprint 定义或检索参数变化时递增，避免新旧语义键互串
CACHE_KEY_VERSION = "v1"


def _client():
    if not settings.enable_redis:
        return None
    return redis.Redis.from_url(settings.redis_url, decode_responses=True, protocol=2)


def compute_fingerprint(candidate_hits: list[dict]) -> str:
    """由 rerank 前的候选 hits 生成稳定的 retrieval fingerprint。

    只依赖 (document_id, chunk_id) 的组合，二者在全库唯一；
    与浮点 score、文本内容无关，因此排序变化、分数微调不会误失效缓存；
    而一旦新文档的 chunk 进入/离开候选集，集合变化，fingerprint 自动变化。
    """
    pairs = sorted(
        (str(hit.get("document_id", "")), str(hit.get("chunk_id", "")))
        for hit in candidate_hits
    )
    digest = hashlib.sha256(
        json.dumps(pairs, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return digest


def _key(question: str, fingerprint: str, top_k: int):
    q_digest = hashlib.sha256(question.strip().encode("utf-8")).hexdigest()
    return f"rag:{CACHE_KEY_VERSION}:{q_digest}:{fingerprint}:{top_k}"


def get_cache(question: str, fingerprint: str, top_k: int):
    client = _client()
    if client is None:
        return None
    value = client.get(_key(question, fingerprint, top_k))
    return json.loads(value) if value else None


def set_cache(question: str, fingerprint: str, top_k: int, data: dict):
    client = _client()
    if client is None:
        return
    client.setex(
        _key(question, fingerprint, top_k),
        settings.cache_ttl_seconds,
        json.dumps(data, ensure_ascii=False),
    )
