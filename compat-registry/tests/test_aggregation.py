from datetime import UTC, datetime

from compat_registry.aggregation import build_model_list, build_model_summary, build_stats
from compat_registry.schemas.submission import SubmissionRecord

RECORDS = [
    SubmissionRecord(
        id="1",
        model_name="qwen2.5-coder:7b",
        model_quantization="q4_K_M",
        ollama_version="0.6.2",
        suite_version="1.0.0",
        os="linux",
        case_results={"single_tool_basic": "structured_pass", "multi_tool_5x": "json_fallback"},
        timestamp=datetime(2026, 8, 1, tzinfo=UTC),
    ),
    SubmissionRecord(
        id="2",
        model_name="qwen2.5-coder:7b",
        model_quantization="q4_K_M",
        ollama_version="0.6.3",
        suite_version="1.0.0",
        os="macos",
        case_results={"single_tool_basic": "structured_pass", "multi_tool_5x": "structured_pass"},
        timestamp=datetime(2026, 8, 2, tzinfo=UTC),
    ),
    SubmissionRecord(
        id="3",
        model_name="llama3:8b",
        model_quantization=None,
        ollama_version="0.6.2",
        suite_version="1.0.0",
        os="linux",
        case_results={"single_tool_basic": "rejected"},
        timestamp=datetime(2026, 8, 1, tzinfo=UTC),
    ),
]


def test_build_model_list_counts_reports_per_model():
    entries = build_model_list(RECORDS)
    by_name = {e.model_name: e for e in entries}
    assert by_name["qwen2.5-coder:7b"].total_reports == 2
    assert by_name["llama3:8b"].total_reports == 1


def test_build_model_summary_computes_pass_rate():
    summary = build_model_summary("qwen2.5-coder:7b", [r for r in RECORDS if r.model_name == "qwen2.5-coder:7b"])
    rates = {r.case_id: r.pass_rate for r in summary.pass_rate_by_case}
    assert rates["single_tool_basic"] == 1.0
    assert rates["multi_tool_5x"] == 0.5


def test_build_stats_totals():
    stats = build_stats(RECORDS, current_suite_version="1.0.0")
    assert stats.total_submissions == 3
    assert stats.total_models == 2
