"""Phase 2 MVP storage: one JSON file per submission under
data/results/<model_name>/<timestamp>-<uuid>.json.

In the earliest MVP these files are written by validated GitHub PRs (see
.github/workflows/validate-submission.yml) and this class just reads them
back. Once the live POST /submissions endpoint is enabled (Phase 3), this
class also handles direct writes -- same file layout either way.

This backend is intentionally simple: no indexing, no caching. It reads the
whole result set on every aggregate query. That's fine at MVP data volumes and
is the entire point of deferring a real database until it's justified.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path

from compat_registry.schemas.submission import SubmissionIn, SubmissionRecord


def _safe_dirname(model_name: str) -> str:
    return model_name.replace("/", "_").replace(":", "_")


class FileStorageBackend:
    def __init__(self, data_dir: Path):
        self.results_dir = data_dir / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

    async def put(self, submission: SubmissionIn) -> SubmissionRecord:
        record_id = str(uuid.uuid4())
        record = SubmissionRecord(id=record_id, **submission.model_dump())

        model_dir = self.results_dir / _safe_dirname(submission.model_name)
        model_dir.mkdir(parents=True, exist_ok=True)

        file_path = model_dir / f"{submission.timestamp:%Y-%m-%d}-{record_id}.json"
        file_path.write_text(record.model_dump_json(indent=2))
        return record

    async def all(self) -> list[SubmissionRecord]:
        records = []
        for file_path in self.results_dir.glob("*/*.json"):
            try:
                data = json.loads(file_path.read_text())
                records.append(SubmissionRecord.model_validate(data))
            except (json.JSONDecodeError, ValueError):
                continue  # skip malformed files rather than fail the whole read
        return records

    async def for_model(self, model_name: str) -> list[SubmissionRecord]:
        model_dir = self.results_dir / _safe_dirname(model_name)
        if not model_dir.exists():
            return []
        records = []
        for file_path in model_dir.glob("*.json"):
            try:
                data = json.loads(file_path.read_text())
                records.append(SubmissionRecord.model_validate(data))
            except (json.JSONDecodeError, ValueError):
                continue
        return records
