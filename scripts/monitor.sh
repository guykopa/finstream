#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"

trap 'echo "[monitor] ERROR on line $LINENO"' EXIT

echo "=== System Resources ==="
echo "CPU:    $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')%"
echo "Memory: $(free -h | awk '/^Mem/{print $3"/"$2}')"
echo "Disk:   $(df -h / | awk 'NR==2{print $5" used ("$3"/"$2")"}')"

echo ""
echo "=== Process Status ==="
pgrep -fa uvicorn && echo "API: running" || echo "API: NOT running"

echo ""
echo "=== API Response Time ==="
curl -s -o /dev/null -w "HTTP %{http_code} in %{time_total}s\n" "$API_URL/health" \
  || echo "API unreachable"

trap - EXIT
