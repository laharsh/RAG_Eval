# Ollama on Windows — fix & use with this project

## What “working” means here

| Layer | Check |
|-------|--------|
| App running | Tray icon **Ollama** or `http://localhost:11434/api/tags` returns JSON |
| Model pulled | `ollama list` shows `llama3.2:3b` |
| Short answer | `ollama run llama3.2:3b "hi"` responds in &lt;30s |
| This repo | `.\scripts\test_ollama.ps1` passes step 5 |

Your machine already has **Ollama 0.34.4** and **llama3.2:3b** when the service is up.

---

## One-command check (run while RAGAS is busy in another terminal)

```powershell
cd rag-eval-platform
.\scripts\test_ollama.ps1
```

If step 2 fails → start **Ollama** from the Start menu and wait 10s, retry.

`listen tcp 127.0.0.1:11434: bind: Only one usage...` means a server is **already** listening. Do not run `ollama serve` again. `ollama run` using the tray app is enough.

---

## Common failures (and fixes)

### “Connection refused” / API unreachable

- Open **Ollama** app (not only the CLI installer).
- Or in a dedicated terminal: `ollama serve` (leave it open).

### CUDA / GPU crash (Windows NVIDIA) — `exit 0xc0000409` / `CUDA error: shared object initialization failed`

This is the usual reason `ollama run` fails on Windows while `/api/tags` still works.

**Fix (try in order):**

1. Quit Ollama from the tray → set in **PowerShell before starting Ollama**:

   ```powershell
   $env:OLLAMA_NUM_GPU = "0"
   $env:CUDA_VISIBLE_DEVICES = ""
   ```

2. Start **Ollama** app again (or `ollama serve` in that same shell).

3. Test:

   ```powershell
   ollama run llama3.2:3b "OK"
   ```

4. In **Ollama app → Settings**, turn off GPU / use CPU if available.

5. Update GPU drivers, or pull a smaller model: `ollama pull llama3.2:1b`

This project also sets `num_gpu: 0` in `src/llm.py` for API calls — but the **Ollama server process** must start cleanly first.

### “Timed out” on long RAG answers (not short tests)

`llama3.2:3b` on **CPU** is slow with **large context** (many chunks). That is expected.

- **Dev / RAGAS judge:** use Ollama for **judge** only (`--judge ollama`) with small judge prompts.
- **UI / Loom:** keep **`LLM_PROVIDER=groq`** for answers.
- Shorter context: `MAX_CONTEXT_CHUNKS=6` in `.env`.

### RAGAS `--judge ollama` import error

```powershell
.\.venv\Scripts\activate
pip install -r requirements-eval.txt
```

Needs `langchain-ollama` (or falls back to community).

### `.env` still says `LLM_PROVIDER=groq`

Ollama is **not** used for `/ask` until you set:

```env
LLM_PROVIDER=ollama
```

For **RAGAS only**, you can leave `LLM_PROVIDER=groq` and run:

```powershell
python -m src.eval --limit 10 --ragas-only --judge ollama
```

Phase A still uses Groq for answers; phase B judge uses Ollama.

---

## Recommended split (save Groq quota)

| Task | Provider |
|------|----------|
| Demo UI / Loom | `LLM_PROVIDER=groq` |
| Golden keyword 50 Q | groq or ollama |
| RAGAS judge | `--judge ollama` |
| Daily hacking | `LLM_PROVIDER=ollama` + small questions |

---

## Security

Never commit `.env`. If `GROQ_API_KEY` was ever pushed, rotate it in the Groq console.
