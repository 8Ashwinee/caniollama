from __future__ import annotations

import shutil
from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from compat_registry.api.deps import get_rate_limiter, get_storage
from compat_registry.config import settings
from compat_registry.main import app
from compat_registry.storage.file_backend import FileStorageBackend


@pytest.fixture
def tmp_data_dir(tmp_path: Path) -> Path:
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    yield data_dir
    shutil.rmtree(data_dir, ignore_errors=True)


@pytest.fixture
def client(tmp_data_dir, monkeypatch):
    monkeypatch.setattr(settings, "data_dir", tmp_data_dir)
    get_storage.cache_clear()
    get_rate_limiter.cache_clear()

    async def _fake_storage_override():
        return FileStorageBackend(tmp_data_dir)

    app.dependency_overrides[get_storage] = lambda: FileStorageBackend(tmp_data_dir)

    transport = ASGITransport(app=app)
    yield AsyncClient(transport=transport, base_url="http://testserver")

    app.dependency_overrides.clear()
    get_storage.cache_clear()
    get_rate_limiter.cache_clear()


SAMPLE_SUBMISSION = {
    "model_name": "qwen2.5-coder:7b",
    "model_quantization": "q4_K_M",
    "ollama_version": "0.6.2",
    "suite_version": "1.0.0",
    "os": "linux",
    "case_results": {
        "single_tool_basic": "structured_pass",
        "multi_tool_5x": "structured_pass",
        "no_tools_needed_control": "structured_pass",
        "multiturn_tool_result": "json_fallback",
    },
    "timestamp": "2026-08-01T10:00:00Z",
}
