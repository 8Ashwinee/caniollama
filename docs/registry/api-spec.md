# API spec (prose)

FastAPI auto-generates the full OpenAPI schema at `/openapi.json` and an interactive UI
at `/docs`. This is a short prose summary for quick reference.

## `POST /submissions`
Create a new compatibility result. Open, no auth, rate-limited per IP
(`COMPAT_REGISTRY_RATE_LIMIT_PER_MINUTE`, default 10/min).
Body: see [data format](data-format.md). Returns `201` with the stored record (including its
generated `id`), or `422` on schema validation failure, or `429` if rate-limited.

## `GET /models`
Returns every model that has at least one submission, with quantizations seen, total
report count, and the latest suite version reported for it.

## `GET /models/{model_name}`
Returns a full compatibility summary for one model: report counts broken down by
quantization and by Ollama version, plus per-test-case pass rates. `404` if the model
has no reports yet. `model_name` may contain a `:` tag (e.g. `qwen2.5-coder:7b`) and is
matched via a path-type parameter to support that.

## `GET /stats`
Registry-wide totals: submission count, model count, most-tested models, and the
current expected suite version.

## `GET /health`
Liveness check, always `200 {"status": "ok"}` if the service is up.

## `GET /version`
Service version and current expected suite version -- lets an out-of-date `caniollama`
CLI install detect it should upgrade.
