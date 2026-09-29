"""
opensearch_store.py — BM25 keyword index (OpenSearch).

Used for hybrid retrieval: exact terms like "Article 5" match via BM25,
semantic questions match via FAISS — merged with RRF in retriever.py.
"""

from __future__ import annotations

import json
from typing import Any

from opensearchpy import OpenSearch, helpers
from opensearchpy.exceptions import NotFoundError

from src.config import (
    CHUNKS_REGISTRY_PATH,
    OPENSEARCH_HOST,
    OPENSEARCH_INDEX,
    OPENSEARCH_PORT,
)

INDEX_BODY = {
    "settings": {
        "index": {"number_of_shards": 1, "number_of_replicas": 0},
        "analysis": {"analyzer": {"default": {"type": "standard"}}},
    },
    "mappings": {
        "properties": {
            "chunk_id": {"type": "keyword"},
            "content": {"type": "text"},
            "source": {"type": "keyword"},
            "page": {"type": "integer"},
        }
    },
}


def get_client() -> OpenSearch:
    return OpenSearch(
        hosts=[{"host": OPENSEARCH_HOST, "port": OPENSEARCH_PORT}],
        http_compress=True,
        use_ssl=False,
        verify_certs=False,
        ssl_assert_hostname=False,
        ssl_show_warn=False,
    )


def is_available() -> bool:
    try:
        return get_client().ping()
    except Exception:
        return False


def ensure_index(client: OpenSearch | None = None) -> None:
    client = client or get_client()
    if not client.indices.exists(index=OPENSEARCH_INDEX):
        client.indices.create(index=OPENSEARCH_INDEX, body=INDEX_BODY)


def delete_index(client: OpenSearch | None = None) -> None:
    client = client or get_client()
    try:
        client.indices.delete(index=OPENSEARCH_INDEX)
    except NotFoundError:
        pass


def index_chunks(chunks: list[dict[str, Any]]) -> int:
    """
    Bulk-index chunks. Each dict: chunk_id, content, source, page.
    """
    client = get_client()
    delete_index(client)
    ensure_index(client)

    actions = [
        {
            "_index": OPENSEARCH_INDEX,
            "_id": c["chunk_id"],
            "_source": {
                "chunk_id": c["chunk_id"],
                "content": c["content"],
                "source": c["source"],
                "page": c["page"],
            },
        }
        for c in chunks
    ]
    success, _ = helpers.bulk(client, actions, refresh=True)
    return success


def bm25_search(question: str, k: int = 10) -> list[str]:
    """
    Return chunk_ids ranked by BM25 relevance to the question.

    Uses a standard OpenSearch pattern:
      - multi_match (bag of words / BM25)
      - match_phrase boost (prefer chunks where words appear together)

    Still no query rewriting or document-specific rules.
    """
    client = get_client()
    body = {
        "size": k,
        "query": {
            "bool": {
                "should": [
                    {
                        "multi_match": {
                            "query": question,
                            "fields": ["content^2", "source"],
                            "type": "best_fields",
                        }
                    },
                    {
                        "match_phrase": {
                            "content": {
                                "query": question,
                                "boost": 3.0,
                                "slop": 3,
                            }
                        }
                    },
                ],
                "minimum_should_match": 1,
            }
        },
    }
    resp = client.search(index=OPENSEARCH_INDEX, body=body)
    return [hit["_source"]["chunk_id"] for hit in resp["hits"]["hits"]]


def save_chunk_registry(chunks: list[dict[str, Any]]) -> None:
    CHUNKS_REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with CHUNKS_REGISTRY_PATH.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")


def load_chunk_registry() -> dict[str, dict[str, Any]]:
    if not CHUNKS_REGISTRY_PATH.exists():
        return {}
    registry: dict[str, dict[str, Any]] = {}
    with CHUNKS_REGISTRY_PATH.open(encoding="utf-8") as f:
        for line in f:
            c = json.loads(line)
            registry[c["chunk_id"]] = c
    return registry
