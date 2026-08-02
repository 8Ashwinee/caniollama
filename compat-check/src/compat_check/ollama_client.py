"""Thin async client around the local Ollama HTTP API. No third-party ollama SDK dependency
by design -- keeps this package's dependency footprint minimal, per the "installs in seconds"
requirement."""

from __future__ import annotations

from typing import Any

import httpx

from compat_check.config import settings


class OllamaError(Exception):
    """Raised for connection failures or unexpected non-tool-related errors."""


class OllamaRejected(Exception):
    """Raised when Ollama returns a 4xx specifically because `tools` was included
    (compatibility category 3: the backend refuses the request outright)."""

    def __init__(self, status_code: int, body: str):
        self.status_code = status_code
        self.body = body
        super().__init__(f"Ollama rejected request with tools: HTTP {status_code}")


class OllamaClient:
    def __init__(self, base_url: str | None = None, timeout: float | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.timeout = timeout or settings.request_timeout_seconds

    async def list_models(self) -> list[dict[str, Any]]:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            resp = await client.get("/api/tags")
            resp.raise_for_status()
            return resp.json().get("models", [])

    async def version(self) -> str:
        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            resp = await client.get("/api/version")
            resp.raise_for_status()
            return resp.json().get("version", "unknown")

    async def chat(
        self,
        model: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """POST /api/chat. Raises OllamaRejected if the backend 4xx's specifically because
        `tools` was included -- that's compatibility category 3, a signal we want to catch
        distinctly from a generic connection error."""

        payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
        if tools:
            payload["tools"] = tools

        async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
            try:
                resp = await client.post("/api/chat", json=payload)
                resp.raise_for_status()
                return resp.json()
            except httpx.HTTPStatusError as exc:
                if tools and 400 <= exc.response.status_code < 500:
                    raise OllamaRejected(exc.response.status_code, exc.response.text) from exc
                raise OllamaError(str(exc)) from exc
            except httpx.RequestError as exc:
                raise OllamaError(str(exc)) from exc
