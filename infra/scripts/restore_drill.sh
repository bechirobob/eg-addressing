#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
RESTORE_DB="${RESTORE_DRILL_DB:-addressing_restore_drill}"
REPORT_FILE="${RESTORE_DRILL_REPORT_FILE:-$ROOT_DIR/artifacts/operator-digests/restore_drill_latest.json}"

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo -n docker info >/dev/null 2>&1; then
    DOCKER=(sudo -n docker)
  else
    echo "Docker daemon is not accessible. Use a fresh docker-group shell or passwordless sudo for docker." >&2
    exit 1
  fi
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

POSTGRES_DB="${POSTGRES_DB:-addressing}"
POSTGRES_USER="${POSTGRES_USER:-addressing}"
LIVE_PROJECT="$("${DOCKER[@]}" inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' eg-addressing-api 2>/dev/null || true)"
COMPOSE_PROJECT="${COMPOSE_PROJECT_OVERRIDE:-${LIVE_PROJECT:-${COMPOSE_PROJECT_NAME:-eg_addressing}}}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

cleanup() {
  "${COMPOSE[@]}" exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$RESTORE_DB" >/dev/null 2>&1 || true
}
trap cleanup EXIT

echo "Creating fresh backup for restore drill..."
"$ROOT_DIR/infra/scripts/backup_database.sh" >/tmp/eg-addressing-restore-drill-backup.log
cat /tmp/eg-addressing-restore-drill-backup.log
BACKUP_FILE="$(readlink -f "$ROOT_DIR/backups/postgres/${POSTGRES_DB}_latest.dump")"
if [[ ! -s "$BACKUP_FILE" ]]; then
  echo "Latest backup is missing or empty: $BACKUP_FILE" >&2
  exit 1
fi

echo "Preparing temporary restore database: $RESTORE_DB"
cleanup
"${COMPOSE[@]}" exec -T postgres createdb -U "$POSTGRES_USER" "$RESTORE_DB"

echo "Restoring backup into temporary database..."
"${COMPOSE[@]}" exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$RESTORE_DB" --no-owner --no-privileges < "$BACKUP_FILE"

echo "Verifying restored data counts..."
COUNTS_FILE="$(mktemp)"
"${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$RESTORE_DB" -v ON_ERROR_STOP=1 -At -F $'\t' <<'SQL' | tee "$COUNTS_FILE"
SELECT 'provinces' AS table_name, count(*) AS rows FROM provinces
UNION ALL SELECT 'territories', count(*) FROM territories
UNION ALL SELECT 'addresses', count(*) FROM addresses
UNION ALL SELECT 'citizen_geotag_submissions', count(*) FROM citizen_geotag_submissions
UNION ALL SELECT 'field_submissions', count(*) FROM field_submissions
UNION ALL SELECT 'audit_logs', count(*) FROM audit_logs
ORDER BY table_name;
SQL

mkdir -p "$(dirname "$REPORT_FILE")"
BACKUP_BYTES="$(wc -c < "$BACKUP_FILE" | tr -d ' ')"
BACKUP_SHA256="$(sha256sum "$BACKUP_FILE" | awk '{print $1}')"
python3 - "$REPORT_FILE" "$BACKUP_FILE" "$BACKUP_BYTES" "$BACKUP_SHA256" "$RESTORE_DB" "$COUNTS_FILE" <<'PY'
import json
import sys
from datetime import datetime, timezone
report_file, backup_file, backup_bytes, backup_sha256, restore_db, counts_file = sys.argv[1:]
counts = []
with open(counts_file, 'r', encoding='utf-8') as handle:
    for line in handle:
        if not line.strip():
            continue
        table_name, rows = line.rstrip('\n').split('\t', 1)
        counts.append({'table_name': table_name, 'rows': int(rows)})
report = {
    'status': 'passed',
    'generated_at': datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace('+00:00', 'Z'),
    'backup_file': backup_file,
    'backup_bytes': int(backup_bytes),
    'backup_sha256': backup_sha256,
    'restore_target': restore_db,
    'temporary_target_removed': True,
    'restored_counts': counts,
    'operator_note': 'Non-destructive restore drill passed against a temporary database; live pilot data was not overwritten.',
}
with open(report_file, 'w', encoding='utf-8') as handle:
    json.dump(report, handle, indent=2, sort_keys=True)
    handle.write('\n')
print(f"Restore drill report written: {report_file}")
PY
rm -f "$COUNTS_FILE"

echo "Restore drill passed. Temporary database will be dropped: $RESTORE_DB"
