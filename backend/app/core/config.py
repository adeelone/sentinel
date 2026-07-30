from __future__ import annotations

import os
from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class Settings(BaseModel):
    app_env: str = "local"
    admin_key_name: str = "x-admin-key"
    admin_key: str = "change-me-local-only"
    public_rate_limit_per_minute: int = Field(default=120, ge=1)
    database_path: Path = Path("data/sentinel.db")
    cors_origins: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @property
    def production(self) -> bool:
        return self.app_env.lower() == "production"

    def validate_runtime(self) -> None:
        if self.production and self.admin_key == "change-me-local-only":
            raise RuntimeError("API_ADMIN_KEY must be set to a non-default value in production")


settings = Settings(
    app_env=os.getenv("APP_ENV", "local"),
    admin_key_name=os.getenv("API_ADMIN_KEY_HEADER", "x-admin-key").lower(),
    admin_key=os.getenv("API_ADMIN_KEY", "change-me-local-only"),
    public_rate_limit_per_minute=int(os.getenv("PUBLIC_RATE_LIMIT_PER_MINUTE", "120")),
    database_path=Path(os.getenv("SENTINEL_DB_PATH", "data/sentinel.db")),
    cors_origins=[
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
        ).split(",")
        if origin.strip()
    ],
)
settings.validate_runtime()
