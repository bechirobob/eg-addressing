#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
MIGRATIONS_DIR="${MIGRATIONS_DIR:-$ROOT_DIR/infra/migrations}"
APPLY_MIGRATIONS="${APPLY_MIGRATIONS:-YES}"

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
if [[ ! -d "$MIGRATIONS_DIR" ]]; then
  echo "Missing migrations dir: $MIGRATIONS_DIR" >&2
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

psql_exec() {
  "${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 "$@"
}

ensure_table() {
  psql_exec <<'SQL'
CREATE TABLE IF NOT EXISTS schema_migrations (
  version TEXT PRIMARY KEY,
  filename TEXT NOT NULL,
  checksum TEXT NOT NULL,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
SQL
}

migration_checksum() {
  sha256sum "$1" | awk '{print $1}'
}

already_applied() {
  local version="$1"
  psql_exec -At -c "SELECT checksum FROM schema_migrations WHERE version = '$version'" | tr -d '[:space:]'
}

apply_one() {
  local file="$1"
  local name version checksum existing
  name="$(basename "$file")"
  version="${name%%_*}"
  checksum="$(migration_checksum "$file")"
  existing="$(already_applied "$version")"
  if [[ -n "$existing" ]]; then
    if [[ "$existing" != "$checksum" ]]; then
      echo "Checksum mismatch for already-applied migration $name" >&2
      echo "Expected current file checksum $checksum but database has $existing" >&2
      exit 1
    fi
    echo "SKIP $name already applied"
    return
  fi
  if [[ "$APPLY_MIGRATIONS" != "YES" ]]; then
    echo "PENDING $name checksum=$checksum"
    return
  fi
  echo "APPLY $name"
  psql_exec -f - < "$file"
  psql_exec -c "INSERT INTO schema_migrations(version, filename, checksum) VALUES ('$version', '$name', '$checksum')"
}

main() {
  ensure_table
  shopt -s nullglob
  local files=("$MIGRATIONS_DIR"/*.sql)
  if [[ ${#files[@]} -eq 0 ]]; then
    echo "No migration files found."
    exit 0
  fi
  for file in "${files[@]}"; do
    apply_one "$file"
  done
  echo "Schema migration status:"
  psql_exec -c "SELECT version, filename, applied_at FROM schema_migrations ORDER BY version"
}

main "$@"
