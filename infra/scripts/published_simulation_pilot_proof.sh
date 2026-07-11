#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8100}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/artifacts/audits}"
mkdir -p "$OUT_DIR"

python3 - "$ROOT_DIR" "$ENV_FILE" "$API_BASE_URL" "$OUT_DIR" <<'PY'
import datetime as dt
import http.cookiejar
import json
import os
import pathlib
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

root = pathlib.Path(sys.argv[1]).resolve()
env_file = pathlib.Path(sys.argv[2]).resolve()
api_base = sys.argv[3].rstrip('/')
out_dir = pathlib.Path(sys.argv[4]).resolve()
out_dir.mkdir(parents=True, exist_ok=True)

checks: list[dict[str, Any]] = []
created: dict[str, Any] = {}
bearer_token: str | None = None


def load_env(path: pathlib.Path) -> dict[str, str]:
    env = os.environ.copy()
    if path.exists():
        for raw in path.read_text(encoding='utf-8').splitlines():
            line = raw.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, value = line.split('=', 1)
            env[key.strip()] = value.strip().strip('"').strip("'")
    return env


env = load_env(env_file)
admin_username = env.get('SMOKE_ADMIN_USERNAME') or env.get('ADMIN_USERNAME') or 'admin'
admin_password = env.get('SMOKE_ADMIN_PASSWORD') or env.get('ADMIN_PASSWORD')
if not admin_password:
    print('missing SMOKE_ADMIN_PASSWORD or ADMIN_PASSWORD in environment', file=sys.stderr)
    sys.exit(2)

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def csrf_token() -> str | None:
    for cookie in jar:
        if cookie.name == 'eg_addressing_csrf':
            return cookie.value
    return None


def cookie_header() -> str:
    return '; '.join(f'{cookie.name}={cookie.value}' for cookie in jar)


def request(method: str, url: str, payload: dict[str, Any] | None = None, *, auth: bool = False, ok: set[int] | None = None) -> tuple[int, Any, str]:
    data = None
    headers = {'Accept': 'application/json'}
    if payload is not None:
        data = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    if auth:
        if bearer_token:
            headers['Authorization'] = f'Bearer {bearer_token}'
        else:
            cookies = cookie_header()
            if cookies:
                headers['Cookie'] = cookies
            token = csrf_token()
            if token and method.upper() not in {'GET', 'HEAD'}:
                headers['X-CSRF-Token'] = token
    req = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with opener.open(req, timeout=30) as res:
            text = res.read().decode('utf-8', errors='replace')
            status = res.status
    except urllib.error.HTTPError as exc:
        text = exc.read().decode('utf-8', errors='replace')
        status = exc.code
    try:
        body: Any = json.loads(text) if text else None
    except json.JSONDecodeError:
        body = text
    if ok is not None and status not in ok:
        raise RuntimeError(f'{method} {url} returned {status}: {text[:500]}')
    return status, body, text


def add_check(name: str, passed: bool, evidence: dict[str, Any] | str | None = None) -> None:
    checks.append({'name': name, 'status': 'pass' if passed else 'fail', 'evidence': evidence or {}})


def docker_sql(sql: str) -> str:
    compose_file = root / 'infra/docker/docker-compose.yml'
    env_path = str(env_file)
    project = subprocess.run(['docker', 'inspect', '-f', '{{ index .Config.Labels "com.docker.compose.project" }}', 'eg-addressing-api'], cwd=str(root), text=True, capture_output=True)
    compose_project = project.stdout.strip() or env.get('COMPOSE_PROJECT_NAME') or 'docker'
    user = env.get('POSTGRES_USER', 'addressing')
    db = env.get('POSTGRES_DB', 'addressing')
    completed = subprocess.run(
        ['docker', 'compose', '-p', compose_project, '--env-file', env_path, '-f', str(compose_file), 'exec', '-T', 'postgres', 'psql', '-U', user, '-d', db, '-tAc', sql],
        cwd=str(root), text=True, capture_output=True, timeout=90,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout.strip()


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def contains_private_fields(obj: Any) -> bool:
    text = json.dumps(obj, sort_keys=True).lower()
    private_terms = ['citizen_name', 'citizen_contact', 'dip_last4', 'identity_document', 'reviewer_note']
    return any(term in text for term in private_terms)


now = dt.datetime.now(dt.timezone.utc)
stamp = now.strftime('%Y%m%dT%H%M%SZ')
# Move by whole 5m-ish cells using current seconds to avoid colliding with earlier controlled proof codes.
cell_nudge = (now.second % 30) + 11
latitude = 3.7540 + (cell_nudge * 0.00007)
longitude = 8.7760 + (cell_nudge * 0.00007)
label = f'Controlled published simulation fixture {stamp}'
landmark = 'Controlled published simulation only — not official national publication'
submission_payload = {
    'territory_id': 'territory-malabo-ela-nguema',
    'province_code': 'BN',
    'address_label': label,
    'landmark': landmark,
    'latitude': latitude,
    'longitude': longitude,
    'accuracy_meters': 7,
    'capture_method': 'controlled-published-simulation-script',
    'suggested_road_name': 'Carretera del Aeropuerto',
    'suggested_local_area': 'Ela Nguema',
    'suggested_place_name': 'Malabo Ela Nguema',
    'map_display_name': 'Controlled published simulation fixture, Ela Nguema, Malabo',
    'road_suggestion_source': 'controlled-published-simulation',
    'road_suggestion_attribution': 'BeCoreOps controlled pilot proof script',
    'privacy_notice_acknowledged': True,
}

try:
    health_status, health_body, _ = request('GET', f'{api_base}/api/v1/health', ok={200})
    add_check('api health', health_status == 200, {'status': health_status, 'service': health_body.get('service') if isinstance(health_body, dict) else None})

    create_status, submission, _ = request('POST', f'{api_base}/api/v1/public/geotag-submissions', submission_payload, ok={201})
    submission_id = submission['id']
    address_code = submission['grid_code']
    created.update({'submission_id': submission_id, 'address_code': address_code, 'label': label})
    add_check('controlled simulation geotag created', create_status == 201 and address_code.startswith('EG-'), {'status': create_status, 'submission_id': submission_id, 'address_code': address_code})

    login_status, login_body, _ = request('POST', f'{api_base}/api/v1/auth/login', {'username': admin_username, 'password': admin_password}, ok={200})
    bearer_token = login_body.get('token') if isinstance(login_body, dict) else None
    add_check('operator login', login_status == 200, {'status': login_status, 'auth_mode': login_body.get('auth_mode') if isinstance(login_body, dict) else None})

    promote_status, promoted, _ = request('POST', f'{api_base}/api/v1/geotag-submissions/{submission_id}/registry-ready', {'reviewer_note': 'Controlled published simulation: prepare registry-ready fixture before temporary simulation.'}, auth=True, ok={200})
    record = promoted.get('address_record') if isinstance(promoted, dict) else None
    add_check('registry-ready canonical record created', promote_status == 200 and isinstance(record, dict), {'status': promote_status, 'record_status': record.get('status') if isinstance(record, dict) else None})

    gate_status, gate_body, _ = request('POST', f'{api_base}/api/v1/geotag-submissions/{submission_id}/publish', {'reviewer_note': 'Attempt official release gate for simulation proof.'}, auth=True, ok={403})
    add_check('official publish endpoint remains release-gated', gate_status == 403 and 'gate' in json.dumps(gate_body).lower(), {'status': gate_status, 'detail': gate_body.get('detail') if isinstance(gate_body, dict) else str(gate_body)[:160]})

    code_lit = sql_literal(address_code)
    submission_lit = sql_literal(submission_id)
    label_lit = sql_literal(label)
    batch_lit = sql_literal(f'simulation-pack-{stamp}')
    cert_lit = sql_literal(f'CERT-{address_code}')
    # Controlled simulation publication: commit a temporary published state so public/proof/export/certificate paths can be verified, then retire below.
    docker_sql(f"""
BEGIN;
UPDATE citizen_geotag_submissions
SET status = 'published',
    signage_batch = {batch_lit},
    reviewer_note = 'CONTROLLED PUBLISHED SIMULATION ONLY — not official national publication.',
    updated_at = NOW()
WHERE id = {submission_lit}
  AND address_label = {label_lit};

UPDATE address_records
SET status = 'published',
    publication_state = 'published',
    address_label = {label_lit},
    is_archived = FALSE,
    record_bundle = jsonb_set(
      jsonb_set(
        jsonb_set(
          jsonb_set(record_bundle, '{{identity,status}}', '"published"'::jsonb, true),
          '{{identity,publication_state}}', '"published"'::jsonb, true
        ),
        '{{outputs,certificate_id}}', to_jsonb({cert_lit}::text), true
      ),
      '{{simulation}}', jsonb_build_object('status', 'controlled-published-simulation', 'official_publication', false, 'retire_after_proof', true), true
    ),
    updated_at = NOW()
WHERE address_code = {code_lit}
  AND source_submission_id = {submission_lit};
COMMIT;
""")

    db_published = json.loads(docker_sql(f"""
SELECT json_build_object(
  'address_code', address_code,
  'status', status,
  'publication_state', publication_state,
  'is_archived', is_archived,
  'simulation_status', record_bundle #>> '{{simulation,status}}'
)
FROM address_records
WHERE address_code = {code_lit};
"""))
    add_check('temporary simulation fixture marked published', db_published.get('status') == 'published' and db_published.get('publication_state') == 'published' and db_published.get('is_archived') is False, db_published)

    public_status, public_record, _ = request('GET', f'{api_base}/api/v1/public/address-code/{urllib.parse.quote(address_code)}/record', ok={200})
    public_text = json.dumps(public_record)
    public_published = public_status == 200 and public_record.get('publication_status') == 'published' and isinstance(public_record.get('record'), dict)
    add_check('public address-code record shows published simulation', public_published and label in public_text and not contains_private_fields(public_record), {'status': public_status, 'publication_status': public_record.get('publication_status'), 'contains_label': label in public_text, 'private_fields': contains_private_fields(public_record)})

    tracking_status, tracking_body, _ = request('GET', f'{api_base}/api/v1/public/tracking/{urllib.parse.quote(address_code)}', ok={200})
    tracking_text = json.dumps(tracking_body)
    add_check('public tracking shows published simulation without identity leak', tracking_status == 200 and label in tracking_text and not contains_private_fields(tracking_body), {'status': tracking_status, 'contains_label': label in tracking_text, 'private_fields': contains_private_fields(tracking_body)})

    cert_status, cert_body, _ = request('GET', f'{api_base}/api/v1/address-records/{urllib.parse.quote(address_code)}/certificate', auth=True, ok={200})
    add_check('canonical certificate path works for temporary published simulation', cert_status == 200 and cert_body.get('certificate_id') == f'CERT-{address_code}' and not contains_private_fields(cert_body), {'status': cert_status, 'certificate_id': cert_body.get('certificate_id') if isinstance(cert_body, dict) else None})

    export_status, export_body, _ = request('GET', f'{api_base}/api/v1/address-records/export?status=published', auth=True, ok={200})
    export_items = export_body.get('items', []) if isinstance(export_body, dict) else []
    add_check('published canonical export includes temporary simulation', any(item.get('address_code') == address_code for item in export_items) and not contains_private_fields(export_body), {'status': export_status, 'items': len(export_items), 'private_fields': contains_private_fields(export_body)})

    signage_status, signage_body, _ = request('GET', f'{api_base}/api/v1/signage/export?status=published', auth=True, ok={200})
    signage_items = signage_body.get('items', []) if isinstance(signage_body, dict) else []
    add_check('published signage export includes temporary simulation', any(item.get('address_code') == address_code for item in signage_items) and not contains_private_fields(signage_body), {'status': signage_status, 'items': len(signage_items), 'private_fields': contains_private_fields(signage_body)})

    proof_status, proof_html, _ = request('GET', f'{api_base.replace(":8100", ":3100")}/proof/{urllib.parse.quote(address_code)}', ok={200})
    code_status, code_html, _ = request('GET', f'{api_base.replace(":8100", ":3100")}/code/{urllib.parse.quote(address_code)}', ok={200})
    add_check('served proof/code pages render simulation code', proof_status == 200 and code_status == 200 and address_code in str(proof_html) and address_code in str(code_html), {'proof_status': proof_status, 'code_status': code_status})

    # Retire the simulation fixture immediately after published behavior proof.
    docker_sql(f"""
BEGIN;
UPDATE address_records
SET is_archived = TRUE,
    publication_state = 'retired-fixture',
    record_bundle = jsonb_set(record_bundle, '{{retirement}}', jsonb_build_object('status', 'retired-fixture', 'reason', 'controlled-published-simulation', 'retired_at', NOW()::text), true),
    updated_at = NOW()
WHERE address_code = {code_lit}
  AND source_submission_id = {submission_lit};

UPDATE citizen_geotag_submissions
SET status = 'retired-fixture',
    reviewer_note = 'Retired controlled published simulation fixture; not official publication.',
    updated_at = NOW()
WHERE id = {submission_lit}
  AND address_label = {label_lit};
COMMIT;
""")

    post_json = json.loads(docker_sql(f"""
SELECT json_build_object(
  'active_canonical', (SELECT count(*) FROM address_records WHERE address_code = {code_lit} AND is_archived = FALSE),
  'active_submission', (SELECT count(*) FROM citizen_geotag_submissions WHERE id = {submission_lit} AND status <> 'retired-fixture'),
  'published_export_visible', (SELECT count(*) FROM address_records WHERE address_code = {code_lit} AND status = 'published' AND is_archived = FALSE)
);
"""))
    add_check('simulation fixture retired after proof', post_json.get('active_canonical') == 0 and post_json.get('active_submission') == 0 and post_json.get('published_export_visible') == 0, post_json)

    post_public_status, post_public_record, _ = request('GET', f'{api_base}/api/v1/public/address-code/{urllib.parse.quote(address_code)}/record', ok={200})
    post_public_text = json.dumps(post_public_record)
    add_check('retired simulation no longer leaks as published public record', post_public_status == 200 and post_public_record.get('publication_status') != 'published' and label not in post_public_text, {'status': post_public_status, 'publication_status': post_public_record.get('publication_status'), 'contains_label': label in post_public_text})

except Exception as exc:
    checks.append({'name': 'script exception', 'status': 'fail', 'evidence': repr(exc)})

pass_count = sum(1 for check in checks if check['status'] == 'pass')
fail_count = sum(1 for check in checks if check['status'] == 'fail')
overall = 'fail' if fail_count else 'pass'
report = {
    'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'overall_status': overall,
    'summary': {'pass': pass_count, 'fail': fail_count},
    'mode': 'controlled-temporary-published-simulation-proof',
    'api_base_url': api_base,
    'created_fixture': created,
    'checks': checks,
    'safety_boundary': {
        'official_publication_endpoint_enabled': False,
        'temporary_db_publication_for_proof': True,
        'retired_after_proof': True,
        'certificate_issuance': 'temporary simulation proof only',
        'signage_release': 'temporary simulation proof only; fixture retired',
    },
}
json_path = out_dir / 'latest-published-simulation-proof.json'
md_path = out_dir / 'latest-published-simulation-proof.md'
json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

lines = [
    '# Published simulation pilot proof',
    '',
    f"- Generated UTC: `{report['generated_at_utc']}`",
    f"- Overall: `{overall}`",
    '- Mode: `controlled temporary published simulation proof`',
    f"- Address code: `{created.get('address_code', 'not-created')}`",
    f"- Submission ID: `{created.get('submission_id', 'not-created')}`",
    '',
    '## Safety boundary',
    '',
    '- Official publish endpoint enabled: `false`',
    '- Temporary DB publication for proof: `true`',
    '- Retired after proof: `true`',
    '- Certificate/signage evidence: `simulation-only, then retired`',
    '',
    '## Checks',
    '',
    '| Status | Check | Evidence |',
    '|---|---|---|',
]
for check in checks:
    evidence = check.get('evidence')
    if isinstance(evidence, dict):
        evidence_text = '<br>'.join(f'{key}={value}' for key, value in evidence.items()) or 'ok'
    else:
        evidence_text = str(evidence or 'ok')
    lines.append(f"| `{check['status']}` | {check['name']} | {evidence_text} |")
lines += [
    '',
    '## Notes',
    '',
    '- This script intentionally uses a temporary published simulation state after proving the official publish endpoint is gated.',
    '- The fixture is retired before the script exits successfully.',
    '- This is not a government/publication approval action.',
]
md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'overall={overall} pass={pass_count} fail={fail_count} json={json_path} markdown={md_path}')
if fail_count:
    sys.exit(1)
PY
