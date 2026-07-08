from __future__ import annotations

import hashlib
import os
from pathlib import Path
from typing import Any

from psycopg.rows import dict_row

from app.db import get_database_url


def _repo_root() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / 'infra' / 'migrations').exists():
            return parent
    return Path('/app')


def _migration_files() -> list[Path]:
    migrations_dir = Path(os.getenv('MIGRATIONS_DIR', _repo_root() / 'infra' / 'migrations'))
    if not migrations_dir.exists():
        return []
    return sorted(migrations_dir.glob('*.sql'))


def _checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def migration_status() -> dict[str, Any]:
    """Return a public-safe migration summary for the operator command center."""
    files = _migration_files()
    expected = [
        {
            'version': path.name.split('_', 1)[0],
            'filename': path.name,
            'checksum': _checksum(path),
        }
        for path in files
    ]
    latest = expected[-1] if expected else None
    database_url = get_database_url()
    if not database_url:
        return {
            'status': 'not-configured',
            'applied_count': 0,
            'expected_count': len(expected),
            'pending_count': len(expected),
            'latest_version': latest['version'] if latest else None,
            'latest_filename': latest['filename'] if latest else None,
            'operator_note': 'Database URL is not configured; migration state cannot be checked.',
        }

    try:
        import psycopg

        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT 1 FROM information_schema.tables
                        WHERE table_schema = 'public' AND table_name = 'schema_migrations'
                    ) AS exists
                    """
                )
                if not cursor.fetchone()['exists']:
                    applied: list[dict[str, Any]] = []
                else:
                    cursor.execute('SELECT version, filename, checksum, applied_at FROM schema_migrations ORDER BY version ASC')
                    applied = list(cursor.fetchall())
    except Exception:
        return {
            'status': 'unreadable',
            'applied_count': 0,
            'expected_count': len(expected),
            'pending_count': len(expected),
            'latest_version': latest['version'] if latest else None,
            'latest_filename': latest['filename'] if latest else None,
            'operator_note': 'Migration table could not be read from the configured database.',
        }

    applied_by_version = {row['version']: row for row in applied}
    pending = [item for item in expected if item['version'] not in applied_by_version]
    mismatched = [
        item
        for item in expected
        if item['version'] in applied_by_version and applied_by_version[item['version']].get('checksum') != item['checksum']
    ]
    status = 'current'
    if mismatched:
        status = 'checksum-mismatch'
    elif pending:
        status = 'pending'

    latest_applied = applied[-1] if applied else None
    return {
        'status': status,
        'applied_count': len(applied),
        'expected_count': len(expected),
        'pending_count': len(pending),
        'latest_version': latest_applied['version'] if latest_applied else None,
        'latest_filename': latest_applied['filename'] if latest_applied else None,
        'pending_versions': [item['version'] for item in pending[:10]],
        'mismatch_versions': [item['version'] for item in mismatched[:10]],
        'operator_note': 'Migration state is current.' if status == 'current' else 'Review migration status before production claims.',
    }
