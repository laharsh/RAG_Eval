# Pinecone demo mode (optional)

P1 runs on **FAISS + OpenSearch** by default (free, local). Pinecone is for **demo / cloud vector** keyword on the resume.

## Status

- Config keys exist in `config.py` (`VECTOR_BACKEND=pinecone`).
- **Upsert + query wiring** is tracked in [TODO.md](../TODO.md) — implement before claiming Pinecone on resume.

## When you implement

1. `pip install pinecone-client` (or current SDK per Pinecone docs).
2. Add `src/pinecone_store.py`: upsert chunk ids + metadata on ingest; similarity search by embedding.
3. In `retriever.py`, when `VECTOR_BACKEND=pinecone`, use Pinecone instead of FAISS for the vector leg (keep BM25 + RRF).
4. Re-ingest once with `VECTOR_BACKEND=pinecone` in `.env`.
5. Add one README line under “Demo mode”.

See [FREE_TIER_BUDGET.md](../../projects-plan/FREE_TIER_BUDGET.md) — use Pinecone only for demos, not daily dev.
