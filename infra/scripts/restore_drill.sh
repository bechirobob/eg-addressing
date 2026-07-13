#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/postgres}"
RESTORE_DB="${RESTORE_DB:-addressing_restore_drill_$(date -u +%Y%m%d%H%M%S)}"
REPORT_DIR="${REPORT_DIR:-$ROOT_DIR/artifacts/restore-drills}"
REPORT_FILE="$REPORT_DIR/restore_drill_$(date -u +%Y%m%dT%H%M%SZ).json"
LATEST_REPORT_FILE="${LATEST_REPORT_FILE:-$ROOT_DIR/artifacts/operator-digests/restore_drill_latest.json}"

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo -n docker info >/dev/null 2>&1; then
    DOCKER=(sudo -n docker)
  else
    echo "Docker daemon is not accessible." >&2
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

mkdir -p "$REPORT_DIR" "$(dirname "$LATEST_REPORT_FILE")"

cleanup() {
  set +e
  "${COMPOSE[@]}" exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$RESTORE_DB" >/dev/null 2>&1
}
trap cleanup EXIT

"$ROOT_DIR/infra/scripts/backup_database.sh" >/tmp/eg_restore_backup.log
BACKUP_PATH="$(awk '/Backup complete:/ {print $3}' /tmp/eg_restore_backup.log | tail -n 1)"
if [[ -z "$BACKUP_PATH" || ! -s "$BACKUP_PATH" ]]; then
  echo "Backup did not produce a non-empty dump." >&2
  cat /tmp/eg_restore_backup.log >&2
  exit 1
fi
BACKUP_FILE="$(basename "$BACKUP_PATH")"
BACKUP_BYTES="$(stat -c '%s' "$BACKUP_PATH")"
BACKUP_SHA256="$(sha256sum "$BACKUP_PATH" | awk '{print $1}')"

# Refuse unsafe target names and live DB names.
if [[ "$RESTORE_DB" == "$POSTGRES_DB" || ! "$RESTORE_DB" =~ ^[a-zA-Z0-9_]+$ ]]; then
  echo "Unsafe restore target name: $RESTORE_DB" >&2
  exit 1
fi

"${COMPOSE[@]}" exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$RESTORE_DB" >/dev/null
"${COMPOSE[@]}" exec -T postgres createdb -U "$POSTGRES_USER" "$RESTORE_DB"
"${COMPOSE[@]}" exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$RESTORE_DB" --no-owner --no-privileges < "$BACKUP_PATH"

COUNTS_JSON="$(${COMPOSE[@]} exec -T postgres psql -U "$POSTGRES_USER" -d "$RESTORE_DB" -At -F $'\t' <<'SQL'
WITH counts AS (
  SELECT 'users' AS table_name, COUNT(*)::int AS row_count FROM users
  UNION ALL SELECT 'territories', COUNT(*)::int FROM territories
  UNION ALL SELECT 'roads', COUNT(*)::int FROM roads
  UNION ALL SELECT 'buildings', COUNT(*)::int FROM buildings
  UNION ALL SELECT 'address_records', COUNT(*)::int FROM address_records
  UNION ALL SELECT 'field_submissions', COUNT(*)::int FROM field_submissions
  UNION ALL SELECT 'audit_logs', COUNT(*)::int FROM audit_logs
)
SELECT jsonb_object_agg(table_name, row_count)::text FROM counts;
SQL
)"

LEDGER_JSON="$(${COMPOSE[@]} exec -T postgres psql -U "$POSTGRES_USER" -d "$RESTORE_DB" -At <<'SQL'
SELECT jsonb_build_object(
  'migration_rows', (SELECT COUNT(*)::int FROM schema_migrations),
  'latest_version', (SELECT MAX(version) FROM schema_migrations),
  'checksum_rows', (SELECT COUNT(*)::int FROM schema_migrations WHERE checksum IS NOT NULL AND checksum <> ''),
  'postgis_extensions', (SELECT COUNT(*)::int FROM pg_extension WHERE extname = 'postgis')
)::text;
SQL
)"

python3 - <<PY
import json, sys
ledger = json.loads('''$LEDGER_JSON''')
if ledger['migration_rows'] < 8 or ledger['latest_version'] != '007' or ledger['checksum_rows'] != ledger['migration_rows'] or ledger['postgis_extensions'] != 1:
    print(json.dumps({'status': 'failed', 'reason': 'invalid migration ledger after restore', 'ledger': ledger}, indent=2), file=sys.stderr)
    raise SystemExit(1)
PY

LIVE_COUNTS_JSON="$(${COMPOSE[@]} exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -F $'\t' <<'SQL'
WITH counts AS (
  SELECT 'users' AS table_name, COUNT(*)::int AS row_count FROM users
  UNION ALL SELECT 'territories', COUNT(*)::int FROM territories
  UNION ALL SELECT 'roads', COUNT(*)::int FROM roads
  UNION ALL SELECT 'buildings', COUNT(*)::int FROM buildings
  UNION ALL SELECT 'address_records', COUNT(*)::int FROM address_records
  UNION ALL SELECT 'field_submissions', COUNT(*)::int FROM field_submissions
  UNION ALL SELECT 'audit_logs', COUNT(*)::int FROM audit_logs
)
SELECT jsonb_object_agg(table_name, row_count)::text FROM counts;
SQL
)"

# Drop now and verify removal before reporting success.
"${COMPOSE[@]}" exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$RESTORE_DB" >/dev/null
trap - EXIT

REMOVED_STATUS="$(${COMPOSE[@]} exec -T postgres psql -U "$POSTGRES_USER" -d postgres -At -c "SELECT COUNT(*) FROM pg_database WHERE datname = '$RESTORE_DB';")"
if [[ "$REMOVED_STATUS" != "0" ]]; then
  echo "Restore target still exists after cleanup: $RESTORE_DB" >&2
  exit 1
fi

python3 - <<PY
import json
from pathlib import Path
report = {
  'status': 'passed',
  'compose_project': '$COMPOSE_PROJECT',
  'source_database': '$POSTGRES_DB',
  'restore_target': '$RESTORE_DB',
  'backup_file': '$BACKUP_FILE',
  'backup_bytes': int('$BACKUP_BYTES'),
  'backup_sha256': '$BACKUP_SHA256',
  'restored_counts': json.loads('''$COUNTS_JSON'''),
  'migration_ledger': json.loads('''$LEDGER_JSON'''),
  'live_counts_at_drill': json.loads('''$LIVE_COUNTS_JSON'''),
  'restore_target_removed': True,
}
Path('$REPORT_FILE').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
Path('$LATEST_REPORT_FILE').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps(report, indent=2, sort_keys=True))
PY
