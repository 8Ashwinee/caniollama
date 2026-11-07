import os
from datetime import UTC, datetime
from pathlib import Path

import pytest

from compat_registry.schemas.submission import SubmissionIn
from compat_registry.storage.db_backend import PostgresStorageBackend, SQLiteStorageBackend
from compat_registry.storage.file_backend import FileStorageBackend

SAMPLE = SubmissionIn(
    model_name="qwen2.5-coder:7b",
    model_quantization="q4_K_M",
    ollama_version="0.6.2",
    suite_version="1.0.0",
    os="linux",
    case_results={"single_tool_basic": "structured_pass"},
    timestamp=datetime(2026, 8, 1, tzinfo=UTC),
)


@pytest.fixture(params=["file", "db", "postgres"])
def backend(request, tmp_path: Path):
    if request.param == "file":
        return FileStorageBackend(tmp_path)
    if request.param == "postgres":
        url = os.environ.get("TEST_DATABASE_URL")
        if not url:
            pytest.skip("TEST_DATABASE_URL not set")
        b = PostgresStorageBackend(url)
        with b._connect() as conn:
            conn.execute("TRUNCATE submissions")
        return b
    return SQLiteStorageBackend(tmp_path / "registry.sqlite3")


@pytest.mark.asyncio
async def test_put_then_all_roundtrips(backend):
    record = await backend.put(SAMPLE)
    assert record.model_name == "qwen2.5-coder:7b"

    all_records = await backend.all()
    assert len(all_records) == 1
    assert all_records[0].id == record.id


@pytest.mark.asyncio
async def test_for_model_filters_correctly(backend):
    await backend.put(SAMPLE)
    other = SAMPLE.model_copy(update={"model_name": "llama3:8b"})
    await backend.put(other)

    matches = await backend.for_model("qwen2.5-coder:7b")
    assert len(matches) == 1
    assert matches[0].model_name == "qwen2.5-coder:7b"

    empty = await backend.for_model("nonexistent:1b")
    assert empty == []
