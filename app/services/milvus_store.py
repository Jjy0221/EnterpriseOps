from functools import lru_cache
from pymilvus import MilvusClient
from app.config import settings


@lru_cache
def get_client():
    client = MilvusClient(settings.milvus_uri)

    if settings.milvus_db not in client.list_databases():
        client.create_database(db_name=settings.milvus_db)

    client.use_database(db_name=settings.milvus_db)

    if not client.has_collection(collection_name=settings.milvus_collection):
        client.create_collection(
            collection_name=settings.milvus_collection,
            dimension=settings.embed_dim,
            metric_type="COSINE",
        )

    return client


def upsert_records(records):
    client = get_client()
    result = client.upsert(
        collection_name=settings.milvus_collection,
        data=records,
    )
    client.flush(collection_name=settings.milvus_collection)
    return result


def search(query_vector, limit):
    client = get_client()
    results = client.search(
        collection_name=settings.milvus_collection,
        data=[query_vector],
        limit=limit,
        output_fields=["text", "source", "chunk_id", "document_id"],
    )
    return results[0]
