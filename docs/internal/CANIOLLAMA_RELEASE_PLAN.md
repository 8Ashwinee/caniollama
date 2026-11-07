# caniollama — Plan to Go From Current State to a Released Package

Scope: `compat-check` (the CLI, published to PyPI as `caniollama`) and
`compat-registry` (the FastAPI backend, deployed as a public service). This
plan assumes both stay independent of localgate, per
`TOOL_CALLING_REGISTRY_PROPOSAL.md`'s non-goals — localgate becomes a
*consumer* of what's produced here, not a co-owner of it.

## Where things actually stand today

- `compat-check`: CLI, test suite (4 cases), report rendering, opt-in
  submission flow, and unit tests all exist and look complete.
  `pyproject.toml` already has a `release.yml` workflow wired for PyPI
  **trusted publishing** (OIDC, tag-triggered) — the pipeline is ready, it
  has just never been run for a real tag.
- `compat-registry`: FastAPI app, all four routes (`/submissions`,
  `/models`, `/models/{name}`, `/stats`), two storage backends behind a
  shared protocol, aggregation logic, and CI — but it has never been
  deployed anywhere. There is no live URL for `compat-check` to submit to
  or for anyone (including localgate) to query.
- The two schemas (`compat_check.models.SubmissionPayload` and
  `compat_registry.schemas.submission.SubmissionIn`) are intentionally
  **hand-mirrored, not shared** — `docs/data-format.md` is supposed to be
  the source of truth both sides follow. This needs to actually be
  verified field-by-field before anyone depends on it, because right now
  nothing enforces that the two definitions stay in sync except a doc.

## Phase 1 — Make the registry real (blocks everything else)

A CLI with nowhere to submit to, and nothing for localgate to query, is
the actual current bottleneck — not the CLI itself.

1. **Pick a deployment target and stand it up.** `Dockerfile` and
   `deploy.yml` already exist under `compat-registry/` — confirm what
   they target (a specific host, Fly.io, Render, a VPS, etc.) and get one
   real deployment live, even if it's a single small instance to start.
2. **Decide the Phase 2 → Phase 3 storage question now, not later.**
   The README says flat JSON files under `data/results/` (merged via PR)
   is the current default, with SQLite as a `COMPAT_REGISTRY_STORAGE_BACKEND=db`
   switch-over. A PR-merge-based write path works for a slow trickle of
   manual contributions; it does **not** work once `compat-check` is
   calling `POST /submissions` programmatically and expects an immediate
   `201`. Decide before launch whether v0.1 ships with the DB backend
   from day one (recommended, since the API already treats writes as
   synchronous HTTP) or whether the PR-based flow is a deliberate
   pre-launch-only stage.
3. **Verify the submission schema round-trip end-to-end**, not just by
   inspection. Run `compat-check`'s `submit_result()` against a live
   local instance of `compat-registry` and confirm a real `201` with a
   real `SubmissionRecord` back — the field-by-field mirror between the
   two `pyproject.toml`-separated schemas is the single most likely
   silent-breakage point in this whole system, since nothing but
   `docs/data-format.md` enforces they match.
4. **Rate limiting sanity-check.** `rate_limit.py` exists — confirm the
   limit is generous enough for a legitimate user running `caniollama
   check` with no argument (which submits once per locally-pulled model,
   potentially many in one run) without tripping it.
5. **`GET /models/{model_name}` response for zero-report models.**
   Confirmed from `models_routes.py`: it 404s. Any consumer (including
   localgate) needs to treat a 404 as "no data yet," not as an error —
   worth stating explicitly in `docs/api-spec.md` so every future
   consumer implements this the same way.

## Phase 2 — Harden compat-check before the first real release

1. **Bump `SUITE_VERSION` discipline.** `cases.py`'s docstring already
   states prompts must not be tweaked without bumping `suite/version.py`.
   Before v0.1.0 ships, make sure this is enforced somewhere (a CI check
   that diffs `cases.py` against the last tagged `SUITE_VERSION`) rather
   than relying on a comment being remembered.
2. **Cross-platform Ollama discovery.** `discovery.py` and `current_os()`
   exist — verify `discover_ollama_version()` and `discover_models()`
   behave correctly against a real Ollama install on macOS, Linux, and
   Windows (WSL), since three-category classification is only useful if
   the discovery step itself doesn't misreport the environment.
3. **Registry-unreachable path.** Confirm the CLI's behavior when
   `registry_base_url` is unset, unreachable, or times out is exactly
   what the README promises — a graceful "Submission failed — registry
   may be unreachable" and nothing else. This is already coded in
   `submission.py` (`httpx.RequestError` → `False`, never raises) — just
   needs an explicit test against a genuinely dead endpoint, not a mock.
4. **`docs/privacy.md` accuracy pass.** Read it against the actual
   `SubmissionPayload` fields one more time before release — this is the
   document a skeptical adopter (including anyone evaluating whether to
   let localgate call this by default) will actually read.

## Phase 3 — The actual PyPI release

1. Register the `caniollama` project name on PyPI and set up the trusted
   publisher (OIDC) binding to the `caniollama` GitHub repo — required
   for `release.yml`'s `pypa/gh-action-pypi-publish` step to work, and
   currently unverified as done.
2. Tag `v0.1.0`, let `release.yml` build and publish.
3. Verify `uvx caniollama check <model>` and `pipx run caniollama check
   <model>` both work against a clean environment — these are the two
   commands the READMEs promise as the "no install needed" path, and
   they're the first impression anyone (localgate users included) will
   have of the tool.
4. Publish the registry's live URL somewhere permanent (its own README,
   plus `docs/api-spec.md`) — this is the URL every future consumer,
   including localgate's `caniollama_registry_url` default, will be
   hardcoded to.

## Phase 4 — Post-release, ahead of localgate depending on it

1. **API stability commitment.** Once localgate (and potentially other
   tools) start depending on `GET /models/{model_name}`'s exact response
   shape (`ModelCompatSummary`), that shape needs a stated stability
   guarantee — even an informal "won't remove fields in a minor version"
   note in `docs/api-spec.md` — so downstream consumers aren't caught off
   guard by a registry-side change.
2. **A "how to integrate" doc**, separate from the CLI README, aimed at
   tool builders (not end users) — covering the read-only `GET` endpoints
   specifically, since that's the integration surface localgate (and
   anyone else) actually needs, distinct from the opt-in `POST` flow the
   current docs are written for.
3. **Seed data.** A brand-new registry with zero submissions makes
   localgate's picker annotations useless on day one. Worth deciding
   whether to pre-seed it with a manual first batch of runs across common
   models (`qwen2.5-coder`, `llama3`, `mistral`, etc.) so early adopters
   — localgate's users included — see something other than "no data yet"
   for the models people actually pull.

## Sequencing note

Phases 1–3 have to happen in something close to this order — there's no
point polishing the CLI (Phase 2) or cutting a release (Phase 3) while
there's nowhere for it to submit to (Phase 1). Phase 4 is what makes the
localgate integration (see `LOCALGATE_CANIOLLAMA_INTEGRATION_PLAN.md`)
actually worth building rather than pointing at a registry with no data
and no stability guarantee.
