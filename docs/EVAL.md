# Evaluation (Phase 4)

## Why evaluate?

Reviewers ask: **"How do you know your RAG is good?"**  
Answer: golden questions + keyword regression + RAGAS metrics.

```text
golden_qa.json (50 questions)
        │
        ▼
   run RAG (ask)
        │
        ├─► Keyword score  (free, fast)     → pass rate
        └─► RAGAS (optional, slower)        → faithfulness, relevancy, context_precision
                │
                ▼
         eval_report.json
```

---

## Commands

```bash
# Fastest: retrieval only (no LLM — works if Ollama/CUDA is broken)
python -m src.eval --limit 10 --retrieval-only

# Fast smoke: 10 questions, answer keyword regression
python -m src.eval --limit 10 --keyword-only

# Full keyword suite (50 questions)
python -m src.eval --keyword-only

# RAGAS metrics (Ollama judge — saves Groq)
python -m src.eval --limit 10 --ragas --judge ollama

# RAGAS only (skip keyword re-run; uses cached answers)
python -m src.eval --limit 10 --ragas-only --judge groq

# Groq models (llama-3.1-8b-instant deprecated Aug 2026):
#   GROQ_MODEL=openai/gpt-oss-20b
#   GROQ_RAGAS_MODEL=openai/gpt-oss-20b
#   GROQ_RAGAS_REASONING_EFFORT=low
# If judge still times out: GROQ_RAGAS_MAX_WORKERS=1
```

Install RAGAS deps once (pinned — avoids vertexai import crash):

```bash
pip install -r requirements-eval.txt
```

---

## Metrics (plain English)

| Metric | Meaning |
|--------|---------|
| **Keyword pass rate** | Did the answer contain ≥ half of the expected keywords? |
| **Faithfulness** | Is the answer supported by retrieved context (no hallucination)? |
| **Answer relevancy** | Does the answer address the question? |
| **Context precision** | Are the retrieved chunks actually useful? |

---

## Free-tier tip

- Develop with `--keyword-only` or `--ragas --judge ollama`
- Run Groq judge **once** for the README metric table
- Answers are cached in `.cache/` so re-runs reuse LLM outputs
