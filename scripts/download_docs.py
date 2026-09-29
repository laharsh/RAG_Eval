"""
download_docs.py — download the 3 official PDFs for the AI Governance use case.

Run once:
    python scripts/download_docs.py

Files land in data/raw/
"""

from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data" / "raw"

# NIST blocks bare urllib; use a browser-like User-Agent.
HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; rag-eval-platform/1.0; educational)"
}

DOCUMENTS = {
    "eu_ai_act.pdf": (
        "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689"
    ),
    "nist_ai_rmf.pdf": (
        "https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf"
    ),
    "india_dpdp_act_2023.pdf": (
        "https://www.meity.gov.in/static/uploads/2024/06/"
        "2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf"
    ),
}


def download_file(url: str, dest: Path) -> None:
    if dest.exists():
        print(f"  skip (exists): {dest.name}")
        return
    print(f"  downloading: {dest.name}")
    with httpx.Client(follow_redirects=True, timeout=120.0) as client:
        resp = client.get(url, headers=HEADERS)
        resp.raise_for_status()
        dest.write_bytes(resp.content)
    print(f"  saved: {dest} ({dest.stat().st_size // 1024} KB)")


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading AI governance corpus to {OUT_DIR}\n")
    for filename, url in DOCUMENTS.items():
        download_file(url, OUT_DIR / filename)
    print("\nDone. Next: python -m src.ingest")


if __name__ == "__main__":
    main()
