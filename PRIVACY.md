# Privacy

Sentinel must not store real cardholder data or PII. Demo and training data must come from the anonymized Kaggle ULB dataset or the synthetic generator.

Uploaded CSVs are parsed in memory. Each scored row, its anonymized feature values, and analyst review are saved in SQLite locally or Postgres in production so the triage queue survives restarts and API replacement.

The dashboard's delete action calls `DELETE /transactions/{id}` and removes that row and its review note. Deleting the SQLite database removes all local demo records; production rows can be removed through the same API. Sentinel does not collect names, card numbers, email addresses, or account identifiers.
