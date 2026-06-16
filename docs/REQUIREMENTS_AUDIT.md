# Requirements Audit

Source: `C:\Users\adeem\Downloads\sentinel-codex-prompt.md`

Date: 2026-06-16

This audit reflects the current local prototype. It is not a claim that Sentinel is production-ready or complete against the full prompt.

## Summary

- PASS: 28
- PARTIAL: 28
- FAIL: 23

Phase 3 from the humanization brief was not completed because the repo has no `origin` remote and the requested `REPO_URL` variable was not supplied.

## Hard Rules

| Requirement | Status | Evidence |
| --- | --- | --- |
| No real PII or cardholder data | PASS | README, `.gitignore`, and synthetic generator avoid real card data; no `data/raw` content is tracked. |
| README prominently states no real PII/cardholder data | PASS | `README.md` opens with the no-PII warning. |
| Do not use accuracy as primary metric | PASS | `README.md`, `METRICS.md`, and evaluation code use precision, recall, F2, and cost. |
| Use PR-AUC, recall at fixed precision, and cost-weighted loss as primary metrics | PARTIAL | Docs mention them; current smoke evaluator only implements a PR-AUC proxy, recall, F2, and cost. |
| UI and README disclaimer | PASS | Footer and README include the required research/demo disclaimer. |

## Product Pillars

| Requirement | Status | Evidence |
| --- | --- | --- |
| Single command for reproducible pipeline/report | PARTIAL | `make train` writes `reports/{run_id}/metrics.json` and `report.md`; it only covers synthetic smoke training. |
| Honest imbalance-aware evaluation | PARTIAL | Cost thresholding and non-accuracy metrics exist; calibration, full PR/ROC curves, and per-threshold reporting are missing. |
| Explainability first | PARTIAL | API returns heuristic feature contributions; full SHAP computation is not implemented. |
| Calm, premium UX | PASS | React dashboard uses restrained layout, cards, tables, and charts rather than a cyber/neon theme. |
| Pluggable models/transforms/datasets | PARTIAL | Registries and interfaces exist, but heavy adapters are not implemented. |
| Self-contained Docker demo with API, UI, Postgres, Redis, MLflow, MinIO | PARTIAL | Compose includes all services; seeded model/artifact wiring is not complete. |

## Data Layer

| Requirement | Status | Evidence |
| --- | --- | --- |
| Kaggle ULB dataset attribution | PASS | README and providers docs name the Kaggle ULB dataset. |
| Kaggle CLI auto-download | PARTIAL | `ml/sentinel_ml/data/download.py` detects env vars and prints the command; it does not invoke the Kaggle CLI. |
| Manual download path documented | PASS | README/providers docs mention `data/raw/creditcard.csv`. |
| Synthetic imbalanced generator | PASS | `ml/sentinel_ml/data/synthetic.py` generates synthetic rows near the requested fraud rate. |
| Correlated features, temporal spikes, log-normal amounts, merchant/category buckets | PASS | Synthetic generator includes latent bucket signal, night factor, log-normal amount, and synthetic buckets. |
| Pydantic plus pandera schema validation | PARTIAL | Pydantic input validation exists in the API; pandera validation is missing. |
| Versioned materialized splits and MinIO hashes | FAIL | No content-hash split materialization or MinIO storage is implemented. |

## Feature Engineering

| Requirement | Status | Evidence |
| --- | --- | --- |
| Deterministic sklearn pipeline and custom transformers | PARTIAL | Deterministic helper functions exist; no sklearn `Pipeline` object is assembled. |
| Robust scaling for `Amount` and `Time` | PARTIAL | Robust stats helpers exist but are not wired into training/serving. |
| Cyclical time encoding | PASS | `cyclical_time` is implemented. |
| Optional synthetic aggregation features | FAIL | Rolling per-card counts/sums are not implemented. |
| Winsorization | PASS | `winsorize` helper exists. |
| Pickled transformers with model bundle | FAIL | No persisted model bundle is implemented. |

## Models

| Requirement | Status | Evidence |
| --- | --- | --- |
| Logistic regression adapter | PARTIAL | Registry has a slot mapped to the smoke heuristic. |
| Random forest adapter | PARTIAL | Registry has a slot mapped to the smoke heuristic. |
| XGBoost adapter | PARTIAL | Registry has a slot mapped to the smoke heuristic. |
| LightGBM adapter | PARTIAL | Registry has a slot mapped to the smoke heuristic. |
| Isolation forest adapter | PARTIAL | Registry has a slot mapped to the smoke heuristic. |
| PyTorch autoencoder | PARTIAL | Registry has a slot mapped to the smoke heuristic; no PyTorch model exists. |
| Stacked ensemble | PARTIAL | Registry has a slot mapped to the smoke heuristic. |
| Stratified 5-fold CV and time split mode | FAIL | No CV orchestration exists. |
| Class weights | FAIL | No real estimator training uses class weights. |
| SMOTE/ADASYN train-fold only | FAIL | Not implemented. |
| Threshold moving | PASS | Smoke model selects the threshold by expected cost. |

## Evaluation And Reporting

| Requirement | Status | Evidence |
| --- | --- | --- |
| Full primary metrics list | PARTIAL | Current evaluator has precision, recall, F2, PR-AUC proxy, and cost only. |
| Cost-weighted loss with configurable FP/FN cost | PARTIAL | Cost is implemented with fixed costs. |
| Calibration and reliability diagram | FAIL | Not implemented. |
| Confusion matrix at threshold | PASS | `confusion` returns `tp/fp/tn/fn`. |
| Per-segment performance | FAIL | Not implemented. |
| Report files under `reports/{run_id}` | PARTIAL | `metrics.json` and `report.md` are written; chart/image outputs are missing. |
| MLflow tracker abstraction | PARTIAL | `ExperimentTracker` and `NoopTracker` exist; MLflow logging is not wired. |

## Explainability

| Requirement | Status | Evidence |
| --- | --- | --- |
| SHAP values for tree models | FAIL | `shap_utils.py` delegates to heuristic contributions only. |
| Per-prediction top positive/negative contributions | PARTIAL | API returns feature contributions but not true SHAP values or positive/negative groups. |
| Human-readable rationale | PASS | API response includes a rationale string. |
| Dashboard global explanations, PDPs, SHAP summary | FAIL | Dashboard does not include those model-report views. |

## API Service

| Requirement | Status | Evidence |
| --- | --- | --- |
| `POST /score` | PASS | Implemented in `backend/app/api/routes.py`. |
| `POST /score/batch` JSON or CSV | PARTIAL | CSV and optional body path exist; streaming response is not implemented. |
| `GET /models` | PASS | Implemented with active model metadata. |
| `POST /models/{id}/activate` admin-gated | PARTIAL | Endpoint exists; admin gate is missing. |
| `GET /transactions` paginated/filterable | PARTIAL | Feed exists; pagination/filtering are missing. |
| `GET /transactions/{id}` | PASS | Implemented. |
| `POST /transactions/{id}/review` | PASS | Implemented in memory. |
| `POST /retrain` admin-gated/background | PARTIAL | Endpoint returns queued; admin gate and job queue are missing. |
| `GET /metrics` Prometheus-compatible | PARTIAL | Text metrics endpoint exists with minimal counters. |
| `GET /healthz`, `GET /readyz` | PASS | Implemented. |
| API key admin auth and rate limits | FAIL | Not implemented. |
| Pydantic v2 input validation and trace IDs | PARTIAL | Pydantic models exist; trace IDs are missing. |

## Dashboard

| Requirement | Status | Evidence |
| --- | --- | --- |
| Overview | PASS | Dashboard has status metrics, score distribution, drift chart, and flagged list. |
| Single scoring form | PASS | Form calls `/score` with local fallback. |
| Batch CSV upload UI | PARTIAL | Dropzone copy exists; upload behavior is not wired. |
| Why drawer with SHAP contributions | PARTIAL | Contributions render as JSON; no drawer or true SHAP. |
| Triage queue with labels/notes/snooze/watchlist | PARTIAL | Queue table exists; actions are not wired. |
| Keyboard shortcuts | FAIL | Not implemented. |
| Models report and activate | PARTIAL | Model row and activate button exist; report details are missing. |
| Drift and monitoring settings | PARTIAL | PSI chart exists; alert config is missing. |
| Settings | PARTIAL | Navigation link exists; settings screen is not implemented. |
| Mobile responsive | PASS | CSS includes mobile layout rules. |
| Light and dark themes | PARTIAL | Light theme exists; dark theme is missing. |
| Skeletons and empty states | FAIL | Not implemented. |
| Accessibility and keyboard nav | PARTIAL | Semantic elements are present; full WCAG/shortcut behavior is incomplete. |
| i18n English and Spanish scaffolding | FAIL | Not implemented. |

## Performance And Resilience

| Requirement | Status | Evidence |
| --- | --- | --- |
| Fast single-row scoring target | PARTIAL | Heuristic scoring is fast; no benchmark exists. |
| Async FastAPI and RQ jobs | PARTIAL | FastAPI is present; routes are sync and RQ is not wired. |
| Rate limiting | FAIL | Not implemented. |
| Model load caching | FAIL | Not implemented. |
| Graceful degradation when explanations fail | PARTIAL | ML `explain` helper catches exceptions; API scoring path does not. |
| Lighthouse targets | FAIL | Not measured. |

## Privacy And Security

| Requirement | Status | Evidence |
| --- | --- | --- |
| No real cardholder data | PASS | No raw data is tracked; docs warn against it. |
| Uploaded CSVs in memory by default | PARTIAL | Batch CSV is read in memory; no persistence layer exists. |
| Analyst labels in Postgres and delete-my-data | FAIL | Labels are in memory; delete flow is missing. |
| API keys hashed at rest | FAIL | Not implemented. |
| Secrets via env vars | PARTIAL | `.env.example` exists; some service defaults are demo values. |

## Tooling, Docs, GitHub

| Requirement | Status | Evidence |
| --- | --- | --- |
| Python and frontend package files | PASS | `pyproject.toml`, `package.json`, and `package-lock.json` exist. |
| Ruff, Black, mypy, ESLint, Prettier, tsc | PASS | Tooling is configured in package files and workflows. |
| Pre-commit and Husky/lint-staged | PASS | `.pre-commit-config.yaml`, `.husky/pre-commit`, and lint-staged config exist. |
| Tailwind and shadcn/ui | FAIL | The dashboard uses plain CSS, not Tailwind/shadcn. |
| Makefile commands | PASS | `Makefile` includes install, dev, data, train, evaluate, report, serve, worker, test, lint, format, typecheck, migrate, seed, and clean. |
| Dockerfiles and Docker Compose | PASS | Present under `backend`, `frontend`, and `infra`. |
| GitHub Actions | PASS | CI, e2e, and release workflows exist. |
| GitHub repo private publish | FAIL | Not pushed; no `origin` remote exists. |
| Branch protection, release, discussions, issues, social preview | FAIL | Not possible until the GitHub repo exists. |
