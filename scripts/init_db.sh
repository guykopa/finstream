#!/usr/bin/env bash
set -euo pipefail

trap 'echo "[init_db] ERROR on line $LINENO"' EXIT

DB_NAME="${POSTGRES_DB:-finstream}"
DB_USER="${POSTGRES_USER:-finstream}"
DB_PASSWORD="${POSTGRES_PASSWORD:-changeme}"

echo "[init_db] Creating database '$DB_NAME'..."
psql -U postgres -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 \
  || psql -U postgres -c "CREATE DATABASE $DB_NAME;"

echo "[init_db] Creating user '$DB_USER'..."
psql -U postgres -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 \
  || psql -U postgres -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';"

psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

echo "[init_db] Running Alembic migrations..."
.venv/bin/alembic upgrade head

echo "[init_db] Done."
trap - EXIT
