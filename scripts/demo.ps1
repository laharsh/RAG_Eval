# P1 demo script (PowerShell) — run from rag-eval-platform with API on :8000
$Base = "http://localhost:8000"

Write-Host "=== Health ===" -ForegroundColor Cyan
Invoke-RestMethod "$Base/health" | ConvertTo-Json

$questions = @(
    "What practices are prohibited under Article 5 of the EU AI Act?",
    "What are the four functions in the NIST AI RMF?",
    "How does India DPDP define personal data?"
)

foreach ($q in $questions) {
    Write-Host "`n=== Ask: $($q.Substring(0, [Math]::Min(60, $q.Length)))... ===" -ForegroundColor Cyan
    $body = @{ question = $q } | ConvertTo-Json
    $resp = Invoke-RestMethod -Method Post -Uri "$Base/ask" -Body $body -ContentType "application/json"
    Write-Host $resp.answer.Substring(0, [Math]::Min(400, $resp.answer.Length))
    Write-Host "Sources: $($resp.sources.Count)" -ForegroundColor DarkGray
}

Write-Host "`n(Optional) python -m src.eval --limit 3 --retrieval-only" -ForegroundColor DarkGray
