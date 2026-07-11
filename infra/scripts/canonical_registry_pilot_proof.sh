#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
API_BASE_URL="${API_BASE_URL:-http://127.0.0.1:8100}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://eg-addressing.51.195.20.137.sslip.io}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/artifacts/audits}"
mkdir -p "$OUT_DIR"

python3 - "$ROOT_DIR" "$ENV_FILE" "$API_BASE_URL" "$PUBLIC_BASE_URL" "$OUT_DIR" <<'PY'
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
public_base = sys.argv[4].rstrip('/')
out_dir = pathlib.Path(sys.argv[5]).resolve()
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
        cwd=str(root), text=True, capture_output=True, timeout=60,
    )
    if completed.returncode != 0:
        raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
    return completed.stdout.strip()


now = dt.datetime.now(dt.timezone.utc)
stamp = now.strftime('%Y%m%dT%H%M%SZ')
label = f'Controlled canonical proof fixture {stamp}'
submission_payload = {
    'territory_id': 'territory-malabo-ela-nguema',
    'province_code': 'BN',
    'address_label': label,
    'landmark': 'Controlled proof fixture near Ela Nguema clinic gate — internal registry only',
    'latitude': 3.7523,
    'longitude': 8.7741,
    'accuracy_meters': 8,
    'capture_method': 'controlled-pilot-proof-script',
    'suggested_road_name': 'Carretera del Aeropuerto',
    'suggested_local_area': 'Ela Nguema',
    'suggested_place_name': 'Malabo Ela Nguema',
    'map_display_name': 'Controlled internal registry proof fixture, Ela Nguema, Malabo',
    'road_suggestion_source': 'controlled-fixture',
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
    add_check('controlled public geotag created', create_status == 201 and address_code.startswith('EG-'), {'status': create_status, 'submission_id': submission_id, 'address_code': address_code})

    login_status, login_body, _ = request('POST', f'{api_base}/api/v1/auth/login', {'username': admin_username, 'password': admin_password}, ok={200})
    bearer_token = login_body.get('token') if isinstance(login_body, dict) else None
    add_check('operator login', login_status == 200, {'status': login_status, 'auth_mode': login_body.get('auth_mode') if isinstance(login_body, dict) else None})

    promote_status, promoted, _ = request('POST', f'{api_base}/api/v1/geotag-submissions/{submission_id}/registry-ready', {'reviewer_note': 'Controlled canonical proof: internal registry-ready only, no publication.'}, auth=True, ok={200})
    record = promoted.get('address_record') if isinstance(promoted, dict) else None
    add_check('registry-ready promotion creates canonical record', promote_status == 200 and isinstance(record, dict), {'status': promote_status, 'address_code': address_code, 'record_status': record.get('status') if isinstance(record, dict) else None})

    case_status, case_file, _ = request('GET', f'{api_base}/api/v1/address-records/{urllib.parse.quote(address_code)}', auth=True, ok={200})
    add_check('protected case file available', case_status == 200 and case_file.get('address_code') == address_code, {'status': case_status})

    export_ready_status, export_ready, _ = request('GET', f'{api_base}/api/v1/address-records/export?status=registry-ready', auth=True, ok={200})
    ready_items = export_ready.get('items', []) if isinstance(export_ready, dict) else []
    add_check('registry-ready export includes fixture', any(item.get('address_code') == address_code for item in ready_items), {'status': export_ready_status, 'items': len(ready_items)})

    export_pub_status, export_pub, _ = request('GET', f'{api_base}/api/v1/address-records/export?status=published', auth=True, ok={200})
    pub_items = export_pub.get('items', []) if isinstance(export_pub, dict) else []
    add_check('published export excludes internal fixture', not any(item.get('address_code') == address_code for item in pub_items), {'status': export_pub_status, 'published_items': len(pub_items)})

    cert_status, cert_body, _ = request('GET', f'{api_base}/api/v1/address-records/{urllib.parse.quote(address_code)}/certificate', auth=True, ok={400, 404})
    add_check('certificate blocked before publication', cert_status == 400 and 'published' in json.dumps(cert_body).lower(), {'status': cert_status, 'detail': cert_body.get('detail') if isinstance(cert_body, dict) else str(cert_body)[:160]})

    public_status, public_record, _ = request('GET', f'{api_base}/api/v1/public/address-code/{urllib.parse.quote(address_code)}/record', ok={200})
    public_text = json.dumps(public_record)
    add_check('public record stays locked and non-leaky', public_status == 200 and 'internal' in public_text.lower() and label not in public_text, {'status': public_status, 'contains_label': label in public_text})

    proof_status, proof_body, _ = request('GET', f'{api_base}/api/v1/public/tracking/{urllib.parse.quote(address_code)}', ok={200})
    proof_text = json.dumps(proof_body)
    proof_publication_state = proof_body.get('publication_state') if isinstance(proof_body, dict) else None
    proof_status_value = proof_body.get('status') if isinstance(proof_body, dict) else None
    tracking_locked = proof_publication_state != 'public' and proof_status_value != 'published' and label not in proof_text
    add_check('public tracking explains locked status', proof_status == 200 and tracking_locked, {'status': proof_status, 'status_value': proof_status_value, 'publication_state': proof_publication_state, 'contains_label': label in proof_text})

    db_json = docker_sql(f"""
SELECT json_build_object(
  'address_code', address_code,
  'status', status,
  'publication_state', publication_state,
  'geom_ready', geom IS NOT NULL,
  'geometry_wkt', ST_AsText(geom::geometry),
  'label_visible_in_db', address_label
)
FROM address_records
WHERE address_code = '{address_code.replace("'", "''")}';
""")
    db_record = json.loads(db_json)
    add_check('canonical database row has PostGIS geometry', bool(db_record.get('geom_ready')), {'geometry_wkt': db_record.get('geometry_wkt')})
    add_check('canonical database row remains internal registry', db_record.get('status') == 'registry-ready' and db_record.get('publication_state') == 'internal-registry', {'status': db_record.get('status'), 'publication_state': db_record.get('publication_state')})

except Exception as exc:
    checks.append({'name': 'script exception', 'status': 'fail', 'evidence': repr(exc)})

pass_count = sum(1 for check in checks if check['status'] == 'pass')
fail_count = sum(1 for check in checks if check['status'] == 'fail')
overall = 'fail' if fail_count else 'pass'
report = {
    'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'overall_status': overall,
    'summary': {'pass': pass_count, 'fail': fail_count},
    'mode': 'controlled-mutating-canonical-proof',
    'api_base_url': api_base,
    'public_base_url': public_base,
    'created_fixture': created,
    'checks': checks,
    'safety_boundary': {
        'official_publication': False,
        'certificate_issuance': False,
        'signage_release': False,
        'fixture_publication_state': 'internal-registry',
    },
}
json_path = out_dir / 'latest-canonical-registry-proof.json'
md_path = out_dir / 'latest-canonical-registry-proof.md'
json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

lines = [
    '# Canonical registry pilot proof',
    '',
    f"- Generated UTC: `{report['generated_at_utc']}`",
    f"- Overall: `{overall}`",
    '- Mode: `controlled mutating proof`',
    f"- Address code: `{created.get('address_code', 'not-created')}`",
    f"- Submission ID: `{created.get('submission_id', 'not-created')}`",
    '',
    '## Safety boundary',
    '',
    '- Official publication: `false`',
    '- Certificate issuance: `false`',
    '- Signage release: `false`',
    '- Fixture state: `registry-ready / internal-registry`',
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
    '- This script intentionally creates one controlled internal-registry fixture per run.',
    '- It does not publish records, issue certificates, or release signage.',
    '- Fixture retirement belongs to the later retirement-policy lane.',
]
md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f"overall={overall}")
print(f"address_code={created.get('address_code', '')}")
print(f"json={json_path}")
print(f"markdown={md_path}")
print(f"summary=pass:{pass_count} fail:{fail_count}")
sys.exit(1 if fail_count else 0)
PY
