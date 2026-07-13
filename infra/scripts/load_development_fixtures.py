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
REQUIRED_TABLES = {'schema_migrations', 'users', 'auth_tokens', 'development_fixture_batches', 'development_fixture_records'}


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


def load(package_path: Path) -> int:
    app_env = require_allowed_environment()
    package, checksum = read_package(package_path)
    batch_id = package['fixture_id']
    users = package['records']['users']
    password_hash = _hash_password(fixture_password())
    created = 0
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                require_migrated_schema(cur)
                cur.execute('SELECT cleaned_at FROM development_fixture_batches WHERE batch_id = %s', (batch_id,))
                existing_batch = cur.fetchone()
                for user in users:
                    cur.execute('SELECT id FROM users WHERE id = %s', (user['id'],))
                    existing_user = cur.fetchone()
                    cur.execute(
                        'SELECT created_by_batch FROM development_fixture_records WHERE batch_id = %s AND table_name = %s AND record_id = %s',
                        (batch_id, 'users', user['id']),
                    )
                    ownership = cur.fetchone()
                    if existing_user and not (ownership and ownership['created_by_batch'] and existing_batch and existing_batch['cleaned_at'] is None):
                        raise SystemExit(json.dumps({'status': 'fixture-collision', 'record': {'table': 'users', 'id': user['id']}}, indent=2))
                cur.execute(
                    '''
                    INSERT INTO development_fixture_batches(batch_id, fixture_version, environment, execution_context)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (batch_id) DO UPDATE SET
                        fixture_version = EXCLUDED.fixture_version,
                        loaded_at = NOW(),
                        cleaned_at = NULL,
                        environment = EXCLUDED.environment,
                        execution_context = EXCLUDED.execution_context
                    ''',
                    (batch_id, package['fixture_version'], app_env, context('load-development-fixtures')),
                )
                for user in users:
                    cur.execute(
                        '''
                        INSERT INTO users (id, username, full_name, role, password_hash, is_active)
                        VALUES (%s, %s, %s, %s, %s, TRUE)
                        ''',
                        (user['id'], user['username'], user['full_name'], user['role'], password_hash),
                    )
                    created += cur.rowcount
                    cur.execute(
                        '''
                        INSERT INTO development_fixture_records(batch_id, table_name, record_id, created_by_batch)
                        VALUES (%s, 'users', %s, TRUE)
                        ON CONFLICT (batch_id, table_name, record_id) DO UPDATE SET created_by_batch = TRUE, recorded_at = NOW()
                        ''',
                        (batch_id, user['id']),
                    )
    print(json.dumps({'status': 'loaded', 'batch_id': batch_id, 'environment': app_env, 'fixture_users': [u['username'] for u in users], 'created_records': created, 'checksum': checksum}, indent=2))
    return 0


def cleanup(package_path: Path) -> int:
    app_env = require_allowed_environment()
    package, _ = read_package(package_path)
    batch_id = package['fixture_id']
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                require_migrated_schema(cur)
                cur.execute(
                    "SELECT record_id FROM development_fixture_records WHERE batch_id = %s AND table_name = 'users' AND created_by_batch = TRUE",
                    (batch_id,),
                )
                user_ids = [row['record_id'] for row in cur.fetchall()]
                deleted = 0
                if user_ids:
                    cur.execute('DELETE FROM auth_tokens WHERE user_id = ANY(%s)', (user_ids,))
                    cur.execute('DELETE FROM users WHERE id = ANY(%s)', (user_ids,))
                    deleted = cur.rowcount
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
