"""Fixed, deterministic test cases. Each targets one dimension of tool-calling
compatibility. Prompts are intentionally simple and unambiguous -- the goal is
to test plumbing ('does it call the tool'), not reasoning quality.

Do not tweak prompt wording casually: any change here requires bumping
SUITE_VERSION in version.py.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

_GET_WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a city.",
        "parameters": {
            "type": "object",
            "properties": {"city": {"type": "string", "description": "City name"}},
            "required": ["city"],
        },
    },
}

_EXTRA_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": f"noop_tool_{i}",
            "description": f"Placeholder tool #{i}, not relevant to the prompt.",
            "parameters": {"type": "object", "properties": {}},
        },
    }
    for i in range(1, 5)
]


@dataclass
class TestCase:
    case_id: str
    description: str
    messages: list[dict[str, Any]]
    tools: list[dict[str, Any]]
    # If True, the correct behavior is to NOT call a tool -- used to catch
    # models that over-eagerly call tools even when none are needed.
    expects_no_tool_call: bool = False
    multiturn_followup: dict[str, Any] | None = field(default=None)


CASES: list[TestCase] = [
    TestCase(
        case_id="single_tool_basic",
        description="One relevant tool, unambiguous prompt -- baseline structured call.",
        messages=[{"role": "user", "content": "What is the weather in Tokyo?"}],
        tools=[_GET_WEATHER_TOOL],
    ),
    TestCase(
        case_id="multi_tool_5x",
        description="Five tools offered, only one relevant -- tests selection under noise.",
        messages=[{"role": "user", "content": "What is the weather in Nairobi?"}],
        tools=[_GET_WEATHER_TOOL, *_EXTRA_TOOLS],
    ),
    TestCase(
        case_id="no_tools_needed_control",
        description="No tool is relevant -- control case; a good model should NOT call one.",
        messages=[{"role": "user", "content": "Say hello in French."}],
        tools=[_GET_WEATHER_TOOL],
        expects_no_tool_call=True,
    ),
    TestCase(
        case_id="multiturn_tool_result",
        description=(
            "Second turn: a tool result is already in the conversation. Tests whether "
            "the model handles a prior tool call/result correctly rather than looping."
        ),
        messages=[
            {"role": "user", "content": "What is the weather in Oslo?"},
        ],
        tools=[_GET_WEATHER_TOOL],
        multiturn_followup={
            "role": "tool",
            "content": '{"city": "Oslo", "condition": "cloudy", "temp_c": 8}',
        },
    ),
]
