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

**Blueprint note:** Only the **Docker API** service uses `plan: free`. The **static UI** must omit `plan` — Render rejects `plan: free` on `runtime: static`.

## Troubleshooting

### “CORS error” in the browser but UI URL looks correct

1. **`CORS_ORIGINS` must not end with `/`.** Use  
   `https://governance-rag-ui.onrender.com,http://localhost:5173`  
   not `https://governance-rag-ui.onrender.com/`. The browser `Origin` header has no trailing slash.
2. **502 / API asleep:** On the free tier the API spins down. A failed gateway response has **no** CORS headers, so DevTools shows “CORS error” even when the real issue is the API down or timing out. Open `https://governance-rag-api.onrender.com/health` in a **new tab** — you should see JSON. Wait ~1 min on first load after sleep.
3. After changing env vars on Render, use **Manual Deploy** on the API service so the new `CORS_ORIGINS` is picked up.
4. **Verify CORS from your machine** (should include `access-control-allow-origin` for the UI):

   ```bash
   curl -s -D - -o NUL -H "Origin: https://governance-rag-ui.onrender.com" "https://governance-rag-api.onrender.com/health"
   ```

   If you only see `localhost` allowed, fix `CORS_ORIGINS` on the API service. With `HOSTED_DEMO=true`, deployed code also allows `https://*.onrender.com` after you redeploy the latest Docker image.

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
