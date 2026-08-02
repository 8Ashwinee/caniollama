"""Classifies a raw /api/chat response (or a raised client exception) into a CaseOutcome.

This is the piece most likely to need refinement as new models and Ollama
versions are observed -- any change here is a SUITE_VERSION bump.
"""

from __future__ import annotations

import json
from typing import Any

from compat_check.models import CaseOutcome
from compat_check.suite.cases import TestCase


def _content_looks_like_tool_call_json(content: str) -> bool:
    """Heuristic for category 2: model knows the *shape* of a tool call but emits it
    as JSON-ish text in `content` instead of the structured `tool_calls` field."""
    stripped = content.strip()
    if not stripped.startswith(("{", "[")):
        return False
    try:
        parsed = json.loads(stripped)
    except (json.JSONDecodeError, TypeError):
        return False

    candidates = parsed if isinstance(parsed, list) else [parsed]
    for candidate in candidates:
        if not isinstance(candidate, dict):
            continue
        keys = {k.lower() for k in candidate}
        if {"name", "arguments"} <= keys or {"function", "arguments"} <= keys:
            return True
        if "tool_calls" in keys or "function_call" in keys:
            return True
    return False


def score_response(case: TestCase, response: dict[str, Any]) -> CaseOutcome:
    message = response.get("message", {})
    tool_calls = message.get("tool_calls")
    content = message.get("content", "") or ""

    if case.expects_no_tool_call:
        # A structured tool call here is arguably "too eager", but plumbing-wise the
        # model still demonstrated structured calling -- so we still score it a pass
        # for *capability*; over-eagerness is a quality concern, out of scope here.
        if tool_calls:
            return CaseOutcome.STRUCTURED_PASS
        if _content_looks_like_tool_call_json(content):
            return CaseOutcome.JSON_IN_CONTENT_FALLBACK
        return CaseOutcome.STRUCTURED_PASS  # correctly answered without calling a tool

    if tool_calls:
        return CaseOutcome.STRUCTURED_PASS
    if _content_looks_like_tool_call_json(content):
        return CaseOutcome.JSON_IN_CONTENT_FALLBACK
    return CaseOutcome.JSON_IN_CONTENT_FALLBACK if content else CaseOutcome.TIMEOUT_OR_ERROR
