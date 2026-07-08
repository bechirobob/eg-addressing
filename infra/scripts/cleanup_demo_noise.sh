#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
APPLY="${APPLY_CLEANUP:-NO}"

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

set -a
# shellcheck disable=SC1090
source "$ENV_FILE"
set +a

POSTGRES_DB="${POSTGRES_DB:-addressing}"
POSTGRES_USER="${POSTGRES_USER:-addressing}"
LIVE_PROJECT="$("${DOCKER[@]}" inspect -f '{{ index .Config.Labels "com.docker.compose.project" }}' eg-addressing-api 2>/dev/null || true)"
COMPOSE_PROJECT="${COMPOSE_PROJECT_OVERRIDE:-${LIVE_PROJECT:-${COMPOSE_PROJECT_NAME:-eg_addressing}}}"
COMPOSE=("${DOCKER[@]}" compose -p "$COMPOSE_PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE_FILE")

SQL_COUNTS="
SELECT 'address_corrections_smoke' AS bucket, count(*) FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review'
UNION ALL SELECT 'field_submissions_smoke', count(*) FROM field_submissions WHERE submitted_by IN ('Smoke automation', 'Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%'
UNION ALL SELECT 'roads_smoke', count(*) FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%'
UNION ALL SELECT 'audit_smoke', count(*) FROM audit_logs WHERE entity_id IN (SELECT id FROM field_submissions WHERE submitted_by IN ('Smoke automation', 'Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%') OR entity_id IN (SELECT id FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review') OR entity_id IN (SELECT id FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%');
"

echo "Demo-noise cleanup target counts before:"
"${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "$SQL_COUNTS"

if [[ "$APPLY" != "YES" ]]; then
  echo "Dry run only. Set APPLY_CLEANUP=YES to delete known smoke-test rows."
  exit 0
fi

echo "Creating safety backup before cleanup..."
"$ROOT_DIR/infra/scripts/backup_database.sh" >/tmp/eg-addressing-cleanup-backup.log
cat /tmp/eg-addressing-cleanup-backup.log

echo "Deleting known smoke-test rows only..."
"${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<'SQL'
BEGIN;
CREATE TEMP TABLE cleanup_smoke_entities(entity_type TEXT, entity_id TEXT) ON COMMIT DROP;
INSERT INTO cleanup_smoke_entities(entity_type, entity_id)
SELECT 'address_correction', id FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review'
UNION ALL SELECT 'field_submission', id FROM field_submissions WHERE submitted_by IN ('Smoke automation', 'Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%'
UNION ALL SELECT 'road', id FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%';

DELETE FROM audit_logs
WHERE (entity_type, entity_id) IN (SELECT entity_type, entity_id FROM cleanup_smoke_entities)
   OR entity_id IN (SELECT entity_id FROM cleanup_smoke_entities);

DELETE FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review';
DELETE FROM field_submissions WHERE submitted_by IN ('Smoke automation', 'Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%';
DELETE FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%';
COMMIT;
SQL

echo "Demo-noise cleanup target counts after:"
"${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -c "$SQL_COUNTS"
