# Test suite spec — v1.0.0

This documents what each fixed case in `src/compat_check/suite/cases.py` tests and why.
Any change to a prompt, a tool schema, or a scoring rule in `scoring.py` requires bumping
`SUITE_VERSION` in `suite/version.py` — this is what keeps registry results comparable
over time (see [data format](registry/data-format.md)).

## `single_tool_basic`
One relevant tool offered, one unambiguous prompt ("What is the weather in Tokyo?").
This is the baseline: does the model return a structured `tool_calls` field at all,
under the easiest possible conditions. If a model fails this one, it almost certainly
falls into compatibility category 2 or 3.

## `multi_tool_5x`
Same prompt shape, but five tools offered (one relevant, four irrelevant no-ops). Tests
whether structured calling holds up once the model has to *select* the right tool from
a small list, rather than just echoing the only option it was given.

## `no_tools_needed_control`
A prompt with no tool relevance at all ("Say hello in French"), with a weather tool
still offered. This is a control: a model that calls a tool here anyway isn't
necessarily marked as failing (over-eager tool use is a reasoning-quality concern, out
of scope for this project), but it's tracked separately so the registry can eventually
surface "tends to over-call tools" as its own signal if that becomes useful.

## `multiturn_tool_result`
First turn asks for weather; the suite then injects a synthetic tool result message and
asks again. Tests whether the model can continue a conversation that already contains a
completed tool call/result correctly, rather than looping, re-calling the same tool, or
breaking format. This is the case most likely to expose category 2 behavior in models
that pass `single_tool_basic` — first-turn tool calling is the easy case; handling the
result correctly is where a lot of "sort of supports tools" models fall down.

## Deliberately out of scope

- Tool call **argument correctness** (e.g. did it extract "Tokyo" correctly) — that's
  reasoning quality, not plumbing, and belongs to a benchmark project, not this one.
- Parallel/simultaneous tool calls — a plausible v1.1.0 addition once the four cases
  above are validated against enough real models.
- Streaming responses (`stream: true`) — Ollama's tool-calling behavior under streaming
  differs from non-streaming in ways worth a dedicated case, deferred to a future
  suite version.

## Adding a new case

1. Add the `TestCase` to `cases.py`.
2. Add scoring logic to `scoring.py` if the existing pass/fail heuristics don't cover it.
3. Document it here.
4. Bump `SUITE_VERSION`.
5. Add a fixture-based test in `tests/test_scoring.py`.
