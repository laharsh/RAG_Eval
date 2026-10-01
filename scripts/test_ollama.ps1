# Verify Ollama on Windows before RAG / RAGAS (--judge ollama)
# Run from repo root: .\scripts\test_ollama.ps1

$ErrorActionPreference = "Stop"
$Base = $env:OLLAMA_BASE_URL
if (-not $Base) { $Base = "http://localhost:11434" }
$Model = $env:OLLAMA_MODEL
if (-not $Model) { $Model = "llama3.2:3b" }

Write-Host "=== 1. Ollama binary ===" -ForegroundColor Cyan
if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    Write-Host "FAIL: ollama not in PATH. Install from https://ollama.com/download" -ForegroundColor Red
    exit 1
}
ollama --version

Write-Host "`n=== 2. API reachable ===" -ForegroundColor Cyan
try {
    $tags = Invoke-RestMethod -Uri "$Base/api/tags" -TimeoutSec 10
    $tags.models | ForEach-Object { Write-Host "  model: $($_.name)" }
} catch {
    Write-Host "FAIL: Cannot reach $Base — start the Ollama app (tray icon) or run: ollama serve" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== 3. Short generation (CLI) ===" -ForegroundColor Cyan
ollama run $Model "Reply with exactly: OLLAMA_OK"

Write-Host "`n=== 4. HTTP generate (same as our API client) ===" -ForegroundColor Cyan
$body = @{
    model = $Model
    prompt = "Reply with one word: OK"
    stream = $false
    options = @{ num_gpu = 0; num_ctx = 2048; temperature = 0 }
} | ConvertTo-Json -Depth 4
$r = Invoke-RestMethod -Method Post -Uri "$Base/api/generate" -Body $body -ContentType "application/json" -TimeoutSec 180
Write-Host $r.response

Write-Host "`n=== 5. Project llm.py ===" -ForegroundColor Cyan
$env:LLM_PROVIDER = "ollama"
Push-Location $PSScriptRoot\..
$py = @'
from src.llm import ask_llm
print(ask_llm("Say OK in one word.", use_cache=False))
'@
.\.venv\Scripts\python.exe -c $py
Pop-Location

Write-Host ""
Write-Host "All checks passed. Dev: LLM_PROVIDER=ollama. RAGAS judge: --judge ollama" -ForegroundColor Green
