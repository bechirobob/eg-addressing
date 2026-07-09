#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
OPERATOR_USERNAME="${OPERATOR_USERNAME:-admin}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  exit 1
fi

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

OPERATOR_USERNAME="${OPERATOR_USERNAME:-admin}"
OPERATOR_PASSWORD="${OPERATOR_PASSWORD:-${SMOKE_ADMIN_PASSWORD:-}}"
if [[ -z "$OPERATOR_PASSWORD" ]]; then
  echo "Set OPERATOR_PASSWORD or SMOKE_ADMIN_PASSWORD in the environment; password is never printed." >&2
  exit 1
fi

DOCKER=(docker)
if ! docker info >/dev/null 2>&1; then
  if sudo -n docker info >/dev/null 2>&1; then
    DOCKER=(sudo -n docker)
  else
    echo "Docker daemon is not accessible." >&2
    exit 1
  fi
fi

LIVE_PROJECT="$("${DOCKER[@]}" inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' eg-addressing-api 2>/dev/null || true)"
COMPOSE_PROJECT="${COMPOSE_PROJECT_OVERRIDE:-${LIVE_PROJECT:-${COMPOSE_PROJECT_NAME:-eg_addressing}}}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

"${COMPOSE[@]}" exec -T \
  -e OPERATOR_USERNAME="$OPERATOR_USERNAME" \
  -e OPERATOR_PASSWORD="$OPERATOR_PASSWORD" \
  api python - <<'PY'
import os
from app.db import db_connection, _hash_password

username = os.environ['OPERATOR_USERNAME']
password = os.environ['OPERATOR_PASSWORD']
if len(password) < 14:
    raise SystemExit('Operator password must be at least 14 characters')

with db_connection() as connection:
    with connection.cursor() as cursor:
        cursor.execute(
            '''
            UPDATE users
            SET password_hash = %s, is_active = TRUE
            WHERE username = %s
            RETURNING id, username, role, is_active
            ''',
            (_hash_password(password), username),
        )
        row = cursor.fetchone()
        if not row:
            raise SystemExit(f'No user found for username: {username}')
    connection.commit()

print(f"updated operator credential for {row['username']} role={row['role']} active={row['is_active']}")
PY
