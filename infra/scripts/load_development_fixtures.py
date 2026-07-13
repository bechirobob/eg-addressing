#!/usr/bin/env python3
"""Explicit non-production development fixture loader for NLI-WO-001."""
from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'services/api'))
from app.data import DEMO_USERS  # noqa: E402
from app.db import _hash_password  # noqa: E402

ALLOWED_ENVS = {'local', 'development', 'dev', 'test'}
FORBIDDEN_ENVS = {'production', 'prod', 'staging', 'controlled-pilot', 'pilot', 'live'}
BATCH_ID = 'development-users-v1'


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
        return psycopg.connect(target)
    return psycopg.connect(**target)


def require_allowed_environment() -> str:
    app_env = os.getenv('APP_ENV', '').strip().lower()
    explicit = os.getenv('EG_ALLOW_DEV_FIXTURES', '').strip().upper() == 'YES'
    if app_env in FORBIDDEN_ENVS or not explicit or app_env not in ALLOWED_ENVS:
        raise SystemExit(json.dumps({'status': 'refused', 'reason': 'development fixtures require EG_ALLOW_DEV_FIXTURES=YES and APP_ENV in allowed non-production set', 'app_env': app_env}))
    return app_env


def context(command: str) -> str:
    return json.dumps({'command': command, 'host': socket.gethostname(), 'actor': os.getenv('USER') or 'unknown', 'timestamp': datetime.now(timezone.utc).isoformat()}, sort_keys=True)


def fixture_password() -> str:
    value = os.getenv('DEVELOPMENT_FIXTURE_PASSWORD')
    if not value or len(value) < 12:
        raise SystemExit('DEVELOPMENT_FIXTURE_PASSWORD of at least 12 characters is required; no source-controlled default passwords are allowed')
    return value


def ensure_batch_table(cur: Any) -> None:
    cur.execute(
        '''
        CREATE TABLE IF NOT EXISTS development_fixture_batches (
            batch_id TEXT PRIMARY KEY,
            fixture_version TEXT NOT NULL,
            environment TEXT NOT NULL,
            loaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            cleaned_at TIMESTAMPTZ,
            execution_context TEXT NOT NULL DEFAULT '{}'
        )
        '''
    )


def load() -> int:
    app_env = require_allowed_environment()
    password_hash = _hash_password(fixture_password())
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                ensure_batch_table(cur)
                for user in DEMO_USERS:
                    cur.execute(
                        '''
                        INSERT INTO users (id, username, full_name, role, password_hash, is_active)
                        VALUES (%s, %s, %s, %s, %s, TRUE)
                        ON CONFLICT (id) DO UPDATE SET
                            username = EXCLUDED.username,
                            full_name = EXCLUDED.full_name,
                            role = EXCLUDED.role,
                            password_hash = users.password_hash,
                            is_active = users.is_active
                        ''',
                        (user['id'], user['username'], user['full_name'], user['role'], password_hash),
                    )
                cur.execute(
                    '''
                    INSERT INTO development_fixture_batches(batch_id, fixture_version, environment, execution_context)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (batch_id) DO UPDATE SET loaded_at = NOW(), cleaned_at = NULL, environment = EXCLUDED.environment, execution_context = EXCLUDED.execution_context
                    ''',
                    (BATCH_ID, '2026-07-13', app_env, context('load-development-fixtures')),
                )
    print(json.dumps({'status': 'loaded', 'batch_id': BATCH_ID, 'environment': app_env, 'fixture_users': [u['username'] for u in DEMO_USERS]}, indent=2))
    return 0


def cleanup() -> int:
    app_env = require_allowed_environment()
    user_ids = [u['id'] for u in DEMO_USERS]
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                ensure_batch_table(cur)
                cur.execute('DELETE FROM auth_tokens WHERE user_id = ANY(%s)', (user_ids,))
                cur.execute('DELETE FROM users WHERE id = ANY(%s)', (user_ids,))
                cur.execute('UPDATE development_fixture_batches SET cleaned_at = NOW(), execution_context = %s WHERE batch_id = %s', (context('cleanup-development-fixtures'), BATCH_ID))
    print(json.dumps({'status': 'cleaned', 'batch_id': BATCH_ID, 'environment': app_env}, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['load', 'cleanup'])
    args = parser.parse_args(argv)
    return load() if args.command == 'load' else cleanup()


if __name__ == '__main__':
    raise SystemExit(main())
