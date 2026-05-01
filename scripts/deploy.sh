#!/usr/bin/env bash
set -euo pipefail

APP_DIR="/opt/finstream"
SERVICE="finstream-api"

trap 'echo "[deploy] ERROR on line $LINENO — rolling back"; systemctl restart "$SERVICE" || true' EXIT

echo "[deploy] Pulling latest code..."
git -C "$APP_DIR" pull --ff-only

echo "[deploy] Installing dependencies..."
"$APP_DIR/.venv/bin/pip" install -q -r "$APP_DIR/requirements.txt"

echo "[deploy] Running migrations..."
"$APP_DIR/.venv/bin/alembic" -c "$APP_DIR/migrations/alembic.ini" upgrade head

echo "[deploy] Restarting service..."
systemctl restart "$SERVICE"
sleep 2
systemctl is-active "$SERVICE"

echo "[deploy] Deploy complete."
trap - EXIT
