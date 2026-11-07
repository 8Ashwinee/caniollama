# caniollama

Does this local Ollama model actually support tool calling? Find out in seconds, not by
reading a six-month-old blog post.

```bash
uvx caniollama check qwen2.5-coder:7b
```

or test everything you've pulled:

```bash
uvx caniollama check
```

## What it does

Runs a small, fixed test suite against a locally running Ollama instance and classifies
the result into one of three real answers:

1. **Structured pass** -- the model returns a proper `tool_calls` field.
2. **JSON-in-content fallback** -- the model knows tool calling exists but emits the
   intent as JSON-shaped text instead of the structured field.
3. **Rejected by backend** -- Ollama 400s the moment `tools` is included.

After a run, you'll be asked -- every time, explicitly -- whether to submit the result
(metadata only: model name, quantization, Ollama version, pass/fail per case) to the
public [caniollama registry](https://github.com/caniollama/caniollama-registry). See
[`docs/privacy.md`](https://anjallll.github.io/caniollama/privacy/) for exactly what is and isn't ever sent.

## Install

No install needed for a one-off check:

```bash
uvx caniollama check <model>
# or
pipx run caniollama check <model>
```

For repeated use:

```bash
uv tool install caniollama
```

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
```

## License

MIT
