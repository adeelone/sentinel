import type { ReviewStatus, ScoreRequest, ScoreResponse, Transaction } from "./types";

const API_BASE = (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000").replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, init);
  if (!response.ok) {
    const body = await response.json().catch(() => null);
    const detail = body?.detail ?? body?.error ?? `HTTP ${response.status}`;
    throw new Error(String(detail));
  }
  return response.status === 204 ? (undefined as T) : response.json();
}

export function scoreTransaction(payload: ScoreRequest): Promise<ScoreResponse> {
  return request("/score", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload)
  });
}

export function scoreBatch(rows: ScoreRequest[], explain = true): Promise<ScoreResponse[]> {
  return request(`/score/batch?explain=${String(explain)}`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(rows)
  });
}

export function getTransactions(): Promise<Transaction[]> {
  return request("/transactions?limit=50");
}

export function reviewTransaction(id: string, status: ReviewStatus, note = ""): Promise<Transaction> {
  return request(`/transactions/${id}/review`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ status, note })
  });
}

export function deleteTransaction(id: string): Promise<void> {
  return request(`/transactions/${id}`, { method: "DELETE" });
}
