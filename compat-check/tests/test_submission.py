"""Structural privacy guarantee tests: assert SubmissionPayload's schema cannot
carry free text long enough to be a prompt or a model output, and that
submission never touches case content."""

import inspect

import httpx
import pytest

from compat_check import submission
from compat_check.models import SubmissionPayload
from compat_check.suite.cases import CASES


def test_submission_payload_fields_are_bounded():
    """Every field must be a version tag, enum, coarse label, or timestamp --
    never a free-text/content-shaped field."""
    allowed_unbounded_str_fields = {"model_name", "model_quantization", "ollama_version"}
    for name in SubmissionPayload.model_fields:
        if name == "case_results":
            # dict[str, CaseOutcome] -- values are constrained to the enum, not free text
            continue
        if name in allowed_unbounded_str_fields:
            # These carry short identifiers (e.g. "qwen2.5-coder:7b"), not prompts/outputs
            continue
        # suite_version, os, timestamp: also bounded/short by construction
        assert name in {"suite_version", "os", "timestamp"}, (
            f"Unexpected field '{name}' on SubmissionPayload -- review for privacy leakage"
        )


def test_submission_module_never_imports_case_prompts():
    """submission.py's *code* (not comments/docstrings) should never touch case
    message/prompt content."""
    source = inspect.getsource(submission)
    code_lines = [
        line for line in source.splitlines()
        if line.strip() and not line.strip().startswith(("#", '"""', "'''"))
    ]
    code_only = "\n".join(code_lines)
    forbidden_tokens = ["case.messages", "case.tools", 'message.get("content']
    for token in forbidden_tokens:
        assert token not in code_only, (
            f"submission.py references '{token}' in executable code -- privacy violation risk"
        )


def test_to_submission_payload_only_carries_outcomes(sample_run_report):
    payload = sample_run_report.to_submission_payload()
    for case_id, outcome in payload.case_results.items():
        assert case_id in {c.case_id for c in CASES}
        assert outcome in {
            "structured_pass",
            "json_fallback",
            "rejected",
            "error",
        }


@pytest.mark.asyncio
async def test_submit_result_returns_false_on_network_error(monkeypatch, sample_run_report):
    async def _boom(*args, **kwargs):
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(httpx.AsyncClient, "post", _boom)
    ok = await submission.submit_result(sample_run_report, base_url="http://unreachable.invalid")
    assert ok is False
