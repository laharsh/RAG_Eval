"""
ingest.py — PDFs → chunks → FAISS (vectors) + OpenSearch (BM25).

Run after adding PDFs to data/raw/:

    docker compose up -d        # start OpenSearch first
    python -m src.ingest
"""

from pathlib import Path

from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    DATA_RAW_DIR,
    EMBEDDING_MODEL,
    FAISS_INDEX_PATH,
    ensure_dirs,
)
from src.opensearch_store import index_chunks, is_available, save_chunk_registry
from src.text_utils import make_chunk_id, normalize_pdf_text


def load_pdfs() -> list[Document]:
    pdf_files = list(DATA_RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError(
            f"No PDFs in {DATA_RAW_DIR}. Run: python scripts/download_docs.py"
        )
    loader = PyPDFDirectoryLoader(str(DATA_RAW_DIR))
    docs = loader.load()
    for doc in docs:
        doc.page_content = normalize_pdf_text(doc.page_content)
    print(f"Loaded {len(docs)} pages from {len(pdf_files)} PDF(s)")
    return docs


def split_documents(docs: list[Document]) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    print(f"Split into {len(chunks)} chunks (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
    return chunks


def assign_chunk_ids(chunks: list[Document]) -> list[dict]:
    """Assign stable IDs and build registry rows for FAISS + OpenSearch."""
    per_page: dict[tuple[str, int], int] = {}
    registry: list[dict] = []

    for seq, doc in enumerate(chunks):
        source = doc.metadata.get("source", "unknown")
        page = int(doc.metadata.get("page", 0))
        key = (source, page)
        per_page[key] = per_page.get(key, 0) + 1
        idx = per_page[key]

        chunk_id = make_chunk_id(source, page, idx)
        doc.metadata["chunk_id"] = chunk_id
        doc.metadata["seq"] = seq

        registry.append(
            {
                "chunk_id": chunk_id,
                "content": doc.page_content,
                "source": source,
                "page": page,
                "seq": seq,  # document order — used for neighbor expansion
            }
        )
    return registry


def build_embeddings() -> HuggingFaceEmbeddings:
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def save_faiss_index(chunks: list[Document], embeddings: HuggingFaceEmbeddings) -> None:
    vectorstore = FAISS.from_documents(chunks, embeddings)
    vectorstore.save_local(str(FAISS_INDEX_PATH))
    print(f"FAISS index saved to {FAISS_INDEX_PATH}")


def run_ingest() -> None:
    ensure_dirs()
    docs = load_pdfs()
    chunks = split_documents(docs)
    registry = assign_chunk_ids(chunks)

    save_chunk_registry(registry)
    print(f"Chunk registry: {len(registry)} chunks")

    embeddings = build_embeddings()
    save_faiss_index(chunks, embeddings)

    if is_available():
        count = index_chunks(registry)
        print(f"OpenSearch indexed {count} chunks (BM25)")
    else:
        print(
            "OpenSearch not reachable — FAISS only. "
            "Start with: docker compose up -d"
        )

    print("Ingest complete.")


if __name__ == "__main__":
    run_ingest()
