# Revamp audit

Date: 2026-07-29

This pass focused on the path a reviewer can finish in a few minutes: score a synthetic transaction, understand the result, see it in the queue, save a review, and delete it.

## Fixed

- Removed the frontend's silent local score fallback. API failures are visible and retryable.
- Replaced two in-memory transaction stores with one SQLite store.
- Persisted single and batch scores, review outcomes, notes, and deletion.
- Removed `/retrain`; it said "queued" without a worker.
- Added production admin-key validation, configured CORS, and defensive response headers.
- Reworked the dashboard with loading, empty, failure, keyboard, responsive, and reduced-motion states.
- Added persistence, deletion, and rate-limit tests.

## Deliberately not done

- The optional XGBoost, LightGBM, PyTorch autoencoder, ensemble, SHAP, MLflow, MinIO, and RQ work is not faked here. The existing sklearn training pipeline remains the honest implemented boundary.
- SQLite remains the local zero-setup path. Production uses Postgres with an Alembic-managed schema.
- i18n, Lighthouse scoring, and the live Railway account connection remain external follow-up work.
