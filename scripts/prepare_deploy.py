"""
Copy FAISS index + chunk registry into deploy/bundle for Docker / Render.

Run locally after ingest (with hybrid or FAISS-only):

    python -m src.ingest
    python scripts/prepare_deploy.py
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "processed"
DEST = ROOT / "deploy" / "bundle"


def main() -> None:
    faiss = SRC / "faiss_index"
    chunks = SRC / "chunks.jsonl"
    if not faiss.exists() or not chunks.exists():
        print("Missing index. Run: python -m src.ingest", file=sys.stderr)
        raise SystemExit(1)

    if DEST.exists():
        shutil.rmtree(DEST)
    DEST.mkdir(parents=True)
    shutil.copytree(faiss, DEST / "faiss_index")
    shutil.copy2(chunks, DEST / "chunks.jsonl")
    print(f"Prepared {DEST} for Docker build ({chunks.stat().st_size // 1024} KB chunks registry)")


if __name__ == "__main__":
    main()
