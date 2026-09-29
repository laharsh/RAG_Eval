# Use Case — AI Governance Knowledge Assistant

## One-line pitch (for README + demo intro)

> **“Compliance teams can’t keyword-search 200-page regulations. This assistant answers natural-language questions over the EU AI Act, NIST AI RMF, and India DPDP Act — with citations.”**

---

## Why this use case (reviewer psychology)

| Boring demo | Our demo |
|-------------|----------|
| “Ask questions about LangChain docs” | “What are high-risk AI obligations under EU AI Act Art. 6?” |
| Looks like a tutorial clone | Looks like **RegTech / enterprise AI** |
| No business story | Maps to TCS/BFSI/consulting clients in India |

Real-world parallels:
- Bayer **PRINCE** — decades of PDF study reports → RAG assistant
- M&A due diligence — cross-reference filings (we use public regulations instead)
- **AI governance** — hottest enterprise GenAI use case in 2025–2026

---

## Document corpus (3 PDFs — all free, legal, official)

| # | Document | Source | Download |
|---|----------|--------|----------|
| 1 | **EU AI Act** (Regulation 2024/1689) | EUR-Lex (official) | `scripts/download_docs.py` |
| 2 | **NIST AI Risk Management Framework 1.0** | NIST (US gov) | same script |
| 3 | **India Digital Personal Data Protection Act, 2023** | MeitY (official) | same script |

### Direct URLs (for manual download)

```text
EU AI Act PDF:
https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689

NIST AI RMF 1.0 PDF:
https://nvlpubs.nist.gov/nistpubs/ai/NIST.AI.100-1.pdf

India DPDP Act 2023 PDF:
https://www.meity.gov.in/static/uploads/2024/06/2bf1f0e9f04e6fb4f8fef35e82c42aa5.pdf
```

**Total size:** ~5–15 MB of PDFs → ~1,500–3,000 chunks after splitting. Trivial for FAISS/Pinecone.

---

## Demo questions (use in video — sound impressive)

1. *“What practices are prohibited under Article 5 of the EU AI Act?”*
2. *“What are the four functions in the NIST AI RMF?”*
3. *“What are the penalties for violating the EU AI Act?”*
4. *“How does India DPDP define personal data?”*
5. *“Compare: is NIST AI RMF legally binding vs EU AI Act?”* (hybrid retrieval stress test)

---

## golden_qa.json themes (50 questions)

| Theme | Count | Example |
|-------|-------|---------|
| EU AI Act — definitions | 15 | “What is a GPAI model under the Act?” |
| EU AI Act — high-risk | 10 | “What obligations apply to high-risk AI providers?” |
| NIST AI RMF | 10 | “What does the MAP function cover?” |
| India DPDP | 10 | “What are data principal rights?” |
| Cross-document | 5 | “Which framework is legally binding in the EU?” |

Write answers yourself from the PDFs — this forces you to learn the content (good for interviews).

---

## What NOT to use

| Source | Why skip |
|--------|----------|
| Random blog PDFs | Looks low-effort |
| Copyrighted books | Legal risk |
| SEC 10-K only | Great but 100+ pages, tables — harder for beginner v1 |
| Medical records | Privacy / compliance issues |

Optional **v2 corpus add-on:** One Apple or Microsoft 10-K from [SEC EDGAR](https://www.sec.gov/edgar) for “financial RAG” variant.
