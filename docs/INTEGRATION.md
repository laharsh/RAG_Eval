# Integration with Project 2 (LangGraph agent)

Project 2 (`langgraph-agent`) calls this API as the **`knowledge_search`** tool.

```text
langgraph-agent  --POST /ask-->  rag-eval-platform :8000
```

## Run both

```powershell
# Terminal 1
cd rag-eval-platform
docker compose up -d
uvicorn src.api:app --port 8000

# Terminal 2
cd langgraph-agent
uvicorn src.api:app --port 8001
```

## Contract

- **POST** `/ask` body: `{"question": "..."}`
- **Response:** `answer`, `sources[]` with `source`, `page`, `snippet`

Set in P2 `.env`: `RAG_API_URL=http://localhost:8000/ask`

Product narrative: [P1_P2_PRODUCT_STORY.md](../../projects-plan/P1_P2_PRODUCT_STORY.md)
