"""Tests for suite runner using mocked Ollama responses.

Covers the paths described in issue #6: structured tool_calls, JSON-in-content
fallback, backend rejection (HTTP 400), and timeout/connection errors.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from compat_check.models import CaseOutcome
from compat_check.ollama_client import OllamaClient
from compat_check.suite.runner import run_suite


@pytest.fixture
def client() -> OllamaClient:
    return OllamaClient(base_url="http://ollama.test", timeout=5.0)


@respx.mock
async def test_run_suite_structured_tool_calls(client: OllamaClient) -> None:
    """A proper tool_calls response should yield STRUCTURED_PASS for relevant cases."""
    respx.post("http://ollama.test/api/chat").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {
                            "function": {
                                "name": "get_weather",
                                "arguments": {"city": "Tokyo"},
                            }
                        }
                    ],
                }
            },
        )
    )

    results = await run_suite(client, "test-model")

    # At least the basic single-tool and multi-tool cases should pass structured.
    outcomes = {r.case_id: r.outcome for r in results}
    assert outcomes.get("single_tool_basic") == CaseOutcome.STRUCTURED_PASS
    assert outcomes.get("multi_tool_5x") == CaseOutcome.STRUCTURED_PASS
    assert all(r.latency_ms is not None and r.latency_ms >= 0 for r in results)


@respx.mock
async def test_run_suite_json_in_content_fallback(client: OllamaClient) -> None:
    """JSON tool call emitted in content (no tool_calls field) should be JSON_IN_CONTENT_FALLBACK."""
    respx.post("http://ollama.test/api/chat").mock(
        return_value=httpx.Response(
            200,
            json={
                "message": {
                    "role": "assistant",
                    "content": '{"name": "get_weather", "arguments": {"city": "Tokyo"}}',
                }
            },
        )
    )

    results = await run_suite(client, "test-model")
    outcomes = {r.case_id: r.outcome for r in results}
    assert outcomes.get("single_tool_basic") == CaseOutcome.JSON_IN_CONTENT_FALLBACK


@respx.mock
async def test_run_suite_rejected_by_backend(client: OllamaClient) -> None:
    """HTTP 400 when tools are present should map to REJECTED_BY_BACKEND."""
    respx.post("http://ollama.test/api/chat").mock(
        return_value=httpx.Response(400, text="model does not support tools")
    )

    results = await run_suite(client, "test-model")
    outcomes = {r.case_id: r.outcome for r in results}
    assert outcomes.get("single_tool_basic") == CaseOutcome.REJECTED_BY_BACKEND
    assert any(r.detail and "HTTP 400" in r.detail for r in results)


@respx.mock
async def test_run_suite_timeout_or_error(client: OllamaClient) -> None:
    """Connection/timeout errors should map to TIMEOUT_OR_ERROR without aborting the suite."""
    respx.post("http://ollama.test/api/chat").mock(
        side_effect=httpx.ConnectTimeout("connection timed out")
    )

    results = await run_suite(client, "test-model")
    outcomes = {r.case_id: r.outcome for r in results}
    assert outcomes.get("single_tool_basic") == CaseOutcome.TIMEOUT_OR_ERROR
    # Suite continues for all cases
    assert len(results) == 4
    assert all(r.outcome == CaseOutcome.TIMEOUT_OR_ERROR for r in results)
