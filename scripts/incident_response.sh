#!/usr/bin/env bash
set -euo pipefail

LOG_DIR="${LOG_DIR:-/var/log/finstream}"
INCIDENT_ID="incident_$(date +%Y%m%d_%H%M%S)"

trap 'echo "[incident] ERROR on line $LINENO"' EXIT

echo "[incident] Starting incident response — $INCIDENT_ID"
mkdir -p "$LOG_DIR"

echo "[incident] 1/4 Collecting system state..."
{
  echo "=== date ==="; date
  echo "=== uptime ==="; uptime
  echo "=== memory ==="; free -h
  echo "=== disk ==="; df -h
  echo "=== processes ==="; ps aux | grep -E "uvicorn|postgres" || true
} > "$LOG_DIR/${INCIDENT_ID}_system.txt"

echo "[incident] 2/4 Collecting API logs..."
journalctl -u finstream-api --since "1 hour ago" --no-pager \
  > "$LOG_DIR/${INCIDENT_ID}_api.log" 2>/dev/null || true

echo "[incident] 3/4 Attempting service restart..."
systemctl restart finstream-api && echo "Service restarted." || echo "Restart failed."

echo "[incident] 4/4 Verifying recovery..."
sleep 3
curl -sf "${API_URL:-http://localhost:8000}/health" \
  && echo "API recovered." || echo "API still down — manual intervention needed."

echo "[incident] Incident log saved to $LOG_DIR/${INCIDENT_ID}_*.txt"
trap - EXIT
