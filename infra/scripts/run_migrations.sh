#!/usr/bin/env bash
# Legacy compatibility wrapper for the controlled NLI migration runner.
# validate_migration_name() is implemented in infra/scripts/migrate.py via
# VALID_NAME before any SQL is executed: ^[0-9]{3}_[A-Za-z0-9_]+\.sql$.
# Invalid migration filename errors are raised by that runner.
set -Eeuo pipefail
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMMAND="${1:-apply}"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
if [[ -z "${DATABASE_URL:-}" && -z "${POSTGRES_HOST:-}" ]]; then
  echo "DATABASE_URL or POSTGRES_HOST is required for controlled migration commands." >&2
  echo "Set it in the environment or env file before running migrations." >&2
  exit 2
fi
PYTHON_BIN="${PYTHON_BIN:-$ROOT_DIR/services/api/.venv/bin/python}"
if [[ ! -x "$PYTHON_BIN" ]]; then
  PYTHON_BIN="${PYTHON_BIN_FALLBACK:-python3}"
fi
case "$COMMAND" in
  apply|status|transition-pilot)
    exec "$PYTHON_BIN" "$ROOT_DIR/infra/scripts/migrate.py" "$COMMAND"
    ;;
  *)
    echo "Usage: $0 [apply|status|transition-pilot]" >&2
    exit 2
    ;;
esac
