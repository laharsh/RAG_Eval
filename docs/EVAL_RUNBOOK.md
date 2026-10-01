# Evaluation runbook — 50 golden questions

Run on your machine when retrieval, chunking, or LLM settings change.

### Why RAGAS feels slow (and uses many Groq calls)

1. **Phase A — 50× `ask()`** — full RAG + **answer generation** (Groq if `LLM_PROVIDER=groq`).
2. **Phase B — RAGAS judge** — progress bar **150** ≈ **50 questions × 3 metrics** (faithfulness, answer relevancy, context precision). Each step calls the **judge** LLM (~5–10 s/step → **~15–25 min** total is normal).

So **50 Q RAGAS + Groq judge** is heavy on the **free tier** (RPM/TPM/daily caps). Watch https://console.groq.com/settings/limits.

**Safer patterns:**

| Goal | Command |
|------|---------|
| Quick sanity check | `python -m src.eval --limit 5 --ragas-only --judge groq` |
| Resume table (balanced) | `python -m src.eval --limit 20 --ragas-only --judge groq` |
| Full 50 Q, save Groq for answers only | `LLM_PROVIDER=groq` + `python -m src.eval --ragas-only --judge ollama` (needs Ollama) |
| Full 50 Q, all Groq | Run off-peak; set `GROQ_RAGAS_MAX_WORKERS=1` in `.env` to reduce rate-limit spikes |

If Groq returns **429** / rate limit: stop, wait 15–60 min, retry with `--limit 10` or lower workers.

## Setup

```powershell
cd rag-eval-platform
.\.venv\Scripts\activate
pip install -r requirements-eval.txt
docker compose up -d   # optional; hybrid retrieval
```

Ensure `.env` has a working LLM for `--keyword-only` and `--ragas-only` (recommend `LLM_PROVIDER=groq` + `GROQ_API_KEY`).

## Standard suite (update README table after)

```powershell
# 1) Retrieval only — 50 Q, no generation
python -m src.eval --retrieval-only

# 2) Full RAG + answer keyword check — 50 Q
python -m src.eval --keyword-only

# 3) RAGAS — 50 Q (writes eval_report.json)
python -m src.eval --ragas-only --judge groq
```

Copy key metrics from terminal output or `eval_report.json` into **README → Evaluation results**.

## Chunking A/B

```powershell
# A — bad
$env:CHUNK_SIZE="1000"
$env:CHUNK_OVERLAP="0"
python -m src.ingest
python -m src.eval --ragas-only --judge groq
Copy-Item eval_report.json eval_report_chunk1000.json

# B — good (defaults)
$env:CHUNK_SIZE="512"
$env:CHUNK_OVERLAP="64"
python -m src.ingest
python -m src.eval --ragas-only --judge groq
Copy-Item eval_report.json eval_report_chunk512.json
```

Add a small comparison table to README (faithfulness + context_precision).

## What not to commit

- `.env`
- Large scratch logs

Do commit: `eval_report.json`, `eval_report_chunk512.json`, etc., if you want reviewers to see frozen numbers.
