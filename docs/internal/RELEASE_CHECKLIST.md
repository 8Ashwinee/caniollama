# Release Checklist for v0.1.0

This checklist tracks what's needed to release caniollama to PyPI.

## ✅ Completed

### Core Package
- [x] CLI implementation (`compat-check`)
- [x] Test suite (12 tests passing)
- [x] Registry backend (`compat-registry`)
- [x] Registry test suite (12 tests passing)
- [x] Schema compatibility verified (end-to-end test)
- [x] Package builds successfully (`uv build`)
- [x] PyPI project created with trusted publishing
- [x] Release workflow configured (`.github/workflows/release.yml`)
- [x] Repository URLs updated in `pyproject.toml`

### Quality Checks
- [x] CI check for SUITE_VERSION discipline
- [x] Cross-platform support documented
- [x] API integration guide created
- [x] Deployment guide created

## 🟡 Before First Release

### 1. Deploy the Registry

**Status:** Documented but not yet deployed

Choose a deployment option from `compat-registry/DEPLOYMENT.md`:
- Railway (recommended for simplicity)
- Render (free tier with auto-sleep)
- Fly.io (free tier, more control)
- VPS (most control, requires more setup)

**Action items:**
1. Choose platform
2. Deploy following DEPLOYMENT.md guide
3. Test endpoints:
   ```bash
   curl https://YOUR-DOMAIN/health
   curl https://YOUR-DOMAIN/models
   curl https://YOUR-DOMAIN/stats
   ```
4. Update registry URL in project

### 2. Update Registry URL in CLI

**Status:** Pending deployment

Once registry is deployed, update the default URL:

File: `compat-check/src/compat_check/config.py`

```python
DEFAULT_REGISTRY_URL = "https://YOUR-DEPLOYED-DOMAIN"
```

### 3. Update Documentation with Live URLs

**Files to update:**
- `README.md` - Add registry URL
- `docs/api-integration.md` - Replace `TBD` with actual URL
- `compat-check/README.md` - Update registry URL
- `compat-registry/README.md` - Add live instance URL

### 4. Seed Initial Data (Optional but Recommended)

**Why:** An empty registry makes the tool less useful initially

**Action:**
```bash
# After registry is deployed and URL is updated:
cd compat-check
uv run caniollama check qwen2.5-coder:7b --submit
uv run caniollama check llama3:8b --submit
uv run caniollama check mistral:7b --submit
uv run caniollama check codellama:7b --submit
uv run caniollama check deepseek-coder:6.7b --submit
```

This gives early users immediate value instead of "no data available."

## 🚀 Release Process

### Step 1: Pre-release Verification

```bash
# Ensure you're on main branch
git checkout main
git pull origin main

# Run all tests
cd compat-check && uv run pytest -v
cd ../compat-registry && uv run pytest -v
cd ../tests && uv run pytest test_e2e_schema_compat.py -v

# Build package locally
cd ../compat-check && uv build

# Test local installation
uvx --from ./dist/caniollama-0.1.0-py3-none-any.whl caniollama --version
```

### Step 2: Tag and Push

```bash
# From repository root
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"
git push origin v0.1.0
```

This triggers `.github/workflows/release.yml` which:
1. Builds the package
2. Publishes to PyPI via trusted publishing

### Step 3: Verify PyPI Release

1. Wait for GitHub Action to complete (~2-3 minutes)
2. Check https://pypi.org/project/caniollama/
3. Test installation:
   ```bash
   # Clean environment test
   uvx caniollama --version
   pipx run caniollama --version
   ```

### Step 4: Post-Release

1. **Create GitHub Release:**
   - Go to https://github.com/AnjalLLL/caniollama/releases/new
   - Select tag `v0.1.0`
   - Title: `v0.1.0 - Initial Release`
   - Description: See template below

2. **Announce:**
   - Update README.md with installation badges
   - Share on relevant communities (r/LocalLLaMA, Ollama Discord, etc.)

3. **Monitor:**
   - Watch GitHub issues for bug reports
   - Monitor registry `/stats` endpoint for usage
   - Check PyPI download statistics

## 📝 GitHub Release Description Template

```markdown
# caniollama v0.1.0 - Initial Release

The first public release of caniollama, a standardized compatibility checker for local Ollama model tool-calling support.

## What is caniollama?

A CLI tool and public registry that tests whether Ollama models properly support tool/function calling. Useful for:
- Selecting models for agents and tools
- Understanding tool-calling capabilities before deployment
- Contributing compatibility data to the community

## Installation

```bash
# Using uvx (recommended)
uvx caniollama check

# Using pipx
pipx run caniollama check

# Or install permanently
pip install caniollama
```

## Quick Start

```bash
# Check all locally pulled models
caniollama check

# Check a specific model
caniollama check qwen2.5-coder:7b

# Submit results to public registry (opt-in)
caniollama check --submit
```

## Features

- ✅ Standardized test suite for tool-calling compatibility
- ✅ Clear categorization: native support, fallback, or rejected
- ✅ Public registry of community-submitted results
- ✅ Privacy-first: never submits prompts or model outputs
- ✅ Cross-platform: macOS, Linux, Windows (WSL)

## Registry API

Query compatibility data programmatically:

```python
import httpx
response = httpx.get("https://registry.caniollama.dev/models/qwen2.5-coder:7b")
print(f"Pass rate: {response.json()['pass_rate']:.0%}")
```

See [API Integration Guide](docs/api-integration.md) for details.

## Documentation

- [CLI Usage](compat-check/README.md)
- [API Integration](docs/api-integration.md)
- [Privacy Policy](docs/privacy.md)
- [Contributing](CONTRIBUTING.md)

## Known Limitations

- Requires Ollama running locally (or accessible via `OLLAMA_HOST`)
- Test suite v1 covers basic tool-calling patterns only
- Registry is read-only via API (submissions via CLI only)

## What's Next

See [GitHub Projects](https://github.com/AnjalLLL/caniollama/projects) for roadmap.

## Contributing

Community contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

**Full Changelog**: https://github.com/AnjalLLL/caniollama/commits/v0.1.0
```

## 🔄 Post-v0.1.0 Improvements

Track these as separate issues/milestones:

- [ ] Add more test cases to suite (bump to suite v2)
- [ ] Web dashboard for browsing registry
- [ ] GitHub Action for automated testing
- [ ] Model recommendation API based on use case
- [ ] Integration with localgate and other tools
- [ ] Community model leaderboard
- [ ] Batch submission mode for CI
- [ ] PostgreSQL backend option for registry

## 📊 Success Metrics

Track after release:
- PyPI downloads per week
- GitHub stars
- Registry API requests
- Number of unique models in registry
- Community contributions (PRs, issues)

## ⚠️ Rollback Plan

If critical issues are discovered post-release:

1. **Yank the release from PyPI:**
   ```bash
   # You'll need PyPI API token
   pip install twine
   twine upload --skip-existing --repository pypi dist/*
   ```
   Then use PyPI web UI to yank the version

2. **Revert the tag:**
   ```bash
   git tag -d v0.1.0
   git push origin :refs/tags/v0.1.0
   ```

3. **Fix and re-release as v0.1.1**

## Support

Questions? Open an issue: https://github.com/AnjalLLL/caniollama/issues
