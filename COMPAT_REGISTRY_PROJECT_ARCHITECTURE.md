# Project Architecture & Implementation Plan
## Local Model Tool-Calling Compatibility Registry

This document turns `TOOL_CALLING_REGISTRY_PROPOSAL.md` into a concrete, buildable architecture: two independent repos, their internal structure, tech stack, data model, CI/release pipelines, and a phased implementation order. It assumes the "separate project, packaged for zero-friction install" decision already made in the prior discussion.

---

## 1. High-level system shape

Two independent, separately-versioned projects. Neither imports the other.

```
┌─────────────────────────┐         ┌──────────────────────────────┐
│   compat-check (CLI)     │  HTTPS  │   compat-registry (backend)   │
│   PyPI package            │ ──────▶ │   FastAPI service + data      │
│   uvx compat-check        │  POST   │   GET /models, /submit         │
└─────────────────────────┘         └──────────────────────────────┘
         ▲                                          ▲
         │ tests local Ollama                       │ read-only queries
         │                                          │
   ┌───────────┐                          ┌─────────────────────┐
   │  Ollama    │                          │  localgate /model     │
   │  (local)   │                          │  picker (consumer)    │
   └───────────┘                          └─────────────────────┘
```

- **`compat-check`** — zero-install CLI, runs the fixed test suite against whatever's pulled locally, optionally submits a metadata-only result.
- **`compat-registry`** — FastAPI backend that accepts submissions, stores them, and serves aggregated pass/fail stats. Starts as the smallest possible thing that can be called an API (Phase 2 below), not a full service from day one.
- **Consumers** (localgate's `/model` picker, Cline, Continue.dev, anyone) hit the registry's public read API. They are not special — same endpoint everyone else uses.

---

## 2. Repo 1 — `compat-check` (the CLI package)

### 2.1 Tech stack
- **Package/dependency management:** `uv` (matches the pattern already established for localgate)
- **Distribution:** PyPI, via `uv build` + trusted publishing (OIDC, no stored API tokens)
- **Runtime deps:** kept deliberately minimal — `httpx` (talk to local Ollama + submit results), `pydantic` (result schema), `typer` or `click` (CLI), `rich` (readable terminal output). No FastAPI, no DB driver — this package must install in seconds.
- **Invocation model:** designed for `uvx compat-check` / `pipx run compat-check` — run-once-and-forget, no persistent install assumed.

### 2.2 Directory structure

```
compat-check/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .github/
│   └── workflows/
│       ├── ci.yml              # lint, type-check, test on PR/push
│       └── release.yml         # build + publish to PyPI on tag
├── src/
│   └── compat_check/
│       ├── __init__.py
│       ├── __main__.py         # `python -m compat_check`
│       ├── cli.py              # entry point, argument parsing, orchestration
│       ├── ollama_client.py    # talks to local Ollama's /api/chat + /api/tags
│       ├── discovery.py        # finds locally pulled models, detects Ollama version
│       ├── suite/
│       │   ├── __init__.py
│       │   ├── version.py      # SUITE_VERSION constant, bump on any prompt/scoring change
│       │   ├── cases.py        # fixed test prompts, one per compatibility dimension
│       │   ├── runner.py       # executes cases against a model, times out safely
│       │   └── scoring.py      # classifies each case as: structured_pass /
│       │                       #   json_in_content_fallback / rejected_by_backend / error
│       ├── report.py           # builds the local pass/fail summary + rich terminal output
│       ├── submission.py       # builds the metadata-only payload, explicit opt-in prompt
│       ├── models.py           # pydantic schemas: TestResult, RunReport, SubmissionPayload
│       └── config.py           # env vars, registry base URL, timeouts
├── tests/
│   ├── conftest.py
│   ├── test_cli.py
│   ├── test_scoring.py         # scoring logic tested against recorded fixture responses
│   ├── test_submission.py      # asserts payload NEVER contains prompt/output content
│   └── fixtures/
│       └── ollama_responses/   # recorded raw responses for each of the 3 categories
└── docs/
    ├── test-suite-spec.md      # what each fixed case tests and why, versioned alongside suite/
    └── privacy.md              # exact shape of what is/isn't ever submitted
```

### 2.3 Key design points

**Test suite versioning is a first-class citizen.** `suite/version.py` holds `SUITE_VERSION = "1.0.0"`. Every case in `cases.py` is tagged with the suite version it belongs to. Any change to a prompt, a scoring rule, or a pass/fail threshold is a version bump — this is what makes registry results comparable over time, per the earlier design decision. `RunReport` always carries `suite_version` alongside the results.

**Scoring categories map directly to the proposal's three "true answers":**
```python
class CaseOutcome(str, Enum):
    STRUCTURED_PASS = "structured_pass"          # category 1
    JSON_IN_CONTENT_FALLBACK = "json_fallback"    # category 2
    REJECTED_BY_BACKEND = "rejected"              # category 3
    TIMEOUT_OR_ERROR = "error"
```

**Submission payload — enforced minimal, not just documented minimal.** `SubmissionPayload` in `models.py` is the *only* pydantic model allowed to reach `submission.py`'s POST call. It has no field capable of holding a prompt or a model output — this is a structural guarantee, not a runtime check:
```python
class SubmissionPayload(BaseModel):
    model_name: str
    model_quantization: str | None
    ollama_version: str
    suite_version: str
    os: str                      # coarse: "linux" / "macos" / "windows"
    case_results: dict[str, CaseOutcome]   # case_id -> outcome, no content
    timestamp: datetime
```
`test_submission.py` asserts (via schema introspection, not just a docstring) that no field type could ever carry free text longer than a version string / enum value.

**Opt-in flow lives in `submission.py`, not `cli.py`.** The prompt is shown *every run*, after results are already printed to the terminal — never before, never silently skipped, never persisted as a "don't ask again" default. This matches the proposal's "opt-in, always" principle literally.

**Entry point (`pyproject.toml` excerpt):**
```toml
[project]
name = "compat-check"
dynamic = ["version"]
requires-python = ">=3.10"
dependencies = ["httpx>=0.27", "pydantic>=2.6", "typer>=0.12", "rich>=13.7"]

[project.scripts]
compat-check = "compat_check.cli:app"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

---

## 3. Repo 2 — `compat-registry` (the backend)

This is where "use FastAPI, use uv" applies directly. Built in two sub-phases (detailed in §5), but the structure below is the end-state shape — Phase 2's GitHub-file store lives at the same paths, just with `storage/file_backend.py` active instead of `storage/db_backend.py`.

### 3.1 Tech stack
- **Framework:** FastAPI
- **Package/dependency management:** `uv`
- **Storage (Phase 2, MVP):** a structured JSON/SQLite file in the repo itself, written to via validated GitHub PRs or a merge Action — no server persistence needed yet.
- **Storage (Phase 3+):** SQLite file on a small persistent volume, or Postgres if/when submission volume justifies it. `storage/` is written as a small interface so this swap doesn't touch route code.
- **Deployment (Phase 3+):** a single small container (Fly.io / Railway / Render-class host) — deliberately not over-provisioned; this is a low-write, read-heavy public API.
- **Validation:** pydantic v2 (shared shape with `compat-check`'s `SubmissionPayload`, kept in sync via a small shared schema doc, not a shared package — the two repos stay dependency-independent per the proposal's "vendor-neutral, decoupled lifecycle" principle).

### 3.2 Directory structure

```
compat-registry/
├── pyproject.toml
├── uv.lock
├── README.md
├── LICENSE
├── CHANGELOG.md
├── .github/
│   └── workflows/
│       ├── ci.yml                  # lint, type-check, test
│       ├── validate-submission.yml # Phase 2: validates PR-submitted result files
│       └── deploy.yml              # Phase 3: build + deploy container on merge to main
├── data/                           # Phase 2 MVP: the registry itself, PR-updated
│   ├── schema.json                 # JSON Schema submissions are validated against
│   └── results/
│       └── <model_name>/<yyyy-mm-dd>-<uuid>.json   # one file per submission
├── src/
│   └── compat_registry/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app instance, router registration, CORS
│       ├── config.py                # settings via pydantic-settings (env-driven)
│       ├── api/
│       │   ├── __init__.py
│       │   ├── deps.py             # shared FastAPI dependencies (rate limiter, storage handle)
│       │   ├── models_routes.py    # GET /models, GET /models/{name}
│       │   ├── submit_routes.py    # POST /submissions
│       │   ├── stats_routes.py     # GET /stats, aggregate pass-rate views
│       │   └── health_routes.py    # GET /health, GET /version
│       ├── schemas/
│       │   ├── __init__.py
│       │   ├── submission.py       # mirrors compat-check's SubmissionPayload shape
│       │   └── aggregate.py        # ModelCompatSummary, per-suite-version breakdowns
│       ├── storage/
│       │   ├── __init__.py
│       │   ├── base.py             # StorageBackend protocol (get, put, aggregate)
│       │   ├── file_backend.py     # Phase 2: reads/writes data/results/*.json
│       │   └── db_backend.py       # Phase 3: SQLite/Postgres implementation
│       ├── aggregation.py          # computes pass-rate %, grouped by suite_version + ollama_version
│       └── rate_limit.py           # basic abuse protection on POST /submissions
├── tests/
│   ├── conftest.py
│   ├── test_submit_routes.py
│   ├── test_aggregation.py
│   └── test_storage_backends.py    # same test suite run against both backends
└── docs/
    ├── api-spec.md                 # OpenAPI is auto-generated by FastAPI; this is the prose version
    └── data-format.md              # the exact JSON Schema submissions must satisfy
```

### 3.3 Core API surface (Phase 3 shape; Phase 2 exposes the same contract via static JSON + a thin FastAPI read layer)

```
POST /submissions
    body: SubmissionPayload (as defined in compat-check, mirrored here)
    -> 201, {id}
    rate-limited per IP, no auth required (open, per proposal's "open data" principle)

GET /models
    -> list of {model_name, quantizations[], total_reports, latest_suite_version}

GET /models/{model_name}
    -> {model_name, per_quantization: [...], per_ollama_version: [...],
        pass_rate_by_case: {...}, total_reports, first_seen, last_seen}

GET /stats
    -> registry-wide totals, most-tested models, suite version distribution

GET /health
GET /version   # exposes current expected suite_version, so old CLI installs can self-detect staleness
```

**`GET /version` matters more than it looks.** It lets an old `compat-check` install notice its `suite_version` is behind and print an upgrade nudge — closing the loop the proposal flags about stale local benchmarks, but for the tool itself.

### 3.4 `pyproject.toml` excerpt

```toml
[project]
name = "compat-registry"
dynamic = ["version"]
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.115",
    "uvicorn[standard]>=0.30",
    "pydantic>=2.6",
    "pydantic-settings>=2.3",
]

[dependency-groups]
dev = ["pytest", "pytest-asyncio", "httpx", "ruff", "mypy"]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

Note: `compat-registry` is a *service*, not something users `pip install` — it's deployed, not published to PyPI. `uv` here is purely for dependency locking and reproducible dev/deploy environments (`uv sync`, `uv run uvicorn compat_registry.main:app`), not for package distribution.

---

## 4. Shared data contract (kept as docs, not shared code)

Both repos independently implement the same shape, documented once and referenced from both READMEs, so neither repo depends on the other:

```json
{
  "model_name": "qwen2.5-coder",
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
This file (`docs/data-format.md` in both repos) is the actual source of truth. Keeping it as a doc rather than a shared PyPI package is deliberate — it preserves the "decoupled release cycles" property from the original architecture decision; a breaking change in one repo doesn't force a synchronized release in the other, only a version bump negotiation.

---

## 5. Phased build order

This mirrors the sequencing already agreed on — prototype cheaply, package once stable, backend starts as a file store before it's a service.

### Phase 0 — Prototype (throwaway, inside localgate's working dir, not shipped)
- Hand-write 5–8 fixed test cases against `llama3` and `qwen2.5-coder` manually.
- Nail down what "pass/fail per category" means in code before it's load-bearing anywhere.
- No packaging, no repo, no CI. Exit criteria: scoring logic feels stable across repeated runs.

### Phase 1 — Extract `compat-check`, no submission yet
- Stand up the repo per §2.2, minus `submission.py` and the registry-facing parts of `config.py`.
- CI (`ci.yml`): `uv run ruff check`, `uv run mypy`, `uv run pytest` on every PR.
- Validate locally against every Ollama model you can pull; treat this as the real test suite validation pass.
- Exit criteria: suite version can be frozen at `1.0.0`.

### Phase 2 — Publish `compat-check` to PyPI; registry MVP as a GitHub-file store
- `release.yml`: on tag push, `uv build` then publish via PyPI trusted publishing (OIDC — reuse the trusted-publisher app setup already done for localgate).
- Verify `uvx compat-check` works end-to-end from a clean machine before announcing anywhere.
- Stand up `compat-registry`'s repo structure with `storage/file_backend.py` only — submissions land as PR-opened JSON files validated by `validate-submission.yml` (schema check + suite-version check), merged by a maintainer or auto-merged if the Action's validation passes.
- `compat-check`'s `submission.py` opens submissions as PRs against this repo (via GitHub API) rather than hitting a live server yet — no server to run at all in this phase.
- Exit criteria: real submissions flowing in from more than just you.

### Phase 3 — Real FastAPI service
- Implement `storage/db_backend.py` (SQLite to start), swap it in behind the same `StorageBackend` protocol — route code in `api/` doesn't change.
- `POST /submissions` goes live; `compat-check`'s `submission.py` switches from "open a PR" to "POST to registry URL," gated by the same opt-in prompt.
- Deploy via `deploy.yml` to a small container host.
- Add `rate_limit.py` before this goes live publicly — this is the first phase with an open write endpoint.
- Exit criteria: `GET /models/{name}` returns real, current aggregate data; dashboard (simple static frontend or just the OpenAPI docs at `/docs`) is publicly linkable.

### Phase 4 — localgate integration (optional, last, per the original proposal)
- `/model` picker in localgate calls `GET /models/{name}` as one read-only client among potentially many.
- No special access, no shared code — proves the registry's public API is actually sufficient for a real consumer, which was the whole point of building it standalone first.

---

## 6. Naming, licensing, repo settings (do before Phase 1 code)

- Pick from `toolcallwatch` / `caniollama` / `localtoolcheck` — check PyPI name availability *and* GitHub org/repo availability together before committing, since the CLI's PyPI name and the registry's repo name should match for discoverability.
- License: permissive (MIT or Apache-2.0) on both repos — matches the "open data, no paid tier" principle; a copyleft license would work against the "anyone can integrate" goal.
- Both repos: enable GitHub Discussions or a `CONTRIBUTING.md` pointing to how to add a new test case — the registry's authority depends on the community trusting the test suite's design, not just the data pipeline.

---

## 7. What deliberately isn't in this architecture

- No shared Python package between the two repos (see §4 — intentional).
- No auth/accounts on the registry's read or write paths in any phase — rate limiting is the only abuse control, matching "open data, no account wall."
- No hosted dashboard framework decision made yet — Phase 3 ships `/docs` (FastAPI's built-in OpenAPI UI) as the interim dashboard; a dedicated frontend is a Phase 5+ decision made only once real usage data justifies it.
