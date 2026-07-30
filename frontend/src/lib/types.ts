export type ScoreRequest = {
  Time: number;
  Amount: number;
  V10: number;
  V14: number;
  V17: number;
};

export type Contribution = {
  feature: string;
  value: number;
  direction: "positive" | "negative";
};

export type ScoreResponse = {
  score: number;
  label: "flagged" | "clear";
  threshold: number;
  contributions: Contribution[] | null;
  model_version: string;
  rationale: string;
  transaction_id: string | null;
};

export type ReviewStatus = "new" | "confirmed_fraud" | "not_fraud" | "needs_more_info" | "snoozed" | "watchlist";

export type Transaction = {
  id: string;
  score: number;
  label: string;
  threshold: number;
  status: ReviewStatus;
  created_at: number;
  transaction: Record<string, number>;
  contributions: Contribution[] | null;
  note: string | null;
};
