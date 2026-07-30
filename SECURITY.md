# Security

Report vulnerabilities privately through GitHub security advisories.

Secrets must be supplied through environment variables or a managed secret store. Never commit `.env`, API keys, OAuth secrets, Kaggle credentials, private keys, model binaries, or real transaction data.

Production startup fails if `API_ADMIN_KEY` is left at the local placeholder. Set `CORS_ORIGINS` to the exact frontend origin. The API sends a restrictive CSP, frame denial, MIME-sniffing protection, and HSTS in production.

Public scoring routes are rate-limited in process. That is enough for this single-instance demo, but a multi-instance deployment needs a shared limiter such as Redis.
