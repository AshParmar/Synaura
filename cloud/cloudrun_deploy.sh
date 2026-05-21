#!/usr/bin/env bash
# cloud/cloudrun_deploy.sh
# Manual deploy script — use when you need to push without Cloud Build.
# Run from the project root: bash cloud/cloudrun_deploy.sh

set -euo pipefail

# ── Configuration — edit these ─────────────────────────────────────────────────
PROJECT_ID="${GCP_PROJECT_ID:-synaura7}"
REGION="us-central1"
SERVICE_NAME="synaura-backend"
REPO="synaura-repo"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE_NAME}"

echo "[setup] Creating Artifact Registry repo if needed..."
gcloud artifacts repositories create "${REPO}" \
  --repository-format=docker \
  --location="${REGION}" \
  --project="${PROJECT_ID}" 2>/dev/null || true

gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet

echo "[build] Building Docker image..."
docker build -f docker/Dockerfile -t "${IMAGE}:latest" .

echo "📤 Pushing to GCR…"
docker push "${IMAGE}:latest"

echo "🚀 Deploying to Cloud Run (${REGION})…"
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}:latest" \
  --region="${REGION}" \
  --platform=managed \
  --allow-unauthenticated \
  --port=8000 \
  --memory=2Gi \
  --cpu=2 \
  --max-instances=10 \
  --project="${PROJECT_ID}"

echo "✅ Deployment complete."
gcloud run services describe "${SERVICE_NAME}" \
  --region="${REGION}" \
  --format="value(status.url)"
