"""
rag_chain.py — RAG orchestration: retrieve → prompt → answer.
"""

from src.config import FAISS_INDEX_PATH
from src.llm import ask_llm
from src.retriever import load_vectorstore, retrieve_chunks

# Prompt template — grounded answers; prefer substance over cross-references
RAG_PROMPT = """You are an AI governance assistant. Answer ONLY using the context below.

Rules:
1. Prefer passages that define, list, or state the substance of the answer.
2. Do NOT say information is missing if any context passage contains it.
3. If a list appears in the context, enumerate the items clearly.
4. Ignore passages that only cross-reference another article without giving details.
5. Cite document name and page.

CONTEXT:
{context}

QUESTION: {question}

ANSWER:"""


def path_label(filepath: str) -> str:
    """Show just the filename, not the full path."""
    from pathlib import Path
    return Path(filepath).name


def format_context(chunks: list) -> str:
    """Turn chunks into one string for the prompt."""
    parts = []
    for i, doc in enumerate(chunks, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "?")
        parts.append(f"[{i}] Source: {path_label(source)}, page {page}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


def ask(question: str) -> dict:
    """
    Main RAG function. Returns answer and sources for the API/demo.

    Returns:
        {
            "question": str,
            "answer": str,
            "sources": [{"source": str, "page": int, "snippet": str}, ...]
        }
    """
    vectorstore = load_vectorstore()
    chunks = retrieve_chunks(vectorstore, question)
    context = format_context(chunks)
    prompt = RAG_PROMPT.format(context=context, question=question)
    answer = ask_llm(prompt)

    sources = []
    seen: set[tuple[str, object]] = set()
    for c in chunks:
        source = path_label(c.metadata.get("source", ""))
        page = c.metadata.get("page")
        key = (source, page)
        if key in seen:
            continue
        seen.add(key)
        snippet = c.page_content[:300] + ("..." if len(c.page_content) > 300 else "")
        sources.append({"source": source, "page": page, "snippet": snippet})
    return {
        "question": question,
        "answer": answer,
        "sources": sources,
        "contexts": [c.page_content for c in chunks],
    }


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print('Usage: python -m src.rag_chain "Your question here"')
        sys.exit(1)

    question = " ".join(sys.argv[1:])
    result = ask(question)
    print("\n=== ANSWER ===")
    print(result["answer"])
    print("\n=== SOURCES ===")
    for s in result["sources"]:
        print(f"  - {s['source']} (page {s['page']})")


if __name__ == "__main__":
    main()
