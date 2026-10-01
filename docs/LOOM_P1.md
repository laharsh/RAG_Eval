# Loom — Project 1 (RAG) action plan

~2 minutes. Record **browser UI**; optional 5s terminal clip for eval.

---

## Before recording (one-time)

1. **Groq for speed** — in `rag-eval-platform/.env`:

   ```env
   LLM_PROVIDER=groq
   GROQ_API_KEY=your_key
   ```

2. **Optional hybrid** (footer shows “hybrid …”):

   ```powershell
   cd rag-eval-platform
   docker compose up -d
   python -m src.ingest
   ```

3. **Warm the stack** — run once before Loom:

   ```powershell
   cd rag-eval-platform
   .\.venv\Scripts\activate
   uvicorn src.api:app --port 8000
   ```

   Wait for log: `Vectorstore warmup finished`.

   ```powershell
   cd demo-ui
   npm run dev
   ```

   Open http://localhost:5173 — click **NIST**, **EU AI Act**, **India DPDP** once each (fills `.cache/`).

---

## Recording day — terminal commands

**Terminal 1 — API (leave running):**

```powershell
cd C:\Users\lahar\OneDrive\Documents\Resume_6-28-2026\rag-eval-platform
.\.venv\Scripts\activate
uvicorn src.api:app --port 8000
```

**Terminal 2 — UI:**

```powershell
cd C:\Users\lahar\OneDrive\Documents\Resume_6-28-2026\rag-eval-platform\demo-ui
npm run dev
```

**Loom:** share **browser tab** only (localhost:5173). Zoom 125%, notifications off.

---

## Script (≈2 min)

| Time | Say / do |
|------|----------|
| 0:00–0:20 | *“This is a governance RAG assistant over three official PDFs—EU AI Act, NIST AI RMF, and India DPDP. Compliance teams need citations, not generic chat.”* Scroll the **corpus** box on screen. |
| 0:20–0:45 | Click **NIST** → **Ask**. Read one sentence of the answer; expand **one source card** (PDF + page). |
| 0:45–1:10 | Click **EU AI Act** → **Ask**. Mention Article 5 / prohibited practices. |
| 1:10–1:35 | Click **India DPDP** → **Ask**. Point at sources. |
| 1:35–1:50 | *“Repo has 50 golden questions and RAGAS eval—hybrid FAISS + BM25 locally.”* Optional: flash GitHub README metric table. |
| 1:50–2:00 | Show GitHub link on screen: https://github.com/laharsh/RAG_Eval |

---

## Optional 5s B-roll (terminal)

```powershell
cd rag-eval-platform
.\.venv\Scripts\activate
python -m src.eval --limit 3 --keyword-only
```

Voice: *“Keyword regression on golden Q&A.”*

---

## After upload

- [ ] Paste Loom URL in `README.md` (Demo video section).
- [ ] Resume: one bullet + link to Loom + GitHub.

---

## If something breaks during recording

- **Slow / timeout:** confirm `LLM_PROVIDER=groq`, restart `uvicorn`.
- **API unreachable:** UI footer — start Terminal 1 again.
- **Skip hybrid:** `docker compose stop` — vector-only still demos fine; say “full hybrid in repo.”
