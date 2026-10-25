#!/usr/bin/env bash
# StarPulse deployment script
# Usage: bash deploy.sh [--profile <profile>] [--skip-build] [--skip-notebooks] [--skip-app]

set -e

PROFILE="stars"
WORKSPACE_PATH="/Workspace/stars-app"
APP_NAME="stars-pulse"
SKIP_BUILD=false
SKIP_NOTEBOOKS=false
SKIP_APP=false

for arg in "$@"; do
  case $arg in
    --profile) PROFILE="$2"; shift ;;
    --skip-build) SKIP_BUILD=true ;;
    --skip-notebooks) SKIP_NOTEBOOKS=true ;;
    --skip-app) SKIP_APP=true ;;
  esac
  shift 2>/dev/null || true
done

echo "==> Profile:    $PROFILE"
echo "==> Workspace:  $WORKSPACE_PATH"
echo ""

# ── Step 1: Build frontend ────────────────────────────────────────────────────
if [ "$SKIP_BUILD" = false ]; then
  echo "[1/4] Building React frontend..."
  cd frontend
  npm run build
  cd ..
  echo "      Done — dist/ ready."
else
  echo "[1/4] Skipping frontend build."
fi

# ── Step 2: Upload backend ────────────────────────────────────────────────────
echo "[2/4] Uploading backend..."
MSYS_NO_PATHCONV=1 databricks workspace import-dir backend \
  "$WORKSPACE_PATH/backend" --overwrite --profile "$PROFILE"

# ── Step 3: Upload compiled frontend assets (dist only, no node_modules) ─────
echo "[3/4] Uploading frontend/dist..."
MSYS_NO_PATHCONV=1 databricks workspace import-dir frontend/dist \
  "$WORKSPACE_PATH/frontend/dist" --overwrite --profile "$PROFILE"

# ── Step 4: Upload root app files ─────────────────────────────────────────────
echo "[4/4] Uploading app.yaml and requirements.txt..."
MSYS_NO_PATHCONV=1 databricks workspace import \
  "$WORKSPACE_PATH/app.yaml" \
  --file app.yaml --format RAW --overwrite --profile "$PROFILE"

MSYS_NO_PATHCONV=1 databricks workspace import \
  "$WORKSPACE_PATH/requirements.txt" \
  --file requirements.txt --format RAW --overwrite --profile "$PROFILE"

# ── Step 5 (optional): Upload notebooks ──────────────────────────────────────
if [ "$SKIP_NOTEBOOKS" = false ]; then
  echo "[5/5] Uploading notebooks..."
  MSYS_NO_PATHCONV=1 databricks workspace import-dir notebooks \
    "$WORKSPACE_PATH/notebooks" --overwrite --profile "$PROFILE"
  echo "      Done — 13 notebooks deployed."
fi

# ── Step 6 (optional): Re-deploy Databricks App ───────────────────────────────
if [ "$SKIP_APP" = false ]; then
  echo "[6/6] Deploying Databricks App '$APP_NAME'..."
  MSYS_NO_PATHCONV=1 databricks apps deploy "$APP_NAME" \
    --source-code-path "$WORKSPACE_PATH" --profile "$PROFILE"
  echo "      App deployed."
fi

echo ""
echo "Deployment complete."
echo "App URL: $(MSYS_NO_PATHCONV=1 databricks apps get $APP_NAME --profile $PROFILE -o json 2>/dev/null | python3 -c 'import json,sys; print(json.load(sys.stdin).get(\"url\",\"\"))' 2>/dev/null)"
