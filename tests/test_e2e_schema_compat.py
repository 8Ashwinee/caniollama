"""End-to-end schema compatibility test between compat-check and compat-registry.

This test ensures that SubmissionPayload from compat-check can actually be
submitted to compat-registry without schema mismatches. Since the two schemas
are intentionally hand-mirrored (not shared), this test catches field drift.
"""

import sys
from pathlib import Path
from datetime import datetime, timezone

import pytest

# Add both packages to path
check_src = Path(__file__).parent.parent / "compat-check" / "src"
registry_src = Path(__file__).parent.parent / "compat-registry" / "src"
sys.path.insert(0, str(check_src))
sys.path.insert(0, str(registry_src))

from compat_check.models import SubmissionPayload, CaseOutcome as CheckOutcome
from compat_registry.schemas.submission import SubmissionIn, CaseOutcome as RegistryOutcome


def test_submission_payload_serializes_to_submission_in():
    """Verify that compat-check's SubmissionPayload can be deserialized as compat-registry's SubmissionIn."""

    # Create a sample payload as compat-check would
    payload = SubmissionPayload(
        model_name="qwen2.5-coder:7b",
        model_quantization="Q4_K_M",
        ollama_version="0.1.20",
        suite_version="1",
        os="darwin",
        case_results={
            "structured_tool_call": CheckOutcome.STRUCTURED_PASS,
            "json_in_content": CheckOutcome.JSON_IN_CONTENT_FALLBACK,
            "control_no_tools": CheckOutcome.STRUCTURED_PASS,
        },
        timestamp=datetime.now(timezone.utc),
    )

    # Serialize to dict (as httpx would when POSTing)
    payload_dict = payload.model_dump(mode="json")

    # Deserialize as compat-registry would receive it
    try:
        submission = SubmissionIn.model_validate(payload_dict)
    except Exception as e:
        pytest.fail(f"Registry failed to parse compat-check payload: {e}")

    # Verify round-trip preserved data
    assert submission.model_name == payload.model_name
    assert submission.model_quantization == payload.model_quantization
    assert submission.ollama_version == payload.ollama_version
    assert submission.suite_version == payload.suite_version
    assert submission.os == payload.os
    assert len(submission.case_results) == len(payload.case_results)


def test_case_outcome_enums_match():
    """Ensure CaseOutcome enum values are identical between both packages."""

    check_values = {e.value for e in CheckOutcome}
    registry_values = {e.value for e in RegistryOutcome}

    assert check_values == registry_values, (
        f"CaseOutcome enums differ!\n"
        f"  compat-check: {check_values}\n"
        f"  compat-registry: {registry_values}\n"
        f"  Missing from check: {registry_values - check_values}\n"
        f"  Missing from registry: {check_values - registry_values}"
    )


def test_all_check_outcomes_can_serialize_to_registry():
    """Verify every CaseOutcome from compat-check can be sent to compat-registry."""

    for outcome in CheckOutcome:
        payload = SubmissionPayload(
            model_name="test",
            ollama_version="0.1.0",
            suite_version="1",
            os="linux",
            case_results={"test_case": outcome},
            timestamp=datetime.now(timezone.utc),
        )

        payload_dict = payload.model_dump(mode="json")

        try:
            SubmissionIn.model_validate(payload_dict)
        except Exception as e:
            pytest.fail(f"Registry rejected compat-check outcome {outcome.value}: {e}")
