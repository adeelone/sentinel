# Requirements Audit

Source: `sentinel-codex-prompt.md`

Date: 2026-07-29

This audit reflects the current implementation. Sentinel is now a working research/demo app with a real synthetic-data ML training path, API, dashboard, CI, release, and GitHub repo. It is still not certified for production fraud prevention.

## Summary

- PASS: 54
- PARTIAL: 13
- FAIL: 12

Public repo: `https://github.com/adeelone/sentinel`

## Hard Rules

| Requirement | Status | Evidence |
| --- | --- | --- |
| No real PII or cardholder data | PASS | README, `.gitignore`, and synthetic generator avoid real card data; no `data/raw` content is tracked. |
| README prominently states no real PII/cardholder data | PASS | `README.md` opens with the no-PII warning. |
| Do not use accuracy as primary metric | PASS | Docs and evaluator use PR-AUC, recall at fixed precision, F2, Brier score, and cost. |
| Primary metrics are PR-AUC, recall at fixed precision, and cost-weighted loss | PASS | `ml/sentinel_ml/evaluate.py` computes those metrics. |
| UI and README disclaimer | PASS | Footer and README include the required research/demo disclaimer. |

## Product Pillars

| Requirement | Status | Evidence |
| --- | --- | --- |
| Single command for reproducible pipeline/report | PASS | `make train` trains real sklearn models, writes metrics, report, and `model_bundle.joblib`. |
| Honest imbalance-aware evaluation | PASS | Evaluator includes cost thresholds, PR-AUC, ROC-AUC, Brier score, fixed operating metrics, confusion matrix, and segment metrics. |
| Explainability first | PARTIAL | API and dashboard show feature contributions; true SHAP values are not implemented. |
| Calm, premium UX | PASS | Dashboard uses restrained operational layout, tables, charts, and theme controls. |
| Pluggable models/transforms/datasets | PARTIAL | Registry and sklearn adapters exist; heavy adapters are not all implemented. |
| Self-contained Docker demo | PASS | Compose runs the UI, trained-bundle API, worker, Postgres, Redis, and MinIO artifact storage. |

## Data Layer

| Requirement | Status | Evidence |
| --- | --- | --- |
| Kaggle ULB attribution | PASS | README and providers docs name the Kaggle ULB dataset. |
| Kaggle CLI auto-download | PARTIAL | Script detects credentials and prints the Kaggle command; it does not execute the CLI. |
| Manual download path documented | PASS | README/providers docs mention `data/raw/creditcard.csv`. |
| Synthetic imbalanced generator | PASS | Synthetic generator creates imbalanced rows with temporal, amount, and bucket signals. |
| Pydantic plus pandera validation | PARTIAL | Pydantic validation exists for synthetic rows and API inputs; pandera is not wired. |
| Versioned materialized splits | PARTIAL | Synthetic CSV output uses content-hash filenames; MinIO split storage is not wired. |

## Feature Engineering

| Requirement | Status | Evidence |
| --- | --- | --- |
| Deterministic sklearn pipeline | PASS | Logistic regression, random forest, and isolation forest use sklearn `Pipeline`. |
| Robust scaling for `Amount` and `Time` | PASS | Pipelines include `RobustScaler`. |
| Cyclical time encoding | PASS | `cyclical_time` is implemented. |
| Optional synthetic aggregation features | FAIL | Rolling per-card counts/sums are not implemented. |
| Winsorization | PASS | `winsorize` helper exists. |
| Pickled transformers with model bundle | PASS | `train.py` writes a `joblib` bundle containing the fitted pipeline. |

## Models

| Requirement | Status | Evidence |
| --- | --- | --- |
| Logistic regression | PASS | Class-weighted sklearn logistic regression trains through the registry. |
| Random forest | PASS | Capped-depth class-weighted random forest trains through the registry. |
| XGBoost | FAIL | Not implemented. |
| LightGBM | FAIL | Not implemented. |
| Isolation forest | PASS | sklearn isolation forest anomaly baseline trains through the registry. |
| PyTorch autoencoder | FAIL | Not implemented. |
| Stacked ensemble | FAIL | Not implemented. |
| Stratified 5-fold CV and time split mode | FAIL | Current path uses a stratified train/test split, not 5-fold CV or time split mode. |
| Class weights | PASS | Logistic regression and random forest use class-weighted training. |
| SMOTE/ADASYN train-fold only | FAIL | Not implemented. |
| Threshold moving | PASS | Threshold is selected by expected cost on training scores. |

## Evaluation And Reporting

| Requirement | Status | Evidence |
| --- | --- | --- |
| Full primary metrics list | PASS | Evaluator computes PR-AUC, ROC-AUC, recall/precision operating metrics, F2, Brier score, and cost. |
| Cost-weighted loss with configurable FP/FN cost | PARTIAL | Cost config exists in code; CLI/env override is not exposed. |
| Calibration | PARTIAL | Brier score is computed; reliability diagram image is not generated. |
| Confusion matrix | PASS | `confusion` returns `tp/fp/tn/fn` at the selected threshold. |
| Per-segment performance | PASS | Evaluation reports amount bucket and day/night segment metrics. |
| Reports under `reports/{run_id}` | PARTIAL | Metrics, markdown report, and model bundle are written; chart PNG/SVG files are not generated. |
| MLflow tracker abstraction | PARTIAL | Tracker interface exists; real MLflow logging is not wired. |

## Explainability

| Requirement | Status | Evidence |
| --- | --- | --- |
| SHAP values for tree models | FAIL | True SHAP computation is not implemented. |
| Per-prediction explanations | PARTIAL | Top feature contributions are returned, but they are model-derived approximations rather than SHAP values. |
| Human-readable rationale | PASS | API response includes a rationale string. |
| Dashboard global explanations/PDPs | FAIL | Dashboard does not include PDPs or SHAP summary plots. |

## API Service

| Requirement | Status | Evidence |
| --- | --- | --- |
| `POST /score` | PASS | Implemented. |
| `POST /score/batch` JSON or CSV | PARTIAL | JSON and CSV work; streaming response is not implemented. |
| `GET /models` | PASS | Implemented with active model metadata. |
| `POST /models/{id}/activate` admin-gated | PASS | Requires `x-admin-key`. |
| `GET /transactions` paginated/filterable | PASS | Supports status, label, score range, limit, and offset. |
| `GET /transactions/{id}` | PASS | Implemented. |
| `POST /transactions/{id}/review` | PASS | Implemented in memory. |
| `POST /retrain` background retrain | PASS | Admin-gated jobs are queued in Redis, processed by the worker, uploaded to artifact storage, and exposed through job status. |
| `GET /metrics` | PASS | Prometheus text includes request counts, latency percentiles, and model load count. |
| `GET /healthz`, `GET /readyz` | PASS | Implemented. |
| API key admin auth and rate limits | PASS | Admin key and in-memory per-key/IP rate limit are implemented. |
| Pydantic validation and trace IDs | PASS | Validation errors include trace IDs. |

## Dashboard

| Requirement | Status | Evidence |
| --- | --- | --- |
| Overview | PASS | Shows threshold, queue score, flagged count, score distribution, and drift chart. |
| Single scoring form | PASS | Scores one transaction and adds it to the triage queue. |
| Batch CSV upload | PASS | CSV upload scores rows and renders a result table. |
| Why drawer/contributions | PARTIAL | Explanation panel shows rationale and contributions; true SHAP drawer is not implemented. |
| Triage queue | PASS | Analyst can mark fraud, not fraud, more info, snooze, and watchlist. |
| Keyboard shortcuts | PASS | `j/k/f/n/s` shortcuts work outside inputs. |
| Models view | PARTIAL | Model table exists; full inline report viewer is missing. |
| Drift and monitoring | PARTIAL | PSI chart exists; alert webhook/email settings are missing. |
| Settings | PASS | FP/FN cost and threshold inputs exist. |
| Mobile responsive | PASS | CSS includes responsive single-column layout. |
| Light and dark themes | PASS | Theme toggle uses CSS variables. |
| Skeletons and empty states | PASS | Queue loading, empty scoring/explanation, and API error/retry states are implemented. |
| Accessibility | PARTIAL | Semantic elements and ARIA label exist; full WCAG audit is not done. |
| i18n English/Spanish | FAIL | Not implemented. |

## Performance And Resilience

| Requirement | Status | Evidence |
| --- | --- | --- |
| Fast single-row scoring | PARTIAL | Runtime model is fast, but no benchmark is committed. |
| Async FastAPI and RQ jobs | PARTIAL | Batch endpoint is async; RQ jobs are not wired. |
| Rate limiting | PASS | Scoring endpoints use an in-memory rate limiter. |
| Model load caching | PASS | The versioned bundle is cached per process and atomically refreshed from artifact storage on a bounded interval. |
| Graceful explanation degradation | PASS | API returns predictions with `contributions: null` if contribution generation fails. |
| Lighthouse targets | FAIL | Not measured. |

## Privacy And Security

| Requirement | Status | Evidence |
| --- | --- | --- |
| No real cardholder data | PASS | No raw data is tracked; docs warn against it. |
| Uploaded CSVs processed in memory | PASS | Batch CSVs are read from upload content and not persisted. |
| Analyst labels in Postgres and delete-my-data | PASS | SQLAlchemy persists reviews in Postgres in production, Alembic owns the schema, and the UI/API delete individual records. |
| API keys hashed at rest | FAIL | Demo admin key is env/config based; persistent key store is not implemented. |
| Secrets via env vars | PASS | Production rejects placeholder admin keys and receives database, Redis, and artifact credentials only through service variables. |

## Tooling, Docs, GitHub

| Requirement | Status | Evidence |
| --- | --- | --- |
| Python and frontend package files | PASS | `pyproject.toml`, `package.json`, and lockfile exist. |
| Ruff, Black, mypy, ESLint, Prettier, tsc | PASS | Tooling is configured in package files and workflows. |
| Pre-commit and Husky/lint-staged | PASS | Hook configs are present. |
| Tailwind and shadcn/ui | FAIL | Dashboard uses plain CSS. |
| Makefile commands | PASS | Required Make targets exist. |
| Dockerfiles and Docker Compose | PASS | Present under `backend`, `frontend`, and `infra`. |
| GitHub Actions | PASS | CI, e2e, and release workflows exist. |
| Public GitHub publish | PASS | Repo is public at `https://github.com/adeelone/sentinel`. |
| Branch protection, release, discussions, issues, social preview | PASS | Branch protection, releases, starter issues, announcement discussion, and `frontend/public/og.png` are present. |
