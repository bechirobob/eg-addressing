#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
RUN_LIVE_HEALTH="${RUN_LIVE_HEALTH:-YES}"
CLEAN_SMOKE_ROWS="${CLEAN_SMOKE_ROWS:-YES}"

section() {
  printf '\n== %s ==\n' "$1"
}

section "Repository hygiene"
cd "$ROOT_DIR"
git status --short

section "Backend tests"
cd "$ROOT_DIR/services/api"
if [[ ! -x .venv/bin/python ]]; then
  echo "Missing services/api/.venv; create it from services/api/requirements.txt before running the audit." >&2
  exit 1
fi
. .venv/bin/activate
pytest -q

section "Frontend API types"
cd "$ROOT_DIR/apps/admin-portal"
npm run generate:api-types

section "Frontend typecheck"
cd "$ROOT_DIR/apps/admin-portal"
npx tsc --noEmit --pretty false

section "Frontend production build"
npm run build

section "Frontend guards"
if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a
fi
export SMOKE_ADMIN_USERNAME="${SMOKE_ADMIN_USERNAME:-${OPERATOR_USERNAME:-admin}}"
if [[ -z "${SMOKE_ADMIN_PASSWORD:-}" ]]; then
  echo "SMOKE_ADMIN_PASSWORD must be set in $ENV_FILE for strict admin smoke tests." >&2
  exit 1
fi
npm run test:copy
npm run test:role-auth
npm run test:registry-actions
npm run test:verification-queue
npm run test:official-geometry
npm run test:spanish-leaks
npm run test:a11y-controls
npm run test:api-types
npm run test:data-command
npm run test:smoke

if [[ "$CLEAN_SMOKE_ROWS" == "YES" ]]; then
  section "Smoke/demo row cleanup"
  cd "$ROOT_DIR"
  APPLY_CLEANUP=YES infra/scripts/cleanup_demo_noise.sh
fi

if [[ "$RUN_LIVE_HEALTH" == "YES" ]]; then
  section "Served stack health"
  cd "$ROOT_DIR"
  infra/scripts/health_check.sh
fi

section "Audit complete"
echo "Government-grade audit gates passed."
