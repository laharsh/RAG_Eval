import { useCallback, useEffect, useState } from "react";

const API = import.meta.env.VITE_API_URL?.replace(/\/$/, "") || "http://localhost:8000";
const GITHUB = "https://github.com/laharsh/RAG_Eval";

type Tab = "knowledge" | "operations";

type Source = { source: string; page: number | null; snippet: string };

type AskResponse = {
  question: string;
  answer: string;
  sources: Source[];
  retrieval: string;
};

const SAMPLE_QUESTIONS: { label: string; question: string; hint: string }[] = [
  {
    label: "NIST",
    hint: "US risk framework",
    question: "What are the four functions in the NIST AI RMF?",
  },
  {
    label: "EU AI Act",
    hint: "Prohibited AI practices",
    question: "What practices are prohibited under Article 5 of the EU AI Act?",
  },
  {
    label: "India DPDP",
    hint: "Personal data definition",
    question: "How does India DPDP define personal data?",
  },
];

const CORPUS = [
  "EU AI Act (Regulation 2024/1689) — binding AI law in the EU",
  "NIST AI Risk Management Framework 1.0 — Govern, Map, Measure, Manage",
  "India Digital Personal Data Protection Act, 2023 — personal data & fiduciaries",
];

export default function App() {
  const [tab, setTab] = useState<Tab>("knowledge");
  const [question, setQuestion] = useState(SAMPLE_QUESTIONS[0].question);
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

  const pickSample = (q: string) => {
    setQuestion(q);
    setError(null);
    setResult(null);
  };

  return (
    <div className="app">
      <header>
        <h1>AI Governance Console</h1>
        <p className="tagline">
          Compliance teams can&apos;t keyword-search 200-page regulations. Ask in plain
          English and get answers with PDF citations.
        </p>
      </header>

      <section className="corpus" aria-label="Document corpus">
        <h2>Official corpus (3 PDFs)</h2>
        <ul>
          {CORPUS.map((line) => (
            <li key={line}>{line}</li>
          ))}
        </ul>
        <p className="corpus-note">
          Ingested into a hybrid index (FAISS + BM25 when OpenSearch runs locally). Eval:
          50 golden Q&amp;A + RAGAS metrics in the{" "}
          <a href={GITHUB} target="_blank" rel="noreferrer">GitHub repo</a>.
        </p>
      </section>

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
          <label className="field-label" htmlFor="question-input">Your question</label>
          <textarea
            id="question-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            aria-label="Question"
          />
          <p className="try-label">Try a demo question</p>
          <div className="actions">
            <button type="button" onClick={ask} disabled={loading}>
              {loading ? "Asking…" : "Ask"}
            </button>
            {SAMPLE_QUESTIONS.map((s) => (
              <button
                key={s.label}
                type="button"
                className="secondary"
                title={s.hint}
                onClick={() => pickSample(s.question)}
              >
                {s.label}
              </button>
            ))}
          </div>
          {error && <p className="error">{error}</p>}
          {result && (
            <>
              <div className="answer">{result.answer}</div>
              <p className="meta">Retrieval: {result.retrieval}</p>
              <div className="sources">
                <strong>Sources ({result.sources.length}) — verify in the PDF</strong>
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
        LLM keys stay on the server. For recording: use <code>LLM_PROVIDER=groq</code> in
        API <code>.env</code> for fast answers.
      </footer>
    </div>
  );
}
