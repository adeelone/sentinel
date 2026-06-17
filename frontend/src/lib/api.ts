import type { ScoreRequest, ScoreResponse } from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function scoreTransaction(payload: ScoreRequest): Promise<ScoreResponse> {
  try {
    const response = await fetch(`${API_BASE}/score`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(payload)
    });
    if (!response.ok) throw new Error(`Score failed: ${response.status}`);
    return await response.json();
  } catch {
    const score = Math.min(0.99, Math.max(0.01, payload.V14 * 0.2 + payload.V17 * 0.15 + payload.Amount / 1000));
    return {
      score,
      label: score >= 0.72 ? "flagged" : "clear",
      threshold: 0.72,
      model_version: "local-demo",
      rationale: "Local fallback score for dashboard demo.",
      contributions: [
        { feature: "V14", value: payload.V14 * 0.2, direction: "positive" },
        { feature: "Amount", value: payload.Amount / 1000, direction: "positive" }
      ]
    };
  }
}

export async function scoreBatch(rows: ScoreRequest[], explain = true): Promise<ScoreResponse[]> {
  try {
    const response = await fetch(`${API_BASE}/score/batch?explain=${String(explain)}`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(rows)
    });
    if (!response.ok) throw new Error(`Batch score failed: ${response.status}`);
    return await response.json();
  } catch {
    return Promise.all(rows.map((row) => scoreTransaction(row)));
  }
}
