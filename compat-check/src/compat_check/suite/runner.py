"""Executes the fixed case list against one model, producing CaseResults.

Every case is isolated: one case erroring or timing out never aborts the run
for the remaining cases.
"""

from __future__ import annotations

import time

from compat_check.models import CaseOutcome, CaseResult
from compat_check.ollama_client import OllamaClient, OllamaError, OllamaRejected
from compat_check.suite.cases import CASES, TestCase
from compat_check.suite.scoring import score_response


async def _run_case(client: OllamaClient, model: str, case: TestCase) -> CaseResult:
    messages = list(case.messages)
    started = time.monotonic()
    try:
        response = await client.chat(model=model, messages=messages, tools=case.tools)

        if case.multiturn_followup:
            # Feed the assistant's reply + a synthetic tool result back in, then
            # score the model's *second* response -- this is what actually tests
            # multi-turn tool-result handling, not just the first call.
            messages.append(response.get("message", {}))
            messages.append(case.multiturn_followup)
            response = await client.chat(model=model, messages=messages, tools=case.tools)

        outcome = score_response(case, response)
        latency_ms = int((time.monotonic() - started) * 1000)
        return CaseResult(case_id=case.case_id, outcome=outcome, latency_ms=latency_ms)

    except OllamaRejected as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        return CaseResult(
            case_id=case.case_id,
            outcome=CaseOutcome.REJECTED_BY_BACKEND,
            latency_ms=latency_ms,
            detail=f"HTTP {exc.status_code}",
        )
    except OllamaError as exc:
        latency_ms = int((time.monotonic() - started) * 1000)
        return CaseResult(
            case_id=case.case_id,
            outcome=CaseOutcome.TIMEOUT_OR_ERROR,
            latency_ms=latency_ms,
            detail=str(exc)[:200],
        )


async def run_suite(client: OllamaClient, model: str) -> list[CaseResult]:
    results = []
    for case in CASES:
        results.append(await _run_case(client, model, case))
    return results
