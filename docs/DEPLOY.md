# Deploy P1 to Render (free demo)

**Model:** FAISS-only API + static React UI. Hybrid (OpenSearch) stays local.  
**Secrets:** `GROQ_API_KEY` only on the API service — never in the UI.

## 1. Prepare bundle (once per index change)

```powershell
cd rag-eval-platform
docker compose up -d          # optional: hybrid ingest locally
python -m src.ingest
python scripts\prepare_deploy.py
```

Commit `deploy/bundle/` (faiss_index + chunks.jsonl) or keep private and build Docker locally.

## 2. Render — API (Docker)

1. [Render](https://render.com) → New → **Blueprint** (connect repo) or **Web Service** → Docker.
2. Set env:
   - `GROQ_API_KEY` (secret)
   - `HOSTED_DEMO=true`
   - `LLM_PROVIDER=groq`
   - `CORS_ORIGINS=https://YOUR-UI.onrender.com,http://localhost:5173`
3. Deploy. Note URL: `https://governance-rag-api.onrender.com`

## 3. Render — UI (static site)

1. New **Static Site**, root `demo-ui`.
2. Build: `npm ci && npm run build`
3. Publish: `dist`
4. Env: `VITE_API_URL=https://governance-rag-api.onrender.com`
5. Update API `CORS_ORIGINS` to match UI URL.

Or use `render.yaml` at repo root (rename services if URLs differ).

## 4. Local UI dev

```powershell
cd demo-ui
copy .env.example .env
npm install
npm run dev
```

API: `uvicorn src.api:app --port 8000` with `CORS_ORIGINS` including `http://localhost:5173`.

## 5. Loom checklist

- Show UI → 3 demo questions (Article 5, NIST functions, DPDP personal data)
- Show `/health` → `hosted_demo: true`, vector-only label
- Mention P2 agent locally (tab “Coming soon” on UI)

## P2 later

Deploy second web service; set UI `VITE_AGENT_URL` when ready.
