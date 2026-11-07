"""Mirrors compat-check's `SubmissionPayload` shape. Kept as an independently
maintained schema (not a shared package) so the two repos stay decoupled --
see docs/registry/data-format.md at the repo root, which is the actual source of truth both sides follow."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class CaseOutcome(str, Enum):
    STRUCTURED_PASS = "structured_pass"
    JSON_IN_CONTENT_FALLBACK = "json_fallback"
    REJECTED_BY_BACKEND = "rejected"
    TIMEOUT_OR_ERROR = "error"


class SubmissionIn(BaseModel):
    model_name: str = Field(min_length=1, max_length=200)
    model_quantization: str | None = Field(default=None, max_length=50)
    ollama_version: str = Field(min_length=1, max_length=50)
    suite_version: str = Field(min_length=1, max_length=50)
    os: str = Field(min_length=1, max_length=20)
    case_results: dict[str, CaseOutcome]
    timestamp: datetime


class SubmissionRecord(SubmissionIn):
    id: str
