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
SKIP_TESTS="${SKIP_TESTS:-false}"
SKIP_BACKUP="${SKIP_BACKUP:-false}"
MIN_AVAILABLE_MB="${MIN_AVAILABLE_MB:-1024}"
MIN_SWAP_MB="${MIN_SWAP_MB:-1024}"
export NODE_OPTIONS="${NODE_OPTIONS:---max-old-space-size=1536}"
API_TEST_PYTEST="${API_TEST_PYTEST:-$ROOT_DIR/.venv-api-test/bin/pytest}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  echo "Create it from env/.env.example and set real secrets outside git." >&2
  exit 1
fi

LIVE_PROJECT="$("${DOCKER[@]}" inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' eg-addressing-api 2>/dev/null || true)"
COMPOSE_PROJECT="${COMPOSE_PROJECT_OVERRIDE:-${LIVE_PROJECT:-${COMPOSE_PROJECT_NAME:-eg_addressing}}}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

run_tests() {
  echo "Running backend tests..."
  if [[ ! -x "$API_TEST_PYTEST" ]]; then
    echo "Missing pytest runner: $API_TEST_PYTEST" >&2
    exit 1
  fi
  (cd "$ROOT_DIR/services/api" && "$API_TEST_PYTEST" -q)

  echo "Running frontend typecheck/tests/build..."
  (cd "$ROOT_DIR/apps/admin-portal" && npx tsc --noEmit --pretty false)
  (cd "$ROOT_DIR/apps/admin-portal" && npm test)
  (cd "$ROOT_DIR/apps/admin-portal" && npm run build)
}

preflight() {
  command -v docker >/dev/null || { echo "docker is required" >&2; exit 1; }
  command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
  "${COMPOSE[@]}" config >/dev/null

  local available_mb swap_total_mb
  available_mb="$(awk '/MemAvailable/ { printf "%d", $2 / 1024 }' /proc/meminfo)"
  swap_total_mb="$(awk '/SwapTotal/ { printf "%d", $2 / 1024 }' /proc/meminfo)"
  if (( available_mb < MIN_AVAILABLE_MB )); then
    echo "Insufficient available memory for a safe build: ${available_mb}MiB available, need at least ${MIN_AVAILABLE_MB}MiB." >&2
    exit 1
  fi
  if (( swap_total_mb < MIN_SWAP_MB )); then
    echo "Swap guard failed: ${swap_total_mb}MiB swap configured, need at least ${MIN_SWAP_MB}MiB." >&2
    exit 1
  fi
  echo "Memory guard passed: ${available_mb}MiB available, ${swap_total_mb}MiB swap, NODE_OPTIONS=$NODE_OPTIONS"
}

main() {
  echo "Deploy root: $ROOT_DIR"
  preflight

  if [[ "$SKIP_TESTS" != "true" ]]; then
    run_tests
  else
    echo "Skipping tests because SKIP_TESTS=true"
  fi

  if [[ "$SKIP_BACKUP" != "true" ]]; then
    echo "Creating pre-deploy database backup..."
    "$ROOT_DIR/infra/scripts/backup_database.sh"
  else
    echo "Skipping backup because SKIP_BACKUP=true"
  fi

  echo "Applying database migrations..."
  "$ROOT_DIR/infra/scripts/run_migrations.sh"

  echo "Building and recreating compose services..."
  "${COMPOSE[@]}" build api admin
  "${COMPOSE[@]}" up -d postgres redis minio api admin

  echo "Running health checks..."
  "$ROOT_DIR/infra/scripts/health_check.sh"

  echo "Deploy complete and health checks passed."
}

main "$@"
