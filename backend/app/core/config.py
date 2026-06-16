from __future__ import annotations

from pydantic import BaseModel


class Settings(BaseModel):
    app_env: str = "local"
    admin_key_name: str = "x-admin-key"
    public_rate_limit_per_minute: int = 120


settings = Settings()

