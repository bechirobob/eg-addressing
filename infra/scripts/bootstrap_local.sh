#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
LOAD_FIXTURES="${LOAD_FIXTURES:-0}"
START_APP="${START_APP:-1}"
DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo -n docker info >/dev/null 2>&1; then
    DOCKER=(sudo -n docker)
  else
    echo "Docker daemon is not accessible." >&2
    exit 1
  fi
fi
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
COMPOSE_PROJECT="${COMPOSE_PROJECT_NAME:-eg_addressing}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")
"${COMPOSE[@]}" up -d postgres redis minio
for attempt in {1..30}; do
  if "${COMPOSE[@]}" exec -T postgres pg_isready -U "${POSTGRES_USER:-addressing}" -d postgres >/dev/null 2>&1; then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    echo "PostgreSQL did not become ready." >&2
    exit 1
  fi
  sleep 2
done
TARGET_DB="${POSTGRES_DB:-addressing}"
if [[ ! "$TARGET_DB" =~ ^[A-Za-z0-9_]+$ ]]; then
  echo "Unsafe POSTGRES_DB name: $TARGET_DB" >&2
  exit 1
fi
if ! "${COMPOSE[@]}" exec -T postgres psql -U "${POSTGRES_USER:-addressing}" -d postgres -At -c "SELECT 1 FROM pg_database WHERE datname = '$TARGET_DB'" | grep -qx '1'; then
  "${COMPOSE[@]}" exec -T postgres createdb -U "${POSTGRES_USER:-addressing}" "$TARGET_DB"
fi
# .env DATABASE_URL uses the Docker service hostname `postgres`; lifecycle
# scripts run on the host, so use explicit localhost connection variables.
if [[ "${DATABASE_URL:-}" == *"@postgres:"* ]]; then
  unset DATABASE_URL
fi
export POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
export POSTGRES_PORT="${POSTGRES_PORT:-5434}"
export POSTGRES_DB="${POSTGRES_DB:-addressing}"
export POSTGRES_USER="${POSTGRES_USER:-addressing}"
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/services/api/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_BIN_FALLBACK:-python3}"
fi
for attempt in {1..30}; do
  if "$PYTHON_BIN" - <<'PY' >/dev/null 2>&1
import os, psycopg
conn = psycopg.connect(
    host=os.environ['POSTGRES_HOST'],
    port=os.environ['POSTGRES_PORT'],
    dbname=os.environ['POSTGRES_DB'],
    user=os.environ['POSTGRES_USER'],
    password=os.environ.get('POSTGRES_PASSWORD', ''),
)
conn.close()
PY
  then
    break
  fi
  if [[ "$attempt" == "30" ]]; then
    echo "Host PostgreSQL connection did not become ready." >&2
    exit 1
  fi
  sleep 2
done
"$PYTHON_BIN" "$ROOT_DIR/infra/scripts/migrate.py" apply
"$PYTHON_BIN" "$ROOT_DIR/infra/scripts/load_reference_data.py" load
if [[ "$LOAD_FIXTURES" == "1" ]]; then
  : "${DEVELOPMENT_FIXTURE_PASSWORD:?DEVELOPMENT_FIXTURE_PASSWORD is required when LOAD_FIXTURES=1}"
  : "${APP_ENV:=development}"
  : "${EG_ALLOW_DEV_FIXTURES:=YES}"
  export APP_ENV EG_ALLOW_DEV_FIXTURES DEVELOPMENT_FIXTURE_PASSWORD
  "$PYTHON_BIN" "$ROOT_DIR/infra/scripts/load_development_fixtures.py" load
fi
"$PYTHON_BIN" "$ROOT_DIR/infra/scripts/migrate.py" status
"$PYTHON_BIN" "$ROOT_DIR/infra/scripts/load_reference_data.py" status
if [[ "$START_APP" == "1" ]]; then
  "${COMPOSE[@]}" up -d --build api admin
  for attempt in {1..30}; do
    if curl -fsS "http://127.0.0.1:${API_PORT:-8100}/api/v1/health" >/dev/null; then
      break
    fi
    if [[ "$attempt" == "30" ]]; then
      echo "API health check did not pass." >&2
      exit 1
    fi
    sleep 2
  done
fi
printf 'bootstrap_local: ok\n'
