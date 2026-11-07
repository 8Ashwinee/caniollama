# Registry Deployment Guide

## Production setup

[`compat-registry/deploy/`](https://github.com/AnjalLLL/caniollama/tree/main/compat-registry/deploy) holds a Docker Compose file for self-hosting: the registry with the SQLite backend on a persistent `./data` directory, behind Caddy for automatic HTTPS.

```bash
# On any Linux server with Docker:
curl -fsSLO https://raw.githubusercontent.com/AnjalLLL/caniollama/main/compat-registry/deploy/docker-compose.yml
curl -fsSLO https://raw.githubusercontent.com/AnjalLLL/caniollama/main/compat-registry/deploy/Caddyfile
REGISTRY_DOMAIN=registry.example.com docker compose up -d
```

Point an `A` record for the domain at the server first (on Cloudflare, use **DNS only**) so Caddy can get a certificate.

**Free hosting (no card): Vercel + Neon Postgres.** This is what the public registry runs.

1. In Vercel, import the repo as a new project with **Root Directory** `compat-registry`.
2. Project → **Storage** → **Create Database** → **Neon** (free). It sets `DATABASE_URL`, and the registry switches to Postgres automatically.
3. Redeploy, then add your domain under **Settings → Domains**.

Then point clients at it with `CANIOLLAMA_REGISTRY_URL=https://registry.example.com`.


This guide covers deploying the caniollama registry as a public service.

## Prerequisites

- A container hosting service (Railway, Render, Fly.io, or similar)
- GitHub repository access for CI/CD
- Domain name (optional, but recommended)

## Deployment Options

### Option 0: Docker with Pre-built Image (Fastest)

Use the official container from GitHub Container Registry:

```bash
# Pull the latest image
docker pull ghcr.io/anjallll/caniollama-registry:latest

# Run with in-memory storage (testing)
docker run -p 8000:8000 ghcr.io/anjallll/caniollama-registry:latest

# Run with persistent database (production)
docker run -d \
  -p 8000:8000 \
  -e COMPAT_REGISTRY_STORAGE_BACKEND=db \
  -v $(pwd)/data:/app/data \
  --name caniollama-registry \
  ghcr.io/anjallll/caniollama-registry:latest
```

Or use Docker Compose (`docker-compose.yml`):

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

Run: `docker compose up -d`

Access at: http://localhost:8000

**Cost:** Free (run on your own hardware)

### Option 1: Railway (Recommended for Cloud)

Railway offers automatic deployments from GitHub with minimal configuration.

#### Steps:

1. **Create Railway account** at https://railway.app

2. **Create new project from GitHub repo:**
   - Connect your GitHub account
   - Select the `AnjalLLL/caniollama` repository
   - Set root directory to `compat-registry`

3. **Configure environment variables:**
   ```
   COMPAT_REGISTRY_STORAGE_BACKEND=db
   ```
   (Uses SQLite, suitable for production since the registry is read-heavy)

4. **Set build configuration:**
   - Build command: (auto-detected from Dockerfile)
   - Start command: (auto-detected from Dockerfile)
   - Port: 8000

5. **Generate domain:**
   - Railway will provide a `*.up.railway.app` domain
   - Or configure custom domain in settings

6. **Update deploy.yml workflow** (see Configuration section below)

**Cost:** Free tier includes 500 hours/month + $5 credit

### Option 2: Render

1. **Create Render account** at https://render.com

2. **Create new Web Service:**
   - Connect repository: `AnjalLLL/caniollama`
   - Root directory: `compat-registry`
   - Runtime: Docker
   - Instance type: Free (or Starter for custom domain)

3. **Set environment variables:**
   ```
   COMPAT_REGISTRY_STORAGE_BACKEND=db
   ```

4. **Deploy** - Render will build from Dockerfile

**Cost:** Free tier available (sleeps after inactivity)

### Option 3: Fly.io

1. **Install flyctl:** https://fly.io/docs/hands-on/install-flyctl/

2. **Create fly.toml** in `compat-registry/`:
   ```toml
   app = "caniollama-registry"
   
   [build]
     dockerfile = "Dockerfile"
   
   [[services]]
     internal_port = 8000
     protocol = "tcp"
   
     [[services.ports]]
       handlers = ["http"]
       port = 80
   
     [[services.ports]]
       handlers = ["tls", "http"]
       port = 443
   
   [env]
     COMPAT_REGISTRY_STORAGE_BACKEND = "db"
   ```

3. **Deploy:**
   ```bash
   cd compat-registry
   flyctl launch
   flyctl deploy
   ```

**Cost:** Free tier includes 3 shared-cpu VMs with 256MB RAM each

### Option 4: VPS (DigitalOcean, Linode, etc.)

For manual VPS deployment using the pre-built image:

```bash
# On your VPS
# Pull the official image
docker pull ghcr.io/anjallll/caniollama-registry:latest

# Run with docker
docker run -d \
  -p 8000:8000 \
  -e COMPAT_REGISTRY_STORAGE_BACKEND=db \
  -v /opt/caniollama/data:/app/data \
  --restart unless-stopped \
  --name caniollama-registry \
  ghcr.io/anjallll/caniollama-registry:latest

# Set up reverse proxy (nginx/caddy) for HTTPS
```

Or build from source:

```bash
git clone https://github.com/AnjalLLL/caniollama.git
cd caniollama/compat-registry
docker build -t caniollama-registry:local .
docker run -d -p 8000:8000 -e COMPAT_REGISTRY_STORAGE_BACKEND=db \
  -v $(pwd)/data:/app/data --name caniollama-registry caniollama-registry:local
```

**Cost:** Starts at $4-6/month for basic VPS

## Configuration

### Storage Backend

The registry supports two storage backends:

1. **File-based (default):**
   - Stores JSON files in `data/results/`
   - Suitable for development
   - Requires git commits for persistence
   - Not recommended for production API use

2. **Database (recommended for production):**
   ```bash
   export COMPAT_REGISTRY_STORAGE_BACKEND=db
   ```
   - Uses SQLite (`data/submissions.db`)
   - Accepts immediate POST requests
   - No manual file management needed
   - Mount `data/` volume for persistence

### Environment Variables

- `COMPAT_REGISTRY_STORAGE_BACKEND`: `file` or `db` (default: `file`)
- `COMPAT_REGISTRY_DB_PATH`: Database file path (default: `data/submissions.db`)
- `PORT`: Port to listen on (default: 8000)

## GitHub Actions CI/CD

### Automated Deployment

Update `.github/workflows/deploy.yml` for your chosen platform:

#### For Railway:

```yaml
- name: Deploy to Railway
  run: |
    npm install -g @railway/cli
    railway up --service compat-registry
  env:
    RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

Generate token: Railway dashboard → Project settings → Tokens

#### For Fly.io:

```yaml
- name: Deploy to Fly.io
  uses: superfly/flyctl-actions/setup-flyctl@master
- run: flyctl deploy --remote-only
  working-directory: compat-registry
  env:
    FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

Generate token: `flyctl auth token`

#### For Render:

Render deploys automatically from GitHub pushes - no workflow changes needed if you enable auto-deploy in Render dashboard.

### Required GitHub Secrets

Add secrets at: Repository → Settings → Secrets and variables → Actions

- Railway: `RAILWAY_TOKEN`
- Fly.io: `FLY_API_TOKEN`
- VPS: `SSH_PRIVATE_KEY`, `VPS_HOST`, `VPS_USER`

## Post-Deployment

### 1. Test the deployment

```bash
# Check health
curl https://your-domain.com/health

# List models (should return empty array initially)
curl https://your-domain.com/models

# Get stats
curl https://your-domain.com/stats
```

### 2. Update registry URL in compat-check

Edit `compat-check/src/compat_check/config.py`:

```python
DEFAULT_REGISTRY_URL = "https://your-domain.com"
```

Commit and release new version.

### 3. Seed initial data (optional)

Run compatibility checks locally and submit to populate the registry:

```bash
# Install CLI
uvx caniollama check qwen2.5-coder:7b --submit
uvx caniollama check llama3:8b --submit
# ... repeat for common models
```

Or import existing results if you have JSON files in `data/results/`.

### 4. Monitor

- **Logs:** Check your platform's logging dashboard
- **Health endpoint:** Set up uptime monitoring (UptimeRobot, Better Uptime)
- **Rate limiting:** Monitor `/stats` to track usage

## Scaling Considerations

The registry is designed to be **read-heavy**:
- Most traffic will be `GET /models` and `GET /models/{name}`
- `POST /submissions` is opt-in and relatively rare

### Performance Tips:

1. **Enable HTTP caching:**
   - Add `Cache-Control` headers for GET endpoints
   - Consider CDN (Cloudflare, Fastly) for global distribution

2. **Database optimization:**
   - SQLite is sufficient for thousands of models
   - Upgrade to PostgreSQL only if you see performance issues

3. **Horizontal scaling:**
   - The app is stateless (besides DB)
   - Can run multiple instances behind a load balancer
   - SQLite limits concurrent writes, so upgrade to PostgreSQL if write traffic increases

## Security

- **No authentication needed** - all endpoints are public read
- **Rate limiting** is configured (10 req/min per IP)
- **Input validation** via Pydantic
- **No sensitive data** - all submissions are metadata only

## Troubleshooting

### "Module not found" errors

Ensure Dockerfile includes `COPY src/ ./src/` before `uv sync`

### Database locked errors

SQLite has write concurrency limits. Switch to `db` backend and ensure only one writer, or upgrade to PostgreSQL.

### High memory usage

Check for accumulated log files. The app itself is lightweight (<50MB RAM).

### Domain not resolving

- Verify DNS propagation (can take up to 48 hours)
- Check platform's custom domain configuration

## Support

- Open issues: https://github.com/AnjalLLL/caniollama/issues
- Deployment problems: Tag with `deployment` label
