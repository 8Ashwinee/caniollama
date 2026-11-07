"""Runtime configuration, resolved from environment variables with sane defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    ollama_base_url: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
    registry_base_url: str = os.environ.get(
        "CANIOLLAMA_REGISTRY_URL", "https://registry.caniollama.ghimireanjal.com.np"
    )
    request_timeout_seconds: float = float(os.environ.get("CANIOLLAMA_TIMEOUT", "30"))
    submit_timeout_seconds: float = float(os.environ.get("CANIOLLAMA_SUBMIT_TIMEOUT", "10"))


settings = Settings()
