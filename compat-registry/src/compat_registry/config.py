from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COMPAT_REGISTRY_")

    data_dir: Path = Path(__file__).resolve().parent.parent.parent / "data"
    current_suite_version: str = "1.0.0"
    rate_limit_per_minute: int = 10
    cors_allow_origins: list[str] = ["*"]
    storage_backend: str = "file"  # "file" (Phase 2 MVP) or "db" (Phase 3+)


settings = Settings()
