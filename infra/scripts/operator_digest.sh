#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
OUTPUT_DIR="${OUTPUT_DIR:-$ROOT_DIR/artifacts/operator-digests}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUTPUT_FILE="${OUTPUT_FILE:-$OUTPUT_DIR/operator_digest_current.md}"
SNAPSHOT_FILE="$OUTPUT_DIR/operator_digest_$STAMP.md"

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
mkdir -p "$OUTPUT_DIR"

run_sql() {
  "${COMPOSE[@]}" exec -T postgres psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -At -F '|' -v ON_ERROR_STOP=1 -c "$1"
}

geotag_counts="$(run_sql "SELECT status, count(*) FROM citizen_geotag_submissions GROUP BY status ORDER BY status")"
correction_counts="$(run_sql "SELECT status, count(*) FROM address_corrections GROUP BY status ORDER BY status")"
field_counts="$(run_sql "SELECT review_status, count(*) FROM field_submissions GROUP BY review_status ORDER BY review_status")"
signage_ready="$(run_sql "SELECT count(*) FROM citizen_geotag_submissions WHERE status='signage-ready'")"
field_required="$(run_sql "SELECT count(*) FROM citizen_geotag_submissions WHERE status='needs-field-check' OR field_status IN ('visited','needs-recapture','blocked')")"
pending_road_suggestions="$(run_sql "SELECT count(*) FROM citizen_geotag_submissions WHERE road_suggestion_status='pending-review'")"
public_corrections_open="$(run_sql "SELECT count(*) FROM address_corrections WHERE status IN ('submitted','under-review')")"

{
  echo "# EG Addressing Operator Digest"
  echo
  echo "Generated: $STAMP UTC"
  echo "Environment: ${APP_ENV:-unknown}"
  echo
  echo "## Next best action"
  if [[ "$field_required" != "0" ]]; then
    echo "- Prioritize field verification: $field_required location request(s) need field attention."
  elif [[ "$pending_road_suggestions" != "0" ]]; then
    echo "- Review map-derived road/local-area suggestions: $pending_road_suggestions pending."
  elif [[ "$signage_ready" != "0" ]]; then
    echo "- Prepare signage/export batch: $signage_ready record(s) ready."
  else
    echo "- No urgent queue pressure detected. Continue routine review."
  fi
  echo
  echo "## Citizen geotag queue"
  if [[ -n "$geotag_counts" ]]; then
    while IFS='|' read -r status count; do echo "- $status: $count"; done <<< "$geotag_counts"
  else
    echo "- No citizen geotag records."
  fi
  echo
  echo "## Field workflow"
  if [[ -n "$field_counts" ]]; then
    while IFS='|' read -r status count; do echo "- $status: $count"; done <<< "$field_counts"
  else
    echo "- No field submissions."
  fi
  echo
  echo "## Public corrections"
  if [[ -n "$correction_counts" ]]; then
    while IFS='|' read -r status count; do echo "- $status: $count"; done <<< "$correction_counts"
  else
    echo "- No correction reports."
  fi
  echo
  echo "## Guardrails"
  echo "- Local file only; no chat notification sent."
  echo "- No secrets or private identity fields included."
  echo "- Use this digest for operator triage, not legal publication status."
} | tee "$SNAPSHOT_FILE" > "$OUTPUT_FILE"

printf 'Wrote %s and %s\n' "$OUTPUT_FILE" "$SNAPSHOT_FILE"
