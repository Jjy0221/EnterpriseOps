from pathlib import Path
from uuid import uuid4

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config import settings
from app.services.embedding import get_embedding_model
from app.services.milvus_store import upsert_records


def load_documents(path: Path):
    if path.suffix.lower() == ".txt":
        return TextLoader(str(path), encoding="utf-8").load()
    if path.suffix.lower() == ".pdf":
        return PyPDFLoader(str(path)).load()
    raise ValueError("暂时只支持 txt / pdf")


def ingest(path: Path):
    document_id = str(uuid4())
    documents = load_documents(path)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
        separators=["\n\n", "\n", "。", "，", " ", ""],
    )
    chunks = splitter.split_documents(documents)

    texts = [chunk.page_content for chunk in chunks]
    vectors = get_embedding_model().embed_documents(texts)

    records = []
    for i, chunk in enumerate(chunks):
        records.append(
            {
                "id": uuid4().int % (2**63 - 1),
                "vector": vectors[i],
                "text": chunk.page_content,
                "source": str(path),
                "chunk_id": i,
                "document_id": document_id,
            }
        )


    result = upsert_records(records)
    return {
        "document_id": document_id,
        "chunk_count": len(chunks),
        "upsert_result": str(result),
    }
