#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
API_BASE_URL="${API_BASE_URL:-}"
ADMIN_BASE_URL="${ADMIN_BASE_URL:-}"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo -n docker info >/dev/null 2>&1; then
    DOCKER=(sudo -n docker)
  else
    echo "Docker daemon is not accessible. Use a fresh docker-group shell or passwordless sudo for docker." >&2
    exit 1
  fi
fi

API_BASE_URL="${API_BASE_URL:-http://localhost:${API_PORT:-8100}}"
ADMIN_BASE_URL="${ADMIN_BASE_URL:-http://localhost:${ADMIN_PORT:-3100}}"
LIVE_PROJECT="$("${DOCKER[@]}" inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' eg-addressing-api 2>/dev/null || true)"
COMPOSE_PROJECT="${COMPOSE_PROJECT_OVERRIDE:-${LIVE_PROJECT:-${COMPOSE_PROJECT_NAME:-eg_addressing}}}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

check_http() {
  local name="$1"
  local url="$2"
  local expected="${3:-200}"
  local attempts="${HEALTH_HTTP_ATTEMPTS:-12}"
  local delay="${HEALTH_HTTP_DELAY_SECONDS:-5}"
  local code=""
  local attempt

  for attempt in $(seq 1 "$attempts"); do
    code="$(curl -fsS -o /tmp/eg-addressing-health-body.txt -w '%{http_code}' "$url" || true)"
    if [[ "$code" == "$expected" ]]; then
      echo "OK   $name $url -> $code"
      return 0
    fi
    if [[ "$attempt" != "$attempts" ]]; then
      echo "WAIT $name $url expected=$expected got=${code:-curl-error} attempt=$attempt/$attempts"
      sleep "$delay"
    fi
  done

  echo "FAIL $name $url expected=$expected got=${code:-curl-error}" >&2
  if [[ -s /tmp/eg-addressing-health-body.txt ]]; then
    sed -n '1,20p' /tmp/eg-addressing-health-body.txt >&2
  fi
  return 1
}

check_compose_service() {
  local service="$1"
  local cid state health
  cid="$(${COMPOSE[@]} ps -q "$service" 2>/dev/null || true)"
  if [[ -z "$cid" ]]; then
    echo "FAIL compose service missing: $service" >&2
    return 1
  fi
  state="$("${DOCKER[@]}" inspect -f '{{.State.Status}}' "$cid")"
  health="$("${DOCKER[@]}" inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid")"
  if [[ "$state" != "running" ]]; then
    echo "FAIL $service state=$state health=$health" >&2
    return 1
  fi
  if [[ "$health" != "healthy" && "$health" != "none" ]]; then
    echo "FAIL $service state=$state health=$health" >&2
    return 1
  fi
  echo "OK   compose $service state=$state health=$health"
}

main() {
  echo "Health check root: $ROOT_DIR"
  check_http "api health" "$API_BASE_URL/api/v1/health"
  check_http "admin home" "$ADMIN_BASE_URL/"
  check_compose_service postgres
  check_compose_service api
  check_compose_service admin
  echo "Health check passed."
}

main "$@"
