import {
  Activity,
  BarChart3,
  BrainCircuit,
  Check,
  ClipboardCheck,
  Gauge,
  Moon,
  Settings,
  Sun,
  Upload
} from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useCallback, useEffect, useMemo, useState, type ReactElement, type ReactNode } from "react";
import { scoreBatch, scoreTransaction } from "./lib/api";
import type { ScoreRequest, ScoreResponse } from "./lib/types";

const distribution = [
  { bucket: "0-.2", count: 1880 },
  { bucket: ".2-.4", count: 420 },
  { bucket: ".4-.6", count: 118 },
  { bucket: ".6-.8", count: 38 },
  { bucket: ".8-1", count: 11 }
];

const drift = [
  { hour: "00", psi: 0.04 },
  { hour: "04", psi: 0.08 },
  { hour: "08", psi: 0.05 },
  { hour: "12", psi: 0.03 },
  { hour: "16", psi: 0.06 },
  { hour: "20", psi: 0.11 }
];

type TriageStatus = "new" | "confirmed_fraud" | "not_fraud" | "needs_more_info" | "snoozed" | "watchlist";

type TriageItem = {
  id: string;
  score: number;
  status: TriageStatus;
  amount: number;
  rationale: string;
  note: string;
};

const initialQueue: TriageItem[] = [
  { id: "tx_1042", score: 0.94, status: "new", amount: 842.1, rationale: "High V14 and unusual amount.", note: "" },
  { id: "tx_1049", score: 0.88, status: "watchlist", amount: 391, rationale: "Past-midnight timing.", note: "" },
  { id: "tx_1056", score: 0.81, status: "needs_more_info", amount: 221.77, rationale: "High V10 and V17.", note: "" }
];

export function App() {
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [batchResults, setBatchResults] = useState<ScoreResponse[]>([]);
  const [amount, setAmount] = useState(249);
  const [v14, setV14] = useState(2.1);
  const [queue, setQueue] = useState(initialQueue);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [dark, setDark] = useState(false);
  const [settingsState, setSettingsState] = useState({ fpCost: 1, fnCost: 25, threshold: 0.72 });

  const selected = queue[selectedIndex] ?? queue[0];
  const flaggedCount = queue.filter((item) => item.score >= settingsState.threshold).length;
  const averageScore = queue.reduce((sum, item) => sum + item.score, 0) / Math.max(queue.length, 1);

  useEffect(() => {
    document.documentElement.dataset.theme = dark ? "dark" : "light";
  }, [dark]);

  const updateSelected = useCallback(
    (status: TriageStatus) => {
      if (!selected) return;
      setQueue((items) =>
        items.map((item, index) =>
          index === selectedIndex ? { ...item, status, note: status === "snoozed" ? "Snoozed from keyboard" : item.note } : item
        )
      );
    },
    [selected, selectedIndex]
  );

  const modelRows = useMemo(
    () => [
      { id: "sentinel-synthetic-v0", status: "Active", prAuc: "0.81", recall: "0.78", threshold: settingsState.threshold },
      { id: "logistic-regression-synthetic", status: "Candidate", prAuc: "0.06", recall: "0.25", threshold: 0.96 },
      { id: "random-forest-synthetic", status: "Candidate", prAuc: "0.04", recall: "0.00", threshold: 0.91 }
    ],
    [settingsState.threshold]
  );

  async function submitScore() {
    const response = await scoreTransaction({ Time: 2_400, Amount: amount, V10: 1.8, V14: v14, V17: 2.0 });
    setScore(response);
    setQueue((items) => [
      {
        id: `tx_${Date.now()}`,
        score: response.score,
        status: "new",
        amount,
        rationale: response.rationale,
        note: ""
      },
      ...items
    ]);
    setSelectedIndex(0);
  }

  async function handleCsv(file: File) {
    const text = await file.text();
    const rows = parseCsv(text);
    setBatchResults(await scoreBatch(rows, false));
  }

  useEffect(() => {
    function handleKey(event: KeyboardEvent) {
      if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) return;
      if (event.key === "j") setSelectedIndex((index) => Math.min(index + 1, queue.length - 1));
      if (event.key === "k") setSelectedIndex((index) => Math.max(index - 1, 0));
      if (event.key === "f") updateSelected("confirmed_fraud");
      if (event.key === "n") updateSelected("not_fraud");
      if (event.key === "s") updateSelected("snoozed");
    }
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [queue.length, updateSelected]);

  return (
    <main className="shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Sentinel</p>
          <h1>Fraud operations dashboard</h1>
        </div>
        <nav aria-label="Primary navigation">
          <a href="#overview"><Activity size={16} />Overview</a>
          <a href="#score"><Upload size={16} />Score</a>
          <a href="#triage"><ClipboardCheck size={16} />Triage</a>
          <a href="#models"><BrainCircuit size={16} />Models</a>
          <a href="#settings"><Settings size={16} />Settings</a>
          <button type="button" aria-label="Toggle theme" onClick={() => setDark((value) => !value)}>
            {dark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
        </nav>
      </header>

      <section id="overview" className="grid metrics">
        <Metric icon={<Gauge />} label="Active threshold" value={settingsState.threshold.toFixed(2)} detail="Cost-based operating point" />
        <Metric icon={<BarChart3 />} label="Average queue score" value={averageScore.toFixed(2)} detail="Current analyst queue" />
        <Metric icon={<Activity />} label="Flagged now" value={String(flaggedCount)} detail="Above threshold in queue" />
      </section>

      <section className="grid two">
        <ChartPanel title="Score distribution">
          <BarChart data={distribution}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="bucket" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="count" fill="#3366cc" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ChartPanel>
        <ChartPanel title="Feature drift">
          <AreaChart data={drift}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="hour" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="psi" fill="#37a987" stroke="#1f7a63" />
          </AreaChart>
        </ChartPanel>
      </section>

      <section id="score" className="grid two">
        <article className="panel">
          <h2>Score a transaction</h2>
          <label>Amount<input value={amount} onChange={(event) => setAmount(Number(event.target.value))} type="number" /></label>
          <label>V14<input value={v14} onChange={(event) => setV14(Number(event.target.value))} type="number" step="0.1" /></label>
          <button onClick={submitScore}>Score transaction</button>
          {score && <Explanation score={score} />}
        </article>
        <article className="panel">
          <h2>Batch CSV</h2>
          <label className="dropzone">
            <Upload size={24} />
            <span>Upload CSV with Time, Amount, V10, V14, V17</span>
            <input className="fileInput" type="file" accept=".csv,text/csv" onChange={(event) => event.target.files?.[0] && handleCsv(event.target.files[0])} />
          </label>
          {batchResults.length > 0 && <ResultTable results={batchResults} />}
        </article>
      </section>

      <section id="triage" className="panel">
        <div className="sectionHeader">
          <h2>Triage queue</h2>
          <span>Keyboard: j/k move, f fraud, n not fraud, s snooze</span>
        </div>
        <table>
          <thead><tr><th>ID</th><th>Score</th><th>Status</th><th>Amount</th><th>Action</th></tr></thead>
          <tbody>
            {queue.map((row, index) => (
              <tr key={row.id} className={index === selectedIndex ? "selected" : ""} onClick={() => setSelectedIndex(index)}>
                <td>{row.id}</td>
                <td>{row.score.toFixed(3)}</td>
                <td><span className="chip">{row.status.replaceAll("_", " ")}</span></td>
                <td>${row.amount.toFixed(2)}</td>
                <td>
                  <button type="button" onClick={() => setSelectedIndex(index)}><Check size={14} />Open</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {selected && (
          <div className="drawer">
            <strong>{selected.id}</strong>
            <p>{selected.rationale}</p>
            <div className="buttonRow">
              <button onClick={() => updateSelected("confirmed_fraud")}>Mark fraud</button>
              <button onClick={() => updateSelected("not_fraud")}>Not fraud</button>
              <button onClick={() => updateSelected("needs_more_info")}>More info</button>
              <button onClick={() => updateSelected("snoozed")}>Snooze</button>
              <button onClick={() => updateSelected("watchlist")}>Watchlist</button>
            </div>
          </div>
        )}
      </section>

      <section id="models" className="panel">
        <h2>Models</h2>
        <table>
          <thead><tr><th>Version</th><th>Status</th><th>PR-AUC</th><th>Recall@P0.7</th><th>Threshold</th></tr></thead>
          <tbody>{modelRows.map((row) => <tr key={row.id}><td>{row.id}</td><td>{row.status}</td><td>{row.prAuc}</td><td>{row.recall}</td><td>{row.threshold.toFixed(2)}</td></tr>)}</tbody>
        </table>
      </section>

      <section id="settings" className="panel settingsGrid">
        <h2>Settings</h2>
        <label>False-positive cost<input type="number" value={settingsState.fpCost} onChange={(event) => setSettingsState({ ...settingsState, fpCost: Number(event.target.value) })} /></label>
        <label>False-negative cost<input type="number" value={settingsState.fnCost} onChange={(event) => setSettingsState({ ...settingsState, fnCost: Number(event.target.value) })} /></label>
        <label>Default threshold<input type="number" min="0" max="1" step="0.01" value={settingsState.threshold} onChange={(event) => setSettingsState({ ...settingsState, threshold: Number(event.target.value) })} /></label>
      </section>

      <footer>
        Research / demo project. Not certified for production fraud prevention. No real cardholder data.
      </footer>
    </main>
  );
}

function parseCsv(text: string): ScoreRequest[] {
  const [headerLine, ...lines] = text.trim().split(/\r?\n/);
  const headers = headerLine.split(",").map((header) => header.trim());
  return lines.filter(Boolean).map((line) => {
    const values = line.split(",").map((value) => Number(value.trim()));
    const row = Object.fromEntries(headers.map((header, index) => [header, values[index] ?? 0]));
    return {
      Time: Number(row.Time ?? 0),
      Amount: Number(row.Amount ?? 0),
      V10: Number(row.V10 ?? 0),
      V14: Number(row.V14 ?? 0),
      V17: Number(row.V17 ?? 0)
    };
  });
}

function Metric({ icon, label, value, detail }: { icon: ReactNode; label: string; value: string; detail: string }) {
  return <article className="metric">{icon}<span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

function ChartPanel({ title, children }: { title: string; children: ReactElement }) {
  return <article className="panel"><h2>{title}</h2><ResponsiveContainer width="100%" height={230}>{children}</ResponsiveContainer></article>;
}

function Explanation({ score }: { score: ScoreResponse }) {
  return (
    <div className="explanation">
      <div><strong>{score.label}</strong><span>{score.score.toFixed(3)} at threshold {score.threshold}</span></div>
      <p>{score.rationale}</p>
      <ul>{score.contributions?.map((item) => <li key={item.feature}>{item.feature}: {item.value.toFixed(3)} {item.direction}</li>)}</ul>
    </div>
  );
}

function ResultTable({ results }: { results: ScoreResponse[] }) {
  return (
    <table>
      <thead><tr><th>#</th><th>Score</th><th>Label</th><th>Model</th></tr></thead>
      <tbody>{results.map((row, index) => <tr key={`${row.model_version}-${index}`}><td>{index + 1}</td><td>{row.score.toFixed(3)}</td><td>{row.label}</td><td>{row.model_version}</td></tr>)}</tbody>
    </table>
  );
}
