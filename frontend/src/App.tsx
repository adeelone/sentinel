import {
  Activity,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  ClipboardCheck,
  Gauge,
  LoaderCircle,
  Moon,
  RefreshCw,
  Search,
  Settings,
  ShieldCheck,
  Sun,
  Trash2,
  Upload
} from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { deleteTransaction, getTransactions, reviewTransaction, scoreBatch, scoreTransaction } from "./lib/api";
import type { ReviewStatus, ScoreRequest, ScoreResponse, Transaction } from "./lib/types";

const models = [
  { name: "Sentinel synthetic v0", state: "Active", prAuc: "0.81", recall: "0.78" },
  { name: "Logistic regression", state: "Candidate", prAuc: "0.06", recall: "0.25" },
  { name: "Random forest", state: "Candidate", prAuc: "0.04", recall: "0.00" }
];

export function App() {
  const [amount, setAmount] = useState(249);
  const [hour, setHour] = useState(22);
  const [v10, setV10] = useState(1.8);
  const [v14, setV14] = useState(2.1);
  const [v17, setV17] = useState(2);
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [queue, setQueue] = useState<Transaction[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [batchResults, setBatchResults] = useState<ScoreResponse[]>([]);
  const [busy, setBusy] = useState(false);
  const [loadingQueue, setLoadingQueue] = useState(true);
  const [error, setError] = useState("");
  const [dark, setDark] = useState(false);

  const selected = queue.find((item) => item.id === selectedId) ?? queue[0];
  const average = queue.reduce((total, item) => total + item.score, 0) / Math.max(queue.length, 1);
  const flagged = queue.filter((item) => item.label === "flagged").length;

  const loadQueue = useCallback(async () => {
    setLoadingQueue(true);
    try {
      const records = await getTransactions();
      setQueue(records);
      setSelectedId((current) => current ?? records[0]?.id ?? null);
      setError("");
    } catch (caught) {
      setError(message(caught, "Could not reach the scoring API."));
    } finally {
      setLoadingQueue(false);
    }
  }, []);

  useEffect(() => {
    void loadQueue();
  }, [loadQueue]);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  const review = useCallback(async (status: ReviewStatus) => {
    if (!selected) return;
    try {
      const updated = await reviewTransaction(selected.id, status);
      setQueue((items) => items.map((item) => item.id === updated.id ? updated : item));
      setError("");
    } catch (caught) {
      setError(message(caught, "Review could not be saved."));
    }
  }, [selected]);

  useEffect(() => {
    function onKey(event: KeyboardEvent) {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
      const index = queue.findIndex((item) => item.id === selected?.id);
      if (event.key === "j") setSelectedId(queue[Math.min(index + 1, queue.length - 1)]?.id ?? null);
      if (event.key === "k") setSelectedId(queue[Math.max(index - 1, 0)]?.id ?? null);
      if (event.key === "f") void review("confirmed_fraud");
      if (event.key === "n") void review("not_fraud");
      if (event.key === "s") void review("snoozed");
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [queue, review, selected?.id]);

  async function submitScore() {
    setBusy(true);
    try {
      const result = await scoreTransaction({ Time: hour * 3600, Amount: amount, V10: v10, V14: v14, V17: v17 });
      setScore(result);
      await loadQueue();
      setSelectedId(result.transaction_id);
      setError("");
    } catch (caught) {
      setError(message(caught, "Transaction could not be scored."));
    } finally {
      setBusy(false);
    }
  }

  async function uploadCsv(file: File) {
    setBusy(true);
    try {
      setBatchResults(await scoreBatch(parseCsv(await file.text()), false));
      await loadQueue();
      setError("");
    } catch (caught) {
      setError(message(caught, "CSV could not be scored."));
    } finally {
      setBusy(false);
    }
  }

  async function removeSelected() {
    if (!selected) return;
    try {
      await deleteTransaction(selected.id);
      setSelectedId(null);
      await loadQueue();
    } catch (caught) {
      setError(message(caught, "Transaction could not be deleted."));
    }
  }

  return (
    <div className="appShell">
      <aside className="sidebar">
        <a className="brand" href="#score" aria-label="Sentinel home"><ShieldCheck /> Sentinel</a>
        <nav aria-label="Primary navigation">
          <a href="#overview"><BarChart3 />Overview</a>
          <a className="active" href="#score"><Gauge />Score</a>
          <a href="#triage"><ClipboardCheck />Triage</a>
          <a href="#models"><BrainCircuit />Models</a>
          <a href="#drift"><Activity />Drift</a>
        </nav>
        <div className="sideBottom">
          <a href="#settings"><Settings />Settings</a>
          <span>AR <small>Analyst</small></span>
        </div>
      </aside>

      <main>
        <header className="topbar">
          <div><h1>Score a transaction</h1><p>Review model output before making a decision.</p></div>
          <div className="topActions">
            <span>Research demo — synthetic data only</span>
            <button className="iconButton" aria-label="Toggle theme" onClick={() => setDark((value) => !value)}>
              {dark ? <Sun /> : <Moon />}
            </button>
          </div>
        </header>

        {error && <div className="errorBanner" role="alert">{error}<button onClick={loadQueue}><RefreshCw />Retry</button></div>}

        <section id="score" className="scoreGrid">
          <article className="surface formPanel">
            <div className="sectionTitle"><h2>Score a transaction</h2><span>All fields use anonymized features.</span></div>
            <div className="formGrid">
              <Field label="Amount (USD)" value={amount} onChange={setAmount} />
              <Field label="Transaction hour" value={hour} onChange={setHour} min={0} max={23} />
              <Field label="V10" value={v10} onChange={setV10} step={0.1} />
              <Field label="V14" value={v14} onChange={setV14} step={0.1} />
              <Field label="V17" value={v17} onChange={setV17} step={0.1} />
            </div>
            <button className="primary" disabled={busy} onClick={submitScore}>
              {busy ? <LoaderCircle className="spin" /> : <Search />} Score transaction
            </button>
            <label className="uploadButton"><Upload />Score a CSV<input type="file" accept=".csv,text/csv" onChange={(event) => event.target.files?.[0] && void uploadCsv(event.target.files[0])} /></label>
            {batchResults.length > 0 && <small>{batchResults.length} CSV rows scored and added to the queue.</small>}
          </article>

          <article className="surface riskPanel">
            <h2>Risk score</h2>
            {score ? (
              <>
                <div className={`riskRing ${score.label}`} style={{ "--score": `${score.score * 360}deg` } as React.CSSProperties}>
                  <div><strong>{score.score.toFixed(2)}</strong><span>{score.label === "flagged" ? "High risk" : "Below threshold"}</span></div>
                </div>
                <p>Threshold {score.threshold.toFixed(2)} · {score.model_version}</p>
              </>
            ) : <Empty icon={<Gauge />} text="Score a transaction to see its risk." />}
          </article>

          <article className="surface reasonPanel">
            <h2>Why this was flagged</h2>
            {score ? <><p>{score.rationale}</p><ContributionList score={score} /></> : <Empty icon={<Activity />} text="The explanation will show the strongest model contributions." />}
          </article>
        </section>

        <section id="overview" className="summaryRow">
          <Summary label="Queue size" value={String(queue.length)} detail="stored reviews" />
          <Summary label="Flagged" value={String(flagged)} detail="above model threshold" />
          <Summary label="Average risk" value={average.toFixed(2)} detail="current queue" />
          <Summary label="Drift PSI" value="0.11" detail="stable synthetic baseline" />
        </section>

        <section id="triage" className="contentGrid">
          <article className="surface queuePanel">
            <div className="sectionTitle"><div><h2>Review queue</h2><span>j/k move · f fraud · n not fraud · s snooze</span></div><button className="quiet" onClick={loadQueue}><RefreshCw />Refresh</button></div>
            {loadingQueue ? <div className="loadingRows"><i /><i /><i /></div> : queue.length === 0 ? (
              <Empty icon={<ClipboardCheck />} text="No transactions yet. Score one above to start the queue." />
            ) : (
              <div className="tableWrap"><table><thead><tr><th>Risk</th><th>Amount</th><th>Time</th><th>Status</th><th>Reason</th></tr></thead>
                <tbody>{queue.map((item) => <tr key={item.id} className={selected?.id === item.id ? "selected" : ""} onClick={() => setSelectedId(item.id)}>
                  <td><strong className={item.label}>{item.score.toFixed(2)}</strong></td>
                  <td>${Number(item.transaction.Amount ?? 0).toFixed(2)}</td>
                  <td>{new Date(item.created_at * 1000).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</td>
                  <td>{item.status.replaceAll("_", " ")}</td>
                  <td>{item.contributions?.[0]?.feature ?? "Model score"}</td>
                </tr>)}</tbody>
              </table></div>
            )}
            {selected && <div className="reviewBar"><div><strong>{selected.id.slice(0, 8)}</strong><span>{selected.note || "Choose an analyst outcome."}</span></div>
              <div><button onClick={() => review("confirmed_fraud")}>Fraud</button><button onClick={() => review("not_fraud")}>Not fraud</button><button onClick={() => review("needs_more_info")}>More info</button><button onClick={() => review("snoozed")}>Snooze</button><button className="danger" aria-label="Delete transaction" onClick={removeSelected}><Trash2 /></button></div>
            </div>}
          </article>

          <aside className="rightRail">
            <article id="models" className="surface compact"><div className="sectionTitle"><h2>Models</h2><span className="healthy"><CheckCircle2 />Healthy</span></div>
              {models.map((model) => <div className="modelRow" key={model.name}><div><strong>{model.name}</strong><span>{model.state}</span></div><span>PR-AUC {model.prAuc}</span></div>)}
            </article>
            <article id="drift" className="surface compact"><div className="sectionTitle"><h2>Drift</h2><span className="healthy">Stable</span></div>
              <div className="driftLine"><span>Amount</span><i style={{ width: "42%" }} /><strong>0.11</strong></div>
              <div className="driftLine"><span>Hour</span><i style={{ width: "24%" }} /><strong>0.06</strong></div>
              <div className="driftLine"><span>V14</span><i style={{ width: "35%" }} /><strong>0.09</strong></div>
            </article>
          </aside>
        </section>

        <footer>Research / demo project. Not certified for production fraud prevention. No real cardholder data.</footer>
      </main>
    </div>
  );
}

function Field({ label, value, onChange, min, max, step = 1 }: { label: string; value: number; onChange: (value: number) => void; min?: number; max?: number; step?: number }) {
  return <label>{label}<input type="number" value={value} min={min} max={max} step={step} onChange={(event) => onChange(Number(event.target.value))} /></label>;
}

function Summary({ label, value, detail }: { label: string; value: string; detail: string }) {
  return <article><span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

function ContributionList({ score }: { score: ScoreResponse }) {
  const max = Math.max(...(score.contributions?.map((item) => Math.abs(item.value)) ?? [1]), 0.01);
  return <ul className="contributions">{score.contributions?.map((item) => <li key={item.feature}><div><strong>{item.feature}</strong><span>{item.value > 0 ? "+" : ""}{item.value.toFixed(3)}</span></div><i><b style={{ width: `${Math.abs(item.value) / max * 100}%` }} /></i></li>)}</ul>;
}

function Empty({ icon, text }: { icon: React.ReactNode; text: string }) {
  return <div className="empty">{icon}<p>{text}</p></div>;
}

function parseCsv(text: string): ScoreRequest[] {
  const [headerLine = "", ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",").map((header) => header.trim());
  return lines.filter(Boolean).map((line) => {
    const row = Object.fromEntries(headers.map((header, index) => [header, Number(line.split(",")[index]?.trim() ?? 0)]));
    return { Time: row.Time ?? 0, Amount: row.Amount ?? 0, V10: row.V10 ?? 0, V14: row.V14 ?? 0, V17: row.V17 ?? 0 };
  });
}

function message(error: unknown, fallback: string): string {
  return error instanceof Error ? `${fallback} ${error.message}` : fallback;
}
