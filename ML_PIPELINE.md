# ML Pipeline

The default dataset path is synthetic and deterministic. Kaggle ULB data is used when `KAGGLE_USERNAME` and `KAGGLE_KEY` are available or when `data/raw/creditcard.csv` is supplied manually.

Models are registered behind a common adapter:

- Logistic regression baseline with class weighting.
- Random forest with capped depth.
- Isolation forest as an unsupervised baseline.

XGBoost, LightGBM, a PyTorch autoencoder, and a stacked ensemble are tracked ideas, not implemented adapters.

The CI smoke path uses the synthetic generator and lightweight adapters so tests stay fast.
