# Submission data format

This is the source of truth both `caniollama` (the CLI) and `compat-registry` (this
service) independently implement. It's kept as a doc, not a shared package, so the two
repos' release cycles stay fully decoupled.

```json
{
  "model_name": "qwen2.5-coder:7b",
  "model_quantization": "q4_K_M",
  "ollama_version": "0.6.2",
  "suite_version": "1.0.0",
  "os": "linux",
  "case_results": {
    "single_tool_basic": "structured_pass",
    "multi_tool_5x": "structured_pass",
    "multiturn_tool_result": "json_fallback",
    "no_tools_needed_control": "structured_pass"
  },
  "timestamp": "2026-08-02T10:15:00Z"
}
```

## Field reference

| Field | Type | Notes |
|---|---|---|
| `model_name` | string | As reported by `ollama list`, e.g. `qwen2.5-coder:7b` |
| `model_quantization` | string \| null | e.g. `q4_K_M`; null if Ollama doesn't report one |
| `ollama_version` | string | From `GET /api/version` on the local Ollama instance |
| `suite_version` | string | The `caniollama` test-suite version that produced this result |
| `os` | string | One of `linux`, `macos`, `windows` |
| `case_results` | object | `case_id -> outcome`, see below |
| `timestamp` | ISO 8601 datetime | UTC |

## Outcome values

- `structured_pass` -- native `tool_calls` field returned
- `json_fallback` -- tool-call intent present but only as JSON-shaped text in `content`
- `rejected` -- Ollama returned a 4xx because `tools` was included in the request
- `error` -- timeout or an unclassifiable failure

## What is never in this payload

No prompts, no model output text, no free-form fields. See `caniollama`'s
[privacy](../privacy.md) for the full explanation shown to users before they submit.
