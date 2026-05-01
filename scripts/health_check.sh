#!/usr/bin/env bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
EXIT_CODE=0

trap 'echo "[health_check] ERROR on line $LINENO"' EXIT

check() {
  local name="$1"; local cmd="$2"
  if eval "$cmd" &>/dev/null; then
    echo "[ OK ] $name"
  else
    echo "[FAIL] $name"
    EXIT_CODE=1
  fi
}

check "API /health"  "curl -sf $API_URL/health"
check "API /ready"   "curl -sf $API_URL/ready"
check "API /metrics" "curl -sf $API_URL/metrics"
check "PostgreSQL"   "pg_isready -q"
check "Disk < 90%"   "[ \$(df / | awk 'NR==2{print \$5}' | tr -d '%') -lt 90 ]"

echo ""
[ "$EXIT_CODE" -eq 0 ] && echo "All checks passed." || echo "Some checks FAILED."
trap - EXIT
exit "$EXIT_CODE"
