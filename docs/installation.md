# Installation Guide

## CLI Tool (`caniollama`)

### Quick Install (No Setup Required)

The fastest way to use `caniollama` without any installation:

```bash
# Using uvx (recommended)
uvx caniollama check

# Or using pipx
pipx run caniollama check
```

These commands download and run the latest version automatically.

### Permanent Installation

If you plan to use `caniollama` regularly:

```bash
# Using pip
pip install caniollama

# Using pipx (isolated environment, recommended)
pipx install caniollama

# Using uv
uv tool install caniollama
```

### Verify Installation

```bash
caniollama --version
caniollama --help
```

### Prerequisites

- **Ollama** must be installed and running
  - Download from: https://ollama.ai
  - Verify: `ollama --version`
  - At least one model pulled: `ollama pull qwen2.5-coder:7b`

- **Python 3.10+** (automatically handled by uvx/pipx)

### Environment Variables

Optional configuration:

```bash
# Custom Ollama instance
export OLLAMA_BASE_URL="http://localhost:11434"

# Custom registry (if self-hosting)
export CANIOLLAMA_REGISTRY_URL="https://your-registry.com"

# Timeout settings (seconds)
export CANIOLLAMA_TIMEOUT="30"
export CANIOLLAMA_SUBMIT_TIMEOUT="10"
```

## Registry Backend (Self-Hosted)

### Using Docker (Recommended)

Pull and run the pre-built container:

```bash
# Pull from GitHub Container Registry
docker pull ghcr.io/anjallll/caniollama-registry:latest

# Run with in-memory storage (testing)
docker run -p 8000:8000 ghcr.io/anjallll/caniollama-registry:latest

# Run with persistent SQLite database
docker run -p 8000:8000 \
  -e COMPAT_REGISTRY_STORAGE_BACKEND=db \
  -v $(pwd)/data:/app/data \
  ghcr.io/anjallll/caniollama-registry:latest
```

### Using Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  registry:
    image: ghcr.io/anjallll/caniollama-registry:latest
    ports:
      - "8000:8000"
    environment:
      - COMPAT_REGISTRY_STORAGE_BACKEND=db
      - COMPAT_REGISTRY_RATE_LIMIT_PER_MINUTE=60
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

Run:

```bash
docker compose up -d
```

### Cloud Deployment

See [the deployment guide](registry/deployment.md) for:
- Railway
- Render
- Fly.io
- DigitalOcean
- AWS/GCP/Azure

### From Source

```bash
# Clone repository
git clone https://github.com/AnjalLLL/caniollama.git
cd caniollama/compat-registry

# Install dependencies
uv sync

# Run development server
uv run uvicorn compat_registry.main:app --reload

# Or production server
uv run uvicorn compat_registry.main:app --host 0.0.0.0 --port 8000
```

## Verify Installation

### CLI

```bash
# Check specific model
caniollama check qwen2.5-coder:7b

# Check all local models
caniollama check

# Submit results to public registry
caniollama check --submit
```

### Registry

```bash
# Check health
curl http://localhost:8000/

# View stats
curl http://localhost:8000/stats

# Query model compatibility
curl http://localhost:8000/models/qwen2.5-coder:7b
```

## Troubleshooting

### Ollama Not Found

**Error:** `Could not connect to Ollama`

**Solutions:**
1. Verify Ollama is running: `ollama list`
2. Check Ollama URL: `echo $OLLAMA_BASE_URL`
3. Try: `export OLLAMA_BASE_URL="http://127.0.0.1:11434"`

### Registry Unreachable

**Error:** `Submission failed - registry may be unreachable`

**Solutions:**
1. Run without submission: `caniollama check` (no `--submit` flag)
2. Check registry URL: `echo $CANIOLLAMA_REGISTRY_URL`
3. Verify registry is running: `curl https://registry.caniollama.dev/`

### Permission Errors

**Error:** `Permission denied` when installing

**Solutions:**
1. Use `pipx` instead: `pipx install caniollama`
2. Or virtual environment: `python -m venv venv && source venv/bin/activate && pip install caniollama`
3. Avoid `sudo pip` (not recommended)

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'compat_check'`

**Solutions:**
1. Reinstall: `pip install --force-reinstall caniollama`
2. Check Python version: `python --version` (must be 3.10+)
3. Try fresh environment: `pipx install caniollama`

## Upgrading

### CLI

```bash
# Using pip
pip install --upgrade caniollama

# Using pipx
pipx upgrade caniollama

# Using uv
uv tool upgrade caniollama

# Or with uvx (always latest)
uvx caniollama check  # automatically uses latest
```

### Registry

```bash
# Pull latest container
docker pull ghcr.io/anjallll/caniollama-registry:latest
docker compose restart

# Or specific version
docker pull ghcr.io/anjallll/caniollama-registry:0.1.0
```

## Uninstalling

### CLI

```bash
# pip
pip uninstall caniollama

# pipx
pipx uninstall caniollama

# uv
uv tool uninstall caniollama
```

### Registry

```bash
# Docker
docker compose down
docker rmi ghcr.io/anjallll/caniollama-registry:latest

# Remove data
rm -rf data/
```

## Next Steps

- 📖 [CLI Usage Guide](https://github.com/AnjalLLL/caniollama/blob/main/compat-check/README.md)
- 🔌 [API Integration Guide](api-integration.md)
- 🚀 [Deployment Guide](registry/deployment.md)
- 🔒 [Privacy Policy](privacy.md)
