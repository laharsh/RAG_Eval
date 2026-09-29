"""
Keyword regression tests against golden_qa.json.

These do NOT call the LLM (fast CI). They validate the golden file shape
and that retrieval returns expected document names for a few key questions.
"""

from pathlib import Path

import pytest

from src.opensearch_store import is_available
from src.retriever import load_vectorstore, retrieve_chunks

ROOT = Path(__file__).resolve().parent.parent
GOLDEN = ROOT / "golden_qa.json"


def test_golden_qa_has_fifty_questions():
    import json

    data = json.loads(GOLDEN.read_text(encoding="utf-8"))
    assert len(data) == 50
    for item in data:
        assert "question" in item
        assert "expected_answer_contains" in item
        assert len(item["expected_answer_contains"]) >= 1


def test_retrieval_finds_nist_for_rmf_question():
    """Retrieval-only check — no LLM required."""
    vs = load_vectorstore()
    docs = retrieve_chunks(vs, "What are the four functions in the NIST AI RMF?", use_bm25=is_available())
    sources = " ".join(d.metadata.get("source", "") for d in docs).lower()
    assert "nist" in sources


def test_retrieval_finds_eu_for_article_5():
    vs = load_vectorstore()
    docs = retrieve_chunks(
        vs,
        "What practices are prohibited under Article 5 of the EU AI Act?",
        use_bm25=is_available(),
    )
    sources = " ".join(d.metadata.get("source", "") for d in docs).lower()
    assert "eu_ai_act" in sources


def test_retrieval_finds_dpdp_for_data_principal():
    vs = load_vectorstore()
    docs = retrieve_chunks(vs, "How does India DPDP define a Data Principal?", use_bm25=is_available())
    sources = " ".join(d.metadata.get("source", "") for d in docs).lower()
    assert "dpdp" in sources or "india" in sources
