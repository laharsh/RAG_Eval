"""
llm.py — one function to call the LLM (Ollama or Groq).

WHY two providers?
  - Ollama  → free, unlimited, use while coding
  - Groq    → fast, use only for demo video (see projects-plan/FREE_TIER_BUDGET.md)

Responses are cached so the same question never hits the API twice.
"""

import hashlib
import json
from typing import Optional

import httpx

from src.config import (
    CACHE_DIR,
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
)


def _cache_key(prompt: str) -> str:
    return hashlib.md5(prompt.encode()).hexdigest()


def _read_cache(prompt: str) -> Optional[str]:
    path = CACHE_DIR / f"{_cache_key(prompt)}.json"
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))["response"]
    return None


def _write_cache(prompt: str, response: str) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CACHE_DIR / f"{_cache_key(prompt)}.json"
    path.write_text(
        json.dumps({"prompt": prompt[:200], "response": response}),
        encoding="utf-8",
    )


def _call_ollama(prompt: str) -> str:
    """Call local Ollama server."""
    url = f"{OLLAMA_BASE_URL}/api/generate"
    # Keep context window modest for small local models.
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "num_ctx": 2048,
            "temperature": 0,
            "num_gpu": 0,  # force CPU — avoids CUDA crashes on some Windows GPUs
        },
    }
    with httpx.Client(timeout=180.0) as client:
        resp = client.post(url, json=payload)
        if resp.status_code >= 400:
            # Surface Ollama's real error (often OOM / context too large).
            detail = resp.text[:500]
            raise RuntimeError(
                f"Ollama error {resp.status_code}: {detail}\n"
                f"Tip: restart Ollama, or shorten context "
                f"(MAX_CONTEXT_CHUNKS in .env), or use LLM_PROVIDER=groq."
            )
        return resp.json()["response"]


def _call_groq(prompt: str) -> str:
    """Call Groq API via langchain-groq."""
    from langchain_groq import ChatGroq
    from langchain_core.messages import HumanMessage

    if not GROQ_API_KEY:
        raise ValueError("GROQ_API_KEY missing in .env")

    llm = ChatGroq(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0)
    result = llm.invoke([HumanMessage(content=prompt)])
    return result.content


def ask_llm(prompt: str, use_cache: bool = True) -> str:
    """
    Send a prompt to the configured LLM and return the text answer.

    Args:
        prompt: The full prompt string (system + context + question).
        use_cache: If True, return cached answer when available.
    """
    if use_cache:
        cached = _read_cache(prompt)
        if cached:
            return cached

    if LLM_PROVIDER == "groq":
        answer = _call_groq(prompt)
    else:
        answer = _call_ollama(prompt)

    if use_cache:
        _write_cache(prompt, answer)
    return answer
