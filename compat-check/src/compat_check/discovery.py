"""Finds locally pulled Ollama models and the current Ollama/OS metadata."""

from __future__ import annotations

import platform
from dataclasses import dataclass

from compat_check.ollama_client import OllamaClient


@dataclass
class DiscoveredModel:
    name: str            # e.g. "qwen2.5-coder:7b"
    quantization: str | None


def _guess_quantization(model_tag: dict) -> str | None:
    details = model_tag.get("details") or {}
    return details.get("quantization_level")


async def discover_models(client: OllamaClient) -> list[DiscoveredModel]:
    raw = await client.list_models()
    return [
        DiscoveredModel(name=m["name"], quantization=_guess_quantization(m))
        for m in raw
        if "name" in m
    ]


async def discover_ollama_version(client: OllamaClient) -> str:
    return await client.version()


def current_os() -> str:
    system = platform.system().lower()
    return {"darwin": "macos", "linux": "linux", "windows": "windows"}.get(system, system)
