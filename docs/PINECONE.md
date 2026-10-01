# Pinecone — managed vector database (cloud leg)

**Why Pinecone after FAISS:** FAISS is an in-process index (great for dev and Docker demos). **Pinecone** is a hosted vector DB—what many teams use when they need scale, uptime, and metadata filters without operating disk indexes.

Config: `VECTOR_BACKEND=pinecone` in `.env` (see `config.py`).

## Implementation checklist

1. `pip install pinecone-client` (or current SDK per Pinecone docs).
2. Add `src/pinecone_store.py`: upsert chunk ids + metadata on ingest; similarity search by embedding.
3. In `retriever.py`, when `VECTOR_BACKEND=pinecone`, use Pinecone instead of FAISS for the vector leg (keep BM25 + RRF).
4. Re-ingest once with `VECTOR_BACKEND=pinecone` in `.env`.
5. Add one README line under “Demo mode”.

See [FREE_TIER_BUDGET.md](../../projects-plan/FREE_TIER_BUDGET.md) — use Pinecone only for demos, not daily dev.
