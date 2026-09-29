import { useCallback, useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

type Tab = "knowledge" | "operations";

type Source = { source: string; page: number | null; snippet: string };

type AskResponse = {
  question: string;
  answer: string;
  sources: Source[];
  retrieval: string;
};

const SAMPLES = [
  "What are the four functions in the NIST AI RMF?",
  "What practices are prohibited under Article 5 of the EU AI Act?",
  "How does India DPDP define personal data?",
];

export default function App() {
  const [tab, setTab] = useState<Tab>("knowledge");
  const [question, setQuestion] = useState(SAMPLES[0]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<AskResponse | null>(null);
  const [health, setHealth] = useState<string>("");

  useEffect(() => {
    fetch(`${API}/health`)
      .then((r) => r.json())
      .then((h) => setHealth(h.retrieval_mode || "ok"))
      .catch(() => setHealth("API unreachable"));
  }, []);

  const ask = useCallback(async () => {
    const q = question.trim();
    if (q.length < 3) {
      setError("Question must be at least 3 characters.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${API}/ask`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: q }),
      });
      if (!res.ok) {
        const body = await res.text();
        throw new Error(body || res.statusText);
      }
      setResult(await res.json());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  }, [question]);

  return (
    <div className="app">
      <header>
        <h1>AI Governance Console</h1>
        <p>Regulatory Q&A over EU AI Act, NIST AI RMF, and India DPDP.</p>
      </header>

      <div className="tabs">
        <button
          type="button"
          className={tab === "knowledge" ? "active" : ""}
          onClick={() => setTab("knowledge")}
        >
          Knowledge (RAG)
        </button>
        <button type="button" disabled title="Deploy P2 API, then enable VITE_AGENT_URL">
          Operations (Agent)
        </button>
      </div>

      {tab === "knowledge" && (
        <div className="panel">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            aria-label="Question"
          />
          <div className="actions">
            <button type="button" onClick={ask} disabled={loading}>
              {loading ? "Asking…" : "Ask"}
            </button>
            {SAMPLES.map((s) => (
              <button
                key={s}
                type="button"
                className="secondary"
                onClick={() => setQuestion(s)}
              >
                Sample
              </button>
            ))}
          </div>
          {error && <p className="error">{error}</p>}
          {result && (
            <>
              <div className="answer">{result.answer}</div>
              <p className="meta">Retrieval: {result.retrieval}</p>
              <div className="sources">
                <strong>Sources ({result.sources.length})</strong>
                {result.sources.map((s, i) => (
                  <div key={i} className="source-card">
                    <strong>{s.source} — page {s.page ?? "?"}</strong>
                    {s.snippet}
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      <footer>
        API: {API} · {health}
        <br />
        Keys stay on the server (Groq). Hybrid search available when running OpenSearch locally.
      </footer>
    </div>
  );
}
