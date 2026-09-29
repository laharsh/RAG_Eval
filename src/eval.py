"""
eval.py — evaluate the RAG pipeline (Phase 4).

Layers:

  1) Retrieval keyword check  — no LLM (works even if Ollama/GPU is broken)
  2) Answer keyword regression — needs LLM (Ollama or Groq)
  3) RAGAS metrics            — optional, needs judge LLM

Usage:
    # Fastest: retrieval only (no LLM, no CUDA)
    python -m src.eval --limit 10 --retrieval-only

    # Answer keywords (needs working LLM)
    python -m src.eval --limit 10 --keyword-only

    # RAGAS on 10 Q
    python -m src.eval --limit 10 --ragas --judge ollama
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from src.config import ROOT
from src.opensearch_store import is_available
from src.rag_chain import ask, path_label
from src.retriever import load_vectorstore, retrieve_chunks

GOLDEN_PATH = ROOT / "golden_qa.json"
REPORT_PATH = ROOT / "eval_report.json"


def load_golden(path: Path = GOLDEN_PATH) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def keyword_score(text: str, expected: list[str]) -> dict:
    """
    Fraction of expected keywords found in text (case-insensitive).
    """
    lower = text.lower()
    hits = [kw for kw in expected if kw.lower() in lower]
    return {
        "hits": hits,
        "misses": [kw for kw in expected if kw.lower() not in lower],
        "score": len(hits) / len(expected) if expected else 0.0,
        "pass": len(hits) >= max(1, (len(expected) + 1) // 2),  # ≥ half keywords
    }


def run_retrieval_eval(items: list[dict]) -> dict:
    """
    Score whether retrieved chunks contain expected keywords.
    Does NOT call the LLM — safe when Ollama/CUDA is down.
    """
    vectorstore = load_vectorstore()
    use_bm25 = is_available()
    rows = []
    passed = 0
    total_score = 0.0

    print(f"Retrieval mode: {'hybrid BM25+FAISS' if use_bm25 else 'FAISS only'}")

    for i, item in enumerate(items, 1):
        q = item["question"]
        print(f"[{i}/{len(items)}] {q[:70]}...")
        t0 = time.time()
        chunks = retrieve_chunks(vectorstore, q, use_bm25=use_bm25)
        elapsed = time.time() - t0

        context_text = "\n".join(c.page_content for c in chunks)
        kw = keyword_score(context_text, item["expected_answer_contains"])
        if kw["pass"]:
            passed += 1
        total_score += kw["score"]

        sources = [
            {
                "source": path_label(c.metadata.get("source", "")),
                "page": c.metadata.get("page"),
            }
            for c in chunks
        ]
        rows.append(
            {
                "id": item["id"],
                "theme": item.get("theme"),
                "question": q,
                "sources": sources,
                "keyword": kw,
                "seconds": round(elapsed, 2),
            }
        )
        print(f"    retrieval_keyword={kw['score']:.2f} pass={kw['pass']} ({elapsed:.1f}s)")

    return {
        "mode": "retrieval_keyword",
        "n": len(items),
        "pass_rate": passed / len(items) if items else 0.0,
        "avg_keyword_score": total_score / len(items) if items else 0.0,
        "rows": rows,
    }


def run_keyword_eval(items: list[dict]) -> dict:
    rows = []
    passed = 0
    total_score = 0.0

    for i, item in enumerate(items, 1):
        q = item["question"]
        print(f"[{i}/{len(items)}] {q[:70]}...")
        t0 = time.time()
        result = ask(q)
        elapsed = time.time() - t0

        kw = keyword_score(result["answer"], item["expected_answer_contains"])
        if kw["pass"]:
            passed += 1
        total_score += kw["score"]

        rows.append(
            {
                "id": item["id"],
                "theme": item.get("theme"),
                "question": q,
                "answer": result["answer"][:500],
                "sources": result["sources"],
                "keyword": kw,
                "seconds": round(elapsed, 2),
            }
        )
        print(f"    answer_keyword={kw['score']:.2f} pass={kw['pass']} ({elapsed:.1f}s)")

    return {
        "mode": "answer_keyword",
        "n": len(items),
        "pass_rate": passed / len(items) if items else 0.0,
        "avg_keyword_score": total_score / len(items) if items else 0.0,
        "rows": rows,
    }


def run_ragas_eval(items: list[dict], judge: str = "ollama") -> dict:
    """
    Run RAGAS metrics. Requires: pip install ragas datasets langchain-ollama
    Judge LLM defaults to Ollama to protect Groq free tier.
    """
    try:
        from datasets import Dataset
        from ragas import evaluate
        from ragas.metrics import answer_relevancy, context_precision, faithfulness
    except ImportError as exc:
        raise SystemExit(
            "RAGAS import failed. Install eval deps with pinned versions:\n"
            "  pip install -r requirements-eval.txt\n"
            f"Original error: {exc}"
        ) from exc

    from ragas.embeddings import LangchainEmbeddingsWrapper
    from ragas.llms import LangchainLLMWrapper

    from langchain_core.outputs import LLMResult

    from ragas.run_config import RunConfig

    from src.config import (
        GROQ_API_KEY,
        GROQ_RAGAS_MAX_TOKENS,
        GROQ_RAGAS_MAX_WORKERS,
        GROQ_RAGAS_MODEL,
        GROQ_RAGAS_REASONING_EFFORT,
        GROQ_RAGAS_TIMEOUT,
        OLLAMA_BASE_URL,
        OLLAMA_MODEL,
        RAGAS_CONTEXT_MAX_CHARS,
        RAGAS_MAX_CONTEXT_CHUNKS,
    )

    questions, answers, contexts, ground_truths = [], [], [], []

    print(f"Collecting RAG answers for {len(items)} questions...")
    for i, item in enumerate(items, 1):
        print(f"[{i}/{len(items)}] {item['question'][:70]}...")
        result = ask(item["question"])
        questions.append(item["question"])
        answers.append(result["answer"])
        # Trim chunks for RAGAS — full chunks overflow judge max_tokens
        trimmed = [
            c[:RAGAS_CONTEXT_MAX_CHARS]
            for c in result["contexts"][:RAGAS_MAX_CONTEXT_CHUNKS]
        ]
        contexts.append(trimmed)
        # Use expected keywords joined as a lightweight ground-truth hint
        ground_truths.append(", ".join(item["expected_answer_contains"]))

    dataset = Dataset.from_dict(
        {
            # Newer RAGAS column names
            "user_input": questions,
            "response": answers,
            "retrieved_contexts": contexts,
            "reference": ground_truths,
            # Older aliases (some ragas versions still read these)
            "question": questions,
            "answer": answers,
            "contexts": contexts,
            "ground_truth": ground_truths,
        }
    )

    if judge == "groq":
        from langchain_groq import ChatGroq

        if not GROQ_API_KEY:
            raise SystemExit("GROQ_API_KEY missing in .env for --judge groq")
        groq_kwargs: dict = {
            "model": GROQ_RAGAS_MODEL,
            "api_key": GROQ_API_KEY,
            "temperature": 0,
            "max_tokens": GROQ_RAGAS_MAX_TOKENS,
            "timeout": GROQ_RAGAS_TIMEOUT,
            "max_retries": 3,
        }
        # gpt-oss models spend tokens on reasoning — cap effort for judge tasks
        if "gpt-oss" in GROQ_RAGAS_MODEL:
            groq_kwargs["reasoning_effort"] = GROQ_RAGAS_REASONING_EFFORT
            groq_kwargs["reasoning_format"] = "hidden"
        print(
            f"RAGAS judge: {GROQ_RAGAS_MODEL} "
            f"(max_tokens={GROQ_RAGAS_MAX_TOKENS}, timeout={GROQ_RAGAS_TIMEOUT}s)"
        )
        lc_llm = ChatGroq(**groq_kwargs)
    else:
        try:
            from langchain_ollama import ChatOllama
        except ImportError:
            from langchain_community.chat_models import ChatOllama
        print(f"RAGAS judge model: {OLLAMA_MODEL}")
        lc_llm = ChatOllama(
            model=OLLAMA_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=0,
            num_predict=GROQ_RAGAS_MAX_TOKENS,
        )

    from langchain_huggingface import HuggingFaceEmbeddings
    from src.config import EMBEDDING_MODEL

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    def _groq_is_finished(response: LLMResult) -> bool:
        """Groq uses finish_reason='length' — accept only if output has text."""
        ok = {"stop", "STOP", "MAX_TOKENS", "eos_token"}
        for g in response.flatten():
            resp = g.generations[0][0]
            text = (getattr(resp, "text", None) or "").strip()
            reason = None
            if resp.generation_info:
                reason = resp.generation_info.get("finish_reason")
            elif hasattr(resp, "message") and resp.message:
                reason = resp.message.response_metadata.get("finish_reason")
            if reason == "length":
                if not text:
                    return False
                continue
            if reason is not None and reason not in ok:
                return False
        return True

    run_config = RunConfig(
        timeout=GROQ_RAGAS_TIMEOUT,
        max_workers=GROQ_RAGAS_MAX_WORKERS,
        max_retries=5,
    )
    is_finished = _groq_is_finished if judge == "groq" else None
    llm = LangchainLLMWrapper(lc_llm, run_config=run_config, is_finished_parser=is_finished)
    emb = LangchainEmbeddingsWrapper(embeddings)

    print(
        f"Running RAGAS with judge={judge} "
        f"(workers={GROQ_RAGAS_MAX_WORKERS}, contexts<={RAGAS_MAX_CONTEXT_CHUNKS})..."
    )
    scores = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=llm,
        embeddings=emb,
        run_config=run_config,
    )

    # ragas returns EvaluationResult — convert to plain dict
    import math

    if hasattr(scores, "to_pandas"):
        df = scores.to_pandas()
        summary = {}
        skip_cols = {
            "question",
            "answer",
            "contexts",
            "ground_truth",
            "user_input",
            "response",
            "retrieved_contexts",
            "reference",
        }
        for col in df.columns:
            if col in skip_cols or df[col].dtype == object:
                continue
            val = float(df[col].mean())
            if not math.isnan(val):
                summary[col] = val
    else:
        summary = {k: v for k, v in dict(scores).items() if v is not None}

    if not summary:
        raise SystemExit(
            "RAGAS returned no valid metrics (all NaN). Common causes:\n"
            "  - Groq model name wrong in .env (use openai/gpt-oss-20b)\n"
            "  - API key invalid or rate limited\n"
            "  - Try: python -m src.eval --limit 3 --ragas-only --judge groq"
        )

    return {
        "mode": "ragas",
        "judge": judge,
        "judge_model": GROQ_RAGAS_MODEL if judge == "groq" else OLLAMA_MODEL,
        "n": len(items),
        "metrics": summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate RAG pipeline")
    parser.add_argument("--limit", type=int, default=0, help="Evaluate only first N questions (0 = all)")
    parser.add_argument(
        "--retrieval-only",
        action="store_true",
        help="Score retrieved contexts only (no LLM — use when Ollama/CUDA is down)",
    )
    parser.add_argument("--keyword-only", action="store_true", help="Answer keyword check; skip RAGAS")
    parser.add_argument("--ragas", action="store_true", help="Also run RAGAS metrics")
    parser.add_argument(
        "--ragas-only",
        action="store_true",
        help="Skip keyword regression; run RAGAS only (uses cached answers)",
    )
    parser.add_argument(
        "--judge",
        choices=["ollama", "groq"],
        default="ollama",
        help="LLM judge for RAGAS (default: ollama to save Groq quota)",
    )
    args = parser.parse_args()

    items = load_golden()
    if args.limit and args.limit > 0:
        items = items[: args.limit]

    report: dict = {"golden_file": str(GOLDEN_PATH), "n_questions": len(items)}

    if args.retrieval_only:
        print("\n=== Retrieval keyword eval (no LLM) ===")
        result = run_retrieval_eval(items)
        report["retrieval_keyword"] = {
            "pass_rate": result["pass_rate"],
            "avg_keyword_score": result["avg_keyword_score"],
            "n": result["n"],
            "rows": result["rows"],
        }
        print(
            f"\nRetrieval pass rate: {result['pass_rate']:.1%} "
            f"(avg score {result['avg_keyword_score']:.2f})"
        )
    elif args.ragas_only:
        print("\n=== RAGAS only ===")
        ragas_result = run_ragas_eval(items, judge=args.judge)
        report["ragas"] = ragas_result
        print("RAGAS metrics:", json.dumps(ragas_result.get("metrics", {}), indent=2))
    else:
        print("\n=== Answer keyword regression ===")
        keyword_result = run_keyword_eval(items)
        report["answer_keyword"] = {
            "pass_rate": keyword_result["pass_rate"],
            "avg_keyword_score": keyword_result["avg_keyword_score"],
            "n": keyword_result["n"],
            "rows": keyword_result["rows"],
        }
        print(
            f"\nAnswer keyword pass rate: {keyword_result['pass_rate']:.1%} "
            f"(avg score {keyword_result['avg_keyword_score']:.2f})"
        )

        if args.ragas and not args.keyword_only:
            print("\n=== RAGAS ===")
            ragas_result = run_ragas_eval(items, judge=args.judge)
            report["ragas"] = ragas_result
            print("RAGAS metrics:", json.dumps(ragas_result.get("metrics", {}), indent=2))
        elif not args.keyword_only and not args.ragas:
            print("\n(Tip: add --ragas for faithfulness / relevancy / context_precision)")

    REPORT_PATH.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved report -> {REPORT_PATH}")


if __name__ == "__main__":
    main()
