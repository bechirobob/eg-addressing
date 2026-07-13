#!/usr/bin/env python3
"""Deterministic PostgreSQL/PostGIS schema and data invariant manifests."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

PROTECTED_ROW_COUNT_TABLES = [
    'schema_migrations',
    'reference_data_loads',
    'reference_data_load_history',
    'development_fixture_batches',
    'development_fixture_records',
    'provinces',
    'admin_units',
    'territories',
    'roads',
    'buildings',
    'addresses',
    'address_points',
    'address_records',
    'address_record_events',
    'citizen_geotag_submissions',
    'field_assignments',
    'field_submissions',
    'address_corrections',
    'import_jobs',
    'import_rows',
    'publication_packs',
    'publication_pack_addresses',
    'users',
    'auth_tokens',
    'audit_logs',
]

HASH_TABLES = [
    'schema_migrations',
    'reference_data_loads',
    'reference_data_load_history',
    'development_fixture_batches',
    'development_fixture_records',
    'provinces',
    'admin_units',
    'territories',
    'roads',
    'buildings',
    'addresses',
    'address_points',
    'address_records',
    'address_record_events',
    'citizen_geotag_submissions',
    'field_assignments',
    'field_submissions',
    'import_jobs',
    'import_rows',
    'publication_packs',
    'publication_pack_addresses',
    'users',
    'auth_tokens',
    'audit_logs',
]

RELATIONSHIP_SQL = {
    'admin_units_with_parent': "SELECT COUNT(*)::int AS count FROM admin_units child JOIN admin_units parent ON child.parent_id = parent.id WHERE child.parent_id IS NOT NULL",
    'territories_with_province': "SELECT COUNT(*)::int AS count FROM territories t JOIN provinces p ON p.code = t.province_code",
    'territories_with_admin_unit': "SELECT COUNT(*)::int AS count FROM territories t JOIN admin_units a ON a.id = t.admin_unit_id WHERE t.admin_unit_id IS NOT NULL",
    'roads_with_territory': "SELECT COUNT(*)::int AS count FROM roads r JOIN territories t ON t.id = r.territory_id",
    'buildings_with_road': "SELECT COUNT(*)::int AS count FROM buildings b JOIN roads r ON r.id = b.road_id WHERE b.road_id IS NOT NULL",
    'buildings_with_territory': "SELECT COUNT(*)::int AS count FROM buildings b JOIN territories t ON t.id = b.territory_id",
    'addresses_with_building': "SELECT COUNT(*)::int AS count FROM addresses a JOIN buildings b ON b.id = a.building_id WHERE a.building_id IS NOT NULL",
    'addresses_with_road': "SELECT COUNT(*)::int AS count FROM addresses a JOIN roads r ON r.id = a.road_id WHERE a.road_id IS NOT NULL",
    "address_records_with_events": "SELECT COUNT(DISTINCT ar.id)::int AS count FROM address_records ar JOIN address_record_events e ON e.address_record_id = ar.id",
    'field_assignments_with_territory': "SELECT COUNT(*)::int AS count FROM field_assignments fa JOIN territories t ON t.id = fa.territory_id WHERE fa.territory_id IS NOT NULL",
    'field_submissions_with_assignment': "SELECT COUNT(*)::int AS count FROM field_submissions fs JOIN field_assignments fa ON fa.assignment_id = fs.assignment_id WHERE fs.assignment_id IS NOT NULL",
    'import_rows_with_job': "SELECT COUNT(*)::int AS count FROM import_rows ir JOIN import_jobs ij ON ij.id = ir.job_id",
    'publication_addresses_with_pack': "SELECT COUNT(*)::int AS count FROM publication_pack_addresses ppa JOIN publication_packs pp ON pp.id = ppa.publication_pack_id",
    'publication_addresses_with_address': "SELECT COUNT(*)::int AS count FROM publication_pack_addresses ppa JOIN addresses a ON a.id = ppa.address_id",
    'auth_tokens_with_user': "SELECT COUNT(*)::int AS count FROM auth_tokens at JOIN users u ON u.id = at.user_id",
}


def database_target() -> str | dict[str, Any]:
    value = os.getenv('DATABASE_URL')
    if value:
        return value.replace('postgresql+psycopg://', 'postgresql://', 1)
    host = os.getenv('POSTGRES_HOST')
    if not host:
        raise SystemExit('DATABASE_URL or POSTGRES_HOST is required')
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


def stable_hash(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode('utf-8')
    return hashlib.sha256(encoded).hexdigest()


def table_exists(conn: Any, table: str) -> bool:
    with conn.cursor() as cur:
        cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name=%s) AS exists", (table,))
        return bool(cur.fetchone()['exists'])


def schema_manifest(conn: Any) -> dict[str, Any]:
    with conn.cursor() as cur:
        cur.execute("SELECT extname, extversion FROM pg_extension ORDER BY extname")
        extensions = [dict(row) for row in cur.fetchall()]
        cur.execute(
            """
            SELECT table_name, column_name, ordinal_position, data_type, udt_name,
                   is_nullable, column_default, character_maximum_length,
                   numeric_precision, numeric_scale, datetime_precision
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position
            """
        )
        columns = [dict(row) for row in cur.fetchall()]
        cur.execute(
            """
            SELECT c.relname AS table_name, con.conname AS constraint_name, con.contype AS constraint_type,
                   pg_get_constraintdef(con.oid, true) AS definition
            FROM pg_constraint con
            JOIN pg_class c ON c.oid = con.conrelid
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
            ORDER BY c.relname, con.conname
            """
        )
        constraints = [dict(row) for row in cur.fetchall()]
        cur.execute(
            """
            SELECT tablename AS table_name, indexname AS index_name, indexdef AS definition
            FROM pg_indexes
            WHERE schemaname = 'public'
            ORDER BY tablename, indexname
            """
        )
        indexes = [dict(row) for row in cur.fetchall()]
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        tables = [row['table_name'] for row in cur.fetchall()]
    manifest = {'extensions': extensions, 'tables': tables, 'columns': columns, 'constraints': constraints, 'indexes': indexes}
    return {'manifest': manifest, 'sha256': stable_hash(manifest)}


def row_counts(conn: Any, tables: list[str] | None = None) -> dict[str, int | None]:
    counts: dict[str, int | None] = {}
    for table in tables or PROTECTED_ROW_COUNT_TABLES:
        if not table_exists(conn, table):
            counts[table] = None
            continue
        with conn.cursor() as cur:
            cur.execute(f'SELECT COUNT(*)::int AS count FROM {table}')
            counts[table] = cur.fetchone()['count']
    return counts


def table_hash(conn: Any, table: str) -> str | None:
    if not table_exists(conn, table):
        return None
    with conn.cursor() as cur:
        cur.execute(f"SELECT COALESCE(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text), '[]'::jsonb) AS rows FROM {table} t")
        rows = cur.fetchone()['rows']
    return stable_hash(rows)


def table_hashes(conn: Any, tables: list[str] | None = None) -> dict[str, str | None]:
    return {table: table_hash(conn, table) for table in tables or HASH_TABLES}


def relationship_counts(conn: Any) -> dict[str, int | None]:
    values: dict[str, int | None] = {}
    for name, sql in RELATIONSHIP_SQL.items():
        try:
            with conn.cursor() as cur:
                cur.execute(sql)
                values[name] = cur.fetchone()['count']
        except Exception:
            values[name] = None
    return values


def data_manifest(conn: Any) -> dict[str, Any]:
    manifest = {
        'row_counts': row_counts(conn),
        'table_hashes': table_hashes(conn),
        'relationships': relationship_counts(conn),
    }
    return {'manifest': manifest, 'sha256': stable_hash(manifest)}


def full_manifest(conn: Any) -> dict[str, Any]:
    schema = schema_manifest(conn)
    data = data_manifest(conn)
    combined = {'schema': schema['manifest'], 'data': data['manifest']}
    return {'schema_sha256': schema['sha256'], 'data_sha256': data['sha256'], 'manifest_sha256': stable_hash(combined), 'manifest': combined}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['schema', 'data', 'full'])
    parser.add_argument('--output')
    args = parser.parse_args(argv)
    with connect_database() as conn:
        if args.command == 'schema':
            result = schema_manifest(conn)
        elif args.command == 'data':
            result = data_manifest(conn)
        else:
            result = full_manifest(conn)
    text = json.dumps(result, indent=2, sort_keys=True, default=str) + '\n'
    if args.output:
        Path(args.output).write_text(text)
    print(text, end='')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
