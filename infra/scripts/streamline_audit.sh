#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
RUN_HEAVY="${RUN_HEAVY:-NO}"
RUN_LIVE="${RUN_LIVE:-YES}"
ENV_FILE="${ENV_FILE:-$ROOT_DIR/.env}"
COMPOSE_FILE="${COMPOSE_FILE:-$ROOT_DIR/infra/docker/docker-compose.yml}"
OUT_DIR="${OUT_DIR:-$ROOT_DIR/artifacts/audits}"
mkdir -p "$OUT_DIR"

python3 - "$ROOT_DIR" "$RUN_HEAVY" "$RUN_LIVE" "$ENV_FILE" "$COMPOSE_FILE" "$OUT_DIR" <<'PY'
import datetime as dt
import json
import os
import pathlib
import re
import shlex
import subprocess
import sys
from typing import Any

root = pathlib.Path(sys.argv[1]).resolve()
run_heavy = sys.argv[2].upper() == 'YES'
run_live = sys.argv[3].upper() == 'YES'
env_file = pathlib.Path(sys.argv[4]).resolve()
compose_file = pathlib.Path(sys.argv[5]).resolve()
out_dir = pathlib.Path(sys.argv[6]).resolve()
out_dir.mkdir(parents=True, exist_ok=True)

checks: list[dict[str, Any]] = []
artifacts: dict[str, str] = {}

def run(name: str, command: list[str], cwd: pathlib.Path | None = None, timeout: int = 120, env: dict[str, str] | None = None, include_output: bool = False) -> dict[str, Any]:
    cwd = cwd or root
    started = dt.datetime.now(dt.timezone.utc)
    try:
        completed = subprocess.run(command, cwd=str(cwd), text=True, capture_output=True, timeout=timeout, env=env)
        output = (completed.stdout + completed.stderr).strip()
        check = {
            'name': name,
            'status': 'pass' if completed.returncode == 0 else 'fail',
            'exit_code': completed.returncode,
            'command': ' '.join(shlex.quote(part) for part in command),
            'cwd': str(cwd),
            'duration_seconds': round((dt.datetime.now(dt.timezone.utc) - started).total_seconds(), 2),
        }
        if include_output or completed.returncode != 0:
            check['output'] = output[-6000:]
    except subprocess.TimeoutExpired as exc:
        check = {
            'name': name,
            'status': 'fail',
            'exit_code': None,
            'command': ' '.join(shlex.quote(part) for part in command),
            'cwd': str(cwd),
            'duration_seconds': timeout,
            'output': f'timeout after {timeout}s: {exc}',
        }
    except Exception as exc:
        check = {
            'name': name,
            'status': 'fail',
            'exit_code': None,
            'command': ' '.join(shlex.quote(part) for part in command),
            'cwd': str(cwd),
            'duration_seconds': 0,
            'output': repr(exc),
        }
    checks.append(check)
    return check

def read(path: pathlib.Path) -> str:
    return path.read_text(encoding='utf-8')

def route_from_page(page: pathlib.Path) -> str:
    rel = page.parent.relative_to(root / 'apps/admin-portal/app')
    if str(rel) == '.':
        return '/'
    return '/' + str(rel).replace(os.sep, '/')

def parse_env_file(path: pathlib.Path) -> dict[str, str]:
    env = os.environ.copy()
    if not path.exists():
        return env
    for raw in path.read_text(encoding='utf-8').splitlines():
        line = raw.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        value = value.strip().strip('"').strip("'")
        env[key.strip()] = value
    return env

report_env = parse_env_file(env_file)

# Source inventory
routes = sorted(route_from_page(path) for path in (root / 'apps/admin-portal/app').glob('**/page.tsx'))
site_data = read(root / 'apps/admin-portal/components/site-data.ts')
api_main = read(root / 'services/api/app/main.py')
endpoints = sorted(set(f'{method.upper()} {path}' for method, path in re.findall(r"@app\.(get|post|patch|delete|put)\(['\"]([^'\"]+)", api_main)))

checks.append({'name': 'route inventory', 'status': 'pass', 'routes': routes, 'count': len(routes)})
checks.append({'name': 'api endpoint inventory', 'status': 'pass', 'count': len(endpoints)})

# Git and source guards
status_check = run('git status clean', ['git', 'status', '--short'], include_output=True)
status_output = status_check.get('output', '')
status_check['status'] = 'pass' if status_output == '' else 'warn'
status_check['dirty_count'] = 0 if status_output == '' else len(status_output.splitlines())

run('route ownership guard', ['npm', 'run', 'test:route-ownership'], cwd=root / 'apps/admin-portal', timeout=120, include_output=True)
run('role/auth guard', ['npm', 'run', 'test:role-auth'], cwd=root / 'apps/admin-portal', timeout=120, include_output=True)

# Live health and data counts are read-only.
if run_live:
    for name, url in [
        ('api health', 'http://127.0.0.1:8100/api/v1/health'),
        ('admin home', 'http://127.0.0.1:3100/'),
        ('reports page', 'http://127.0.0.1:3100/reports'),
        ('geotag page', 'http://127.0.0.1:3100/geotag'),
    ]:
        run(name, ['curl', '-fsS', '-o', '/dev/null', '-w', '%{http_code}', url], timeout=30, include_output=True)

    docker_ok = run('docker availability', ['docker', 'info'], timeout=30)
    if docker_ok['status'] == 'pass' and env_file.exists():
        live_project = subprocess.run(['docker', 'inspect', '-f', '{{ index .Config.Labels "com.docker.compose.project" }}', 'eg-addressing-api'], cwd=str(root), text=True, capture_output=True)
        compose_project = (live_project.stdout.strip() or report_env.get('COMPOSE_PROJECT_NAME') or 'eg_addressing')
        postgres_db = report_env.get('POSTGRES_DB', 'addressing')
        postgres_user = report_env.get('POSTGRES_USER', 'addressing')
        sql = """
SELECT json_build_object(
  'field_submissions', (SELECT COUNT(*) FROM field_submissions),
  'roads', (SELECT COUNT(*) FROM roads),
  'address_corrections', (SELECT COUNT(*) FROM address_corrections),
  'address_records', (SELECT COUNT(*) FROM address_records),
  'audit_logs', (SELECT COUNT(*) FROM audit_logs),
  'users_active', (SELECT COUNT(*) FROM users WHERE is_active=true),
  'smoke_field_submissions', (SELECT COUNT(*) FROM field_submissions WHERE submitted_by IN ('Smoke automation','Browser smoke') OR candidate_name ILIKE 'Smoke Flow Road%' OR candidate_name ILIKE 'Smoke Map Grid Road%' OR candidate_name ILIKE 'Smoke Browser Map Grid%'),
  'smoke_roads', (SELECT COUNT(*) FROM roads WHERE name ILIKE 'Smoke Flow Road%' OR name ILIKE 'Smoke Map Grid Road%' OR name ILIKE 'Smoke Browser Map Grid%'),
  'smoke_corrections', (SELECT COUNT(*) FROM address_corrections WHERE reporter_contact='smoke@example.invalid' OR reason='smoke-test-review')
);
"""
        check = run(
            'database readiness counts',
            ['docker', 'compose', '-p', compose_project, '--env-file', str(env_file), '-f', str(compose_file), 'exec', '-T', 'postgres', 'psql', '-U', postgres_user, '-d', postgres_db, '-tAc', sql],
            timeout=60,
            include_output=True,
        )
        if check['status'] == 'pass':
            try:
                counts = json.loads(str(check.get('output', '{}')).strip())
                check['counts'] = counts
                smoke_total = counts.get('smoke_field_submissions', 0) + counts.get('smoke_roads', 0) + counts.get('smoke_corrections', 0)
                check['status'] = 'pass' if smoke_total == 0 else 'warn'
                check['smoke_total'] = smoke_total
            except Exception as exc:
                check['status'] = 'warn'
                check['parse_warning'] = repr(exc)

if run_heavy:
    api_venv = root / 'services/api/.venv/bin/python'
    if api_venv.exists():
        run('backend pytest', [str(api_venv), '-m', 'pytest', '-q'], cwd=root / 'services/api', timeout=300)
    else:
        checks.append({'name': 'backend pytest', 'status': 'warn', 'output': 'services/api/.venv missing; heavy backend tests skipped'})
    heavy_scripts = ['test:copy', 'test:data-command', 'test:official-geometry', 'test:api-types']
    for script in heavy_scripts:
        run(f'frontend {script}', ['npm', 'run', script], cwd=root / 'apps/admin-portal', timeout=180)
    run('frontend build', ['npm', 'run', 'build'], cwd=root / 'apps/admin-portal', timeout=600)

pass_count = sum(1 for check in checks if check.get('status') == 'pass')
warn_count = sum(1 for check in checks if check.get('status') == 'warn')
fail_count = sum(1 for check in checks if check.get('status') == 'fail')
overall = 'fail' if fail_count else 'warn' if warn_count else 'pass'

report = {
    'generated_at_utc': dt.datetime.now(dt.timezone.utc).isoformat(),
    'root': str(root),
    'mode': {'run_heavy': run_heavy, 'run_live': run_live},
    'overall_status': overall,
    'summary': {'pass': pass_count, 'warn': warn_count, 'fail': fail_count},
    'routes': routes,
    'api_endpoint_count': len(endpoints),
    'checks': checks,
}

json_path = out_dir / 'latest-streamline-audit.json'
md_path = out_dir / 'latest-streamline-audit.md'
json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')

lines = [
    '# Streamline audit report',
    '',
    f"- Generated UTC: `{report['generated_at_utc']}`",
    f"- Overall: `{overall}`",
    f"- Mode: `RUN_HEAVY={'YES' if run_heavy else 'NO'}`, `RUN_LIVE={'YES' if run_live else 'NO'}`",
    f"- Routes discovered: `{len(routes)}`",
    f"- API endpoints discovered: `{len(endpoints)}`",
    '',
    '## Check summary',
    '',
    '| Status | Count |',
    '|---|---:|',
    f"| pass | {pass_count} |",
    f"| warn | {warn_count} |",
    f"| fail | {fail_count} |",
    '',
    '## Checks',
    '',
    '| Status | Check | Evidence |',
    '|---|---|---|',
]
for check in checks:
    evidence_parts = []
    if 'count' in check:
        evidence_parts.append(f"count={check['count']}")
    if 'dirty_count' in check:
        evidence_parts.append(f"dirty_count={check['dirty_count']}")
    if 'smoke_total' in check:
        evidence_parts.append(f"smoke_total={check['smoke_total']}")
    if 'exit_code' in check:
        evidence_parts.append(f"exit={check['exit_code']}")
    if 'output' in check and check.get('status') != 'pass':
        excerpt = str(check['output']).replace('\n', ' ')[:220]
        evidence_parts.append(f"`{excerpt}`")
    evidence = '<br>'.join(evidence_parts) if evidence_parts else 'ok'
    lines.append(f"| `{check.get('status')}` | {check.get('name')} | {evidence} |")

lines += ['', '## Routes', '']
for route in routes:
    lines.append(f'- `{route}`')

lines += ['', '## Notes', '', '- This audit is read-only. It does not deploy, mutate records, or run the smoke test.', '- If smoke residue is reported, run cleanup separately with explicit approval: `APPLY_CLEANUP=YES infra/scripts/cleanup_demo_noise.sh`.']
md_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')

print(f"overall={overall}")
print(f"json={json_path}")
print(f"markdown={md_path}")
print(f"summary=pass:{pass_count} warn:{warn_count} fail:{fail_count}")
sys.exit(1 if overall == 'fail' else 0)
PY
