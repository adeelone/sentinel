from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_env: str = "local"
    admin_key_name: str = "x-admin-key"
    admin_key: str = "change-me-local-only"
    public_rate_limit_per_minute: int = Field(default=120, ge=1)
    database_url: str = "sqlite:///data/sentinel.db"
    redis_url: str | None = None
    model_bundle_path: Path = Path("artifacts/model_bundle.joblib")
    artifact_bucket: str | None = None
    artifact_endpoint: str | None = None
    artifact_access_key: str | None = None
    artifact_secret_key: str | None = None
    artifact_region: str = "auto"
    cors_origins: list[str]

    @property
    def production(self) -> bool:
        return self.app_env.lower() == "production"

    def validate_runtime(self) -> None:
        if self.production and self.admin_key == "change-me-local-only":
            raise RuntimeError("API_ADMIN_KEY must be set to a non-default value in production")
        if self.production and not self.database_url.startswith("postgresql"):
            raise RuntimeError("DATABASE_URL must point to Postgres in production")
        if self.production and not self.redis_url:
            raise RuntimeError("REDIS_URL is required in production")
        if self.production and not self.model_bundle_path.exists():
            raise RuntimeError(f"trained model bundle not found: {self.model_bundle_path}")
        if self.production and not all(
            (
                self.artifact_bucket,
                self.artifact_endpoint,
                self.artifact_access_key,
                self.artifact_secret_key,
            )
        ):
            raise RuntimeError("artifact bucket credentials are required in production")


default_origins = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"
settings = Settings(
    app_env=os.getenv("APP_ENV", "local"),
    admin_key_name=os.getenv("API_ADMIN_KEY_HEADER", "x-admin-key").lower(),
    admin_key=os.getenv("API_ADMIN_KEY", "change-me-local-only"),
    public_rate_limit_per_minute=int(os.getenv("PUBLIC_RATE_LIMIT_PER_MINUTE", "120")),
    database_url=os.getenv("DATABASE_URL", "sqlite:///data/sentinel.db"),
    redis_url=os.getenv("REDIS_URL"),
    model_bundle_path=Path(os.getenv("MODEL_BUNDLE_PATH", "artifacts/model_bundle.joblib")),
    artifact_bucket=os.getenv("ARTIFACT_BUCKET"),
    artifact_endpoint=os.getenv("ARTIFACT_ENDPOINT"),
    artifact_access_key=os.getenv("ARTIFACT_ACCESS_KEY"),
    artifact_secret_key=os.getenv("ARTIFACT_SECRET_KEY"),
    artifact_region=os.getenv("ARTIFACT_REGION", "auto"),
    cors_origins=[
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", default_origins).split(",")
        if origin.strip()
    ],
)
settings.validate_runtime()
