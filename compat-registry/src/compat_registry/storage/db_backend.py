"""Phase 3+ storage backend: SQLite (or Postgres, via the same DB-API-ish shape).

Implements the same `StorageBackend` protocol as `file_backend.FileStorageBackend`
so route code in `api/` never has to change when this is swapped in -- flip
`COMPAT_REGISTRY_STORAGE_BACKEND=db` and point `DB_PATH`/`DATABASE_URL` at a
real database.

This is intentionally left as a thin, working skeleton rather than a full
implementation: at MVP volumes the file backend is sufficient (see
storage/file_backend.py's docstring), and building this out further should
wait until submission volume actually justifies it, per the project's phased
build order.
"""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Any

from compat_registry.schemas.submission import SubmissionIn, SubmissionRecord

_SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id TEXT PRIMARY KEY,
    model_name TEXT NOT NULL,
    model_quantization TEXT,
    ollama_version TEXT NOT NULL,
    suite_version TEXT NOT NULL,
    os TEXT NOT NULL,
    case_results TEXT NOT NULL,  -- JSON-encoded dict[str, str]
    timestamp TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_submissions_model_name ON submissions(model_name);
"""


class SQLiteStorageBackend:
    _ph = "?"  # DB-API placeholder style

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.db_path)) as conn:
            conn.executescript(_SCHEMA)
            conn.commit()

    def _connect(self) -> Any:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    async def put(self, submission: SubmissionIn) -> SubmissionRecord:
        import json
        import uuid

        record_id = str(uuid.uuid4())
        record = SubmissionRecord(id=record_id, **submission.model_dump())

        with closing(self._connect()) as conn:
            conn.execute(
                "INSERT INTO submissions (id, model_name, model_quantization, ollama_version,"
                " suite_version, os, case_results, timestamp)"
                f" VALUES ({', '.join([self._ph] * 8)})",
                (
                    record.id,
                    record.model_name,
                    record.model_quantization,
                    record.ollama_version,
                    record.suite_version,
                    record.os,
                    json.dumps({k: v.value for k, v in record.case_results.items()}),
                    record.timestamp.isoformat(),
                ),
            )
            conn.commit()
        return record

    async def all(self) -> list[SubmissionRecord]:
        return self._query("SELECT * FROM submissions")

    async def for_model(self, model_name: str) -> list[SubmissionRecord]:
        return self._query(
            f"SELECT * FROM submissions WHERE model_name = {self._ph}", (model_name,)
        )

    def _query(self, sql: str, params: tuple = ()) -> list[SubmissionRecord]:
        import json

        with closing(self._connect()) as conn:
            rows = conn.execute(sql, params).fetchall()

        records = []
        for row in rows:
            records.append(
                SubmissionRecord(
                    id=row["id"],
                    model_name=row["model_name"],
                    model_quantization=row["model_quantization"],
                    ollama_version=row["ollama_version"],
                    suite_version=row["suite_version"],
                    os=row["os"],
                    case_results=json.loads(row["case_results"]),
                    timestamp=row["timestamp"],
                )
            )
        return records


class PostgresStorageBackend(SQLiteStorageBackend):
    """Same SQL as SQLite; used when DATABASE_URL is set (e.g. Neon on Vercel)."""

    _ph = "%s"

    def __init__(self, database_url: str):
        self.database_url = database_url
        with closing(self._connect()) as conn:
            conn.execute(_SCHEMA)
            conn.commit()

    def _connect(self) -> Any:
        import psycopg
        from psycopg.rows import dict_row

        return psycopg.connect(self.database_url, row_factory=dict_row)
