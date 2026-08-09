# 🚀 Quick Release Guide

## Prerequisites (One-Time)

1. **Configure PyPI Trusted Publisher:**
   - Go to: https://pypi.org/manage/account/publishing/
   - Add new publisher:
     - Project: `caniollama`
     - Owner: `AnjalLLL`
     - Repository: `caniollama`
     - Workflow: `release.yml`
     - Environment: `pypi`

## Release v0.1.0

```bash
# Create and push tag
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

## Monitor

- **Actions:** https://github.com/AnjalLLL/caniollama/actions
- **PyPI:** https://pypi.org/project/caniollama/
- **GHCR:** https://github.com/AnjalLLL/caniollama/pkgs/container/caniollama-registry

## Test

```bash
# CLI
uvx caniollama --version

# Container
docker pull ghcr.io/anjalll/caniollama-registry:0.1.0
```

## What Gets Published

1. **PyPI Package** - `pip install caniollama`
2. **Docker Image** - `ghcr.io/anjalll/caniollama-registry:latest`

Both happen automatically on tag push!

---

See `RELEASE_SUMMARY.md` for complete details.
