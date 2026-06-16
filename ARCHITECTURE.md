# Architecture

Sentinel has four loops: data preparation, model training, online scoring, and analyst feedback.

```mermaid
flowchart LR
  A["Kaggle or synthetic data"] --> B["Validation and feature pipeline"]
  B --> C["Training and evaluation"]
  C --> D["Model bundle and report"]
  D --> E["FastAPI scoring service"]
  E --> F["React dashboard"]
  F --> G["Analyst review labels"]
  G --> H["Feedback dataset"]
  H --> C
```

The model bundle contains the fitted transformer, estimator, threshold metadata, calibration metadata, and explanation configuration so training and serving use the same feature contract.

