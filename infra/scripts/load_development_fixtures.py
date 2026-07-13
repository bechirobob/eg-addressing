#!/usr/bin/env python3
"""Explicit non-production development fixture loader for NLI-WO-001."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/api'))
from app.db import _hash_password  # noqa: E402

DEFAULT_PACKAGE = ROOT / 'infra/fixtures/development-fixtures-v1.json'
ALLOWED_ENVS = {'local', 'development', 'dev', 'test'}
FORBIDDEN_ENVS = {'production', 'prod', 'staging', 'controlled-pilot', 'pilot', 'live'}
REQUIRED_TABLES = {
    'schema_migrations', 'users', 'auth_tokens', 'development_fixture_batches', 'development_fixture_records',
    'territories', 'roads', 'buildings', 'addresses', 'field_assignments',
}
LOAD_ORDER = ['users', 'territories', 'roads', 'buildings', 'addresses', 'field_assignments']
CLEANUP_ORDER = ['field_assignments', 'addresses', 'buildings', 'roads', 'territories', 'users']
ID_COLUMNS = {'users': 'id', 'territories': 'id', 'roads': 'id', 'buildings': 'id', 'addresses': 'id', 'field_assignments': 'assignment_id'}


def database_target() -> str | dict[str, Any]:
    value = os.getenv('DATABASE_URL')
    if value:
        return value.replace('postgresql+psycopg://', 'postgresql://', 1)
    host = os.getenv('POSTGRES_HOST')
    if not host:
        raise SystemExit('DATABASE_URL or POSTGRES_HOST is required for fixture commands')
    return {
        'host': host,
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'dbname': os.getenv('POSTGRES_DB', 'addressing'),
        'user': os.getenv('POSTGRES_USER', 'addressing'),
        'password': os.getenv('POSTGRES_PASSWORD', ''),
    }


def connect_database() -> psycopg.Connection:
    target = database_target()
    if isinstance(target, str):
        return psycopg.connect(target, row_factory=dict_row)
    return psycopg.connect(row_factory=dict_row, **target)


def require_allowed_environment() -> str:
    app_env = os.getenv('APP_ENV', '').strip().lower()
    explicit = os.getenv('EG_ALLOW_DEV_FIXTURES', '').strip().upper() == 'YES'
    if app_env in FORBIDDEN_ENVS or not explicit or app_env not in ALLOWED_ENVS:
        raise SystemExit(json.dumps({'status': 'refused', 'reason': 'development fixtures require EG_ALLOW_DEV_FIXTURES=YES and APP_ENV in allowed non-production set', 'app_env': app_env}))
    return app_env


def existing_tables(cur: Any) -> set[str]:
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    return {row['table_name'] for row in cur.fetchall()}


def require_migrated_schema(cur: Any) -> None:
    missing = sorted(REQUIRED_TABLES - existing_tables(cur))
    if missing:
        raise SystemExit(json.dumps({'status': 'missing-migrations', 'missing_tables': missing}, indent=2))


def context(command: str) -> str:
    return json.dumps({'command': command, 'host': socket.gethostname(), 'actor': os.getenv('USER') or 'unknown', 'timestamp': datetime.now(timezone.utc).isoformat()}, sort_keys=True)


def fixture_password() -> str:
    value = os.getenv('DEVELOPMENT_FIXTURE_PASSWORD')
    if not value or len(value) < 12:
        raise SystemExit('DEVELOPMENT_FIXTURE_PASSWORD of at least 12 characters is required; no source-controlled default passwords are allowed')
    return value


def read_package(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    return json.loads(raw.decode('utf-8')), hashlib.sha256(raw).hexdigest()


def record_id(table: str, record: dict[str, Any]) -> str:
    return str(record[ID_COLUMNS[table]])


def assert_no_non_owned_collision(cur: Any, batch_id: str, table: str, rid: str) -> bool:
    id_column = ID_COLUMNS[table]
    cur.execute(f'SELECT {id_column} FROM {table} WHERE {id_column} = %s', (rid,))
    existing = cur.fetchone()
    cur.execute(
        'SELECT created_by_batch FROM development_fixture_records WHERE batch_id = %s AND table_name = %s AND record_id = %s',
        (batch_id, table, rid),
    )
    ownership = cur.fetchone()
    cur.execute('SELECT cleaned_at FROM development_fixture_batches WHERE batch_id = %s', (batch_id,))
    batch = cur.fetchone()
    owned_active = bool(ownership and ownership['created_by_batch'] and batch and batch['cleaned_at'] is None)
    if existing and not owned_active:
        raise SystemExit(json.dumps({'status': 'fixture-collision', 'record': {'table': table, 'id': rid}}, indent=2))
    return bool(existing)


def mark_owned(cur: Any, batch_id: str, table: str, rid: str) -> None:
    cur.execute(
        '''
        INSERT INTO development_fixture_records(batch_id, table_name, record_id, created_by_batch)
        VALUES (%s, %s, %s, TRUE)
        ON CONFLICT (batch_id, table_name, record_id) DO UPDATE SET created_by_batch = TRUE, recorded_at = NOW()
        ''',
        (batch_id, table, rid),
    )


def upsert_record(cur: Any, table: str, record: dict[str, Any], password_hash: str | None = None) -> None:
    if table == 'users':
        cur.execute(
            '''
            INSERT INTO users (id, username, full_name, role, password_hash, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
            ON CONFLICT (id) DO UPDATE SET username=EXCLUDED.username, full_name=EXCLUDED.full_name, role=EXCLUDED.role, password_hash=EXCLUDED.password_hash, is_active=TRUE
            ''',
            (record['id'], record['username'], record['full_name'], record['role'], password_hash),
        )
    elif table == 'territories':
        cur.execute(
            '''
            INSERT INTO territories (id, name, province_code, admin_unit_id, type, readiness)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, province_code=EXCLUDED.province_code, admin_unit_id=EXCLUDED.admin_unit_id, type=EXCLUDED.type, readiness=EXCLUDED.readiness, is_archived=FALSE
            ''',
            (record['id'], record['name'], record['province_code'], record.get('admin_unit_id'), record['type'], record['readiness']),
        )
    elif table == 'roads':
        cur.execute(
            '''
            INSERT INTO roads (id, name, territory_id, status, length_km)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET name=EXCLUDED.name, territory_id=EXCLUDED.territory_id, status=EXCLUDED.status, length_km=EXCLUDED.length_km, is_archived=FALSE
            ''',
            (record['id'], record['name'], record['territory_id'], record['status'], record['length_km']),
        )
    elif table == 'buildings':
        cur.execute(
            '''
            INSERT INTO buildings (id, label, territory_id, road_id, status, usage)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET label=EXCLUDED.label, territory_id=EXCLUDED.territory_id, road_id=EXCLUDED.road_id, status=EXCLUDED.status, usage=EXCLUDED.usage, is_archived=FALSE
            ''',
            (record['id'], record['label'], record['territory_id'], record['road_id'], record['status'], record['usage']),
        )
    elif table == 'addresses':
        cur.execute(
            '''
            INSERT INTO addresses (id, formatted, territory_id, road_id, building_id, province_code, public_code, issuance_method, source, verification_status, status, publication_state)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET formatted=EXCLUDED.formatted, territory_id=EXCLUDED.territory_id, road_id=EXCLUDED.road_id, building_id=EXCLUDED.building_id, province_code=EXCLUDED.province_code, public_code=EXCLUDED.public_code, issuance_method=EXCLUDED.issuance_method, source=EXCLUDED.source, verification_status=EXCLUDED.verification_status, status=EXCLUDED.status, publication_state=EXCLUDED.publication_state, is_archived=FALSE
            ''',
            (record['id'], record['formatted'], record['territory_id'], record['road_id'], record['building_id'], record['province_code'], record.get('public_code'), record.get('issuance_method', 'manual'), record.get('source', 'admin-portal'), record.get('verification_status', 'provisional'), record['status'], record['publication_state']),
        )
    elif table == 'field_assignments':
        cur.execute(
            '''
            INSERT INTO field_assignments (assignment_id, territory_id, territory, task, team, priority)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (assignment_id) DO UPDATE SET territory_id=EXCLUDED.territory_id, territory=EXCLUDED.territory, task=EXCLUDED.task, team=EXCLUDED.team, priority=EXCLUDED.priority
            ''',
            (record['assignment_id'], record['territory_id'], record['territory'], record['task'], record['team'], record['priority']),
        )
    else:
        raise ValueError(f'Unsupported fixture table: {table}')


def load(package_path: Path) -> int:
    app_env = require_allowed_environment()
    package, checksum = read_package(package_path)
    batch_id = package['fixture_id']
    records = package['records']
    password_hash = _hash_password(fixture_password())
    created = 0
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                require_migrated_schema(cur)
                for table in LOAD_ORDER:
                    for record in records.get(table, []):
                        if not assert_no_non_owned_collision(cur, batch_id, table, record_id(table, record)):
                            created += 1
                cur.execute(
                    '''
                    INSERT INTO development_fixture_batches(batch_id, fixture_version, environment, execution_context)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (batch_id) DO UPDATE SET fixture_version=EXCLUDED.fixture_version, loaded_at=NOW(), cleaned_at=NULL, environment=EXCLUDED.environment, execution_context=EXCLUDED.execution_context
                    ''',
                    (batch_id, package['fixture_version'], app_env, context('load-development-fixtures')),
                )
                for table in LOAD_ORDER:
                    for record in records.get(table, []):
                        rid = record_id(table, record)
                        upsert_record(cur, table, record, password_hash)
                        mark_owned(cur, batch_id, table, rid)
    print(json.dumps({'status': 'loaded', 'batch_id': batch_id, 'environment': app_env, 'created_records': created, 'checksum': checksum}, indent=2))
    return 0


def cleanup(package_path: Path) -> int:
    app_env = require_allowed_environment()
    package, _ = read_package(package_path)
    batch_id = package['fixture_id']
    deleted = 0
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                require_migrated_schema(cur)
                for table in CLEANUP_ORDER:
                    id_column = ID_COLUMNS[table]
                    cur.execute(
                        'SELECT record_id FROM development_fixture_records WHERE batch_id = %s AND table_name = %s AND created_by_batch = TRUE',
                        (batch_id, table),
                    )
                    ids = [row['record_id'] for row in cur.fetchall()]
                    if ids:
                        if table == 'users':
                            cur.execute('DELETE FROM auth_tokens WHERE user_id = ANY(%s)', (ids,))
                        cur.execute(f'DELETE FROM {table} WHERE {id_column} = ANY(%s)', (ids,))
                        deleted += cur.rowcount
                cur.execute('DELETE FROM development_fixture_records WHERE batch_id = %s', (batch_id,))
                cur.execute('UPDATE development_fixture_batches SET cleaned_at = NOW(), execution_context = %s WHERE batch_id = %s', (context('cleanup-development-fixtures'), batch_id))
    print(json.dumps({'status': 'cleaned', 'batch_id': batch_id, 'environment': app_env, 'deleted_records': deleted}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['load', 'cleanup'])
    parser.add_argument('--package', default=str(DEFAULT_PACKAGE))
    args = parser.parse_args(argv)
    return load(Path(args.package)) if args.command == 'load' else cleanup(Path(args.package))


if __name__ == '__main__':
    raise SystemExit(main())
