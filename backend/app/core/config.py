from __future__ import annotations

import os

from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = "local"
    admin_key_name: str = "x-admin-key"
    admin_key: str
    public_rate_limit_per_minute: int = 120


settings = Settings(
    app_env=os.getenv("APP_ENV", "local"),
    admin_key_name=os.getenv("API_ADMIN_KEY_HEADER", "x-admin-key"),
    admin_key=os.getenv("API_ADMIN_KEY", "change-me-local-only"),
    public_rate_limit_per_minute=int(os.getenv("PUBLIC_RATE_LIMIT_PER_MINUTE", "120")),
)
