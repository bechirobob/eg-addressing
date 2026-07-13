#!/usr/bin/env python3
"""Controlled PostgreSQL/PostGIS migration runner for NLI-WO-001."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import socket
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MIGRATIONS_DIR = ROOT / 'infra' / 'migrations'
LOCK_KEY = 2026071301
VALID_NAME = re.compile(r'^(?P<version>[0-9]{3})_[A-Za-z0-9_]+\.sql$')
REQUIRED_TRANSITION_TABLES = {
    'provinces', 'admin_units', 'users', 'auth_tokens', 'audit_logs', 'territories',
    'roads', 'buildings', 'addresses', 'address_points', 'address_corrections',
    'citizen_geotag_submissions', 'address_records', 'address_record_events',
    'field_assignments', 'field_submissions', 'import_jobs', 'import_rows',
    'publication_packs', 'publication_pack_addresses',
}

REQUIRED_TRANSITION_COLUMNS = {
    'provinces': {'code', 'name'},
    'admin_units': {'id', 'level', 'code', 'parent_id', 'province_code', 'name_es', 'name_en', 'status', 'sort_order'},
    'users': {'id', 'username', 'full_name', 'role', 'password_hash', 'is_active'},
    'auth_tokens': {'token', 'user_id', 'created_at', 'expires_at', 'revoked_at', 'last_seen_at'},
    'territories': {'id', 'name', 'province_code', 'admin_unit_id', 'type', 'readiness', 'is_archived'},
    'roads': {'id', 'name', 'territory_id', 'status', 'length_km', 'spatial_evidence', 'is_archived'},
    'buildings': {'id', 'label', 'territory_id', 'road_id', 'status', 'usage', 'spatial_evidence', 'is_archived'},
    'addresses': {'id', 'formatted', 'territory_id', 'road_id', 'building_id', 'province_code', 'status', 'publication_state', 'is_archived'},
    'address_records': {'id', 'address_code', 'address_label', 'status', 'publication_state', 'latitude', 'longitude'},
    'citizen_geotag_submissions': {'id', 'address_label', 'latitude', 'longitude', 'grid_code', 'status'},
    'field_assignments': {'assignment_id', 'territory_id', 'territory', 'task', 'team', 'priority'},
    'field_submissions': {'id', 'territory_id', 'submission_type', 'candidate_name', 'candidate_status', 'review_status'},
    'import_jobs': {'id', 'name', 'source_name', 'status'},
    'import_rows': {'job_id', 'row_number', 'territory_id', 'validation_status'},
    'publication_packs': {'id', 'name', 'status', 'audience'},
    'publication_pack_addresses': {'publication_pack_id', 'address_id'},
}


@dataclass(frozen=True)
class Migration:
    version: str
    filename: str
    path: Path
    checksum: str


def database_target() -> str | dict[str, Any]:
    value = os.getenv('DATABASE_URL')
    if value:
        return value.replace('postgresql+psycopg://', 'postgresql://', 1)
    host = os.getenv('POSTGRES_HOST')
    if not host:
        raise SystemExit('DATABASE_URL or POSTGRES_HOST is required for controlled migration commands')
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



def execution_context(command: str) -> str:
    payload = {
        'command': command,
        'host': socket.gethostname(),
        'actor': os.getenv('MIGRATION_ACTOR') or os.getenv('USER') or 'unknown',
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
    return json.dumps(payload, sort_keys=True)


def load_migrations(migrations_dir: Path) -> list[Migration]:
    if not migrations_dir.exists():
        raise SystemExit(f'Missing migrations dir: {migrations_dir}')
    migrations: list[Migration] = []
    seen: set[str] = set()
    for path in sorted(migrations_dir.glob('*.sql')):
        match = VALID_NAME.match(path.name)
        if not match:
            raise SystemExit(f'Invalid migration filename: {path.name}')
        version = match.group('version')
        if version in seen:
            raise SystemExit(f'Duplicate migration version: {version}')
        seen.add(version)
        migrations.append(Migration(version, path.name, path, hashlib.sha256(path.read_bytes()).hexdigest()))
    return migrations


def ensure_ledger(conn: psycopg.Connection) -> None:
    with conn.cursor() as cur:
        cur.execute(
            '''
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                checksum TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                execution_context TEXT NOT NULL DEFAULT '{}'
            )
            '''
        )
        cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS filename TEXT NOT NULL DEFAULT 'unknown.sql'")
        cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS checksum TEXT NOT NULL DEFAULT ''")
        cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()")
        cur.execute("ALTER TABLE schema_migrations ADD COLUMN IF NOT EXISTS execution_context TEXT NOT NULL DEFAULT '{}'")
    conn.commit()


def applied_rows(conn: psycopg.Connection) -> dict[str, dict[str, Any]]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'schema_migrations'
            ) AS exists
            """
        )
        if not cur.fetchone()['exists']:
            return {}
        cur.execute('SELECT version, filename, checksum, applied_at, execution_context FROM schema_migrations ORDER BY version')
        return {row['version']: dict(row) for row in cur.fetchall()}


def compute_status(conn: psycopg.Connection, migrations: list[Migration]) -> dict[str, Any]:
    applied = applied_rows(conn)
    expected = {m.version: m for m in migrations}
    pending = [m for m in migrations if m.version not in applied]
    mismatched = [
        m for m in migrations
        if m.version in applied
        and (applied[m.version]['checksum'] != m.checksum or applied[m.version]['filename'] != m.filename)
    ]
    unknown = [version for version in applied if version not in expected]
    if mismatched:
        state = 'checksum-mismatch'
    elif unknown:
        state = 'unknown-ledger-state'
    elif pending:
        state = 'pending'
    else:
        state = 'current'
    return {
        'status': state,
        'applied_count': len(applied),
        'expected_count': len(migrations),
        'pending_count': len(pending),
        'pending_versions': [m.version for m in pending],
        'mismatch_versions': [m.version for m in mismatched],
        'filename_mismatch_versions': [m.version for m in mismatched if m.version in applied and applied[m.version]['filename'] != m.filename],
        'unknown_versions': unknown,
        'latest_version': max(applied) if applied else None,
    }


def print_status(status: dict[str, Any]) -> None:
    print(json.dumps(status, indent=2, sort_keys=True, default=str))


def apply_migrations(conn: psycopg.Connection, migrations: list[Migration], command: str, *, lock_already_held: bool = False) -> int:
    ensure_ledger(conn)
    if not lock_already_held:
        with conn.cursor() as cur:
            cur.execute('SELECT pg_advisory_lock(%s)', (LOCK_KEY,))
    try:
        status = compute_status(conn, migrations)
        if status['mismatch_versions']:
            print_status(status | {'error': 'checksum-mismatch'})
            return 2
        if status['unknown_versions']:
            print_status(status | {'error': 'unknown-ledger-state'})
            return 2
        applied = applied_rows(conn)
        for migration in migrations:
            row = applied.get(migration.version)
            if row:
                if row['checksum'] != migration.checksum or row['filename'] != migration.filename:
                    print(f'ledger-mismatch {migration.filename}', file=sys.stderr)
                    return 2
                print(f'SKIP {migration.filename}')
                continue
            print(f'APPLY {migration.filename}')
            try:
                with conn.transaction():
                    with conn.cursor() as cur:
                        cur.execute(migration.path.read_text(encoding='utf-8'))
                        cur.execute(
                            '''
                            INSERT INTO schema_migrations(version, filename, checksum, execution_context)
                            VALUES (%s, %s, %s, %s)
                            ''',
                            (migration.version, migration.filename, migration.checksum, execution_context(command)),
                        )
            except Exception as exc:
                print(f'FAILED {migration.filename}: {exc}', file=sys.stderr)
                return 1
            applied[migration.version] = {
                'version': migration.version,
                'filename': migration.filename,
                'checksum': migration.checksum,
            }
        print_status(compute_status(conn, migrations))
        return 0
    finally:
        if not lock_already_held:
            with conn.cursor() as cur:
                cur.execute('SELECT pg_advisory_unlock(%s)', (LOCK_KEY,))
            conn.commit()


def table_names(conn: psycopg.Connection) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        return {row['table_name'] for row in cur.fetchall()}


def table_columns(conn: psycopg.Connection) -> dict[str, set[str]]:
    with conn.cursor() as cur:
        cur.execute("SELECT table_name, column_name FROM information_schema.columns WHERE table_schema = 'public'")
        result: dict[str, set[str]] = {}
        for row in cur.fetchall():
            result.setdefault(row['table_name'], set()).add(row['column_name'])
        return result


def transition_compatibility_errors(conn: psycopg.Connection) -> dict[str, Any]:
    present = table_names(conn)
    missing_tables = sorted(REQUIRED_TRANSITION_TABLES - present)
    columns = table_columns(conn)
    missing_columns = {
        table: sorted(required - columns.get(table, set()))
        for table, required in REQUIRED_TRANSITION_COLUMNS.items()
        if required - columns.get(table, set())
    }
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM pg_extension WHERE extname = 'postgis'")
        postgis_extensions = cur.fetchone()['count']
        invalid_users = 0
        if not (REQUIRED_TRANSITION_COLUMNS['users'] - columns.get('users', set())):
            cur.execute("SELECT COUNT(*) AS count FROM users WHERE id IS NULL OR username IS NULL OR password_hash IS NULL")
            invalid_users = cur.fetchone()['count']
    errors: dict[str, Any] = {'postgis_extensions_before_transition': postgis_extensions}
    if missing_tables:
        errors['missing_tables'] = missing_tables
    if missing_columns:
        errors['missing_columns'] = missing_columns
    if invalid_users:
        errors['invalid_users'] = invalid_users
    return errors


def transition_pilot(conn: psycopg.Connection, migrations: list[Migration], command: str) -> int:
    ensure_ledger(conn)
    with conn.cursor() as cur:
        cur.execute('SELECT pg_advisory_lock(%s)', (LOCK_KEY,))
    try:
        compatibility = transition_compatibility_errors(conn)
        blocking = {k: v for k, v in compatibility.items() if k != 'postgis_extensions_before_transition' and v}
        if blocking:
            print_status({'status': 'incompatible-source-state', **compatibility})
            return 2
        status = compute_status(conn, migrations)
        if status['mismatch_versions'] or status['unknown_versions']:
            print_status(status)
            return 2
        return apply_migrations(conn, migrations, command, lock_already_held=True)
    finally:
        with conn.cursor() as cur:
            cur.execute('SELECT pg_advisory_unlock(%s)', (LOCK_KEY,))
        conn.commit()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Controlled NLI migration lifecycle runner')
    parser.add_argument('command', choices=['status', 'apply', 'transition-pilot'])
    parser.add_argument('--migrations-dir', default=os.getenv('MIGRATIONS_DIR', str(DEFAULT_MIGRATIONS_DIR)))
    parser.add_argument('--database-url', default=None)
    args = parser.parse_args(argv)
    migrations = load_migrations(Path(args.migrations_dir))
    if args.database_url:
        os.environ['DATABASE_URL'] = args.database_url
    with connect_database() as conn:
        if args.command == 'status':
            print_status(compute_status(conn, migrations))
            status = compute_status(conn, migrations)['status']
            return 0 if status == 'current' else 1
        if args.command == 'apply':
            return apply_migrations(conn, migrations, 'apply')
        if args.command == 'transition-pilot':
            return transition_pilot(conn, migrations, 'transition-pilot')
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
