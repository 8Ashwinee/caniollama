# 🚀 Release Setup Complete!

Everything is ready for v0.1.0 release. Here's what was done and what's next.

## ✅ What Was Completed

### 1. Dual Publishing Workflows
- **PyPI Release** (`.github/workflows/release.yml`)
  - Publishes `caniollama` CLI to PyPI
  - Triggered on version tags (e.g., `v0.1.0`)
  - Uses trusted publishing (OIDC) - no API keys needed

- **GHCR Container Release** (`.github/workflows/release-container.yml`)
  - Publishes Docker image to GitHub Container Registry
  - Image: `ghcr.io/anjalll/caniollama-registry`
  - Multiple tags: `latest`, `0.1.0`, `0.1`, `0`
  - Triggered on same version tags

### 2. Comprehensive Documentation
- **Installation Guide** (`docs/installation.md`)
  - CLI installation (pip, pipx, uv, uvx)
  - Registry deployment (Docker, Docker Compose, cloud platforms)
  - Troubleshooting and upgrading

- **Updated README** with:
  - Clear installation section
  - Docker deployment instructions
  - Links to all documentation

- **Enhanced Deployment Guide** (`compat-registry/DEPLOYMENT.md`)
  - Pre-built Docker image usage (Option 0)
  - Cloud platform options
  - VPS deployment with GHCR

### 3. Repository Cleanup
- Updated `.gitignore` with `.ruff_cache/` and `.mypy_cache/`
- Added release planning documents
- Organized documentation structure

### 4. Pushed to GitHub
- All changes committed and pushed to `main`
- Ready for tagging

## 🎯 Next Steps to Release

### One-Time Setup (First Release Only)

#### Configure PyPI Trusted Publisher

1. Go to: https://pypi.org/manage/account/publishing/
2. Click "Add a new pending publisher"
3. Fill in:
   - **PyPI Project Name:** `caniollama`
   - **Owner:** `AnjalLLL`
   - **Repository name:** `caniollama`
   - **Workflow name:** `release.yml`
   - **Environment name:** `pypi`
4. Save

This allows GitHub Actions to publish without storing API tokens.

### Release v0.1.0

Once PyPI is configured:

```bash
# Create and push the tag
git tag -a v0.1.0 -m "Release v0.1.0 - Initial public release"
git push origin v0.1.0
```

This automatically triggers BOTH workflows:
1. PyPI release (~2-3 minutes)
2. Docker container release (~3-5 minutes)

### Monitor the Release

Watch both workflows:
- GitHub Actions: https://github.com/AnjalLLL/caniollama/actions

After completion:
- PyPI package: https://pypi.org/project/caniollama/
- Container image: https://github.com/AnjalLLL/caniollama/pkgs/container/caniollama-registry

### Test the Release

**CLI:**
```bash
uvx caniollama --version
pipx run caniollama check
```

**Container:**
```bash
docker pull ghcr.io/anjalll/caniollama-registry:0.1.0
docker run -p 8000:8000 ghcr.io/anjalll/caniollama-registry:0.1.0
curl http://localhost:8000/
```

### Create GitHub Release

1. Go to: https://github.com/AnjalLLL/caniollama/releases/new
2. Select tag: `v0.1.0`
3. Title: "v0.1.0 - Initial Release"
4. Description (suggested):

```markdown
## 🎉 First Release

`caniollama` is now available! Test your Ollama models for tool-calling compatibility.

### Installation

**CLI:**
```bash
pip install caniollama
# or
uvx caniollama check
```

**Registry (Docker):**
```bash
docker pull ghcr.io/anjalll/caniollama-registry:latest
```

### What's Included

- ✅ CLI tool for testing model compatibility
- ✅ Standardized test suite (4 test cases)
- ✅ Registry backend for storing/querying results
- ✅ Docker container for easy deployment
- ✅ Comprehensive documentation

### Links

- 📦 PyPI: https://pypi.org/project/caniollama/
- 🐳 Docker: https://github.com/AnjalLLL/caniollama/pkgs/container/caniollama-registry
- 📖 Docs: https://github.com/AnjalLLL/caniollama#documentation

### Requirements

- Python 3.10+
- Ollama running locally

See [Installation Guide](docs/installation.md) for details.
```

5. Publish release

## 📊 What Users Can Do Now

### Install the CLI

```bash
# Quick try (no install)
uvx caniollama check

# Permanent install
pip install caniollama
```

### Deploy the Registry

```bash
# Pull from GHCR
docker pull ghcr.io/anjalll/caniollama-registry:latest

# Run with persistent storage
docker run -d -p 8000:8000 \
  -e COMPAT_REGISTRY_STORAGE_BACKEND=db \
  -v /opt/caniollama/data:/app/data \
  --restart unless-stopped \
  ghcr.io/anjalll/caniollama-registry:latest
```

### Use Docker Compose

```yaml
version: '3.8'
services:
  registry:
    image: ghcr.io/anjalll/caniollama-registry:latest
    ports:
      - "8000:8000"
    environment:
      - COMPAT_REGISTRY_STORAGE_BACKEND=db
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

## 🎁 Bonus: What's Already Working

- ✅ All tests passing (27 total)
- ✅ CI/CD configured
- ✅ Cross-platform support (macOS, Linux, Windows/WSL)
- ✅ Privacy-preserving submission (metadata only)
- ✅ Rate limiting
- ✅ API documentation (FastAPI /docs)
- ✅ Comprehensive README and guides

## 📝 Optional: After Release

### Deploy a Public Registry Instance

If you want to host the official public registry at `registry.caniollama.dev`:

1. Deploy container to Railway/Render/Fly.io (see `compat-registry/DEPLOYMENT.md`)
2. Get the public URL
3. Update `compat-check/src/compat_check/config.py`:
   ```python
   registry_base_url: str = os.environ.get(
       "CANIOLLAMA_REGISTRY_URL", "https://registry.caniollama.dev"
   )
   ```
4. Release v0.1.1 with updated URL

### Seed Initial Data

```bash
cd compat-check
uv run caniollama check qwen2.5-coder:7b --submit
uv run caniollama check llama3:8b --submit
uv run caniollama check mistral:7b --submit
```

### Share the Release

- Reddit: r/LocalLLaMA, r/ollama, r/Python
- Hacker News
- Twitter/X
- Ollama Discord
- Dev.to or Medium article

## 🐛 Troubleshooting

### If PyPI release fails:

1. Check GitHub Actions logs
2. Verify PyPI trusted publishing is configured
3. Ensure tag matches pattern `v*.*.*`

### If Container release fails:

1. Check Dockerfile builds locally:
   ```bash
   cd compat-registry
   docker build -t test .
   ```
2. Verify GHCR permissions (should be automatic for repo owner)

### If users can't install:

1. Check PyPI shows the package
2. Test: `pip install --index-url https://pypi.org/simple/ caniollama`
3. Verify package includes all required files

## 📚 Documentation Quick Links

- [Installation Guide](docs/installation.md) - How to install CLI and deploy registry
- [CLI Usage](compat-check/README.md) - Command-line tool documentation
- [API Integration](docs/api-integration.md) - For tool builders
- [Deployment Guide](compat-registry/DEPLOYMENT.md) - Cloud deployment options
- [Contributing](CONTRIBUTING.md) - How to contribute
- [Privacy Policy](docs/privacy.md) - What data is collected

## 🎉 You're Ready!

Just configure PyPI trusted publishing and push the tag. Everything else is automatic.

```bash
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Then watch the magic happen at: https://github.com/AnjalLLL/caniollama/actions
