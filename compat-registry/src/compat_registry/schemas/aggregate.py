from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class ModelListEntry(BaseModel):
    model_name: str
    quantizations: list[str]
    total_reports: int
    latest_suite_version: str


class CasePassRate(BaseModel):
    case_id: str
    pass_rate: float
    total_reports: int


class ModelCompatSummary(BaseModel):
    model_name: str
    total_reports: int
    first_seen: datetime | None
    last_seen: datetime | None
    per_quantization: dict[str, int]
    per_ollama_version: dict[str, int]
    pass_rate_by_case: list[CasePassRate]


class RegistryStats(BaseModel):
    total_submissions: int
    total_models: int
    most_tested_models: list[str]
    current_suite_version: str
