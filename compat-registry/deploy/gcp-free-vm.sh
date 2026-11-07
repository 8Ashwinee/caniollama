#!/usr/bin/env bash
# Creates an Always-Free e2-micro VM (us-central1) running the registry.
# Usage: PROJECT=my-project REGISTRY_DOMAIN=registry.example.com ./gcp-free-vm.sh
set -euo pipefail
: "${PROJECT:?}" "${REGISTRY_DOMAIN:?}"
ZONE=${ZONE:-us-central1-a}
NAME=${NAME:-caniollama-registry}
RAW=https://raw.githubusercontent.com/AnjalLLL/caniollama/main/compat-registry/deploy

gcloud services enable compute.googleapis.com --project "$PROJECT"

# Startup script runs on every boot; idempotent.
cat > /tmp/caniollama-startup.sh <<STARTUP
#!/bin/bash
set -e
command -v docker >/dev/null || (curl -fsSL https://get.docker.com | sh)
mkdir -p /opt/registry/data && cd /opt/registry
curl -fsSLO $RAW/docker-compose.yml
curl -fsSLO $RAW/Caddyfile
REGISTRY_DOMAIN=$REGISTRY_DOMAIN docker compose pull
REGISTRY_DOMAIN=$REGISTRY_DOMAIN docker compose up -d
STARTUP

gcloud compute firewall-rules describe allow-http-https --project "$PROJECT" >/dev/null 2>&1 || \
  gcloud compute firewall-rules create allow-http-https --project "$PROJECT" \
    --allow tcp:80,tcp:443 --target-tags web

# Free tier: e2-micro, pd-standard <= 30GB, us-central1/us-west1/us-east1 only.
gcloud compute instances create "$NAME" --project "$PROJECT" --zone "$ZONE" \
  --machine-type e2-micro --boot-disk-type pd-standard --boot-disk-size 30GB \
  --image-family debian-12 --image-project debian-cloud \
  --network-tier STANDARD --tags web \
  --metadata-from-file startup-script=/tmp/caniollama-startup.sh

IP=$(gcloud compute instances describe "$NAME" --project "$PROJECT" --zone "$ZONE" \
  --format='value(networkInterfaces[0].accessConfigs[0].natIP)')
echo "VM IP: $IP  -> create DNS A record: $REGISTRY_DOMAIN -> $IP (Cloudflare: DNS only / grey cloud)"
