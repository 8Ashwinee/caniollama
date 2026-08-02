"""Data shapes used across the CLI.

`SubmissionPayload` is deliberately the *only* model allowed to reach
`submission.py`'s network call. Every field is a bounded type (str version
tag, enum, datetime) -- none of them are capable of carrying a prompt or a
raw model output. That's a structural guarantee, not just a convention;
`tests/test_submission.py` asserts it via schema introspection.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class CaseOutcome(str, Enum):
    """The three real-world answers to 'does tool calling work', plus a bucket for errors."""

    STRUCTURED_PASS = "structured_pass"            # category 1: native tool_calls field
    JSON_IN_CONTENT_FALLBACK = "json_fallback"      # category 2: intent, but shoved into content
    REJECTED_BY_BACKEND = "rejected"                # category 3: backend 400s on `tools`
    TIMEOUT_OR_ERROR = "error"


class CaseResult(BaseModel):
    """Local-only, detailed result for a single test case. Never submitted as-is."""

    case_id: str
    outcome: CaseOutcome
    latency_ms: int | None = None
    detail: str | None = None  # short internal note, e.g. "HTTP 400", never model output


class RunReport(BaseModel):
    """Full local report for a single model run. Rich detail lives here, on disk / terminal only."""

    model_name: str
    model_quantization: str | None
    ollama_version: str
    suite_version: str
    os_name: str
    results: list[CaseResult]
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def to_submission_payload(self) -> SubmissionPayload:
        return SubmissionPayload(
            model_name=self.model_name,
            model_quantization=self.model_quantization,
            ollama_version=self.ollama_version,
            suite_version=self.suite_version,
            os=self.os_name,
            case_results={r.case_id: r.outcome for r in self.results},
            timestamp=self.timestamp,
        )


class SubmissionPayload(BaseModel):
    """The ONLY thing ever sent to the registry. Metadata only -- never prompts, never outputs."""

    model_name: str
    model_quantization: str | None = None
    ollama_version: str
    suite_version: str
    os: str
    case_results: dict[str, CaseOutcome]
    timestamp: datetime
