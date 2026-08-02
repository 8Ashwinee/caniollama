from __future__ import annotations

from typing import Protocol

from compat_registry.schemas.submission import SubmissionIn, SubmissionRecord


class StorageBackend(Protocol):
    """Route code (api/) only ever talks to this interface, so swapping the
    Phase 2 file-backed store for the Phase 3 SQLite/Postgres backend never
    touches route code."""

    async def put(self, submission: SubmissionIn) -> SubmissionRecord: ...

    async def all(self) -> list[SubmissionRecord]: ...

    async def for_model(self, model_name: str) -> list[SubmissionRecord]: ...
