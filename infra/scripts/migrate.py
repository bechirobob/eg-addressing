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

from migration_state import evaluate_migration_state

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

REQUIRED_TRANSITION_COLUMN_SPECS = {
    ('users', 'id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('users', 'password_hash'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('auth_tokens', 'user_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('territories', 'province_code'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('roads', 'territory_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('buildings', 'road_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('addresses', 'building_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('address_records', 'latitude'): {'udt_name': 'float8', 'is_nullable': 'NO'},
    ('address_records', 'longitude'): {'udt_name': 'float8', 'is_nullable': 'NO'},
    ('address_record_events', 'address_record_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('field_assignments', 'territory_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('field_submissions', 'territory_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('import_rows', 'job_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
    ('publication_pack_addresses', 'publication_pack_id'): {'udt_name': 'text', 'is_nullable': 'NO'},
}

REQUIRED_TRANSITION_INDEXES = {
    'idx_addresses_public_code_unique',
    'idx_address_records_code',
    'idx_address_records_active_status_updated',
    'idx_address_record_events_record_created',
    'idx_citizen_geotag_status_created_at',
}

REQUIRED_TRANSITION_CONSTRAINTS = {
    'users_pkey',
    'users_username_key',
    'auth_tokens_user_id_fkey',
    'roads_territory_id_fkey',
    'buildings_road_id_fkey',
    'addresses_building_id_fkey',
    'address_records_source_submission_id_fkey',
    'address_record_events_address_record_id_fkey',
    'field_submissions_assignment_id_fkey',
    'publication_pack_addresses_publication_pack_id_fkey',
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
    expected = [{'version': m.version, 'filename': m.filename, 'checksum': m.checksum} for m in migrations]
    return evaluate_migration_state(conn, expected)


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


def table_columns(conn: psycopg.Connection) -> dict[str, dict[str, dict[str, Any]]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT table_name, column_name, udt_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
        )
        result: dict[str, dict[str, dict[str, Any]]] = {}
        for row in cur.fetchall():
            result.setdefault(row['table_name'], {})[row['column_name']] = dict(row)
        return result


def index_names(conn: psycopg.Connection) -> set[str]:
    with conn.cursor() as cur:
        cur.execute("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
        return {row['indexname'] for row in cur.fetchall()}


def constraint_names(conn: psycopg.Connection) -> set[str]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT con.conname AS constraint_name
            FROM pg_constraint con
            JOIN pg_class c ON c.oid = con.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
            """
        )
        return {row['constraint_name'] for row in cur.fetchall()}


def transition_compatibility_errors(conn: psycopg.Connection) -> dict[str, Any]:
    present = table_names(conn)
    missing_tables = sorted(REQUIRED_TRANSITION_TABLES - present)
    columns = table_columns(conn)
    missing_columns = {
        table: sorted(required - set(columns.get(table, {}).keys()))
        for table, required in REQUIRED_TRANSITION_COLUMNS.items()
        if required - set(columns.get(table, {}).keys())
    }
    type_mismatches: dict[str, dict[str, Any]] = {}
    for (table, column), expected in REQUIRED_TRANSITION_COLUMN_SPECS.items():
        actual = columns.get(table, {}).get(column)
        if not actual:
            continue
        problems = {key: {'expected': value, 'actual': actual.get(key)} for key, value in expected.items() if actual.get(key) != value}
        if problems:
            type_mismatches[f'{table}.{column}'] = problems
    missing_indexes = sorted(REQUIRED_TRANSITION_INDEXES - index_names(conn))
    missing_constraints = sorted(REQUIRED_TRANSITION_CONSTRAINTS - constraint_names(conn))
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) AS count FROM pg_extension WHERE extname = 'postgis'")
        postgis_extensions = cur.fetchone()['count']
        invalid_users = 0
        if not (REQUIRED_TRANSITION_COLUMNS['users'] - set(columns.get('users', {}).keys())):
            cur.execute("SELECT COUNT(*) AS count FROM users WHERE id IS NULL OR username IS NULL OR password_hash IS NULL")
            invalid_users = cur.fetchone()['count']
    errors: dict[str, Any] = {'postgis_extensions_before_transition': postgis_extensions}
    if postgis_extensions != 1:
        errors['postgis_extension_required'] = True
    if missing_tables:
        errors['missing_tables'] = missing_tables
    if missing_columns:
        errors['missing_columns'] = missing_columns
    if type_mismatches:
        errors['type_mismatches'] = type_mismatches
    if missing_indexes:
        errors['missing_indexes'] = missing_indexes
    if missing_constraints:
        errors['missing_constraints'] = missing_constraints
    if invalid_users:
        errors['invalid_users'] = invalid_users
    return errors


def transition_pilot(conn: psycopg.Connection, migrations: list[Migration], command: str) -> int:
    with conn.cursor() as cur:
        cur.execute('SELECT pg_advisory_lock(%s)', (LOCK_KEY,))
    try:
        compatibility = transition_compatibility_errors(conn)
        blocking = {k: v for k, v in compatibility.items() if k != 'postgis_extensions_before_transition' and v}
        if blocking:
            print_status({'status': 'incompatible-source-state', **compatibility})
            return 2
        ensure_ledger(conn)
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
