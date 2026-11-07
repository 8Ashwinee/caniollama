# compat-registry

The open, vendor-neutral registry behind [caniollama](https://github.com/caniollama/caniollama):
a continuously-updated answer to "does this local Ollama model actually support tool calling?"

Not owned by any one tool-builder's project -- that neutrality is the point.

## Run locally

```bash
uv sync
uv run uvicorn compat_registry.main:app --reload
```

Then visit `http://localhost:8000/docs` for the interactive OpenAPI UI.

## API surface

- `POST /submissions` -- open, unauthenticated, rate-limited. Body must match
  [`docs/data-format.md`](https://anjallll.github.io/caniollama/registry/data-format/).
- `GET /models` -- list of all tested models with report counts.
- `GET /models/{model_name}` -- per-quantization / per-Ollama-version / per-case
  pass-rate breakdown for one model.
- `GET /stats` -- registry-wide totals.
- `GET /health`, `GET /version`.

## Storage

Phase 2 MVP (current default): flat JSON files under `data/results/`, validated and
merged via PR (see `.github/workflows/validate-submission.yml`). No server-side database
required.

Phase 3+: set `COMPAT_REGISTRY_STORAGE_BACKEND=db` to switch to the SQLite-backed
implementation in `storage/db_backend.py`. Both backends implement the same
`StorageBackend` protocol (`storage/base.py`), so route code never changes.

## Development

```bash
uv sync
uv run pytest
uv run ruff check .
uv run mypy src
```

## License

MIT -- the aggregated data is open and freely queryable/exportable, not locked behind
an account or paid tier.
