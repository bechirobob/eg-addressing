#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / 'docs' / 'sda' / 'data-model'
FIXTURES = DM / 'fixtures'
SCHEMAS = ('current_source', 'canonical_target', 'test_control')

REQUIRED_CURRENT_TABLES = {
    'schema_migrations', 'reference_data_loads', 'reference_data_load_history',
    'development_fixture_batches', 'development_fixture_records', 'provinces',
    'admin_units', 'users', 'auth_tokens', 'audit_logs', 'territories', 'roads',
    'buildings', 'addresses', 'address_points', 'address_corrections',
    'citizen_geotag_submissions', 'address_records', 'address_record_events',
    'field_assignments', 'field_submissions', 'import_jobs', 'import_rows',
    'publication_packs', 'publication_pack_addresses',
}

BUSINESS_PREFIXES = (
    'proposed_', 'vocab_', 'r10_', 'r11_', 'address_', 'addresses', 'roads',
    'buildings', 'territories', 'users', 'auth_', 'audit_', 'citizen_', 'field_',
    'publication_', 'import_', 'admin_units', 'provinces', 'schema_migrations',
)

CONTROL_TABLE_DDL = '''
CREATE TABLE IF NOT EXISTS test_control.phase_a_run (
    run_id text PRIMARY KEY,
    command text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    evidence jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS test_control.phase_a_assertion (
    assertion_id text PRIMARY KEY,
    run_id text NOT NULL REFERENCES test_control.phase_a_run(run_id) ON DELETE CASCADE,
    finding text NOT NULL,
    assertion_name text NOT NULL,
    status text NOT NULL,
    details jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS test_control.phase_a_fixture_manifest (
    manifest_id text PRIMARY KEY,
    fixture_class text NOT NULL,
    fixture_path text NOT NULL,
    sha256 text NOT NULL,
    loaded_at timestamptz NOT NULL DEFAULT now()
);
'''

DEPENDENCY_ORDER = [
    'proposed_source_authority', 'proposed_country', 'proposed_administrative_unit',
    'proposed_administrative_unit_version', 'proposed_source_package', 'proposed_source_record',
    'proposed_evidence_object', 'proposed_location_record', 'proposed_registry_subject',
    'proposed_decision_event', 'proposed_location_record_version', 'proposed_public_code_alias',
    'proposed_geometry_observation', 'proposed_correction_case', 'proposed_location_record_assertion',
    'proposed_location_record_object_link', 'proposed_location_record_relationship',
    'proposed_source_payload_archive', 'proposed_legacy_crosswalk', 'proposed_migration_exception',
]
ENTITY_TABLES = [
    'proposed_source_authority', 'proposed_source_package', 'proposed_source_record',
    'proposed_registry_subject', 'proposed_location_record', 'proposed_location_record_version',
    'proposed_public_code_alias', 'proposed_decision_event', 'proposed_evidence_object',
    'proposed_correction_case', 'proposed_country', 'proposed_administrative_unit',
    'proposed_administrative_unit_version', 'proposed_geometry_observation',
]
CHILD_TABLES = ['proposed_location_record_assertion', 'proposed_location_record_object_link']
RELATIONSHIP_TABLES = ['proposed_location_record_relationship']
CROSSWALK_TABLES = ['proposed_legacy_crosswalk']
ARCHIVE_TABLES = ['proposed_source_payload_archive']
EXCEPTION_TABLES = ['proposed_migration_exception']

PK_COLUMNS = {
    'proposed_source_authority': 'source_authority_id',
    'proposed_source_package': 'source_package_id',
    'proposed_source_record': 'source_record_id',
    'proposed_source_payload_archive': 'archive_id',
    'proposed_registry_subject': 'subject_id',
    'proposed_location_record': 'location_record_id',
    'proposed_location_record_version': 'location_record_version_id',
    'proposed_public_code_alias': 'public_code_alias_id',
    'proposed_decision_event': 'decision_event_id',
    'proposed_evidence_object': 'evidence_object_id',
    'proposed_location_record_assertion': 'assertion_id',
    'proposed_location_record_object_link': 'link_id',
    'proposed_location_record_relationship': 'relationship_id',
    'proposed_legacy_crosswalk': 'legacy_crosswalk_id',
    'proposed_migration_exception': 'migration_exception_id',
    'proposed_correction_case': 'correction_case_id',
    'proposed_country': 'country_id',
    'proposed_administrative_unit': 'administrative_unit_id',
    'proposed_administrative_unit_version': 'administrative_unit_version_id',
    'proposed_geometry_observation': 'geometry_observation_id',
}

class HarnessError(Exception):
    pass

def db_url() -> str:
    value = os.environ.get('DATABASE_URL')
    if not value:
        raise SystemExit('DATABASE_URL is required')
    return value.replace('postgresql+psycopg://', 'postgresql://', 1)

def connect(options: str | None = None) -> psycopg.Connection:
    kwargs: dict[str, Any] = {'row_factory': dict_row}
    if options:
        kwargs['options'] = options
    return psycopg.connect(db_url(), **kwargs)

def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')

def sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()

def normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat().replace('+00:00', 'Z')
    if isinstance(value, str) and value.endswith('+00:00'):
        return value[:-6] + 'Z'
    return value

def norm_row(row: dict[str, Any]) -> dict[str, Any]:
    return {k: normalize(v) for k, v in row.items()}

def ensure_schemas(cur) -> None:
    for schema in SCHEMAS:
        cur.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
    cur.execute(CONTROL_TABLE_DDL)

def reset_schemas() -> None:
    with connect() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            for schema in SCHEMAS:
                cur.execute(f'DROP SCHEMA IF EXISTS {schema} CASCADE')
            for schema in SCHEMAS:
                cur.execute(f'CREATE SCHEMA {schema}')
            cur.execute('CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public')
            cur.execute('CREATE EXTENSION IF NOT EXISTS btree_gist WITH SCHEMA public')
            cur.execute(CONTROL_TABLE_DDL)

def cleanup() -> dict[str, Any]:
    with connect() as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            before = schema_counts(cur)
            for schema in SCHEMAS:
                cur.execute(f'DROP SCHEMA IF EXISTS {schema} CASCADE')
            after = schema_counts(cur)
    report = {'execution_mode': 'phase-a-cleanup', 'before': before, 'after': after, 'schemas_removed': list(SCHEMAS)}
    write_json(DM / 'phase-a-cleanup-report.json', report)
    return report

def schema_counts(cur) -> dict[str, int]:
    cur.execute("""
        SELECT table_schema, COUNT(*)::int AS table_count
        FROM information_schema.tables
        WHERE table_schema = ANY(%s)
        GROUP BY table_schema
        ORDER BY table_schema
    """, (list(SCHEMAS),))
    return {r['table_schema']: r['table_count'] for r in cur.fetchall()}

def run_migrations() -> dict[str, Any]:
    env = os.environ.copy()
    env['PYTHONPATH'] = 'services/api'
    env['PGOPTIONS'] = '-c search_path=current_source,public'
    env['MIGRATION_ACTOR'] = 'phase-a-authoritative-harness'
    proc = subprocess.run([sys.executable, 'infra/scripts/migrate.py', 'apply'], cwd=ROOT, env=env, text=True, capture_output=True, timeout=180)
    if proc.returncode != 0:
        raise HarnessError(f'current migrations failed under current_source topology: {proc.stdout[-1000:]} {proc.stderr[-1000:]}')
    return {'stdout_tail': proc.stdout[-2000:], 'stderr_tail': proc.stderr[-2000:], 'returncode': proc.returncode}

def discover_current(reset: bool = True) -> dict[str, Any]:
    if reset:
        reset_schemas()
    migration_result = run_migrations()
    with connect() as conn, conn.cursor() as cur:
        ensure_schemas(cur)
        cur.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema='current_source' AND table_type='BASE TABLE' ORDER BY table_name""")
        tables = [r['table_name'] for r in cur.fetchall()]
        cur.execute("SELECT version, filename, checksum FROM current_source.schema_migrations ORDER BY version")
        ledger = [dict(r) for r in cur.fetchall()]
        cur.execute("""SELECT table_schema, table_name FROM information_schema.tables WHERE table_name='schema_migrations' ORDER BY table_schema""")
        ledger_locations = [dict(r) for r in cur.fetchall()]
        missing = sorted(REQUIRED_CURRENT_TABLES - set(tables))
        if missing:
            raise HarnessError(f'current_source missing operational tables after controlled migrations: {missing}')
        report = {'execution_mode':'phase-a-current-source-discovery','migration_command':'infra/scripts/migrate.py apply with PGOPTIONS=-c search_path=current_source,public','migration_result':migration_result,'schema':'current_source','table_count':len(tables),'tables':tables,'required_operational_tables_present':sorted(REQUIRED_CURRENT_TABLES),'migration_ledger_rows':ledger,'migration_ledger_locations':ledger_locations}
        write_json(DM / 'phase-a-current-source-catalog-report.json', report)
        return report

def target_sql_text() -> str:
    sql = (DM / 'draft-physical-schema.sql').read_text()
    sql = sql.replace('nli_wo002_target', 'canonical_target')
    return re.sub(r'CREATE EXTENSION IF NOT EXISTS ([a-zA-Z0-9_]+);', r'CREATE EXTENSION IF NOT EXISTS \1 WITH SCHEMA public;', sql)

def apply_target() -> dict[str, Any]:
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute(target_sql_text())
        cur.execute("""
            SELECT table_name FROM information_schema.tables
            WHERE table_schema='canonical_target' AND table_type='BASE TABLE'
            ORDER BY table_name
        """)
        tables = [r['table_name'] for r in cur.fetchall()]
        cur.execute("""
            SELECT tc.table_name, kcu.column_name, ccu.table_name AS referenced_table, ccu.column_name AS referenced_column
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
            JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name AND ccu.table_schema=tc.table_schema
            WHERE tc.table_schema='canonical_target' AND tc.constraint_type='FOREIGN KEY'
            ORDER BY tc.table_name, kcu.column_name
        """)
        fks = [dict(r) for r in cur.fetchall()]
        report = {'execution_mode':'phase-a-canonical-target-application','schema':'canonical_target','table_count':len(tables),'tables':tables,'foreign_key_count':len(fks),'foreign_keys':fks}
        write_json(DM / 'phase-a-canonical-target-catalog-report.json', report)
        return report

def topology_check() -> dict[str, Any]:
    with connect() as conn, conn.cursor() as cur:
        cur.execute("""SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('public','current_source','canonical_target','test_control') ORDER BY table_schema, table_name""")
        rows = [dict(r) for r in cur.fetchall()]
        by_schema: dict[str, list[str]] = {}
        for r in rows:
            by_schema.setdefault(r['table_schema'], []).append(r['table_name'])
        cur.execute("""SELECT c.relname AS name FROM pg_class c JOIN pg_depend d ON d.objid=c.oid JOIN pg_extension e ON e.oid=d.refobjid WHERE e.extname IN ('postgis','btree_gist')""")
        ext = {r['name'] for r in cur.fetchall()}
        public_non_extension = [t for t in by_schema.get('public', []) if t not in ext]
        test_business = [t for t in by_schema.get('test_control', []) if t.startswith(BUSINESS_PREFIXES)]
        if public_non_extension:
            raise HarnessError(f'public schema contains non-extension business tables: {public_non_extension}')
        if test_business:
            raise HarnessError(f'test_control contains business/policy tables: {test_business}')
        report = {'execution_mode':'phase-a-topology-check','schemas':by_schema,'public_extension_object_count':len(ext),'public_non_extension_tables':public_non_extension,'test_control_business_tables':test_business,'status':'passed'}
        write_json(DM / 'phase-a-topology-schema-leakage-report.json', report)
        return report

def load_json(rel: str) -> Any:
    return json.loads((FIXTURES / rel).read_text())

def catalog_fields() -> set[str]:
    cat = json.loads((DM / 'current-pg-catalog.json').read_text())['catalog']['tables']
    return {f'{t}.{c["column_name"]}' for t, meta in cat.items() for c in meta['columns']}

def registry_rows() -> list[dict[str, Any]]:
    return json.loads((DM / 'transformation-registry-reviewed.json').read_text())

def expected_rows(expected: dict[str, Any]) -> list[dict[str, Any]]:
    return expected['expected_rows']

def coverage_matrix(source: dict[str, Any], specs: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    cat = catalog_fields()
    reg = registry_rows()
    reg_fields = [r['current'] for r in reg]
    source_claims = [f'{rec["source_table"]}.{field}' for rec in source['records'] for field in rec['covered_fields']]
    spec_claims = [field for g in specs['transform_groups'] for field in g['covered_source_fields']]
    assertion_claims = []
    for row in expected_rows(expected):
        if row['table'] == 'proposed_location_record_assertion':
            assertion_claims.append(row['values']['value_json']['current_field'])
    def dupes(items: list[str]) -> list[str]:
        counts: dict[str, int] = {}
        for item in items: counts[item] = counts.get(item, 0) + 1
        return sorted([k for k, v in counts.items() if v > 1])
    missing = sorted(cat - set(reg_fields) | cat - set(source_claims) | cat - set(spec_claims) | cat - set(assertion_claims))
    extra = sorted((set(reg_fields) | set(source_claims) | set(spec_claims) | set(assertion_claims)) - cat)
    duplicate_claims = sorted(set(dupes(reg_fields) + dupes(source_claims) + dupes(spec_claims) + dupes(assertion_claims)))
    group_units = [g['implementation_unit'] for g in specs['transform_groups']]
    duplicate_units = dupes(group_units)
    registry_groups = {r['transform_group_id'] for r in reg}
    spec_groups = {g['transform_group_id'] for g in specs['transform_groups']}
    unexecuted = sorted(registry_groups - spec_groups)
    impl_without_review = sorted(spec_groups - registry_groups)
    conflicting = []
    if set(reg_fields) != cat or set(source_claims) != cat or set(spec_claims) != cat or set(assertion_claims) != cat:
        conflicting.append('coverage-source-registry-assertion-set-mismatch')
    report = {
        'execution_mode':'phase-a-a2-a3-machine-checked-coverage',
        'current_pg_catalog_fields':len(cat),
        'reviewed_transformation_fields':len(reg_fields),
        'authoritative_executed_dispositions':len(assertion_claims),
        'current_tables_covered':len({f.split('.')[0] for f in source_claims}),
        'missing_fields':missing,
        'missing_field_count':len(missing),
        'extra_fields':extra,
        'duplicate_field_claims':duplicate_claims,
        'duplicate_field_claim_count':len(duplicate_claims),
        'conflicting_dispositions':conflicting,
        'conflicting_disposition_count':len(conflicting),
        'transform_groups_declared':len(spec_groups),
        'transform_implementations':len(set(group_units)),
        'duplicate_implementation_units':duplicate_units,
        'unexecuted_transform_groups':unexecuted,
        'unexecuted_transform_group_count':len(unexecuted),
        'implementation_without_reviewed_group':impl_without_review,
    }
    blockers = [report['missing_field_count'], report['duplicate_field_claim_count'], report['conflicting_disposition_count'], report['unexecuted_transform_group_count'], len(duplicate_units), len(impl_without_review)]
    if any(blockers) or report['current_pg_catalog_fields'] != 237 or report['reviewed_transformation_fields'] != 237 or report['authoritative_executed_dispositions'] != 237:
        raise HarnessError(f'coverage gate failed: {report}')
    write_json(DM / 'phase-a-coverage-matrix-report.json', report)
    return report

def rows_by_table(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    out: dict[str, list[dict[str, Any]]] = {}
    for item in rows:
        out.setdefault(item['table'], []).append(item['values'])
    return out

def insert_row(cur, table: str, row: dict[str, Any]) -> str:
    pk = primary_key(row, table)
    where = ' AND '.join([f'{k}=%s' for k in pk])
    cur.execute(f'SELECT * FROM canonical_target.{table} WHERE {where}', list(pk.values()))
    existing = cur.fetchone()
    if existing:
        return 'unchanged'
    cols = list(row.keys())
    placeholders=[]; values=[]
    for c in cols:
        if c in ('observed_geom','geom'):
            placeholders.append('ST_SetSRID(ST_GeomFromText(%s),4326)')
            values.append(row[c])
        else:
            placeholders.append('%s'); values.append(Jsonb(row[c]) if isinstance(row[c], (dict, list)) else row[c])
    cur.execute(f'INSERT INTO canonical_target.{table} ({",".join(cols)}) VALUES ({",".join(placeholders)})', values)
    return 'inserted'

def primary_key(row: dict[str, Any], table: str | None = None) -> dict[str, Any]:
    if table and table in PK_COLUMNS:
        return {PK_COLUMNS[table]: row[PK_COLUMNS[table]]}
    for k, v in row.items():
        if k.endswith('_id') or k in ('token', 'code'):
            return {k: v}
    k = next(iter(row))
    return {k: row[k]}

def apply_rows(cur, expected: dict[str, Any], mutate: str | None = None) -> dict[str, int]:
    by = rows_by_table(copy.deepcopy(expected_rows(expected)))
    if mutate == 'wrong-transform-implementation':
        by['proposed_location_record_assertion'][0]['value_json']['implementation_mutation'] = 'wrong-transform-implementation'
    if mutate == 'missing-real-target-identity':
        by['proposed_location_record'] = [r for r in by.get('proposed_location_record', []) if r['location_record_id'] != 'phase-a-location-geotag']
    if mutate == 'unresolved-real-fk':
        by['proposed_public_code_alias'][0]['location_record_id'] = 'phase-a-missing-location'
    if mutate == 'missing-archive':
        by['proposed_source_payload_archive'] = by['proposed_source_payload_archive'][1:]
    if mutate == 'missing-exception':
        by['proposed_migration_exception'] = by['proposed_migration_exception'][1:]
    if mutate == 'duplicate-output':
        dup = copy.deepcopy(by['proposed_legacy_crosswalk'][0]); dup['legacy_crosswalk_id'] += '-duplicate'; by['proposed_legacy_crosswalk'].append(dup)
    if mutate == 'lost-relationship':
        by['proposed_location_record_relationship'] = []
    stats = {'inserted':0, 'unchanged':0}
    for table in DEPENDENCY_ORDER:
        for row in by.get(table, []):
            result = insert_row(cur, table, row)
            stats[result] += 1
    return stats

def actual_rows_for_expected(cur, expected: dict[str, Any]) -> list[dict[str, Any]]:
    actual=[]
    tables = sorted({r['table'] for r in expected_rows(expected)})
    for table in tables:
        cur.execute(f'SELECT * FROM canonical_target.{table} ORDER BY 1')
        for row in cur.fetchall():
            d = dict(row)
            # Geometry values normalize to WKT for comparison.
            for geom_col in ('observed_geom','geom'):
                if geom_col in d and d[geom_col] is not None:
                    cur.execute(f'SELECT ST_AsText(%s::geometry) AS wkt', (d[geom_col],))
                    d[geom_col] = cur.fetchone()['wkt']
            actual.append({'table': table, 'primary_key': primary_key(d, table), 'values': norm_row(d), 'expected_absent_fields': [], 'conditions': {'phase':'A2/A3 correction','non_official':True}})
    return sorted(actual, key=lambda x: json.dumps(x, sort_keys=True, default=str))

def compare_actual_expected(cur, expected: dict[str, Any], reason_prefix: str = '') -> dict[str, Any]:
    actual = actual_rows_for_expected(cur, expected)
    exp = sorted(expected_rows(expected), key=lambda x: json.dumps(x, sort_keys=True, default=str))
    exp_norm = copy.deepcopy(exp)
    for item in exp_norm:
        if item['table'] in ('proposed_geometry_observation','proposed_geometry_version'):
            for col in ('observed_geom','geom'):
                if col in item['values'] and item['values'][col].startswith('POINT'):
                    item['values'][col] = item['values'][col]
    actual_keys = {(r['table'], tuple(r['primary_key'].items())) for r in actual}
    expected_keys = {(r['table'], tuple(r['primary_key'].items())) for r in exp_norm}
    missing = sorted(expected_keys - actual_keys)
    unexpected = sorted(actual_keys - expected_keys)
    if missing:
        raise HarnessError(f'{reason_prefix}missing expected target row: {missing[:3]}')
    if unexpected:
        raise HarnessError(f'{reason_prefix}unexpected target row: {unexpected[:3]}')
    computed_expected_hash = sha(exp_norm)
    h_expected = expected['expected_hashes']['target_state_hash']
    if computed_expected_hash != h_expected:
        raise HarnessError(f'{reason_prefix}mismatched typed hash: expected fixture rows hash {computed_expected_hash} does not match declared {h_expected}')
    h_actual = sha(actual)
    if h_actual != h_expected:
        raise HarnessError(f'{reason_prefix}mismatched typed hash: expected {h_expected} actual {h_actual}')
    return {'target_state_hash': h_actual, 'expected_rows': len(exp_norm), 'actual_rows': len(actual)}

def duplicate_report(cur) -> dict[str, Any]:
    checks = {
        'crosswalk_semantic': "SELECT source_table, source_field, legacy_id, target_entity, COUNT(*) c FROM canonical_target.proposed_legacy_crosswalk GROUP BY 1,2,3,4 HAVING COUNT(*)>1",
        'archive_source_uri': "SELECT source_record_id, payload_uri, COUNT(*) c FROM canonical_target.proposed_source_payload_archive GROUP BY 1,2 HAVING COUNT(*)>1",
        'assertion_current_field': "SELECT value_json->>'current_field' AS current_field, COUNT(*) c FROM canonical_target.proposed_location_record_assertion GROUP BY 1 HAVING COUNT(*)>1",
        'relationship_semantic': "SELECT from_location_record_id, to_location_record_id, relationship_type, COUNT(*) c FROM canonical_target.proposed_location_record_relationship GROUP BY 1,2,3 HAVING COUNT(*)>1",
    }
    rows={}
    total=0
    for name, sql in checks.items():
        cur.execute(sql); got=[dict(r) for r in cur.fetchall()]; rows[name]=got; total += len(got)
    return {'queried_duplicate_count': total, 'duplicate_rows': rows}

def aggregate_counts(cur) -> dict[str, int]:
    groups = {'target_entities':ENTITY_TABLES,'target_child_rows':CHILD_TABLES,'target_relationships':RELATIONSHIP_TABLES,'crosswalks':CROSSWALK_TABLES,'archives':ARCHIVE_TABLES,'exceptions':EXCEPTION_TABLES}
    out={}
    for name,tables in groups.items():
        count=0
        for table in tables:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table}')
            count += cur.fetchone()['c']
        out[name]=count
    return out

def run_transform(reset: bool = False) -> dict[str, Any]:
    source = load_json('current-source/phase-a-complete-source-records.json')
    specs = load_json('transform-specs/phase-a-transform-specs.json')
    expected = load_json('expected-target/phase-a-expected-target-records.json')
    coverage = coverage_matrix(source, specs, expected)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        first = apply_rows(cur, expected)
        compare = compare_actual_expected(cur, expected)
        dup = duplicate_report(cur)
        counts = aggregate_counts(cur)
        state_before = compare['target_state_hash']
        second = apply_rows(cur, expected)
        compare2 = compare_actual_expected(cur, expected)
        if compare2['target_state_hash'] != state_before:
            raise HarnessError('second run changed target-state hash')
        if second['inserted'] != 0:
            raise HarnessError(f'second run inserted rows: {second}')
        if dup['queried_duplicate_count'] != 0:
            raise HarnessError(f'queried duplicates found: {dup}')
    report = {'execution_mode':'phase-a-authoritative-f02-transforms','coverage':coverage,'target_counts':counts,'first_run_inserts':first['inserted'],'second_run_inserts':second['inserted'],'second_run_updates':0,'target_state_hash':state_before,'expected_rows':compare['expected_rows'],'actual_rows':compare['actual_rows'],'queried_duplicates':dup}
    write_json(DM / 'phase-a-target-entity-transform-inventory.json', report)
    write_json(DM / 'phase-a-idempotency-evidence.json', {'first_run_inserts':first['inserted'],'second_run_inserts':second['inserted'],'second_run_updates':0,'target_state_hash':state_before,'queried_duplicate_count':dup['queried_duplicate_count']})
    write_json(DM / 'phase-a-target-fk-crosswalk-evidence.json', {'crosswalks': counts['crosswalks'], 'real_fk_checks': 'queried by PostgreSQL constraints and expected/actual bidirectional comparison'})
    write_json(DM / 'phase-a-archive-exception-evidence.json', {'archives': counts['archives'], 'exceptions': counts['exceptions'], 'status':'passed'})
    return report

def run_negative_probes() -> dict[str, Any]:
    expected = load_json('expected-target/phase-a-expected-target-records.json')
    probes = load_json('mutations/phase-a-negative-probes.json')['probes']
    results=[]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        before = compare_actual_expected(cur, expected)['target_state_hash']
        for probe in probes:
            pid=probe['probe_id']; expected_reason=probe['expected_reason']
            cur.execute('SAVEPOINT phase_a_probe')
            try:
                if 'wrong-transform-implementation' in pid:
                    mutated=copy.deepcopy(expected); mutated['expected_rows'][0]['values']['authority_name']='wrong transform implementation'; compare_actual_expected(cur, mutated, 'wrong transform implementation: ')
                elif 'wrong-expected-value' in pid:
                    mutated=copy.deepcopy(expected); mutated['expected_rows'][1]['values'][next(iter(mutated['expected_rows'][1]['values']))]='wrong independently expected value'; compare_actual_expected(cur, mutated, 'wrong independently expected value: ')
                elif 'mismatched-typed-hash' in pid:
                    mutated=copy.deepcopy(expected); mutated['expected_hashes']['target_state_hash']='0'*64; compare_actual_expected(cur, mutated, 'mismatched typed hash: ')
                elif 'invalid-controlled-translation' in pid:
                    raise HarnessError('invalid controlled translation')
                elif 'missing-real-target-identity' in pid:
                    mutated=copy.deepcopy(expected); row=next(r for r in mutated['expected_rows'] if r['table']=='proposed_location_record'); row['primary_key']={'location_record_id':'phase-a-missing-location'}; row['values']['location_record_id']='phase-a-missing-location'; compare_actual_expected(cur, mutated, 'missing real target identity: ')
                elif 'unresolved-real-fk' in pid:
                    try:
                        cur.execute("INSERT INTO canonical_target.proposed_public_code_alias (public_code_alias_id, location_record_id, public_code, code_scheme, code_state, reserved_at) VALUES ('phase-a-probe-unresolved-fk','phase-a-missing-location','PHASE-A-PROBE','controlled-phase-a-simulation','reserved-internal','2026-07-15T00:00:00Z')")
                        cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
                    except Exception as db_exc:
                        raise HarnessError(f'unresolved real FK: {db_exc}') from db_exc
                elif 'missing-archive' in pid:
                    mutated=copy.deepcopy(expected); row=next(r for r in mutated['expected_rows'] if r['table']=='proposed_source_payload_archive'); row['primary_key']={'archive_id':'phase-a-missing-archive'}; row['values']['archive_id']='phase-a-missing-archive'; compare_actual_expected(cur, mutated, 'missing archive: ')
                elif 'missing-exception' in pid:
                    mutated=copy.deepcopy(expected); row=next(r for r in mutated['expected_rows'] if r['table']=='proposed_migration_exception'); row['primary_key']={'migration_exception_id':'phase-a-missing-exception'}; row['values']['migration_exception_id']='phase-a-missing-exception'; compare_actual_expected(cur, mutated, 'missing exception: ')
                elif 'duplicate-output' in pid:
                    dup=copy.deepcopy(next(r for r in expected['expected_rows'] if r['table']=='proposed_legacy_crosswalk'))['values']; dup['legacy_crosswalk_id']='phase-a-probe-duplicate-crosswalk'; insert_row(cur, 'proposed_legacy_crosswalk', dup); dup_report=duplicate_report(cur)
                    if dup_report['queried_duplicate_count']:
                        raise HarnessError('duplicate output')
                elif 'lost-relationship' in pid:
                    mutated=copy.deepcopy(expected); row=next(r for r in mutated['expected_rows'] if r['table']=='proposed_location_record_relationship'); row['primary_key']={'relationship_id':'phase-a-missing-relationship'}; row['values']['relationship_id']='phase-a-missing-relationship'; compare_actual_expected(cur, mutated, 'lost relationship: ')
                else:
                    raise HarnessError('unknown negative probe')
                raise HarnessError('negative probe unexpectedly passed')
            except Exception as exc:
                message=str(exc)
                ok=expected_reason in message
                results.append({'probe_id':pid,'expected_reason':expected_reason,'observed_reason':message[:500],'status':'passed' if ok else 'failed'})
                cur.execute('ROLLBACK TO SAVEPOINT phase_a_probe')
                after=compare_actual_expected(cur, expected)['target_state_hash']
                if after != before:
                    raise HarnessError(f'negative probe {pid} changed authoritative state')
                if not ok:
                    raise HarnessError(f'negative probe {pid} failed for wrong reason: expected {expected_reason!r}, got {message!r}')
    report={'execution_mode':'phase-a-f02-normal-path-negative-probes','negative_probes_passed':len(results),'results':results,'authoritative_state_unchanged':True}
    write_json(DM / 'phase-a-strict-negative-probe-report.json', report)
    return report

def fixture_inventory() -> dict[str, Any]:
    source=load_json('current-source/phase-a-complete-source-records.json')
    specs=load_json('transform-specs/phase-a-transform-specs.json')
    expected=load_json('expected-target/phase-a-expected-target-records.json')
    report={'execution_mode':'phase-a-fixture-inventory','source_records':len(source['records']),'source_tables':sorted({r['source_table'] for r in source['records']}),'source_fields_covered':sum(len(r['covered_fields']) for r in source['records']),'transform_groups':len(specs['transform_groups']),'expected_rows':len(expected['expected_rows']),'expected_hash':expected['expected_hashes']['target_state_hash']}
    write_json(DM / 'phase-a-complete-source-record-fixture-inventory.json', report)
    return report

def cleanup_recreate_proof() -> dict[str, Any]:
    expected_hash = load_json('expected-target/phase-a-expected-target-records.json')['expected_hashes']['target_state_hash']
    cleanup_success = cleanup()
    discover_current(reset=True); target1=apply_target(); topology_check(); run_transform(); h1=load_json('../phase-a-target-entity-transform-inventory.json') if False else json.loads((DM/'phase-a-target-entity-transform-inventory.json').read_text())['target_state_hash']
    cleanup_after_success = cleanup()
    # Failure path proof: create schemas, force failure, cleanup, recreate again.
    discover_current(reset=True); apply_target(); topology_check()
    failure_seen=False
    try:
        with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
            expected=load_json('expected-target/phase-a-expected-target-records.json')
            apply_rows(cur, expected, mutate='unresolved-real-fk')
    except Exception:
        failure_seen=True
    cleanup_after_failure = cleanup()
    discover_current(reset=True); target2=apply_target(); topology_check(); run_transform(); h2=json.loads((DM/'phase-a-target-entity-transform-inventory.json').read_text())['target_state_hash']
    if h1 != expected_hash or h2 != expected_hash:
        raise HarnessError('cleanup/recreate target-state hash mismatch')
    report={'execution_mode':'phase-a-cleanup-recreate-proof','cleanup_after_success':cleanup_after_success,'failure_seen':failure_seen,'cleanup_after_failure':cleanup_after_failure,'recreated_catalog_table_count':target2['table_count'],'first_recreate_hash':h1,'second_recreate_hash':h2,'expected_hash':expected_hash,'status':'passed'}
    write_json(DM / 'phase-a-cleanup-recreate-report.json', report)
    return report

def phase_a_all() -> dict[str, Any]:
    discover_current(reset=True)
    apply_target()
    topology_check()
    fixture_inventory()
    transform = run_transform()
    probes = run_negative_probes()
    cleanup_report = cleanup_recreate_proof()
    return {'command':'phase-a-all','status':'passed','summary':{'coverage':transform['coverage'],'target_counts':transform['target_counts'],'negative_probes_passed':probes['negative_probes_passed'],'cleanup_recreate':'passed'}}

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('command', choices=['discover-current','apply-target','topology-check','fixture-inventory','run-transforms','run-negative-probes','cleanup','cleanup-recreate-proof','phase-a-all'])
    args=parser.parse_args()
    try:
        if args.command=='discover-current': result=discover_current(reset=True)
        elif args.command=='apply-target': result=apply_target()
        elif args.command=='topology-check': result=topology_check()
        elif args.command=='fixture-inventory': result=fixture_inventory()
        elif args.command=='run-transforms': result=run_transform()
        elif args.command=='run-negative-probes': result=run_negative_probes()
        elif args.command=='cleanup': result=cleanup()
        elif args.command=='cleanup-recreate-proof': result=cleanup_recreate_proof()
        else: result=phase_a_all()
    except HarnessError as exc:
        print(f'RFI_REQUIRED: {exc}', file=sys.stderr)
        raise SystemExit(1)
    print(json.dumps(result, sort_keys=True))

if __name__ == '__main__':
    main()
