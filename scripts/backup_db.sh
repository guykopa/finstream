#!/usr/bin/env bash
set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-/var/backups/finstream}"
DB_NAME="${POSTGRES_DB:-finstream}"
KEEP_DAYS=7
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
FILE="$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

trap 'echo "[backup] ERROR on line $LINENO"' EXIT

mkdir -p "$BACKUP_DIR"

echo "[backup] Dumping $DB_NAME → $FILE"
pg_dump "$DB_NAME" | gzip > "$FILE"

echo "[backup] Rotating backups older than $KEEP_DAYS days..."
find "$BACKUP_DIR" -name "*.sql.gz" -mtime +"$KEEP_DAYS" -delete

echo "[backup] Done. Backup size: $(du -sh "$FILE" | cut -f1)"
trap - EXIT
