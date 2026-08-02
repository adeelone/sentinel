# Railway deployment

Sentinel's production layout uses five Railway services plus one object-storage bucket: `sentinel-web`, `sentinel-api`, `sentinel-worker`, Postgres, Redis, and `sentinel-artifacts`. Only the web and API services need public domains.

## Account setup

1. Create a Railway project and connect `adeelone/sentinel` from GitHub.
2. Add Railway Postgres, Redis, and a Bucket named `sentinel-artifacts`.
3. Create three services from the same GitHub repository: `sentinel-api`, `sentinel-worker`, and `sentinel-web`.

## API service

Keep the repository root as `/`. Set the config file path to `/infra/deploy/railway-api.json` and generate a public domain. Add:

```dotenv
APP_ENV=production
PORT=8000
API_ADMIN_KEY=<64 random hex characters>
API_ADMIN_KEY_HEADER=x-admin-key
PUBLIC_RATE_LIMIT_PER_MINUTE=120
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
CORS_ORIGINS=https://${{sentinel-web.RAILWAY_PUBLIC_DOMAIN}}
MODEL_BUNDLE_PATH=/app/artifacts/model_bundle.joblib
ARTIFACT_BUCKET=${{sentinel-artifacts.BUCKET}}
ARTIFACT_ENDPOINT=${{sentinel-artifacts.ENDPOINT}}
ARTIFACT_ACCESS_KEY=${{sentinel-artifacts.ACCESS_KEY_ID}}
ARTIFACT_SECRET_KEY=${{sentinel-artifacts.SECRET_ACCESS_KEY}}
ARTIFACT_REGION=${{sentinel-artifacts.REGION}}
```

The image trains a deterministic synthetic model during its build, so `/readyz` never promotes an API without a model.

## Worker service

Keep the repository root as `/`. Set the config file path to `/infra/deploy/railway-worker.json`. Do not generate a public domain. Add:

```dotenv
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
MODEL_BUNDLE_PATH=/tmp/sentinel/model_bundle.joblib
ARTIFACT_BUCKET=${{sentinel-artifacts.BUCKET}}
ARTIFACT_ENDPOINT=${{sentinel-artifacts.ENDPOINT}}
ARTIFACT_ACCESS_KEY=${{sentinel-artifacts.ACCESS_KEY_ID}}
ARTIFACT_SECRET_KEY=${{sentinel-artifacts.SECRET_ACCESS_KEY}}
ARTIFACT_REGION=${{sentinel-artifacts.REGION}}
```

## Web service

Set the root directory to `/frontend`, set `PORT=8080`, and set:

```dotenv
VITE_API_BASE_URL=https://${{sentinel-api.RAILWAY_PUBLIC_DOMAIN}}
```

Use `/healthz` as the health-check path and generate a public domain. Because Vite embeds the API URL during the build, redeploy the web service after its variable is set.

## Sign-off

Verify `/healthz`, `/readyz`, `/models`, `/drift`, `/metrics`, and `/docs`. In the UI, score a transaction, review it, reload, and confirm the review persists. Queue a retrain with the admin key, poll `/jobs/{job_id}`, and confirm it reaches `complete`. Then score again and confirm `/models` reports the new run ID within one minute.

Enable Postgres point-in-time recovery or scheduled backups before calling the deployment complete. Keep Postgres, Redis, the worker, and the bucket private.
