"""
config.py — loads all settings from .env in one place.

Every other file imports from here so you never scatter magic strings.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (folder above src/)
ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

# ── Paths ──────────────────────────────────────────────────────────────────
DATA_RAW_DIR = ROOT / os.getenv("DATA_RAW_DIR", "data/raw")
DATA_PROCESSED_DIR = ROOT / os.getenv("DATA_PROCESSED_DIR", "data/processed")
FAISS_INDEX_PATH = DATA_PROCESSED_DIR / "faiss_index"
CHUNKS_REGISTRY_PATH = DATA_PROCESSED_DIR / "chunks.jsonl"
CACHE_DIR = ROOT / ".cache"

# ── LLM ────────────────────────────────────────────────────────────────────
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama").lower()
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
# llama-3.1-8b-instant deprecated on Groq Aug 2026 → use gpt-oss-20b
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
# Defaults to GROQ_MODEL (gpt-oss-20b on free tier). Enterprise: llama-3.3-70b-versatile.
GROQ_RAGAS_MODEL = os.getenv("GROQ_RAGAS_MODEL", GROQ_MODEL)
GROQ_RAGAS_MAX_TOKENS = int(os.getenv("GROQ_RAGAS_MAX_TOKENS", "8192"))
GROQ_RAGAS_TIMEOUT = int(os.getenv("GROQ_RAGAS_TIMEOUT", "300"))
GROQ_RAGAS_MAX_WORKERS = int(os.getenv("GROQ_RAGAS_MAX_WORKERS", "2"))
# low/medium/high — only for openai/gpt-oss-* judge models
GROQ_RAGAS_REASONING_EFFORT = os.getenv("GROQ_RAGAS_REASONING_EFFORT", "low")
RAGAS_CONTEXT_MAX_CHARS = int(os.getenv("RAGAS_CONTEXT_MAX_CHARS", "400"))
RAGAS_MAX_CONTEXT_CHUNKS = int(os.getenv("RAGAS_MAX_CONTEXT_CHUNKS", "4"))

# ── Embeddings (always local) ──────────────────────────────────────────────
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
)

# ── Vector backend: "faiss" (dev) or "pinecone" (demo) ─────────────────────
VECTOR_BACKEND = os.getenv("VECTOR_BACKEND", "faiss").lower()

# ── RAG tuning ─────────────────────────────────────────────────────────────
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))
TOP_K = int(os.getenv("TOP_K", "8"))
RRF_K = int(os.getenv("RRF_K", "60"))  # RRF constant (standard default)
NEIGHBOR_WINDOW = int(os.getenv("NEIGHBOR_WINDOW", "1"))  # ±1 adjacent chunks
# Cap final chunks sent to the LLM (neighbor expansion can grow fast;
# small local models like llama3.2:3b crash on oversized prompts).
MAX_CONTEXT_CHUNKS = int(os.getenv("MAX_CONTEXT_CHUNKS", "10"))

# ── OpenSearch (BM25 keyword index) ───────────────────────────────────────
OPENSEARCH_HOST = os.getenv("OPENSEARCH_HOST", "localhost")
OPENSEARCH_PORT = int(os.getenv("OPENSEARCH_PORT", "9200"))
OPENSEARCH_INDEX = os.getenv("OPENSEARCH_INDEX", "governance-chunks")

# ── Pinecone (only used when VECTOR_BACKEND=pinecone) ────────────────────
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY", "")
PINECONE_INDEX = os.getenv("PINECONE_INDEX", "portfolio-rag")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE", "p1-governance")

# ── Hosted demo (Render) ───────────────────────────────────────────────────
HOSTED_DEMO = os.getenv("HOSTED_DEMO", "false").lower() in ("1", "true", "yes")
# Comma-separated origins for demo UI (no secrets in the browser)
def _normalize_origin(origin: str) -> str:
    """Browsers send Origin without a trailing slash; match that in allow_origins."""
    o = origin.strip()
    return o.rstrip("/") if o.startswith("http") else o


CORS_ORIGINS = [
    _normalize_origin(o)
    for o in os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if o.strip()
]


def ensure_dirs() -> None:
    """Create folders if they don't exist yet."""
    DATA_RAW_DIR.mkdir(parents=True, exist_ok=True)
    DATA_PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
