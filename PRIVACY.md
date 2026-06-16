# Privacy

Sentinel must not store real cardholder data or PII. Demo and training data must come from the anonymized Kaggle ULB dataset or the synthetic generator.

Uploaded CSVs are processed in memory by default. Analyst notes and review labels are stored in Postgres and can be deleted per user. API keys are hashed at rest.

