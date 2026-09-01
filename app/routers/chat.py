from fastapi import APIRouter
from app.schemas import ChatRequest
from app.services.cache import compute_fingerprint, get_cache, set_cache
from app.services.rag import (
    DEFAULT_CANDIDATE_K,
    complete_answer,
    retrieve_candidates,
)


router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
def chat(req: ChatRequest):
    # embedding + Milvus candidate retrieval：每次必跑，用于生成缓存指纹
    candidate_hits = retrieve_candidates(req.question, candidate_k=DEFAULT_CANDIDATE_K)
    fingerprint = compute_fingerprint(candidate_hits)

    cached = get_cache(req.question, fingerprint, req.top_k)

    if cached is not None:
        cached["cached"] = True
        return cached

    result = complete_answer(req.question, candidate_hits, top_k=req.top_k)

    # 仅 grounded=true（有知识依据）的结果进入缓存；
    # grounded=false / 解析失败（None）一律不缓存，避免拒答长期滞留。
    if result.get("grounded") is True:
        set_cache(req.question, fingerprint, req.top_k, result)

    result["cached"] = False
    return result
