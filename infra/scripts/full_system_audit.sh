#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/artifacts/audits}"
RUN_HEAVY="${RUN_HEAVY:-NO}"
RUN_MUTATING="${RUN_MUTATING:-NO}"
RUN_AUTH_CHECKS="${RUN_AUTH_CHECKS:-NO}"
RUN_PUBLIC_SCAN="${RUN_PUBLIC_SCAN:-YES}"
PUBLIC_BASE_URL="${PUBLIC_BASE_URL:-https://eg-addressing.51.195.20.137.sslip.io}"
LOCAL_API_BASE="${LOCAL_API_BASE:-http://127.0.0.1:8100}"
LOCAL_ADMIN_BASE="${LOCAL_ADMIN_BASE:-http://127.0.0.1:3100}"
PUBLIC_HOST="${PUBLIC_HOST:-51.195.20.137}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"

mkdir -p "$OUT_DIR"

python3 - "$ROOT_DIR" "$ENV_FILE" "$OUT_DIR" "$RUN_HEAVY" "$RUN_MUTATING" "$RUN_AUTH_CHECKS" "$RUN_PUBLIC_SCAN" "$PUBLIC_BASE_URL" "$LOCAL_API_BASE" "$LOCAL_ADMIN_BASE" "$PUBLIC_HOST" "$COMPOSE_FILE" <<'PY'
import datetime as dt
import html
import json
import os
import pathlib
import re
import shlex
import socket
import subprocess
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from http.cookiejar import MozillaCookieJar
from typing import Any

root = pathlib.Path(sys.argv[1]).resolve()
env_file = pathlib.Path(sys.argv[2]).resolve()
out_dir = pathlib.Path(sys.argv[3]).resolve()
run_heavy = sys.argv[4].upper() == 'YES'
run_mutating = sys.argv[5].upper() == 'YES'
run_auth_checks = sys.argv[6].upper() == 'YES'
run_public_scan = sys.argv[7].upper() == 'YES'
public_base_url = sys.argv[8].rstrip('/')
local_api_base = sys.argv[9].rstrip('/')
local_admin_base = sys.argv[10].rstrip('/')
public_host = sys.argv[11]
compose_file = pathlib.Path(sys.argv[12]).resolve()
out_dir.mkdir(parents=True, exist_ok=True)

started = dt.datetime.now(dt.timezone.utc)
checks: list[dict[str, Any]] = []
artifacts: dict[str, str] = {}


def parse_env(path: pathlib.Path) -> dict[str, str]:
    env = os.environ.copy()
    if not path.exists():
        return env
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def redact(text: str) -> str:
    env = runtime_env
    secrets = [env.get('SMOKE_ADMIN_PASSWORD'), env.get('OPERATOR_PASSWORD'), env.get('POSTGRES_PASSWORD'), env.get('SESSION_SECRET_KEY'), env.get('PASSWORD_SALT')]
    for secret in [s for s in secrets if s and len(s) >= 4]:
        text = text.replace(secret, '***')
    return text


def run_check(name: str, command: list[str], cwd: pathlib.Path | None = None, timeout: int = 180, include_output: bool = False, env: dict[str, str] | None = None, warn_on_fail: bool = False) -> dict[str, Any]:
    cwd = cwd or root
    item: dict[str, Any] = {
        'name': name,
        'command': ' '.join(shlex.quote(part) for part in command),
        'cwd': str(cwd),
    }
    before = dt.datetime.now(dt.timezone.utc)
    try:
        completed = subprocess.run(command, cwd=str(cwd), env=env, text=True, capture_output=True, timeout=timeout)
        output = redact((completed.stdout + completed.stderr).strip())
        item.update({
            'exit_code': completed.returncode,
            'duration_seconds': round((dt.datetime.now(dt.timezone.utc) - before).total_seconds(), 2),
            'status': 'pass' if completed.returncode == 0 else ('warn' if warn_on_fail else 'fail'),
        })
        if include_output or completed.returncode != 0:
            item['output'] = output[-8000:]
    except subprocess.TimeoutExpired as exc:
        item.update({'exit_code': None, 'duration_seconds': timeout, 'status': 'warn' if warn_on_fail else 'fail', 'output': redact(f'timeout after {timeout}s: {exc}')})
    checks.append(item)
    return item


def add_check(name: str, status: str, **kwargs: Any) -> dict[str, Any]:
    item = {'name': name, 'status': status, **kwargs}
    checks.append(item)
    return item


def http_request(method: str, url: str, *, body: bytes | None = None, headers: dict[str, str] | None = None, jar: MozillaCookieJar | None = None, timeout: int = 30) -> tuple[int, str, dict[str, str]]:
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar)) if jar is not None else urllib.request.build_opener()
    request = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with opener.open(request, timeout=timeout) as response:
            return response.status, response.read().decode('utf-8', errors='replace'), dict(response.headers.items())
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode('utf-8', errors='replace'), dict(exc.headers.items())


def strip_text(source: str) -> str:
    source = re.sub(r'<script[\s\S]*?</script>', ' ', source, flags=re.I)
    source = re.sub(r'<style[\s\S]*?</style>', ' ', source, flags=re.I)
    source = re.sub(r'<[^>]+>', ' ', source)
    return re.sub(r'\s+', ' ', html.unescape(source)).strip()

runtime_env = parse_env(env_file)

# Repo state
head = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=str(root), text=True, capture_output=True).stdout.strip()
status = subprocess.run(['git', 'status', '--short'], cwd=str(root), text=True, capture_output=True).stdout.strip()
add_check('git status', 'pass' if not status else 'warn', head=head, dirty_count=0 if not status else len(status.splitlines()), output=status[:2000])

# Existing audit harnesses
streamline = run_check('streamline audit', ['bash', 'infra/scripts/streamline_audit.sh'], cwd=root, timeout=600, env={**runtime_env, 'RUN_LIVE': 'YES', 'RUN_HEAVY': 'YES' if run_heavy else 'NO'}, include_output=True)
if streamline['status'] == 'pass':
    match = re.search(r'summary=pass:(\d+) warn:(\d+) fail:(\d+)', streamline.get('output', ''))
    if match:
        streamline['summary'] = {'pass': int(match.group(1)), 'warn': int(match.group(2)), 'fail': int(match.group(3))}

if run_mutating:
    run_check('full mutating audit_all', ['bash', 'infra/scripts/audit_all.sh'], cwd=root, timeout=600, env=runtime_env, include_output=True)
else:
    add_check('full mutating audit_all', 'skip', reason='RUN_MUTATING=NO; smoke tests and cleanup intentionally skipped')

# Fast local service checks
for name, url in [
    ('local api health', f'{local_api_base}/api/v1/health'),
    ('local admin home', f'{local_admin_base}/'),
    ('public https home', f'{public_base_url}/'),
    ('public https api health', f'{public_base_url}/api/v1/health'),
]:
    status_code, body, _headers = http_request('GET', url)
    add_check(name, 'pass' if 200 <= status_code < 300 else 'fail', status_code=status_code, body_excerpt=strip_text(body)[:180])

# Public route scan, HTML/text only and dependency-free.
if run_public_scan:
    routes = ['/', '/geotag', '/issue', '/track', '/code/EG-BN-MALABO-001A', '/proof/EG-BN-MALABO-001A', '/operations-runbook', '/login']
    forbidden = ['admin123', 'editor123', 'viewer123', 'MVP', 'prototype', 'lorem ipsum', 'http://api:8100', 'localhost:8100', '/home/ubuntu']
    route_results = []
    bad = []
    for route in routes:
        url = public_base_url + route
        status_code, body, headers = http_request('GET', url)
        text = strip_text(body)
        visible_bad = [term for term in forbidden if term in text]
        html_bad = [term for term in ['http://api:8100', 'localhost:8100', '/home/ubuntu'] if term in body]
        has_banner = 'STAGING' in text or 'NOT AN OFFICIAL PRODUCTION RECORD' in text
        result = {'route': route, 'status_code': status_code, 'has_staging_banner': has_banner, 'visible_forbidden': visible_bad, 'html_raw_leaks': html_bad, 'body_chars': len(text)}
        route_results.append(result)
        if status_code != 200 or visible_bad or html_bad or not has_banner:
            bad.append(result)
    route_artifact = out_dir / 'latest-full-system-public-routes.json'
    route_artifact.write_text(json.dumps(route_results, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    artifacts['public_routes_json'] = str(route_artifact)
    add_check('public route text scan', 'pass' if not bad else 'fail', routes=len(route_results), failures=bad[:8], artifact=str(route_artifact))
else:
    add_check('public route text scan', 'skip', reason='RUN_PUBLIC_SCAN=NO')

# Port containment
ports = [3100, 8100, 9100, 9101, 5434, 6384]
port_results = []
open_ports = []
for port in ports:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect((public_host, port))
        state = 'open'
        open_ports.append(port)
    except OSError:
        state = 'closed'
    finally:
        sock.close()
    port_results.append({'port': port, 'state': state})
add_check('raw public service port containment', 'pass' if not open_ports else 'fail', host=public_host, ports=port_results)

# Data hygiene counts; read-only.
if env_file.exists():
    live_project = subprocess.run(['docker', 'inspect', '-f', '{{ index .Config.Labels "com.docker.compose.project" }}', 'eg-addressing-api'], cwd=str(root), text=True, capture_output=True)
    compose_project = (live_project.stdout.strip() or runtime_env.get('COMPOSE_PROJECT_NAME') or 'docker')
    postgres_user = runtime_env.get('POSTGRES_USER', 'addressing')
    postgres_db = runtime_env.get('POSTGRES_DB', 'addressing')
    sql = """
SELECT json_build_object(
  'address_records', (SELECT COUNT(*) FROM address_records),
  'active_controlled_address_records', (SELECT COUNT(*) FROM address_records WHERE is_archived = FALSE AND (address_label ILIKE 'Controlled canonical proof fixture%' OR address_label ILIKE 'Controlled canonical pilot address%' OR address_label ILIKE 'Controlled published simulation fixture%' OR record_bundle::text ILIKE '%controlled-fixture%' OR record_bundle::text ILIKE '%controlled-published-simulation%')),
  'active_controlled_submissions', (SELECT COUNT(*) FROM citizen_geotag_submissions WHERE status <> 'retired-fixture' AND (address_label ILIKE 'Controlled canonical proof fixture%' OR address_label ILIKE 'Controlled canonical pilot address%' OR address_label ILIKE 'Controlled published simulation fixture%' OR landmark ILIKE '%Controlled proof fixture%' OR reviewer_note ILIKE '%controlled proof fixture%' OR reviewer_note ILIKE '%controlled-published-simulation%')),
  'smoke_field_submissions', (SELECT COUNT(*) FROM field_submissions WHERE submitted_by IN ('Smoke automation','Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%'),
  'smoke_roads', (SELECT COUNT(*) FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%'),
  'smoke_corrections', (SELECT COUNT(*) FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review')
);
"""
    db_check = run_check('database hygiene counts', ['docker', 'compose', '-p', compose_project, '--env-file', str(env_file), '-f', str(compose_file), 'exec', '-T', 'postgres', 'psql', '-U', postgres_user, '-d', postgres_db, '-tAc', sql], cwd=root, timeout=120, include_output=True, warn_on_fail=False)
    if db_check['status'] == 'pass':
        try:
            counts = json.loads(str(db_check.get('output', '{}')).strip())
            db_check['counts'] = counts
            residue = counts.get('active_controlled_address_records', 0) + counts.get('active_controlled_submissions', 0) + counts.get('smoke_field_submissions', 0) + counts.get('smoke_roads', 0) + counts.get('smoke_corrections', 0)
            db_check['residue_count'] = residue
            db_check['status'] = 'pass' if residue == 0 else 'warn'
        except Exception as exc:
            db_check['status'] = 'warn'
            db_check['parse_error'] = repr(exc)
else:
    add_check('database hygiene counts', 'skip', reason='env file missing')

# Optional auth/security checks. Login/logout writes session/audit entries, so this is explicit.
if run_auth_checks:
    username = runtime_env.get('SMOKE_ADMIN_USERNAME') or runtime_env.get('OPERATOR_USERNAME') or 'admin'
    password = runtime_env.get('SMOKE_ADMIN_PASSWORD') or runtime_env.get('OPERATOR_PASSWORD')
    if not password:
        add_check('auth safety gates', 'warn', reason='RUN_AUTH_CHECKS=YES but no smoke/operator password found')
    else:
        jar = MozillaCookieJar(str(pathlib.Path(tempfile.mkstemp(prefix='eg-audit-cookie-', suffix='.txt')[1])))
        # Auth checks intentionally use the public HTTPS origin so Secure cookies are handled like a real browser path.
        api_auth_base = f'{public_base_url}/api/v1'
        login_body = json.dumps({'username': username, 'password': password}).encode('utf-8')
        login_status, login_text, _ = http_request('POST', f'{api_auth_base}/auth/login', body=login_body, headers={'Content-Type': 'application/json'}, jar=jar)
        csrf = None
        for cookie in jar:
            if cookie.name == 'eg_addressing_csrf':
                csrf = cookie.value
        me_status, _me_text, _ = http_request('GET', f'{api_auth_base}/auth/me', jar=jar)
        release_status, release_text, _ = http_request('POST', f'{api_auth_base}/geotag-submissions/nonexistent/publish', body=b'{"reviewer_note":"audit gate check"}', headers={'Content-Type': 'application/json', 'X-CSRF-Token': csrf or ''}, jar=jar)
        ack_payload = json.dumps({'territory_id':'territory-malabo-ela-nguema','province_code':'BN','address_label':'Audit no ack','latitude':3.75,'longitude':8.77,'capture_method':'audit'}).encode('utf-8')
        ack_status, ack_text, _ = http_request('POST', f'{api_auth_base}/public/geotag-submissions', body=ack_payload, headers={'Content-Type':'application/json'})
        logout_status, _logout_text, _ = http_request('POST', f'{api_auth_base}/auth/logout', headers={'X-CSRF-Token': csrf or ''}, jar=jar)
        revoked_status, _revoked_text, _ = http_request('GET', f'{api_auth_base}/auth/me', jar=jar)
        try:
            login_json = json.loads(login_text)
        except Exception:
            login_json = {}
        try:
            release_detail = json.loads(release_text).get('detail')
        except Exception:
            release_detail = release_text[:120]
        try:
            ack_detail = json.loads(ack_text).get('detail')
        except Exception:
            ack_detail = ack_text[:120]
        ok = login_status == 200 and me_status == 200 and release_status == 403 and ack_status == 400 and logout_status == 204 and revoked_status == 401 and 'token' not in login_json and 'csrf_token' not in login_json
        add_check('auth/privacy/release safety gates', 'pass' if ok else 'fail', login_status=login_status, auth_mode=login_json.get('auth_mode'), login_json_has_token='token' in login_json, login_json_has_csrf='csrf_token' in login_json, auth_me_status=me_status, release_gate_status=release_status, release_detail=release_detail, privacy_missing_ack_status=ack_status, privacy_missing_ack_detail=ack_detail, logout_status=logout_status, revoked_me_status=revoked_status)
else:
    add_check('auth/privacy/release safety gates', 'skip', reason='RUN_AUTH_CHECKS=NO; avoids session/audit writes by default')

# Source-size and clutter signals.
skip_names = {'.git', 'node_modules', '.next', '.pytest_cache', '__pycache__', 'data', 'backups', 'artifacts'}
exts = {'.py', '.ts', '.tsx', '.js', '.mjs', '.css', '.sql', '.sh', '.md', '.yml', '.yaml', '.json'}
line_counts: dict[str, int] = {}
large_files: list[tuple[int, str]] = []
for path in root.rglob('*'):
    if not path.is_file():
        continue
    if set(path.parts) & skip_names or any(part.startswith('.venv') for part in path.parts):
        continue
    if path.suffix not in exts:
        continue
    try:
        text = path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        continue
    lines = text.count('\n') + 1 if text else 0
    line_counts[path.suffix] = line_counts.get(path.suffix, 0) + lines
    if lines > 500:
        large_files.append((lines, str(path.relative_to(root))))
large_files = sorted(large_files, reverse=True)[:25]
source_artifact = out_dir / 'latest-full-system-source-size.json'
source_artifact.write_text(json.dumps({'line_counts': line_counts, 'large_files': large_files}, indent=2, sort_keys=True) + '\n', encoding='utf-8')
artifacts['source_size_json'] = str(source_artifact)
add_check('source size inventory', 'pass', large_file_count=len(large_files), largest=large_files[:8], artifact=str(source_artifact))

pass_count = sum(1 for c in checks if c.get('status') == 'pass')
warn_count = sum(1 for c in checks if c.get('status') == 'warn')
fail_count = sum(1 for c in checks if c.get('status') == 'fail')
skip_count = sum(1 for c in checks if c.get('status') == 'skip')
overall = 'fail' if fail_count else 'warn' if warn_count else 'pass'
report = {
    'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'duration_seconds': round((dt.datetime.now(dt.timezone.utc) - started).total_seconds(), 2),
    'root': str(root),
    'commit': head,
    'mode': {'run_heavy': run_heavy, 'run_mutating': run_mutating, 'run_auth_checks': run_auth_checks, 'run_public_scan': run_public_scan},
    'overall_status': overall,
    'summary': {'pass': pass_count, 'warn': warn_count, 'fail': fail_count, 'skip': skip_count},
    'artifacts': artifacts,
    'checks': checks,
}
json_path = out_dir / 'latest-full-system-audit.json'
md_path = out_dir / 'latest-full-system-audit.md'
json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

lines = [
    '# Full system audit', '',
    f"- Generated UTC: `{report['generated_at_utc']}`",
    f"- Commit: `{head}`",
    f"- Overall: `{overall}`",
    f"- Mode: `RUN_HEAVY={'YES' if run_heavy else 'NO'}`, `RUN_MUTATING={'YES' if run_mutating else 'NO'}`, `RUN_AUTH_CHECKS={'YES' if run_auth_checks else 'NO'}`",
    '', '## Summary', '',
    '| Status | Count |', '|---|---:|',
    f"| pass | {pass_count} |", f"| warn | {warn_count} |", f"| fail | {fail_count} |", f"| skip | {skip_count} |",
    '', '## Checks', '',
    '| Status | Check | Evidence |', '|---|---|---|',
]
for check in checks:
    evidence = []
    for key in ['exit_code', 'status_code', 'dirty_count', 'routes', 'residue_count', 'large_file_count', 'auth_mode', 'release_gate_status', 'privacy_missing_ack_status']:
        if key in check:
            evidence.append(f'{key}={check[key]}')
    if 'summary' in check:
        evidence.append(f"summary={check['summary']}")
    if 'reason' in check:
        evidence.append(str(check['reason']))
    if check.get('status') in {'fail', 'warn'} and check.get('output'):
        evidence.append('`' + str(check.get('output')).replace('\n', ' ')[:260] + '`')
    if 'artifact' in check:
        evidence.append(f"artifact=`{check['artifact']}`")
    lines.append(f"| `{check.get('status')}` | {check.get('name')} | {'<br>'.join(evidence) if evidence else 'ok'} |")
lines += ['', '## Artifacts', '']
for key, value in artifacts.items():
    lines.append(f'- `{key}`: `{value}`')
lines += ['', '## Notes', '', '- Default mode avoids mutating smoke tests. Use `RUN_MUTATING=YES` intentionally when the audit should run smoke and cleanup.', '- Auth safety checks are optional with `RUN_AUTH_CHECKS=YES` because login/logout creates session/audit entries.']
md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

print(f'overall={overall}')
print(f'json={json_path}')
print(f'markdown={md_path}')
print(f'summary=pass:{pass_count} warn:{warn_count} fail:{fail_count} skip:{skip_count}')
sys.exit(1 if overall == 'fail' else 0)
PY
