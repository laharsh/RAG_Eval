# Architecture — Beginner's Guide (Phase 2)

## Hybrid retrieval (the proper fix)

Pure vector search fails when:
- The question says **"Article 5"** but embeddings don't align with the right chunk
- Keywords matter more than meaning (legal references, acronyms, section numbers)

**Solution:** run two searches and merge with **Reciprocal Rank Fusion (RRF)**:

```text
                    ┌─── FAISS (semantic) ───┐
Question ──────────┤                        ├──► RRF merge ──► top 5 chunks
                    └─── OpenSearch (BM25) ─┘
```

No hardcoded rules per question. Same code for every query.

### RRF in one sentence

If a chunk ranks high in **both** lists, it gets a higher combined score than a chunk that only appears in one.

---

## Data flow

```text
INGEST (once):
  PDF → normalize text → chunks → chunk_id
                              ├─► FAISS (embeddings)
                              ├─► OpenSearch (BM25 index)
                              └─► chunks.jsonl (registry)

QUERY (each question):
  question → FAISS top 10 ──┐
  question → BM25 top 10  ──┼──► RRF → top 5 → LLM → answer + sources
```

---

## File map

| File | Role |
|------|------|
| `docker-compose.yml` | OpenSearch server |
| `src/opensearch_store.py` | BM25 index + search |
| `src/retriever.py` | FAISS + BM25 + RRF |
| `src/text_utils.py` | Ingest-time PDF cleanup only |
| `src/api.py` | REST API (`/health`, `/ask`, `/ingest`) |
| `src/eval.py` | Keyword regression + RAGAS evaluation |
| `golden_qa.json` | 50 fixed Q&A checks for regression |
| `data/processed/chunks.jsonl` | Chunk registry (id → text) |

---

## Evaluation flow (Phase 4)

```text
golden_qa.json → ask() for each question
                      ├─ keyword pass rate
                      └─ RAGAS (faithfulness, relevancy, context_precision)
                              → eval_report.json
```

---

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Status + whether OpenSearch is connected |
| POST | `/ask` | `{"question": "..."}` → answer + sources |
| POST | `/ingest` | Re-index all PDFs |
