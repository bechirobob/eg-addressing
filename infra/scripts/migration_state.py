#!/usr/bin/env python3
"""Shared migration-state evaluator for operator/API/CLI lifecycle checks."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

VALID_NAME = re.compile(r'^(?P<version>[0-9]{3})_[A-Za-z0-9_]+\.sql$')


def migration_files(migrations_dir: Path) -> list[dict[str, str]]:
    if not migrations_dir.exists():
        return []
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in sorted(migrations_dir.glob('*.sql')):
        match = VALID_NAME.match(path.name)
        if not match:
            raise ValueError(f'Invalid migration filename: {path.name}')
        version = match.group('version')
        if version in seen:
            raise ValueError(f'Duplicate migration version: {version}')
        seen.add(version)
        rows.append({'version': version, 'filename': path.name, 'checksum': hashlib.sha256(path.read_bytes()).hexdigest()})
    return rows


def applied_rows(conn: Any) -> list[dict[str, Any]]:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables
                WHERE table_schema = 'public' AND table_name = 'schema_migrations'
            ) AS exists
            """
        )
        if not cur.fetchone()['exists']:
            return []
        cur.execute('SELECT version, filename, checksum, applied_at, execution_context FROM schema_migrations ORDER BY version ASC')
        return [dict(row) for row in cur.fetchall()]


def evaluate_migration_state(conn: Any, expected: list[dict[str, str]]) -> dict[str, Any]:
    expected_by_version = {row['version']: row for row in expected}
    applied = applied_rows(conn)
    applied_by_version = {row['version']: row for row in applied}
    pending = [row for row in expected if row['version'] not in applied_by_version]
    checksum_mismatched = [
        row for row in expected
        if row['version'] in applied_by_version and applied_by_version[row['version']].get('checksum') != row['checksum']
    ]
    filename_mismatched = [
        row for row in expected
        if row['version'] in applied_by_version and applied_by_version[row['version']].get('filename') != row['filename']
    ]
    unknown = [row for row in applied if row['version'] not in expected_by_version]
    if checksum_mismatched:
        status = 'checksum-mismatch'
    elif filename_mismatched:
        status = 'filename-mismatch'
    elif unknown:
        status = 'unknown-ledger-state'
    elif pending:
        status = 'pending'
    else:
        status = 'current'
    return {
        'status': status,
        'applied_count': len(applied),
        'expected_count': len(expected),
        'pending_count': len(pending),
        'pending_versions': [row['version'] for row in pending],
        'mismatch_versions': sorted({row['version'] for row in checksum_mismatched + filename_mismatched}),
        'checksum_mismatch_versions': [row['version'] for row in checksum_mismatched],
        'filename_mismatch_versions': [row['version'] for row in filename_mismatched],
        'unknown_versions': [row['version'] for row in unknown],
        'latest_version': applied[-1]['version'] if applied else None,
        'latest_filename': applied[-1]['filename'] if applied else None,
        'current': status == 'current',
    }


def safe_public_status(status: dict[str, Any]) -> dict[str, Any]:
    note = 'Migration state is current.' if status.get('status') == 'current' else 'Review migration state before production or readiness claims.'
    return {**status, 'operator_note': note}


def main() -> int:
    import argparse
    import psycopg
    from psycopg.rows import dict_row

    parser = argparse.ArgumentParser()
    parser.add_argument('database_url')
    parser.add_argument('migrations_dir')
    args = parser.parse_args()
    expected = migration_files(Path(args.migrations_dir))
    with psycopg.connect(args.database_url, row_factory=dict_row) as conn:
        print(json.dumps(safe_public_status(evaluate_migration_state(conn, expected)), indent=2, sort_keys=True, default=str))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
