# Providers

## Kaggle

Set `KAGGLE_USERNAME` and `KAGGLE_KEY`, then run:

```bash
make data
```

Without credentials, Sentinel prints the manual download path and uses synthetic data for demos and tests.

## MLflow

Set `MLFLOW_TRACKING_URI`. If it is not set, Sentinel uses a no-op tracker and still writes local reports.

## Optional Weights & Biases

Add a tracker implementation under `ml/sentinel_ml/tracking/` and set `SENTINEL_TRACKER=wandb`.

