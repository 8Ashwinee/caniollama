# What caniollama sends, and what it never sends

## Sent, only if you say yes, every single run

- Model name (e.g. `qwen2.5-coder:7b`)
- Quantization level (e.g. `q4_K_M`), if Ollama reports one
- Ollama version
- Test suite version
- Coarse OS (`linux` / `macos` / `windows`)
- Pass/fail outcome per test case (one of: structured pass, JSON-in-content
  fallback, rejected by backend, error/timeout)
- Timestamp

## Never sent, under any circumstances

- The test prompts themselves
- Any model output, structured or otherwise
- Anything from your local filesystem, environment, or network beyond the above
- Anything if you decline the prompt -- there is no "phone home anyway" path

## Why so little

This project measures whether the *plumbing* works (does tool calling return
a structured field, does it fall back to text, does the backend reject the
request) -- not how good a model's reasoning is. That narrower question needs
far less data than a quality benchmark would, so we ask for less than we
technically could.
