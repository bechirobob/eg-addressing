#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
APPLY="${APPLY_RETIREMENT:-NO}"
REPORT_DIR="$ROOT_DIR/artifacts/audits"
REPORT_MD="$REPORT_DIR/latest-fixture-retirement.md"
REPORT_JSON="$REPORT_DIR/latest-fixture-retirement.json"

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
mkdir -p "$REPORT_DIR"

COUNTS_SQL="
WITH controlled_records AS (
  SELECT id, address_code, source_submission_id, status, publication_state, is_archived
  FROM address_records
  WHERE address_label ILIKE 'Controlled canonical proof fixture%'
     OR address_label ILIKE 'Controlled canonical pilot address%'
     OR address_label ILIKE 'Controlled published simulation fixture%'
     OR record_bundle::text ILIKE '%controlled-fixture%'
     OR record_bundle::text ILIKE '%controlled-published-simulation%'
), controlled_submissions AS (
  SELECT id, grid_code, status
  FROM citizen_geotag_submissions
  WHERE address_label ILIKE 'Controlled canonical proof fixture%'
     OR address_label ILIKE 'Controlled canonical pilot address%'
     OR address_label ILIKE 'Controlled published simulation fixture%'
     OR landmark ILIKE '%Controlled proof fixture%'
     OR landmark ILIKE '%Controlled published simulation%'
     OR reviewer_note ILIKE '%Controlled canonical proof%'
     OR reviewer_note ILIKE '%controlled published simulation%'
     OR id IN (SELECT source_submission_id FROM controlled_records)
), smoke_noise AS (
  SELECT 'field_submission' AS type, id FROM field_submissions WHERE submitted_by IN ('Smoke automation', 'Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%'
  UNION ALL SELECT 'road', id FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%'
  UNION ALL SELECT 'address_correction', id FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review'
)
SELECT jsonb_pretty(jsonb_build_object(
  'controlled_address_records', (SELECT count(*) FROM controlled_records),
  'controlled_address_records_active', (SELECT count(*) FROM controlled_records WHERE is_archived = FALSE),
  'controlled_submissions', (SELECT count(*) FROM controlled_submissions),
  'controlled_submissions_active', (SELECT count(*) FROM controlled_submissions WHERE status <> 'retired-fixture'),
  'disposable_smoke_noise', (SELECT count(*) FROM smoke_noise),
  'active_address_codes', COALESCE((SELECT jsonb_agg(address_code ORDER BY address_code) FROM controlled_records WHERE is_archived = FALSE), '[]'::jsonb),
  'active_submission_ids', COALESCE((SELECT jsonb_agg(id ORDER BY id) FROM controlled_submissions WHERE status <> 'retired-fixture'), '[]'::jsonb)
));
"

before_json="$("${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -tAc "$COUNTS_SQL")"

backup_log='not-run-dry-run'
if [[ "$APPLY" == "YES" ]]; then
  backup_log="$($ROOT_DIR/infra/scripts/backup_database.sh | tr '\n' ' ')"
  "${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 <<'SQL'
BEGIN;
WITH controlled_records AS (
  SELECT id, address_code, source_submission_id
  FROM address_records
  WHERE address_label ILIKE 'Controlled canonical proof fixture%'
     OR address_label ILIKE 'Controlled canonical pilot address%'
     OR address_label ILIKE 'Controlled published simulation fixture%'
     OR record_bundle::text ILIKE '%controlled-fixture%'
     OR record_bundle::text ILIKE '%controlled-published-simulation%'
), controlled_submissions AS (
  SELECT id
  FROM citizen_geotag_submissions
  WHERE address_label ILIKE 'Controlled canonical proof fixture%'
     OR address_label ILIKE 'Controlled canonical pilot address%'
     OR address_label ILIKE 'Controlled published simulation fixture%'
     OR landmark ILIKE '%Controlled proof fixture%'
     OR landmark ILIKE '%Controlled published simulation%'
     OR reviewer_note ILIKE '%Controlled canonical proof%'
     OR reviewer_note ILIKE '%controlled published simulation%'
     OR id IN (SELECT source_submission_id FROM controlled_records)
)
UPDATE address_records
SET is_archived = TRUE,
    publication_state = CASE WHEN publication_state = 'published' THEN 'retired-fixture' ELSE publication_state END,
    record_bundle = jsonb_set(
      jsonb_set(record_bundle, '{retirement,status}', '"retired-fixture"'::jsonb, true),
      '{retirement,reason}', '"controlled-proof-fixture"'::jsonb, true
    ),
    updated_at = NOW()
WHERE id IN (SELECT id FROM controlled_records);

WITH controlled_records AS (
  SELECT id, source_submission_id
  FROM address_records
  WHERE address_label ILIKE 'Controlled canonical proof fixture%'
     OR address_label ILIKE 'Controlled canonical pilot address%'
     OR address_label ILIKE 'Controlled published simulation fixture%'
     OR record_bundle::text ILIKE '%controlled-fixture%'
     OR record_bundle::text ILIKE '%controlled-published-simulation%'
     OR record_bundle #>> '{retirement,reason}' = 'controlled-proof-fixture'
), controlled_submissions AS (
  SELECT id
  FROM citizen_geotag_submissions
  WHERE address_label ILIKE 'Controlled canonical proof fixture%'
     OR address_label ILIKE 'Controlled canonical pilot address%'
     OR address_label ILIKE 'Controlled published simulation fixture%'
     OR landmark ILIKE '%Controlled proof fixture%'
     OR landmark ILIKE '%Controlled published simulation%'
     OR reviewer_note ILIKE '%Controlled canonical proof%'
     OR reviewer_note ILIKE '%controlled published simulation%'
     OR id IN (SELECT source_submission_id FROM controlled_records)
)
UPDATE citizen_geotag_submissions
SET status = 'retired-fixture',
    reviewer_note = trim(both ' ' from concat(COALESCE(NULLIF(reviewer_note, ''), ''), ' Retired controlled proof fixture; not official publication.')),
    updated_at = NOW()
WHERE id IN (SELECT id FROM controlled_submissions);
COMMIT;
SQL
fi

after_json="$("${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v ON_ERROR_STOP=1 -tAc "$COUNTS_SQL")"

python3 - "$REPORT_JSON" "$REPORT_MD" "$APPLY" "$before_json" "$after_json" "$backup_log" <<'PY'
import datetime as dt
import json
import sys

json_path, md_path, apply_mode, before_raw, after_raw, backup_log = sys.argv[1:]
before = json.loads(before_raw)
after = json.loads(after_raw)
report = {
    'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'mode': 'apply' if apply_mode == 'YES' else 'dry-run',
    'policy': 'Archive canonical controlled fixtures; mark matching intake submissions retired-fixture; do not delete identity-bearing rows.',
    'backup_log': backup_log,
    'before': before,
    'after': after,
}
with open(json_path, 'w', encoding='utf-8') as fh:
    json.dump(report, fh, indent=2, sort_keys=True)
lines = [
    '# Fixture retirement policy report',
    '',
    f"- Mode: `{report['mode']}`",
    f"- Generated UTC: `{report['generated_at_utc']}`",
    f"- Policy: {report['policy']}",
    f"- Backup: `{backup_log}`",
    '',
    '## Counts',
    '',
    '| Bucket | Before | After |',
    '|---|---:|---:|',
]
for key in ['controlled_address_records', 'controlled_address_records_active', 'controlled_submissions', 'controlled_submissions_active', 'disposable_smoke_noise']:
    lines.append(f"| {key} | {before.get(key)} | {after.get(key)} |")
lines.extend([
    '',
    '## Active controlled identifiers after',
    '',
    f"- Address codes: `{after.get('active_address_codes')}`",
    f"- Submission IDs: `{after.get('active_submission_ids')}`",
    '',
    '## Safety boundary',
    '',
    '- Canonical address records are archived, not deleted.',
    '- Citizen intake rows are marked `retired-fixture`, not deleted.',
    '- Smoke-row deletion remains handled separately by `cleanup_demo_noise.sh`.',
])
with open(md_path, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(lines) + '\n')
print(json.dumps({'mode': report['mode'], 'before': before, 'after': after}, sort_keys=True))
PY
