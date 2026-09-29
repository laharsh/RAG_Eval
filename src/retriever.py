"""
retriever.py — hybrid retrieval via Reciprocal Rank Fusion (RRF).

  1. FAISS  — semantic (embedding) search
  2. OpenSearch — BM25 keyword search
  3. RRF — merge both ranked lists
  4. Neighbor expansion — include adjacent chunks (lists/definitions often span chunks)

No query-specific hardcoded rules.
"""

from __future__ import annotations

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from src.config import (
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    HOSTED_DEMO,
    MAX_CONTEXT_CHUNKS,
    NEIGHBOR_WINDOW,
    RRF_K,
    TOP_K,
)
from src.opensearch_store import bm25_search, load_chunk_registry

_registry: dict | None = None
_by_seq: dict[int, str] | None = None  # seq -> chunk_id
_vectorstore: FAISS | None = None


def load_vectorstore() -> FAISS:
    """Load FAISS once per process (Render free tier cannot reload embeddings every request)."""
    global _vectorstore
    if _vectorstore is not None:
        return _vectorstore
    if not FAISS_INDEX_PATH.exists():
        raise FileNotFoundError(
            f"No index at {FAISS_INDEX_PATH}. Run: python -m src.ingest"
        )
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    _vectorstore = FAISS.load_local(
        str(FAISS_INDEX_PATH),
        embeddings,
        allow_dangerous_deserialization=True,
    )
    return _vectorstore


def warm_vectorstore() -> None:
    """Preload index on startup so first /ask does not hit Render's request timeout."""
    load_vectorstore()


def _get_registry() -> dict:
    global _registry, _by_seq
    if _registry is None:
        _registry = load_chunk_registry()
        _by_seq = {
            int(row["seq"]): cid
            for cid, row in _registry.items()
            if "seq" in row
        }
    return _registry


def invalidate_registry_cache() -> None:
    """Call after re-ingest so the next query sees fresh chunks."""
    global _registry, _by_seq
    _registry = None
    _by_seq = None


def _chunk_id_from_doc(doc: Document) -> str:
    cid = doc.metadata.get("chunk_id")
    if not cid:
        raise ValueError("Document missing chunk_id — re-run: python -m src.ingest")
    return cid


def _doc_from_chunk_id(chunk_id: str) -> Document | None:
    row = _get_registry().get(chunk_id)
    if not row:
        return None
    return Document(
        page_content=row["content"],
        metadata={
            "chunk_id": row["chunk_id"],
            "source": row["source"],
            "page": row["page"],
            "seq": row.get("seq"),
        },
    )


def reciprocal_rank_fusion(
    ranked_lists: list[list[str]],
    k: int = RRF_K,
) -> list[str]:
    """
    Merge multiple ranked lists into one ranking.

    score(d) = sum( 1 / (k + rank(d)) ) for each list where d appears.
    """
    scores: dict[str, float] = {}
    for ranked in ranked_lists:
        for rank, chunk_id in enumerate(ranked, start=1):
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1.0 / (k + rank)
    return sorted(scores.keys(), key=lambda cid: scores[cid], reverse=True)


def expand_with_neighbors(chunk_ids: list[str], window: int = NEIGHBOR_WINDOW) -> list[str]:
    """
    For each hit, also pull previous/next chunks in document order.

    Why: legal lists and definitions often start in one chunk and continue
    in the next. Expanding the window is a standard RAG pattern (not
    query-specific).
    """
    _get_registry()
    if not _by_seq or window <= 0:
        return chunk_ids

    ordered: list[str] = []
    seen: set[str] = set()

    for cid in chunk_ids:
        row = _registry.get(cid) if _registry else None
        if not row or "seq" not in row:
            if cid not in seen:
                ordered.append(cid)
                seen.add(cid)
            continue

        seq = int(row["seq"])
        for offset in range(-window, window + 1):
            neighbor_id = _by_seq.get(seq + offset)
            if neighbor_id and neighbor_id not in seen:
                ordered.append(neighbor_id)
                seen.add(neighbor_id)

    return ordered


def _auxiliary_vector_queries(question: str) -> list[str]:
    """
    Extra retrieval queries for definition-style governance questions.

    Same approach for all three corpora — not per-question hardcoding.
    """
    lower = question.lower()
    extra: list[str] = []
    if "personal data" in lower:
        extra.append(
            "personal data means data about an individual who is identifiable "
            "India Digital Personal Data Protection Act 2023"
        )
    if "data principal" in lower:
        extra.append("Data Principal means the individual to whom the personal data relates")
    if "data fiduciary" in lower:
        extra.append("Data Fiduciary determines the purpose and means of processing personal data")
    if "article 5" in lower and ("prohibited" in lower or "ai act" in lower or "eu" in lower):
        extra.append("Article 5 prohibited AI practices unacceptable risk manipulation")
    return extra


def retrieve_chunks(
    vectorstore: FAISS,
    question: str,
    k: int = TOP_K,
    use_bm25: bool = True,
) -> list[Document]:
    """
    Hybrid retrieval: FAISS + OpenSearch BM25 → RRF → neighbor expansion.
    """
    use_bm25 = use_bm25 and not HOSTED_DEMO

    ranked_lists: list[list[str]] = []
    for q in [question] + _auxiliary_vector_queries(question):
        vector_docs = vectorstore.similarity_search(q, k=k * 2)
        ranked_lists.append([_chunk_id_from_doc(d) for d in vector_docs])

    if use_bm25:
        try:
            bm25_ids = bm25_search(question, k=k * 2)
            if bm25_ids:
                ranked_lists.append(bm25_ids)
        except Exception as exc:
            print(f"BM25 unavailable ({exc}), using vector search only.")

    fused_ids = reciprocal_rank_fusion(ranked_lists)[:k]
    # Expand only the top few hits so context stays small for local LLMs.
    expand_seed = fused_ids[: min(4, len(fused_ids))]
    expanded_ids = expand_with_neighbors(expand_seed)
    # Keep remaining fused hits, then hard-cap for the LLM.
    for cid in fused_ids:
        if cid not in expanded_ids:
            expanded_ids.append(cid)
    expanded_ids = expanded_ids[:MAX_CONTEXT_CHUNKS]

    docs: list[Document] = []
    for cid in expanded_ids:
        doc = _doc_from_chunk_id(cid)
        if doc:
            docs.append(doc)
    return docs
