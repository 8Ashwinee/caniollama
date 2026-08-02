# caniollama

Two independent projects implementing the registry described in `TOOL_CALLING_REGISTRY_PROPOSAL.md`:

- **`compat-check/`** — the `caniollama` CLI (PyPI package, uv-managed). Run
  `uvx caniollama check <model>` against a local Ollama instance.
- **`compat-registry/`** — the FastAPI backend behind the public registry (uv-managed).
  `POST /submissions`, `GET /models`, `GET /models/{name}`, `GET /stats`.

See each subdirectory's own README for setup, and `COMPAT_REGISTRY_PROJECT_ARCHITECTURE.md`
for the full architecture writeup and phased build order.

## Quick start

```bash
# CLI
cd compat-check && uv sync && uv run pytest

# Backend
cd compat-registry && uv sync && uv run pytest
uv run uvicorn compat_registry.main:app --reload   # http://localhost:8000/docs
```
