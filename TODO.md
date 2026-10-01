# Project 1 close-out — tracking

> **Purpose:** Finish packaging before calling P1 “done” on resume/GitHub.  
> **Not blocking:** Project 2 work can continue in parallel.  
> **Last updated:** 2026-03-23

---

## Status snapshot (fill README from here when done)

| Eval run | Questions | Faithfulness | Answer relevancy | Context precision | Notes |
|----------|-----------|--------------|------------------|-------------------|--------|
| RAGAS (Groq judge) | 50 | **0.44** | **0.86** | **0.27** | `eval_summary.json` |
| Keyword (full RAG) | 50 | — | — | — | **80%** pass, avg 0.76 |

**Commands to refresh metrics:**

```powershell
python -m src.eval --limit 10 --keyword-only
python -m src.eval --limit 10 --ragas-only --judge groq
# Final snapshot (once, saves Groq quota):
python -m src.eval --ragas-only --judge groq
```

---

## Checklist

### Demo & docs

- [x] **`scripts/demo.ps1` / `demo.sh`** — Loom curl sequence
- [x] **README metric table** — snapshot from `eval_report.json` (re-run before final resume)
- [x] **`docs/INTEGRATION.md`** — link to P2
- [ ] **`docs/ARCHITECTURE.md`** — confirm diagram matches hybrid RRF flow (quick read-through)

### Resume & GitHub

- [ ] **Resume bullets** — replace placeholders with real numbers (see template below)
- [ ] **2-min demo video** — record Loom (hosted UI + 3 questions); link in README
- [x] **Deploy path** — Dockerfile + `demo-ui` + [docs/DEPLOY.md](docs/DEPLOY.md)
- [x] **GitHub push** — https://github.com/laharsh/RAG_Eval (merge resolved placeholder README)

### Engineering (planned, not skipped)

- [ ] **Pinecone backend** — implement per [docs/PINECONE.md](docs/PINECONE.md) ([FREE_TIER_BUDGET.md](../projects-plan/FREE_TIER_BUDGET.md))
- [ ] **Before/after chunking comparison** — run RAGAS twice:
  - [ ] **Bad:** `CHUNK_SIZE=1000`, `CHUNK_OVERLAP=0` → re-ingest → save `eval_report_chunk1000.json`
  - [ ] **Good:** `CHUNK_SIZE=512`, `CHUNK_OVERLAP=64` (current) → re-ingest → save `eval_report_chunk512.json`
  - [ ] **README table** — show faithfulness / context_precision delta

### Optional polish (nice for interviews)

- [ ] Dedupe repeated sources in `/ask` response
- [ ] Cache embeddings / vectorstore load (faster API)
- [ ] Full **50-question** RAGAS run for final resume number (one Groq session)

---

## Resume bullet template (copy when checklist above is done)

```text
• Built hybrid RAG (FAISS + OpenSearch BM25 + RRF) over EU AI Act, NIST AI RMF, and India DPDP;
  RAGAS faithfulness X / answer relevancy Y on N golden Q&A pairs (Groq judge).
• Implemented 50-question golden eval harness (keyword regression + RAGAS) and FastAPI API with
  source citations; deployed locally via Docker Compose (OpenSearch).
```

Replace **X**, **Y**, **N** from final `eval_report.json` and keyword pass rate.

---

## Demo script outline (for `scripts/demo.sh`)

1. `docker compose up -d` (OpenSearch)
2. `GET /health`
3. `POST /ask` — Article 5 EU AI Act
4. `POST /ask` — NIST four functions
5. `POST /ask` — India DPDP personal data
6. (Optional) `python -m src.eval --limit 3 --retrieval-only` — show pass rate in terminal

---

## Done when

- [ ] All items in **Checklist** checked (except optional polish)
- [ ] README links to demo video
- [ ] You are comfortable walking a recruiter through the repo in 5 minutes
