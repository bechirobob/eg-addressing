#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo -n docker info >/dev/null 2>&1; then
    DOCKER=(sudo -n docker)
  else
    echo "Docker daemon is not accessible. Use a fresh docker-group shell or passwordless sudo for docker." >&2
    exit 1
  fi
fi
BACKUP_FILE="${1:-}"
CONFIRM="${CONFIRM_RESTORE:-}"

if [[ -z "$BACKUP_FILE" ]]; then
  echo "Usage: CONFIRM_RESTORE=YES $0 /absolute/or/relative/path/to/backup.dump" >&2
  exit 2
fi

if [[ "$CONFIRM" != "YES" ]]; then
  echo "Refusing restore without CONFIRM_RESTORE=YES." >&2
  echo "This operation replaces database contents. Read docs/pilot-ready-v1/05-backup-restore-runbook.md first." >&2
  exit 2
fi

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

if [[ ! -f "$BACKUP_FILE" ]]; then
  echo "Backup file not found: $BACKUP_FILE" >&2
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

cid="$(${COMPOSE[@]} ps -q postgres)"
if [[ -z "$cid" ]]; then
  echo "Postgres service is not running under compose file $COMPOSE_FILE" >&2
  exit 1
fi

pre_restore="$ROOT_DIR/backups/postgres/pre_restore_${POSTGRES_DB}_$(date -u +%Y%m%dT%H%M%SZ).dump"
mkdir -p "$(dirname "$pre_restore")"
echo "Creating safety backup before restore: $pre_restore"
"$ROOT_DIR/infra/scripts/backup_database.sh" >/tmp/eg-addressing-pre-restore-backup.log
cp -f "$(readlink -f "$ROOT_DIR/backups/postgres/${POSTGRES_DB}_latest.dump")" "$pre_restore"
chmod 0600 "$pre_restore"

echo "Terminating active database sessions..."
"${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d postgres -v ON_ERROR_STOP=1 <<SQL
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname = '$POSTGRES_DB' AND pid <> pg_backend_pid();
SQL

echo "Dropping and recreating database: $POSTGRES_DB"
"${COMPOSE[@]}" exec -T postgres dropdb -U "$POSTGRES_USER" --if-exists "$POSTGRES_DB"
"${COMPOSE[@]}" exec -T postgres createdb -U "$POSTGRES_USER" "$POSTGRES_DB"

echo "Restoring from: $BACKUP_FILE"
"${COMPOSE[@]}" exec -T postgres pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --clean --if-exists --no-owner --no-privileges < "$BACKUP_FILE"

echo "Restore complete. Run infra/scripts/health_check.sh next."
