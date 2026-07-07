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
BACKUP_DIR="${BACKUP_DIR:-$ROOT_DIR/backups/postgres}"
KEEP_DAILY="${KEEP_DAILY:-14}"

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
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$BACKUP_DIR/${POSTGRES_DB}_${STAMP}.dump"
LATEST="$BACKUP_DIR/${POSTGRES_DB}_latest.dump"

mkdir -p "$BACKUP_DIR"

cid="$(${COMPOSE[@]} ps -q postgres)"
if [[ -z "$cid" ]]; then
  echo "Postgres service is not running under compose file $COMPOSE_FILE" >&2
  exit 1
fi

status="$("${DOCKER[@]}" inspect -f '{{.State.Status}}' "$cid")"
if [[ "$status" != "running" ]]; then
  echo "Postgres container is not running: $status" >&2
  exit 1
fi

echo "Creating PostgreSQL custom-format backup: $OUT"
"${COMPOSE[@]}" exec -T postgres pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc --no-owner --no-privileges > "$OUT"
chmod 0600 "$OUT"
ln -sfn "$(basename "$OUT")" "$LATEST"

bytes="$(stat -c '%s' "$OUT")"
sha="$(sha256sum "$OUT" | awk '{print $1}')"
printf '%s  %s\n' "$sha" "$OUT" > "$OUT.sha256"
chmod 0600 "$OUT.sha256"

# Retain the newest KEEP_DAILY backups. This is intentionally simple for pilot ops.
find "$BACKUP_DIR" -maxdepth 1 -type f -name "${POSTGRES_DB}_*.dump" -printf '%T@ %p\n' \
  | sort -nr \
  | awk -v keep="$KEEP_DAILY" 'NR>keep {print $2}' \
  | while read -r old; do rm -f "$old" "$old.sha256"; done

echo "Backup complete: $OUT"
echo "Size bytes: $bytes"
echo "SHA256: $sha"
