from __future__ import annotations

import pytest

from compat_check.models import RunReport


@pytest.fixture
def sample_run_report() -> RunReport:
    from compat_check.models import CaseOutcome, CaseResult

    return RunReport(
        model_name="qwen2.5-coder:7b",
        model_quantization="q4_K_M",
        ollama_version="0.6.2",
        suite_version="1.0.0",
        os_name="linux",
        results=[
            CaseResult(case_id="single_tool_basic", outcome=CaseOutcome.STRUCTURED_PASS, latency_ms=120),
            CaseResult(case_id="multi_tool_5x", outcome=CaseOutcome.STRUCTURED_PASS, latency_ms=180),
            CaseResult(case_id="no_tools_needed_control", outcome=CaseOutcome.STRUCTURED_PASS, latency_ms=90),
            CaseResult(case_id="multiturn_tool_result", outcome=CaseOutcome.JSON_IN_CONTENT_FALLBACK, latency_ms=200),
        ],
    )
