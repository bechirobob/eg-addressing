#!/usr/bin/env bash
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
LOAD_FIXTURES="${LOAD_FIXTURES:-0}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
if [[ -z "${DATABASE_URL:-}" && -z "${POSTGRES_HOST:-}" ]]; then
  export POSTGRES_HOST="${POSTGRES_HOST:-127.0.0.1}"
  export POSTGRES_PORT="${POSTGRES_PORT:-5434}"
fi
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/services/api/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_BIN_FALLBACK:-python3}"
fi
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
