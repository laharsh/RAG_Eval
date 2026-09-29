#!/usr/bin/env bash
# P1 demo — API on http://localhost:8000
set -e
BASE="${BASE_URL:-http://localhost:8000}"

echo "=== Health ==="
curl -s "$BASE/health" | jq .

ask() {
  echo ""
  echo "=== Ask: ${1:0:60}... ==="
  curl -s -X POST "$BASE/ask" -H "Content-Type: application/json" \
    -d "$(jq -n --arg q "$1" '{question:$q}')" | jq -r '.answer' | head -c 400
  echo ""
}

ask "What practices are prohibited under Article 5 of the EU AI Act?"
ask "What are the four functions in the NIST AI RMF?"
ask "How does India DPDP define personal data?"

echo "(Optional) python -m src.eval --limit 3 --retrieval-only"
