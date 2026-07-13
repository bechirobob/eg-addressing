#!/usr/bin/env python3
"""Explicit governed reference-data loader for NLI-WO-001."""
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
DEFAULT_PACKAGE = ROOT / 'infra/reference-data/eg-admin-units-v1.json'
REQUIRED_TABLES = {'schema_migrations', 'provinces', 'admin_units', 'reference_data_loads', 'reference_data_load_history'}


def database_target() -> str | dict[str, Any]:
    value = os.getenv('DATABASE_URL')
    if value:
        return value.replace('postgresql+psycopg://', 'postgresql://', 1)
    host = os.getenv('POSTGRES_HOST')
    if not host:
        raise SystemExit('DATABASE_URL or POSTGRES_HOST is required for reference-data commands')
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


def context(command: str) -> str:
    return json.dumps({
        'command': command,
        'actor': os.getenv('REFERENCE_DATA_ACTOR') or os.getenv('USER') or 'unknown',
        'host': socket.gethostname(),
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }, sort_keys=True)


def read_package(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_bytes()
    return json.loads(raw.decode('utf-8')), hashlib.sha256(raw).hexdigest()


def existing_tables(cur: Any) -> set[str]:
    cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    return {row['table_name'] for row in cur.fetchall()}


def require_migrated_schema(cur: Any) -> None:
    missing = sorted(REQUIRED_TABLES - existing_tables(cur))
    if missing:
        raise SystemExit(json.dumps({'status': 'missing-migrations', 'missing_tables': missing}, indent=2))


def expected_state(cur: Any, package: dict[str, Any], checksum: str) -> dict[str, Any]:
    cur.execute('SELECT package_id, package_version, package_checksum, loaded_at FROM reference_data_loads WHERE package_id = %s', (package['package_id'],))
    loaded = cur.fetchone()
    if not loaded:
        state = 'not-loaded'
    elif loaded['package_checksum'] == checksum and loaded['package_version'] == package['package_version']:
        state = 'current'
    else:
        state = 'drift'
    return {
        'package_id': package['package_id'],
        'expected_version': package['package_version'],
        'expected_checksum': checksum,
        'state': state,
        'loaded': dict(loaded) if loaded else None,
    }


def load(package_path: Path) -> int:
    package, checksum = read_package(package_path)
    records = package['records']
    changed = 0
    conflicts: list[str] = []
    with connect_database() as conn:
        with conn.transaction():
            with conn.cursor() as cur:
                require_migrated_schema(cur)
                state = expected_state(cur, package, checksum)
                if state['state'] == 'drift':
                    raise SystemExit(json.dumps({'status': 'package-drift', **state}, indent=2, default=str))
                for province in records['provinces']:
                    cur.execute('SELECT name FROM provinces WHERE code = %s', (province['code'],))
                    existing = cur.fetchone()
                    if existing and existing['name'] != province['name']:
                        conflicts.append(f"province:{province['code']}")
                        continue
                    cur.execute(
                        'INSERT INTO provinces (code, name) VALUES (%s, %s) ON CONFLICT (code) DO NOTHING',
                        (province['code'], province['name']),
                    )
                    changed += cur.rowcount
                for unit in records['admin_units']:
                    cur.execute('SELECT level, code, parent_id, province_code, name_es, name_en, status, sort_order FROM admin_units WHERE id = %s', (unit['id'],))
                    existing = cur.fetchone()
                    values = (unit['id'], unit['level'], unit['code'], unit.get('parent_id'), unit.get('province_code') or unit['code'], unit['name_es'], unit['name_en'], unit.get('status', 'active'), unit.get('sort_order', 0))
                    if existing:
                        expected = {
                            'level': unit['level'], 'code': unit['code'], 'parent_id': unit.get('parent_id'),
                            'province_code': unit.get('province_code') or unit['code'], 'name_es': unit['name_es'],
                            'name_en': unit['name_en'], 'status': unit.get('status', 'active'), 'sort_order': unit.get('sort_order', 0),
                        }
                        if any(existing[key] != expected[key] for key in expected):
                            conflicts.append(f"admin_unit:{unit['id']}")
                        continue
                    cur.execute(
                        '''
                        INSERT INTO admin_units (id, level, code, parent_id, province_code, name_es, name_en, status, sort_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''',
                        values,
                    )
                    changed += cur.rowcount
                if conflicts:
                    raise SystemExit(json.dumps({'status': 'conflict', 'conflicts': conflicts}, indent=2))
                cur.execute(
                    '''
                    INSERT INTO reference_data_loads(package_id, package_version, source, authority_status, package_checksum, execution_context)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (package_id) DO UPDATE SET
                        package_version = EXCLUDED.package_version,
                        source = EXCLUDED.source,
                        authority_status = EXCLUDED.authority_status,
                        package_checksum = EXCLUDED.package_checksum,
                        loaded_at = CASE WHEN reference_data_loads.package_checksum = EXCLUDED.package_checksum THEN reference_data_loads.loaded_at ELSE NOW() END,
                        execution_context = EXCLUDED.execution_context
                    ''',
                    (package['package_id'], package['package_version'], package['source'], package['authority_status'], checksum, context('load-reference-data')),
                )
                cur.execute(
                    '''
                    INSERT INTO reference_data_load_history(package_id, package_version, source, authority_status, package_checksum, execution_context)
                    SELECT %s, %s, %s, %s, %s, %s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM reference_data_load_history WHERE package_id = %s AND package_checksum = %s
                    )
                    ''',
                    (package['package_id'], package['package_version'], package['source'], package['authority_status'], checksum, context('load-reference-data'), package['package_id'], checksum),
                )
        print(json.dumps({'status': 'loaded', 'changed_rows': changed, 'package_id': package['package_id'], 'package_version': package['package_version'], 'checksum': checksum}, indent=2))
    return 0


def status(package_path: Path) -> int:
    package, checksum = read_package(package_path)
    with connect_database() as conn:
        with conn.cursor() as cur:
            require_migrated_schema(cur)
            state = expected_state(cur, package, checksum)
            cur.execute('SELECT package_id, package_version, source, authority_status, package_checksum, loaded_at FROM reference_data_loads ORDER BY package_id')
            rows = [dict(row) for row in cur.fetchall()]
            cur.execute('SELECT COUNT(*) AS count FROM reference_data_load_history')
            history_count = cur.fetchone()['count']
    print(json.dumps({'status': state['state'], 'expected': state, 'packages': rows, 'history_count': history_count}, indent=2, default=str))
    return 0 if state['state'] == 'current' else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['load', 'status'])
    parser.add_argument('--package', default=str(DEFAULT_PACKAGE))
    args = parser.parse_args(argv)
    if args.command == 'load':
        return load(Path(args.package))
    return status(Path(args.package))


if __name__ == '__main__':
    raise SystemExit(main())
