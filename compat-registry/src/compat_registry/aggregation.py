from __future__ import annotations

from collections import Counter, defaultdict

from compat_registry.schemas.aggregate import (
    CasePassRate,
    ModelCompatSummary,
    ModelListEntry,
    RegistryStats,
)
from compat_registry.schemas.submission import CaseOutcome, SubmissionRecord


def build_model_list(records: list[SubmissionRecord]) -> list[ModelListEntry]:
    by_model: dict[str, list[SubmissionRecord]] = defaultdict(list)
    for record in records:
        by_model[record.model_name].append(record)

    entries = []
    for model_name, model_records in by_model.items():
        quantizations = sorted(
            {r.model_quantization for r in model_records if r.model_quantization}
        )
        latest_suite = max(r.suite_version for r in model_records)
        entries.append(
            ModelListEntry(
                model_name=model_name,
                quantizations=quantizations,
                total_reports=len(model_records),
                latest_suite_version=latest_suite,
            )
        )
    return sorted(entries, key=lambda e: e.total_reports, reverse=True)


def build_model_summary(model_name: str, records: list[SubmissionRecord]) -> ModelCompatSummary:
    if not records:
        return ModelCompatSummary(
            model_name=model_name,
            total_reports=0,
            first_seen=None,
            last_seen=None,
            per_quantization={},
            per_ollama_version={},
            pass_rate_by_case=[],
        )

    per_quant = Counter(r.model_quantization or "unknown" for r in records)
    per_version = Counter(r.ollama_version for r in records)

    case_totals: dict[str, int] = defaultdict(int)
    case_passes: dict[str, int] = defaultdict(int)
    for record in records:
        for case_id, outcome in record.case_results.items():
            case_totals[case_id] += 1
            if outcome == CaseOutcome.STRUCTURED_PASS:
                case_passes[case_id] += 1

    pass_rates = [
        CasePassRate(
            case_id=case_id,
            pass_rate=round(case_passes.get(case_id, 0) / total, 4) if total else 0.0,
            total_reports=total,
        )
        for case_id, total in sorted(case_totals.items())
    ]

    timestamps = sorted(r.timestamp for r in records)

    return ModelCompatSummary(
        model_name=model_name,
        total_reports=len(records),
        first_seen=timestamps[0],
        last_seen=timestamps[-1],
        per_quantization=dict(per_quant),
        per_ollama_version=dict(per_version),
        pass_rate_by_case=pass_rates,
    )


def build_stats(records: list[SubmissionRecord], current_suite_version: str) -> RegistryStats:
    by_model = Counter(r.model_name for r in records)
    most_tested = [name for name, _ in by_model.most_common(10)]
    return RegistryStats(
        total_submissions=len(records),
        total_models=len(by_model),
        most_tested_models=most_tested,
        current_suite_version=current_suite_version,
    )
