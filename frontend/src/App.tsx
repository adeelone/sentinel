import { Activity, BarChart3, BrainCircuit, ClipboardCheck, Gauge, Settings, Upload } from "lucide-react";
import { Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { useMemo, useState } from "react";
import { scoreTransaction } from "./lib/api";
import type { ScoreResponse } from "./lib/types";

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

export function App() {
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [amount, setAmount] = useState(249);
  const [v14, setV14] = useState(2.1);
  const flagged = useMemo(() => [
    { id: "tx_1042", score: 0.94, status: "Needs review", amount: "$842.10" },
    { id: "tx_1049", score: 0.88, status: "Watchlist", amount: "$391.00" },
    { id: "tx_1056", score: 0.81, status: "New", amount: "$221.77" }
  ], []);

  async function submitScore() {
    setScore(await scoreTransaction({ Time: 2_400, Amount: amount, V10: 1.8, V14: v14, V17: 2.0 }));
  }

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
        </nav>
      </header>

      <section id="overview" className="grid metrics">
        <Metric icon={<Gauge />} label="Active threshold" value="0.72" detail="Cost-minimized validation point" />
        <Metric icon={<BarChart3 />} label="PR-AUC proxy" value="0.81" detail="Synthetic smoke baseline" />
        <Metric icon={<Activity />} label="Flagged today" value="11" detail="0.44% of scored traffic" />
      </section>

      <section className="grid two">
        <article className="panel">
          <h2>Score distribution</h2>
          <ResponsiveContainer width="100%" height={230}>
            <BarChart data={distribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="bucket" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3366cc" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </article>
        <article className="panel">
          <h2>Feature drift</h2>
          <ResponsiveContainer width="100%" height={230}>
            <AreaChart data={drift}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="hour" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="psi" fill="#37a987" stroke="#1f7a63" />
            </AreaChart>
          </ResponsiveContainer>
        </article>
      </section>

      <section id="score" className="grid two">
        <article className="panel">
          <h2>Score a transaction</h2>
          <label>Amount<input value={amount} onChange={(event) => setAmount(Number(event.target.value))} type="number" /></label>
          <label>V14<input value={v14} onChange={(event) => setV14(Number(event.target.value))} type="number" step="0.1" /></label>
          <button onClick={submitScore}>Score transaction</button>
          {score && <pre>{JSON.stringify(score, null, 2)}</pre>}
        </article>
        <article className="panel">
          <h2>Batch CSV</h2>
          <div className="dropzone">Drop a CSV with Time, Amount, V1..V28, and optional synthetic metadata.</div>
        </article>
      </section>

      <section id="triage" className="panel">
        <h2>Triage queue</h2>
        <table>
          <thead><tr><th>ID</th><th>Score</th><th>Status</th><th>Amount</th></tr></thead>
          <tbody>{flagged.map((row) => <tr key={row.id}><td>{row.id}</td><td>{row.score}</td><td>{row.status}</td><td>{row.amount}</td></tr>)}</tbody>
        </table>
      </section>

      <section id="models" className="panel">
        <h2>Models</h2>
        <div className="modelRow"><strong>sentinel-synthetic-v0</strong><span>Active</span><span>Recall@P0.7 0.78</span><button>Activate</button></div>
      </section>

      <footer>
        Research / demo project. Not certified for production fraud prevention. No real cardholder data.
      </footer>
    </main>
  );
}

function Metric({ icon, label, value, detail }: { icon: React.ReactNode; label: string; value: string; detail: string }) {
  return <article className="metric">{icon}<span>{label}</span><strong>{value}</strong><small>{detail}</small></article>;
}

