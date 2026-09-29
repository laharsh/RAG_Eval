"""
api.py — FastAPI REST endpoints for the RAG service.

Start:
    docker compose up -d
    python -m src.ingest          # if not done yet
    uvicorn src.api:app --reload --port 8000

Test:
    curl http://localhost:8000/health
    curl -X POST http://localhost:8000/ask -H "Content-Type: application/json" \\
         -d "{\"question\": \"What are the NIST AI RMF functions?\"}"
"""

from pydantic import BaseModel, Field
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.config import CORS_ORIGINS, HOSTED_DEMO
from src.ingest import run_ingest
from src.opensearch_store import is_available
from src.rag_chain import ask

app = FastAPI(
    title="AI Governance Knowledge Assistant",
    description="Hybrid RAG over EU AI Act, NIST AI RMF, India DPDP",
    version="0.3.0",
)

# Hosted demo: allow any Render static-site origin (env typos/trailing slashes are common).
_cors_origins = list(CORS_ORIGINS)
_cors_origin_regex: str | None = None
if HOSTED_DEMO:
    _cors_origin_regex = r"https://[\w-]+\.onrender\.com$"

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_origin_regex=_cors_origin_regex,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class AskRequest(BaseModel):
    question: str = Field(..., min_length=3, examples=["What is a Data Principal?"])


class SourceItem(BaseModel):
    source: str
    page: int | None
    snippet: str


class AskResponse(BaseModel):
    question: str
    answer: str
    sources: list[SourceItem]
    retrieval: str


def _retrieval_label() -> str:
    if is_available():
        return "hybrid (FAISS + BM25 + RRF)"
    if HOSTED_DEMO:
        return "vector only (hosted demo — hybrid disabled)"
    return "vector only"


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "hosted_demo": HOSTED_DEMO,
        "opensearch": is_available(),
        "retrieval_mode": _retrieval_label(),
    }


@app.post("/ingest")
def ingest() -> dict:
    """Re-index all PDFs (run after adding documents)."""
    if HOSTED_DEMO:
        raise HTTPException(status_code=403, detail="Ingest disabled on hosted demo")
    try:
        run_ingest()
        return {"status": "ok", "message": "Ingest complete"}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ask", response_model=AskResponse)
def ask_endpoint(body: AskRequest) -> AskResponse:
    try:
        result = ask(body.question)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return AskResponse(
        question=result["question"],
        answer=result["answer"],
        sources=[SourceItem(**s) for s in result["sources"]],
        retrieval=_retrieval_label(),
    )
