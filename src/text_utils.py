"""
text_utils.py — ingest-time PDF text cleanup (not query-specific).

Government PDFs often break words across spaces ("Ar ticle"). We repair
that once during ingest so BM25 and embeddings both see clean text.
"""

import re


def normalize_pdf_text(text: str) -> str:
    """
    Generic cleanup for PDF extraction artifacts.

    Does NOT encode knowledge about specific articles or documents.
    """
    if not text:
        return text

    # Common PDF / font encoding glitches (India DPDP export)
    replacements = {
        "â": "",
        "Ã¢": "",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
    }
    for bad, good in replacements.items():
        text = text.replace(bad, good)

    # Line-break hyphenation: "regula-\n tion" -> "regulation"
    text = re.sub(r"-\s+", "", text)

    # Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Repair split words: short fragment + continuation ("Ar ticle" -> "Article")
    words = text.split(" ")
    fixed: list[str] = []
    i = 0
    while i < len(words):
        word = words[i]
        if (
            i + 1 < len(words)
            and word
            and len(word) <= 4
            and word[0].isupper()
            and words[i + 1]
            and words[i + 1][0].islower()
        ):
            merged = word
            j = i + 1
            while j < len(words) and words[j][0].islower():
                merged += words[j]
                j += 1
                if len(merged) >= 8:
                    break
            fixed.append(merged)
            i = j
        else:
            fixed.append(word)
            i += 1

    return " ".join(fixed)


def make_chunk_id(source: str, page: int, chunk_index: int) -> str:
    """Stable ID shared by FAISS metadata and OpenSearch."""
    from pathlib import Path

    name = Path(source).name
    return f"{name}::p{page}::c{chunk_index}"
