# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.4] - 2026-11-07
### Changed
- Default registry URL is now `https://registry.caniollama.ghimireanjal.com.np` (the old `registry.caniollama.dev` never resolved, so `--submit` always failed).
### Fixed
- `caniollama --version` and the registry's `/health` reported `0.1.0`; the version now comes from package metadata.
### Added
- Postgres storage backend, used automatically when `DATABASE_URL` is set.
- Vercel deployment (`compat-registry/api/index.py`, `vercel.json`) for the public registry, backed by Neon Postgres.
- `compat-registry/deploy/`: Docker Compose + Caddy (automatic HTTPS) for self-hosting.
- Root CI (lint, type check, tests with coverage), CodeQL, Dependabot, docs site.
- Build provenance attestations for PyPI and container releases.

## [0.1.3] - 2026-08-09
### Fixed
- Clean release; Dockerfile no longer depends on `uv.lock`.

## [0.1.0] - 2026-08-09
### Added
- Initial CLI: `caniollama check [model]`
- Fixed test suite v1.0.0: single tool, 5-tool selection, no-tool control, multi-turn tool result
- Opt-in, metadata-only submission to the registry

[Unreleased]: https://github.com/AnjalLLL/caniollama/compare/v0.1.4...HEAD
[0.1.4]: https://github.com/AnjalLLL/caniollama/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/AnjalLLL/caniollama/compare/v0.1.0...v0.1.3
[0.1.0]: https://github.com/AnjalLLL/caniollama/releases/tag/v0.1.0
