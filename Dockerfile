# Hosted demo — FAISS-only (no OpenSearch). Set GROQ_API_KEY on Render.
FROM python:3.11-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    HOSTED_DEMO=true \
    LLM_PROVIDER=groq \
    VECTOR_BACKEND=faiss

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Pre-download embedding model (faster cold start)
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

COPY src ./src
COPY deploy/bundle/faiss_index ./data/processed/faiss_index
COPY deploy/bundle/chunks.jsonl ./data/processed/chunks.jsonl

EXPOSE 8000

CMD uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}
