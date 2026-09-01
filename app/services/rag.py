import json
import re

from langchain_core.messages import HumanMessage, SystemMessage

from app.services.embedding import get_embedding_model
from app.services.llm import get_chat_model
from app.services.milvus_store import search
from app.services.reranker import rerank

DEFAULT_CANDIDATE_K = 10

# grounded=false 时后端统一返回的拒答文本，不把模型推测内容直接透出
REFUSAL_TEXT = "根据当前知识库无法确定。"

SYSTEM_PROMPT = (
    "你是企业知识库问答助手。"
    "只能根据提供的上下文回答。"
    "如果上下文不足、无法依据知识库确定答案，请回答：根据当前知识库无法确定。"
    "你必须以 JSON 对象形式输出，格式为："
    '{"answer": "你的回答", "grounded": true 或 false}'
    "grounded 表示你是否基于上下文给出了有知识依据的回答。"
    "当 grounded 为 false 时，answer 必须严格为：根据当前知识库无法确定。"
)


def retrieve(question: str, top_k: int = 5):
    query_vector = get_embedding_model().embed_query(question)
    results = search(query_vector=query_vector, limit=top_k)

    hits = []
    for hit in results:
        entity = hit["entity"]
        hits.append(
            {
                "score": float(hit["distance"]),
                "text": entity["text"],
                "source": entity.get("source", "unknown"),
                "chunk_id": entity.get("chunk_id", "unknown"),
                "document_id": entity.get("document_id", ""),
            }
        )
    return hits


def retrieve_with_rerank(
    question: str,
    top_k: int = 5,
    candidate_k: int = DEFAULT_CANDIDATE_K,
):
    candidate_hits = retrieve(
        question,
        top_k=candidate_k,
    )
    return rerank(
        question,
        candidate_hits,
        top_n=top_k,
    )


def retrieve_candidates(question: str, candidate_k: int = DEFAULT_CANDIDATE_K):
    """仅做 embedding + Milvus candidate retrieval，供缓存指纹与后续拼装使用。"""
    return retrieve(question, top_k=candidate_k)


def complete_answer(question: str, candidate_hits: list, top_k: int = 5):
    """给定候选 hits，执行 rerank + final LLM，返回 answer / sources / grounded。"""
    reranked_hits = rerank(
        question,
        candidate_hits,
        top_n=top_k,
    )

    context_blocks = []
    sources = []

    for i, hit in enumerate(reranked_hits, 1):
        context_blocks.append(
            f"[片段{i} | chunk_id={hit['chunk_id']} | source={hit['source']}]\n"
            f"{hit['text']}"
        )
        sources.append(
            {
                "rank": i,
                "chunk_id": hit["chunk_id"],
                "source": hit["source"],
                "vector_score": hit["score"],
            }
        )

    context = "\n\n".join(context_blocks)

    user_prompt = (
        f"问题：\n{question}\n\n"
        f"上下文：\n{context}\n"
    )

    result = get_chat_model().invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    answer, grounded = _parse_grounded_answer(result.content)

    if grounded is False:
        answer = REFUSAL_TEXT

    return {
        "answer": answer,
        "sources": sources,
        "grounded": grounded,
    }


def _parse_grounded_answer(content: str):
    """解析 final LLM 的 JSON verdict。

    返回 (answer, grounded)：
    - grounded=True  → 有知识依据的回答，可正常缓存
    - grounded=False → 拒答（后端统一覆盖为 REFUSAL_TEXT），不缓存
    - grounded=None  → JSON / grounded 解析失败，保守策略：不缓存、不默认 grounded=True
    """
    if not isinstance(content, str):
        return REFUSAL_TEXT, None

    text = content.strip()

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            parsed = json.loads(match.group())
        except json.JSONDecodeError:
            parsed = None
        if (
            isinstance(parsed, dict)
            and "answer" in parsed
            and "grounded" in parsed
            and isinstance(parsed["grounded"], bool)
        ):
            return str(parsed["answer"]).strip(), parsed["grounded"]

    # 解析失败：尝试从原文中 salvage answer 字段，grounded 视为未知（不缓存）
    answer_match = re.search(r'"answer"\s*:\s*"((?:[^"\\]|\\.)*)"', text)
    if answer_match:
        return answer_match.group(1), None

    return REFUSAL_TEXT, None
