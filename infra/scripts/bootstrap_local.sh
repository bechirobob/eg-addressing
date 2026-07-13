#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
LOAD_FIXTURES="${LOAD_FIXTURES:-0}"
START_APP="${START_APP:-1}"
HOST_API="${HOST_API:-0}"
RUN_SMOKE_CHECKS="${RUN_SMOKE_CHECKS:-0}"
BOOTSTRAP_REPORT_FILE="${BOOTSTRAP_REPORT_FILE:-$ROOT_DIR/artifacts/operator-digests/bootstrap_local_latest.json}"
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
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/services/api/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_BIN_FALLBACK:-python3}"
fi
LIVE_PROJECT="$(${DOCKER[@]} inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' eg-addressing-postgres 2>/dev/null || true)"
COMPOSE_PROJECT="${COMPOSE_PROJECT_NAME:-${LIVE_PROJECT:-eg_addressing}}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")
REUSE_EXISTING_CORE=0
if docker ps --format '{{.Names}}' | grep -qx 'eg-addressing-postgres' \
  && docker ps --format '{{.Names}}' | grep -qx 'eg-addressing-redis' \
  && docker ps --format '{{.Names}}' | grep -qx 'eg-addressing-minio'; then
  echo 'bootstrap_local: reusing running postgres/redis/minio containers'
  REUSE_EXISTING_CORE=1
else
  "${COMPOSE[@]}" up -d postgres redis minio
fi
pg_exec() {
  if [[ "$REUSE_EXISTING_CORE" == "1" ]]; then
    docker exec -i eg-addressing-postgres "$@"
  else
    "${COMPOSE[@]}" exec -T postgres "$@"
  fi
}
for attempt in {1..30}; do
  if pg_exec pg_isready -U "${POSTGRES_USER:-addressing}" -d postgres >/dev/null 2>&1; then
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
if ! pg_exec psql -U "${POSTGRES_USER:-addressing}" -d postgres -At -c "SELECT 1 FROM pg_database WHERE datname = '$TARGET_DB'" | grep -qx '1'; then
  pg_exec createdb -U "${POSTGRES_USER:-addressing}" "$TARGET_DB"
fi
if [[ "${DATABASE_URL:-}" == *"@postgres:"* ]]; then
  unset DATABASE_URL
fi
export POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
export POSTGRES_PORT="${POSTGRES_PORT:-5434}"
export POSTGRES_DB="${POSTGRES_DB:-addressing}"
export POSTGRES_USER="${POSTGRES_USER:-addressing}"
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
  if [[ "$HOST_API" == "1" ]]; then
    "$PYTHON_BIN" -m uvicorn app.main:app --app-dir "$ROOT_DIR/services/api" --host 127.0.0.1 --port "${API_PORT:-8100}" >/tmp/eg_bootstrap_host_api.log 2>&1 &
    HOST_API_PID=$!
    trap 'kill $HOST_API_PID 2>/dev/null || true' EXIT
  elif docker ps --format '{{.Names}}' | grep -qx 'eg-addressing-api' && docker ps --format '{{.Names}}' | grep -qx 'eg-addressing-admin'; then
    echo 'bootstrap_local: reusing running api/admin containers'
  else
    "${COMPOSE[@]}" up -d --build api admin
  fi
  for attempt in {1..30}; do
    if curl -fsS "http://127.0.0.1:${API_PORT:-8100}/api/v1/health" >/dev/null; then
      break
    fi
    if [[ "$attempt" == "30" ]]; then
      [[ -f /tmp/eg_bootstrap_host_api.log ]] && cat /tmp/eg_bootstrap_host_api.log >&2
      echo "API health check did not pass." >&2
      exit 1
    fi
    sleep 2
  done
fi
if [[ "$RUN_SMOKE_CHECKS" == "1" ]]; then
  : "${DEVELOPMENT_FIXTURE_PASSWORD:?DEVELOPMENT_FIXTURE_PASSWORD is required when RUN_SMOKE_CHECKS=1}"
  SMOKE_API_BASE_URL="${SMOKE_API_BASE_URL:-http://127.0.0.1:${API_PORT:-8100}}" \
  SMOKE_ADMIN_USERNAME="${SMOKE_ADMIN_USERNAME:-admin}" \
  SMOKE_ADMIN_PASSWORD="$DEVELOPMENT_FIXTURE_PASSWORD" \
    node "$ROOT_DIR/apps/admin-portal/scripts/admin-flow-smoke.mjs" >/tmp/eg_bootstrap_smoke.json
fi
mkdir -p "$(dirname "$BOOTSTRAP_REPORT_FILE")"
"$PYTHON_BIN" - <<PY
import json, subprocess
from pathlib import Path
report = {
    'status': 'passed',
    'git_head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd='$ROOT_DIR', text=True).strip(),
    'migrations': 'current',
    'reference_data': 'checked',
    'fixtures_loaded': '$LOAD_FIXTURES' == '1',
    'app_started': '$START_APP' == '1',
    'app_runtime': 'host' if '$HOST_API' == '1' else 'compose',
    'smoke_checks': 'passed' if '$RUN_SMOKE_CHECKS' == '1' else 'not-run',
}
Path('$BOOTSTRAP_REPORT_FILE').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
print(json.dumps(report, indent=2, sort_keys=True))
PY
printf 'bootstrap_local: ok\n'
