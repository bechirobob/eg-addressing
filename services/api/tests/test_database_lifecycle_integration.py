from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import psycopg
import pytest
from fastapi.testclient import TestClient
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[3]
MIGRATIONS = ROOT / 'infra/migrations'
PYTHON = str(ROOT / 'services/api/.venv/bin/python') if (ROOT / 'services/api/.venv/bin/python').exists() else 'python3'


def pg_env_available() -> bool:
    return bool(os.getenv('POSTGRES_HOST') or os.getenv('DATABASE_URL'))


pytestmark = pytest.mark.skipif(not pg_env_available(), reason='real PostgreSQL/PostGIS env is required')


def admin_target(dbname: str = 'postgres') -> dict[str, str]:
    if os.getenv('DATABASE_URL') and not os.getenv('POSTGRES_HOST'):
        pytest.skip('POSTGRES_HOST-style admin connection is required for disposable DB tests')
    return {
        'host': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'dbname': dbname,
        'user': os.getenv('POSTGRES_USER', 'addressing'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
    }


@pytest.fixture()
def db_name(request):
    name = 'wo001_' + request.node.name.lower().replace('[', '_').replace(']', '_').replace('-', '_')[:40]
    with psycopg.connect(**admin_target('postgres'), autocommit=True) as conn:
        conn.execute(f'DROP DATABASE IF EXISTS {name}')
        conn.execute(f'CREATE DATABASE {name}')
    try:
        yield name
    finally:
        with psycopg.connect(**admin_target('postgres'), autocommit=True) as conn:
            conn.execute(f'DROP DATABASE IF EXISTS {name}')


@pytest.fixture()
def db_env(db_name):
    env = os.environ.copy()
    env.pop('DATABASE_URL', None)
    env.update({
        'POSTGRES_HOST': os.getenv('POSTGRES_HOST', '127.0.0.1'),
        'POSTGRES_PORT': os.getenv('POSTGRES_PORT', '5432'),
        'POSTGRES_DB': db_name,
        'POSTGRES_USER': os.getenv('POSTGRES_USER', 'addressing'),
        'POSTGRES_PASSWORD': os.getenv('POSTGRES_PASSWORD', ''),
        'PYTHONPATH': str(ROOT / 'services/api'),
    })
    return env


def run_cmd(args: list[str], env: dict[str, str], *, check: bool = True, cwd: Path = ROOT) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(args, cwd=cwd, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=90)
    if check and result.returncode != 0:
        raise AssertionError(f"command failed {args}\nstdout={result.stdout}\nstderr={result.stderr}")
    return result


def connect_db(env: dict[str, str]):
    return psycopg.connect(
        host=env['POSTGRES_HOST'],
        port=env['POSTGRES_PORT'],
        dbname=env['POSTGRES_DB'],
        user=env['POSTGRES_USER'],
        password=env.get('POSTGRES_PASSWORD', ''),
        row_factory=dict_row,
    )


def apply_migrations(env: dict[str, str], migrations_dir: Path = MIGRATIONS) -> subprocess.CompletedProcess[str]:
    return run_cmd([PYTHON, 'infra/scripts/migrate.py', 'apply', '--migrations-dir', str(migrations_dir)], env)


def migration_status(env: dict[str, str], migrations_dir: Path = MIGRATIONS, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return run_cmd([PYTHON, 'infra/scripts/migrate.py', 'status', '--migrations-dir', str(migrations_dir)], env, check=check)


def copy_migrations(tmp_path: Path) -> Path:
    dest = tmp_path / 'migrations'
    dest.mkdir()
    for path in sorted(MIGRATIONS.glob('*.sql')):
        shutil.copy2(path, dest / path.name)
    return dest


def ledger_rows(env: dict[str, str]) -> list[dict]:
    with connect_db(env) as conn:
        with conn.cursor() as cur:
            cur.execute('SELECT version, filename, checksum FROM schema_migrations ORDER BY version')
            return [dict(row) for row in cur.fetchall()]


def table_exists(env: dict[str, str], table: str) -> bool:
    with connect_db(env) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s) AS exists", (table,))
            return cur.fetchone()['exists']


def test_empty_postgis_database_migrates_with_full_ledger(db_env):
    result = apply_migrations(db_env)
    assert result.returncode == 0
    rows = ledger_rows(db_env)
    assert [row['version'] for row in rows] == ['000', '001', '002', '003', '004', '005', '006', '007']
    assert all(row['filename'] and row['checksum'] for row in rows)
    with connect_db(db_env) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM pg_extension WHERE extname='postgis'")
            assert cur.fetchone()['count'] == 1
            cur.execute("SELECT COUNT(*) AS count FROM information_schema.tables WHERE table_schema='public' AND table_name IN ('reference_data_load_history','development_fixture_records','address_records')")
            assert cur.fetchone()['count'] == 3


def test_checksum_and_filename_drift_make_status_non_current(db_env, tmp_path):
    migrations = copy_migrations(tmp_path)
    apply_migrations(db_env, migrations)
    (migrations / '001_schema_migration_baseline.sql').write_text('-- changed after apply\nSELECT 1;\n')
    drift = migration_status(db_env, migrations, check=False)
    assert drift.returncode == 1
    assert 'checksum-mismatch' in drift.stdout
    with connect_db(db_env) as conn:
        conn.execute("UPDATE schema_migrations SET filename = '001_wrong_name.sql' WHERE version = '001'")
        conn.commit()
    filename_drift = migration_status(db_env, MIGRATIONS, check=False)
    assert filename_drift.returncode == 1
    assert 'filename_mismatch_versions' in filename_drift.stdout


def test_failed_migration_rolls_back_and_does_not_continue(db_env, tmp_path):
    migrations = tmp_path / 'migrations'
    migrations.mkdir()
    (migrations / '000_create_good.sql').write_text('CREATE TABLE good_table(id integer PRIMARY KEY);')
    (migrations / '001_bad.sql').write_text('CREATE TABLE bad_table(id integer PRIMARY KEY); SELECT * FROM missing_table;')
    (migrations / '002_later.sql').write_text('CREATE TABLE later_table(id integer PRIMARY KEY);')
    result = run_cmd([PYTHON, 'infra/scripts/migrate.py', 'apply', '--migrations-dir', str(migrations)], db_env, check=False)
    assert result.returncode == 1
    assert table_exists(db_env, 'good_table') is True
    assert table_exists(db_env, 'bad_table') is False
    assert table_exists(db_env, 'later_table') is False
    assert [row['version'] for row in ledger_rows(db_env)] == ['000']


def test_concurrent_migration_execution_uses_single_ledger(db_env, tmp_path):
    migrations = tmp_path / 'migrations'
    migrations.mkdir()
    (migrations / '000_slow.sql').write_text('SELECT pg_sleep(1); CREATE TABLE concurrency_probe(id integer PRIMARY KEY);')
    args = [PYTHON, 'infra/scripts/migrate.py', 'apply', '--migrations-dir', str(migrations)]
    first = subprocess.Popen(args, cwd=ROOT, env=db_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(0.1)
    second = subprocess.Popen(args, cwd=ROOT, env=db_env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out1, err1 = first.communicate(timeout=30)
    out2, err2 = second.communicate(timeout=30)
    assert first.returncode == 0, err1
    assert second.returncode == 0, err2
    assert [row['version'] for row in ledger_rows(db_env)] == ['000']
    assert ('APPLY 000_slow.sql' in out1) ^ ('APPLY 000_slow.sql' in out2)


def test_api_startup_does_not_change_schema_or_rows(db_env, monkeypatch):
    apply_migrations(db_env)
    before = fingerprint(db_env)
    monkeypatch.setenv('POSTGRES_HOST', db_env['POSTGRES_HOST'])
    monkeypatch.setenv('POSTGRES_PORT', db_env['POSTGRES_PORT'])
    monkeypatch.setenv('POSTGRES_DB', db_env['POSTGRES_DB'])
    monkeypatch.setenv('POSTGRES_USER', db_env['POSTGRES_USER'])
    monkeypatch.setenv('POSTGRES_PASSWORD', db_env.get('POSTGRES_PASSWORD', ''))
    monkeypatch.delenv('DATABASE_URL', raising=False)
    from app.main import app
    with TestClient(app) as client:
        response = client.get('/api/v1/health')
    assert response.status_code == 200
    assert fingerprint(db_env) == before


def fingerprint(env: dict[str, str]) -> dict[str, int]:
    with connect_db(env) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS count FROM information_schema.tables WHERE table_schema='public'")
            tables = cur.fetchone()['count']
            counts = {'tables': tables}
            for table in ['users', 'auth_tokens', 'provinces', 'admin_units', 'schema_migrations']:
                if table_exists(env, table):
                    cur.execute(f'SELECT COUNT(*) AS count FROM {table}')
                    counts[table] = cur.fetchone()['count']
            return counts


def test_pending_migration_readiness_does_not_auto_apply(db_env, tmp_path, monkeypatch):
    migrations = copy_migrations(tmp_path)
    (migrations / '007_lifecycle_metadata_hardening.sql').unlink()
    apply_migrations(db_env, migrations)
    monkeypatch.setenv('MIGRATIONS_DIR', str(MIGRATIONS))
    monkeypatch.setenv('POSTGRES_HOST', db_env['POSTGRES_HOST'])
    monkeypatch.setenv('POSTGRES_PORT', db_env['POSTGRES_PORT'])
    monkeypatch.setenv('POSTGRES_DB', db_env['POSTGRES_DB'])
    monkeypatch.setenv('POSTGRES_USER', db_env['POSTGRES_USER'])
    monkeypatch.setenv('POSTGRES_PASSWORD', db_env.get('POSTGRES_PASSWORD', ''))
    monkeypatch.delenv('DATABASE_URL', raising=False)
    from app.ops_status import migration_status as app_migration_status
    from app.main import app
    before = [row['version'] for row in ledger_rows(db_env)]
    status = app_migration_status()
    assert status['status'] == 'pending'
    assert '007' in status['pending_versions']
    with TestClient(app) as client:
        assert client.get('/api/v1/health').status_code == 200
    assert [row['version'] for row in ledger_rows(db_env)] == before


def test_credentials_and_sessions_survive_migrate_and_reference_load(db_env):
    apply_migrations(db_env)
    with connect_db(db_env) as conn:
        conn.execute("INSERT INTO users(id, username, full_name, role, password_hash, is_active) VALUES ('u-preserve','preserve','Preserve User','admin','hash-before', FALSE)")
        conn.execute("INSERT INTO auth_tokens(token, user_id, expires_at, last_seen_at) VALUES ('tok-preserve','u-preserve', NOW() + INTERVAL '1 hour', NOW())")
        conn.commit()
    apply_migrations(db_env)
    run_cmd([PYTHON, 'infra/scripts/load_reference_data.py', 'load'], db_env)
    with connect_db(db_env) as conn:
        cur = conn.execute("SELECT password_hash, role, is_active FROM users WHERE id='u-preserve'")
        assert dict(cur.fetchone()) == {'password_hash': 'hash-before', 'role': 'admin', 'is_active': False}
        cur = conn.execute("SELECT COUNT(*) AS count FROM auth_tokens WHERE token='tok-preserve' AND user_id='u-preserve'")
        assert cur.fetchone()['count'] == 1


def test_existing_pilot_transition_preserves_counts_and_rejects_drift(db_env, tmp_path):
    # Simulate a pre-WO database with current operational tables but no ledger rows.
    schema_sql = (MIGRATIONS / '000_current_operational_schema.sql').read_text()
    with connect_db(db_env) as conn:
        conn.execute(schema_sql)
        conn.execute("INSERT INTO provinces(code, name) VALUES ('BN','Bioko Norte')")
        conn.execute("INSERT INTO users(id, username, full_name, role, password_hash) VALUES ('legacy-admin','legacy','Legacy Admin','admin','legacy-hash')")
        conn.commit()
    before = fingerprint(db_env)
    result = run_cmd([PYTHON, 'infra/scripts/migrate.py', 'transition-pilot'], db_env)
    assert result.returncode == 0
    after = fingerprint(db_env)
    assert after['users'] == before['users']
    assert after['provinces'] == before['provinces']
    assert [row['version'] for row in ledger_rows(db_env)] == ['000', '001', '002', '003', '004', '005', '006', '007']

    drift_db = db_env.copy()
    drift_db['POSTGRES_DB'] = db_env['POSTGRES_DB']
    with connect_db(drift_db) as conn:
        conn.execute('ALTER TABLE users DROP COLUMN password_hash')
        conn.commit()
    failed = run_cmd([PYTHON, 'infra/scripts/migrate.py', 'transition-pilot'], drift_db, check=False)
    assert failed.returncode == 2
    assert 'incompatible-source-state' in failed.stdout


def test_reference_data_missing_migrations_status_and_drift(db_env, tmp_path):
    status_missing = run_cmd([PYTHON, 'infra/scripts/load_reference_data.py', 'status'], db_env, check=False)
    assert status_missing.returncode != 0
    assert 'missing-migrations' in (status_missing.stdout + status_missing.stderr)
    assert table_exists(db_env, 'reference_data_loads') is False
    apply_migrations(db_env)
    first = run_cmd([PYTHON, 'infra/scripts/load_reference_data.py', 'load'], db_env)
    second = run_cmd([PYTHON, 'infra/scripts/load_reference_data.py', 'load'], db_env)
    assert json.loads(first.stdout)['changed_rows'] > 0
    assert json.loads(second.stdout)['changed_rows'] == 0
    package = json.loads((ROOT / 'infra/reference-data/eg-admin-units-v1.json').read_text())
    package['records']['provinces'][0]['name'] = 'Changed Province Name'
    changed = tmp_path / 'eg-admin-units-v1-drift.json'
    changed.write_text(json.dumps(package))
    drift = run_cmd([PYTHON, 'infra/scripts/load_reference_data.py', 'status', '--package', str(changed)], db_env, check=False)
    assert drift.returncode == 1
    assert 'drift' in drift.stdout
    load_drift = run_cmd([PYTHON, 'infra/scripts/load_reference_data.py', 'load', '--package', str(changed)], db_env, check=False)
    assert load_drift.returncode != 0
    assert 'package-drift' in (load_drift.stdout + load_drift.stderr)


def test_fixture_missing_migrations_collision_ownership_and_cleanup(db_env):
    env = db_env | {'APP_ENV': 'test', 'EG_ALLOW_DEV_FIXTURES': 'YES', 'DEVELOPMENT_FIXTURE_PASSWORD': 'controlled-fixture-password'}
    missing = run_cmd([PYTHON, 'infra/scripts/load_development_fixtures.py', 'load'], env, check=False)
    assert missing.returncode != 0
    assert 'missing-migrations' in (missing.stdout + missing.stderr)
    assert table_exists(db_env, 'development_fixture_batches') is False
    apply_migrations(db_env)
    with connect_db(db_env) as conn:
        conn.execute("INSERT INTO users(id, username, full_name, role, password_hash) VALUES ('user-admin','real-admin','Real Admin','admin','real-hash')")
        conn.commit()
    collision = run_cmd([PYTHON, 'infra/scripts/load_development_fixtures.py', 'load'], env, check=False)
    assert collision.returncode != 0
    assert 'fixture-collision' in (collision.stdout + collision.stderr)
    cleanup_collision = run_cmd([PYTHON, 'infra/scripts/load_development_fixtures.py', 'cleanup'], env)
    assert json.loads(cleanup_collision.stdout)['deleted_records'] == 0
    with connect_db(db_env) as conn:
        cur = conn.execute("SELECT username, password_hash FROM users WHERE id='user-admin'")
        assert dict(cur.fetchone()) == {'username': 'real-admin', 'password_hash': 'real-hash'}


def test_fixture_owned_records_cleanup(db_env):
    apply_migrations(db_env)
    env = db_env | {'APP_ENV': 'test', 'EG_ALLOW_DEV_FIXTURES': 'YES', 'DEVELOPMENT_FIXTURE_PASSWORD': 'controlled-fixture-password'}
    loaded = run_cmd([PYTHON, 'infra/scripts/load_development_fixtures.py', 'load'], env)
    assert json.loads(loaded.stdout)['created_records'] == 4
    with connect_db(db_env) as conn:
        cur = conn.execute("SELECT COUNT(*) AS count FROM development_fixture_records WHERE batch_id='development-users-v1'")
        assert cur.fetchone()['count'] == 4
    cleaned = run_cmd([PYTHON, 'infra/scripts/load_development_fixtures.py', 'cleanup'], env)
    assert json.loads(cleaned.stdout)['deleted_records'] == 4
    with connect_db(db_env) as conn:
        cur = conn.execute("SELECT COUNT(*) AS count FROM users WHERE id LIKE 'user-%'")
        assert cur.fetchone()['count'] == 0
