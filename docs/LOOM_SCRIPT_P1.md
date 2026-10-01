# Loom narration script — Project 1 (RAG)

**Length:** ~2–2.5 minutes spoken + UI actions  
**Tone:** Clear student/portfolio project — you built it, you measured it, you can explain it.

**How to use:** Record screen **with mic**, or record **mute** and read this as **Loom voiceover** / captions later. Pause between sections while you click.

---

## Section 0 — Before you talk (on screen only, 5 sec)

Show: Governance Console + corpus box visible. No need to speak yet.

---

## Section 1 — Intro & use case (~25 sec)

> Hi, I’m [Name]. This is **Project 1** from my AI engineering portfolio — an **AI Governance Knowledge Assistant**.
>
> **Use case:** Compliance and GRC teams work with long official regulations — the EU AI Act, NIST’s AI Risk Management Framework, and India’s DPDP Act. You can’t just Ctrl+F a two-hundred-page PDF. This app lets you **ask in plain English** and get an answer **with citations** back to the source PDF and page.

**On screen:** Scroll slowly through the three bullets in **Official corpus**.

---

## Section 2 — What you built (scope, not hype) (~30 sec)

> I didn’t build a generic chatbot. I built a **RAG pipeline**: ingest PDFs, chunk them, index them, retrieve the right passages, then generate an answer **only from that context**.
>
> On my machine I use **hybrid retrieval** — **FAISS** for semantic search plus **OpenSearch BM25** for keyword matches like “Article 5”, merged with **RRF**, reciprocal rank fusion. The API is **FastAPI**; this UI is a small **React** front end that only talks to the API — **no API keys in the browser**.
>
> For the **hosted demo on Render**, I ship a **FAISS-only** bundle to stay on the free tier; hybrid search is in the repo when you run Docker locally.

**On screen:** Point at footer: `hybrid (FAISS + BM25 + RRF)` or vector-only if that’s what you have.

---

## Section 3 — Models & stack (one breath each) (~25 sec)

> **Embeddings** are local: **sentence-transformers / MiniLM** — free, no embedding API cost.  
> **Generation** for demos: **Groq** with an open-weight model — fast for recordings; I also support **Ollama** locally for unlimited dev.  
> **Vector store:** FAISS on disk; optional Pinecone is documented but not required for the demo.

**On screen:** You can stay on the UI; optional 3-second flash of `README.md` architecture diagram if you want.

---

## Section 4 — Live demo (show, don’t over-narrate) (~45 sec)

> I’ll run three questions — one per regulation.

| Button | Say briefly (optional) | Do |
|--------|------------------------|-----|
| **NIST** | “Framework structure — the four functions.” | Ask → read **first sentence** of answer → open **one source card** |
| **EU AI Act** | “Legally sensitive — prohibited practices under Article 5.” | Ask → point at **PDF name + page** |
| **India DPDP** | “India data protection — definition of personal data.” | Ask → sources |

**If Groq is slow:** “First question warms the embedding model; the next ones are faster.”

---

## Section 5 — Evaluation (your differentiator) (~25 sec)

> What I’m proud of for a portfolio project is **evaluation**, not just a demo UI. I wrote about **fifty golden question–answer pairs** in `golden_qa.json` — keyword checks for regression — and ran **RAGAS** metrics with a Groq judge: faithfulness, answer relevancy, context precision. Numbers are in the README and `eval_report.json`. That’s how I know retrieval changes actually help before I trust the answers.

**On screen (pick one):**

- Scroll GitHub README metric table, **or**
- 5 sec terminal: `python -m src.eval --limit 3 --keyword-only`

---

## Section 6 — Close & what’s next (~15 sec)

> Code is public: **github.com/laharsh/RAG_Eval**.  
> **Project 2** in the same portfolio is a **LangGraph agent** that calls this API for regulatory Q&A and uses SQL on a mock compliance database — I’ll link that in the README.  
> Thanks for watching.

**On screen:** Browser tab on GitHub repo.

---

## Cheat sheet (if interviewer asks one follow-up)

| Question | Short answer |
|----------|----------------|
| Why these three PDFs? | Official, free, real **AI governance** story for India + EU + US framework. |
| Why hybrid vs vector only? | Keywords like “Article 5” need **BM25**; semantics need **embeddings**; **RRF** merges both. |
| How do you reduce hallucinations? | Grounded prompt + citations; **RAGAS faithfulness** measures it. |
| What would you improve next? | Pinecone deploy path, chunking A/B in README, more eval at 50 Q. |

---

## Mute recording workflow

1. Record UI actions following **Section 4** table (no mic).  
2. In Loom, **Add voiceover** or upload audio reading Sections 1–3 and 5–6.  
3. Or paste Section text into **Loom AI captions** and edit timing.

---

## What NOT to say (keeps credibility)

- Don’t claim “production enterprise deployment” — say **portfolio / demo**.  
- Don’t memorize RAGAS numbers if they’re stale — say “see README for latest run”.  
- Don’t apologize for 0–2 YOE — say **“I focused on ingest, retrieval, API, eval, and a deploy path.”**
