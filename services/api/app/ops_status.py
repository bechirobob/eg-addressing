from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from psycopg.rows import dict_row

from app.db import get_database_url
from app.migration_state import MigrationPackageError, evaluate_migration_state, migration_files, safe_public_status


def _repo_root() -> Path:
    path = Path(__file__).resolve()
    for parent in path.parents:
        if (parent / 'infra' / 'migrations').exists():
            return parent
    return Path('/app')


ROOT = _repo_root()


def _migration_files_status() -> tuple[list[dict[str, str]], dict[str, Any] | None]:
    migrations_dir = Path(os.getenv('MIGRATIONS_DIR', ROOT / 'infra' / 'migrations'))
    try:
        return migration_files(migrations_dir), None
    except MigrationPackageError as exc:
        return [], safe_public_status(exc.to_status())


def migration_status() -> dict[str, Any]:
    """Return a public-safe migration summary for the operator command center."""
    expected, package_error = _migration_files_status()
    if package_error is not None:
        return package_error
    latest = expected[-1] if expected else None
    database_url = get_database_url()
    if not database_url:
        return {
            'status': 'not-configured',
            'applied_count': 0,
            'expected_count': len(expected),
            'pending_count': len(expected),
            'pending_versions': [row['version'] for row in expected],
            'mismatch_versions': [],
            'checksum_mismatch_versions': [],
            'filename_mismatch_versions': [],
            'unknown_versions': [],
            'latest_version': latest['version'] if latest else None,
            'latest_filename': latest['filename'] if latest else None,
            'current': False,
            'operator_note': 'Database URL is not configured; migration state cannot be checked.',
        }

    try:
        import psycopg

        with psycopg.connect(database_url, row_factory=dict_row) as connection:
            return safe_public_status(evaluate_migration_state(connection, expected))
    except Exception:
        return {
            'status': 'unreadable',
            'applied_count': 0,
            'expected_count': len(expected),
            'pending_count': len(expected),
            'pending_versions': [row['version'] for row in expected],
            'mismatch_versions': [],
            'checksum_mismatch_versions': [],
            'filename_mismatch_versions': [],
            'unknown_versions': [],
            'latest_version': latest['version'] if latest else None,
            'latest_filename': latest['filename'] if latest else None,
            'current': False,
            'operator_note': 'Migration table could not be read from the configured database.',
        }
