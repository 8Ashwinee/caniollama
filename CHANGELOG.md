# Changelog

All notable changes to this project are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
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

[Unreleased]: https://github.com/AnjalLLL/caniollama/compare/v0.1.3...HEAD
[0.1.3]: https://github.com/AnjalLLL/caniollama/compare/v0.1.0...v0.1.3
[0.1.0]: https://github.com/AnjalLLL/caniollama/releases/tag/v0.1.0
