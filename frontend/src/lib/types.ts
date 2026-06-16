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
};

