## What and why

<!-- What does this change, and why? Link the issue: Fixes #123 -->

## Checklist

- [ ] `uv run ruff check . && uv run mypy src && uv run pytest` pass in each changed package
- [ ] Tests added or updated for behavior changes
- [ ] `SUITE_VERSION` bumped if `suite/cases.py` changed
- [ ] `CHANGELOG.md` updated under **Unreleased** for user-facing changes
- [ ] Docs updated if behavior or commands changed
