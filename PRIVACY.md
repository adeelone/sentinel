# Privacy

Sentinel must not store real cardholder data or PII. Demo and training data must come from the anonymized Kaggle ULB dataset or the synthetic generator.

Uploaded CSVs are parsed in memory. Each scored row, its anonymized feature values, and analyst review are then saved in the configured SQLite database so the triage queue survives a restart.

The dashboard's delete action calls `DELETE /transactions/{id}` and removes that row and its review note. Deleting the SQLite database removes all locally stored demo records. Sentinel does not collect names, card numbers, email addresses, or account identifiers.
