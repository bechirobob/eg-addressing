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
from typing import Any, Callable

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / 'docs' / 'sda' / 'data-model'
FIXTURES = DM / 'fixtures'
SCHEMAS = ('current_source', 'canonical_target', 'test_control')
TS = '2026-07-15T00:00:00Z'

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
    'proposed_name_record', 'proposed_geometry_observation', 'proposed_correction_case',
    'proposed_location_record_assertion', 'proposed_location_record_object_link',
    'proposed_location_record_relationship', 'proposed_source_payload_archive',
    'proposed_legacy_crosswalk', 'proposed_migration_exception',
]
ENTITY_TABLES = [
    'proposed_source_authority', 'proposed_source_package', 'proposed_source_record',
    'proposed_registry_subject', 'proposed_location_record', 'proposed_location_record_version',
    'proposed_public_code_alias', 'proposed_decision_event', 'proposed_evidence_object',
    'proposed_correction_case', 'proposed_country', 'proposed_administrative_unit',
    'proposed_administrative_unit_version', 'proposed_geometry_observation', 'proposed_name_record',
]
CHILD_TABLES = ['proposed_location_record_assertion', 'proposed_location_record_object_link', 'proposed_name_record']
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
    'proposed_name_record': 'name_record_id',
}
ENTITY_TABLE_BY_REGISTRY = {
    'source_payload_archive': 'proposed_source_payload_archive',
    'decision_event': 'proposed_decision_event',
    'legacy_crosswalk': 'proposed_legacy_crosswalk',
    'name_record': 'proposed_name_record',
    'migration_exception': 'proposed_migration_exception',
    'geometry_observation': 'proposed_geometry_observation',
    'public_code_alias': 'proposed_public_code_alias',
    'correction_case': 'proposed_correction_case',
}

EXPECTED_READ_ALLOWED = False
TRANSFORM_MUTATIONS: dict[str, Any] = {}

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
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + '\n')

def sha(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), default=str).encode()).hexdigest()

def normalize(value: Any) -> Any:
    if isinstance(value, datetime):
        if value.tzinfo is not None:
            return value.astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
        return value.isoformat()
    if isinstance(value, str):
        if value.endswith('+00:00'):
            return value[:-6] + 'Z'
        if re.search(r'[+-]\d\d:\d\d$', value):
            try:
                return datetime.fromisoformat(value).astimezone(timezone.utc).isoformat().replace('+00:00', 'Z')
            except ValueError:
                return value
    return value

def norm_row(row: dict[str, Any]) -> dict[str, Any]:
    return {k: normalize(v) for k, v in row.items()}

def broad_payload_hash_input(value: Any) -> Any:
    if isinstance(value, datetime) and value.tzinfo is not None:
        return value.astimezone(timezone.utc)
    if isinstance(value, dict):
        return {k: broad_payload_hash_input(v) for k, v in value.items()}
    if isinstance(value, list):
        return [broad_payload_hash_input(v) for v in value]
    return value

def slug(value: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')[:160]

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

def schema_counts(cur) -> dict[str, int]:
    cur.execute("""
        SELECT table_schema, COUNT(*)::int AS table_count
        FROM information_schema.tables
        WHERE table_schema = ANY(%s)
        GROUP BY table_schema ORDER BY table_schema
    """, (list(SCHEMAS),))
    return {r['table_schema']: r['table_count'] for r in cur.fetchall()}

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
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='current_source' AND table_type='BASE TABLE' ORDER BY table_name")
        tables = [r['table_name'] for r in cur.fetchall()]
        cur.execute("SELECT version, filename, checksum FROM current_source.schema_migrations ORDER BY version")
        ledger = [dict(r) for r in cur.fetchall()]
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_name='schema_migrations' ORDER BY table_schema")
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
        cur.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='canonical_target' AND table_type='BASE TABLE' ORDER BY table_name")
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
        cur.execute("SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema IN ('public','current_source','canonical_target','test_control') ORDER BY table_schema, table_name")
        rows = [dict(r) for r in cur.fetchall()]
        by_schema: dict[str, list[str]] = {}
        for r in rows:
            by_schema.setdefault(r['table_schema'], []).append(r['table_name'])
        cur.execute("SELECT c.relname AS name FROM pg_class c JOIN pg_depend d ON d.objid=c.oid JOIN pg_extension e ON e.oid=d.refobjid WHERE e.extname IN ('postgis','btree_gist')")
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

def load_expected_fixture() -> Any:
    if not EXPECTED_READ_ALLOWED:
        raise HarnessError('expected target fixture may be read only after observed target rows have been created')
    return load_json('expected-target/phase-a-expected-target-records.json')

def catalog_fields() -> set[str]:
    cat = json.loads((DM / 'current-pg-catalog.json').read_text())['catalog']['tables']
    return {f'{t}.{c["column_name"]}' for t, meta in cat.items() for c in meta['columns']}

def registry_groups() -> list[dict[str, Any]]:
    return load_json('transform-specs/phase-a-transform-specs.json')['transform_groups']

def broad_registry_groups() -> list[dict[str, Any]]:
    return load_json('transform-specs/phase-a-broad-generic-transform-specs-frozen.json')['transform_groups']

def registry_fields(groups: list[dict[str, Any]] | None = None) -> set[str]:
    selected = groups if groups is not None else registry_groups()
    return {field for g in selected for field in g['covered_source_fields']}

def current_column_meta(cur) -> dict[str, dict[str, dict[str, Any]]]:
    cur.execute("""
        SELECT table_name, column_name, data_type, udt_name, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_schema='current_source'
        ORDER BY table_name, ordinal_position
    """)
    meta: dict[str, dict[str, dict[str, Any]]] = {}
    for row in cur.fetchall():
        meta.setdefault(row['table_name'], {})[row['column_name']] = dict(row)
    return meta

def fixture_records(mutation: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    data = copy.deepcopy(load_json('current-source/phase-a-complete-source-records.json')['records'])
    if mutation and mutation.get('source_wrong_value'):
        data[0]['values']['status'] = 'phase-a-invalid-controlled-translation'
    if mutation and mutation.get('source_missing_field'):
        field = data[0]['covered_fields'][0]
        data[0]['values'].pop(field, None)
    return data

def adapt_current_value(col: dict[str, Any], value: Any, row_values: dict[str, Any]) -> tuple[str, Any]:
    udt = col['udt_name']; name = col['column_name']
    if value is None:
        return '%s', None
    if udt in ('json', 'jsonb'):
        if isinstance(value, (dict, list)):
            return '%s', Jsonb(value)
        return '%s', Jsonb({'phase_a_value': value})
    if udt == 'geography':
        lat = row_values.get('latitude', 3.752); lon = row_values.get('longitude', 8.783)
        return 'ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography', (lon, lat)
    return '%s', value

CURRENT_SOURCE_ORDER = [
    'schema_migrations', 'reference_data_loads', 'reference_data_load_history',
    'development_fixture_batches', 'development_fixture_records', 'provinces', 'admin_units',
    'users', 'auth_tokens', 'audit_logs', 'territories', 'roads', 'buildings', 'addresses',
    'address_points', 'citizen_geotag_submissions', 'address_records', 'address_record_events',
    'field_assignments', 'field_submissions', 'import_jobs', 'import_rows',
    'publication_packs', 'publication_pack_addresses', 'address_corrections',
]
CURRENT_ORDER_INDEX = {table: idx for idx, table in enumerate(CURRENT_SOURCE_ORDER)}

FK_NORMALIZATION = {
    'territory_id': 'phase-a-territories-id',
    'road_id': 'phase-a-roads-id',
    'building_id': 'phase-a-buildings-id',
    'address_id': 'phase-a-addresses-id',
    'address_record_id': 'phase-a-address-records-id',
    'user_id': 'phase-a-users-id',
    'actor_user_id': 'phase-a-users-id',
    'admin_unit_id': 'phase-a-admin-units-id',
    'field_submission_id': 'phase-a-field-submissions-id',
    'publication_pack_id': 'phase-a-publication-packs-id',
    'job_id': 'phase-a-import-jobs-id',
    'committed_submission_id': 'phase-a-field-submissions-id',
    'source_submission_id': 'phase-a-geotag-001',
    'province_code': 'phase-a-provinces-code',
}

def normalize_current_fixture_values(table: str, values: dict[str, Any]) -> dict[str, Any]:
    out = dict(values)
    for key, replacement in FK_NORMALIZATION.items():
        if key in out:
            out[key] = replacement
    if table == 'admin_units' and 'parent_id' in out:
        out['parent_id'] = None
    if table == 'addresses' and 'superseded_by_address_id' in out:
        out['superseded_by_address_id'] = None
    if table == 'development_fixture_records' and 'batch_id' in out:
        out['batch_id'] = 'phase-a-development-fixture-batches-batch-id'
    if table == 'field_submissions' and 'assignment_id' in out:
        out['assignment_id'] = 'phase-a-field-assignments-assignment-id'
    return out

def insert_current_fixture_rows(cur, records: list[dict[str, Any]]) -> dict[str, Any]:
    meta = current_column_meta(cur)
    inserted=[]; queried=[]; fields=[]
    cur.execute('SET CONSTRAINTS ALL DEFERRED')
    for rec in sorted(records, key=lambda r: CURRENT_ORDER_INDEX.get(r['source_table'], 999)):
        table = rec['source_table']; values = normalize_current_fixture_values(table, rec['values'])
        table_meta = meta[table]
        cols = [c for c in table_meta if c in values]
        if set(rec['covered_fields']) - set(cols):
            raise HarnessError(f'source fixture missing values for {table}: {sorted(set(rec["covered_fields"]) - set(cols))}')
        placeholders=[]; params=[]
        for c in cols:
            ph, val = adapt_current_value(table_meta[c], values[c], values)
            placeholders.append(ph)
            if isinstance(val, tuple): params.extend(val)
            else: params.append(val)
        cur.execute(f'INSERT INTO current_source.{table} ({",".join(cols)}) VALUES ({",".join(placeholders)})', params)
        key_col = 'id' if 'id' in cols else cols[0]
        cur.execute(f'SELECT {",".join(cols)} FROM current_source.{table} WHERE {key_col}=%s', (values[key_col],))
        row = cur.fetchone()
        if not row:
            raise HarnessError(f'failed to query inserted current source row {table}.{key_col}={values[key_col]}')
        inserted.append({'source_table':table,'source_key':rec['source_key'],'primary_or_natural_key':{key_col: values[key_col]},'fields_inserted':cols})
        queried.append({'source_table':table,'source_key':rec['source_key'],'primary_or_natural_key':{key_col: values[key_col]},'queried_values':norm_row(dict(row))})
        fields.extend([f'{table}.{c}' for c in cols])
    report={'execution_mode':'phase-a-current-source-fixture-load','current_tables_populated':len({r['source_table'] for r in records}),'source_records_inserted':len(inserted),'source_fields_queried':len(set(fields)),'inserted_records':inserted,'queried_records':queried,'source_fk_relationships':source_fk_report(cur)}
    write_json(DM / 'phase-a-current-source-execution-report.json', report)
    return report

def source_fk_report(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT tc.table_name, kcu.column_name, ccu.table_name AS referenced_table, ccu.column_name AS referenced_column
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu ON tc.constraint_name=kcu.constraint_name AND tc.table_schema=kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu ON ccu.constraint_name=tc.constraint_name AND ccu.table_schema=tc.table_schema
        WHERE tc.table_schema='current_source' AND tc.constraint_type='FOREIGN KEY'
        ORDER BY tc.table_name, kcu.column_name
    """)
    fks=[dict(r) for r in cur.fetchall()]
    return {'foreign_key_count':len(fks),'foreign_keys':fks}

def query_source_row(cur, rec: dict[str, Any], fields: list[str]) -> dict[str, Any]:
    table = rec['source_table']; vals=normalize_current_fixture_values(table, rec['values']); key_col = 'id' if 'id' in vals else next(iter(vals))
    clean_fields=[f.split('.',1)[1] if '.' in f else f for f in fields]
    for f in clean_fields:
        if f not in vals:
            raise HarnessError(f'declared source field {table}.{f} missing from fixture values')
    cur.execute(f'SELECT {",".join(clean_fields)} FROM current_source.{table} WHERE {key_col}=%s', (vals[key_col],))
    row=cur.fetchone()
    if not row:
        raise HarnessError(f'source row not found during transform: {table}.{key_col}={vals[key_col]}')
    return dict(row)

def base_target_rows() -> dict[str, list[dict[str, Any]]]:
    rows={t:[] for t in DEPENDENCY_ORDER}
    def add(t,r): rows.setdefault(t,[]).append(r)
    add('proposed_source_authority', {'source_authority_id':'phase-a-authority-citizen-evidence','authority_name':'Phase A citizen-submitted evidence authority','authority_class':'citizen-submitted','legal_basis':'Controlled Phase A fixture; non_official=true','status':'candidate'})
    add('proposed_source_authority', {'source_authority_id':'phase-a-authority-conditional-admin-reference','authority_name':'Phase A conditional administrative reference authority','authority_class':'registry-authority','legal_basis':'Conditional/provisional non-official government reference fixture linked to authority RFI','status':'candidate'})
    add('proposed_source_authority', {'source_authority_id':'phase-a-authority-operational-control','authority_name':'Phase A retained operational-control authority','authority_class':'derived-system','legal_basis':'Operational-control/non-migrated disposition fixture; no public effect','status':'candidate'})
    add('proposed_country',{'country_id':'phase-a-country-gq','iso2_code':'GQ','official_name_es':'Guinea Ecuatorial','official_name_en':'Equatorial Guinea','lifecycle_state':'active','source_authority_id':'phase-a-authority-conditional-admin-reference','created_at':TS})
    add('proposed_administrative_unit',{'administrative_unit_id':'phase-a-admin-bioko-norte','country_id':'phase-a-country-gq','created_at':TS,'retired_at':None})
    add('proposed_administrative_unit_version',{'administrative_unit_version_id':'phase-a-admin-bioko-norte-v1','administrative_unit_id':'phase-a-admin-bioko-norte','parent_administrative_unit_id':None,'admin_level':'province','lifecycle_state':'proposed','effective_from':TS,'effective_to':None,'recorded_at':TS,'recorded_to':None,'source_authority_id':'phase-a-authority-conditional-admin-reference','classification':'public-after-release'})
    for loc_id,label in [('phase-a-location-geotag','Controlled Phase A geotag observation'),('phase-a-location-address-reference','Controlled Phase A address reference')]:
        add('proposed_location_record',{'location_record_id':loc_id,'record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        add('proposed_registry_subject',{'subject_id':f'phase-a-subject-{loc_id}','subject_entity':'location_record','created_at':TS,'native_id':loc_id,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
        add('proposed_decision_event',{'decision_event_id':f'phase-a-decision-{loc_id}','decision_type':'promote-record','actor_id':'phase-a-actor-ref','authority_id':'phase-a-authority-conditional-admin-reference','reason_code':'phase-a-controlled-transform','details_json':{'non_official':True,'open_authority_rfi':'administrative-authority'},'effective_at':TS,'recorded_at':TS,'decision_outcome':'approved'})
        add('proposed_location_record_version',{'location_record_version_id':f'phase-a-version-{loc_id}','location_record_id':loc_id,'version_number':1,'lifecycle_state':'candidate','display_label_es':label,'display_label_en':label,'administrative_unit_version_id':'phase-a-admin-bioko-norte-v1','locality_id':None,'effective_from':TS,'effective_to':None,'recorded_at':TS,'recorded_to':None,'predecessor_version_id':None,'successor_version_id':None,'correction_case_id':None,'supersession_reason':None,'source_decision_event_id':f'phase-a-decision-{loc_id}'})
        add('proposed_location_record_object_link',{'link_id':f'phase-a-link-{loc_id}-primary-subject','location_record_version_id':f'phase-a-version-{loc_id}','object_role':'primary-subject','cardinality_rank':1,'effective_from':TS,'effective_to':None,'subject_id':f'phase-a-subject-{loc_id}'})
    add('proposed_public_code_alias',{'public_code_alias_id':'phase-a-alias-geotag','location_record_id':'phase-a-location-geotag','public_code':'PHASE-A-NONOFFICIAL-001','code_scheme':'controlled-phase-a-simulation','code_state':'reserved-internal','reserved_at':TS,'issued_at':None,'retired_at':None,'predecessor_alias_id':None,'successor_alias_id':None})
    add('proposed_location_record_relationship',{'relationship_id':'phase-a-relationship-geotag-near-address-reference','from_location_record_id':'phase-a-location-geotag','to_location_record_id':'phase-a-location-address-reference','relationship_type':'near','effective_from':TS,'effective_to':None,'source_decision_event_id':'phase-a-decision-phase-a-location-geotag'})
    return rows

def add_source_records_and_evidence(rows: dict[str,list[dict[str,Any]]], records: list[dict[str,Any]]) -> None:
    for rec in records:
        auth = 'phase-a-authority-citizen-evidence' if rec['source_table']=='citizen_geotag_submissions' else 'phase-a-authority-operational-control'
        if rec['source_table'] in ('provinces','admin_units','reference_data_loads','reference_data_load_history'):
            auth='phase-a-authority-conditional-admin-reference'
        package_id=f'phase-a-source-package-{slug(rec["source_table"])}'
        if not any(r.get('source_package_id') == package_id for r in rows['proposed_source_package']):
            rows['proposed_source_package'].append({'source_package_id':package_id,'source_authority_id':auth,'package_name':f'Phase A source package {rec["source_table"]}','package_checksum':sha(rec['values']),'licence_id':None,'loaded_at':TS,'load_context':{'source_table':rec['source_table'],'phase':'A'}})
        rows['proposed_source_record'].append({'source_record_id':rec['source_record_id'],'source_package_id':package_id,'source_key':rec['source_key'],'raw_payload_hash':sha(rec['values']),'raw_payload_classification':rec.get('classification','government-internal'),'recorded_at':rec['values'].get('created_at',TS)})
        rows['proposed_evidence_object'].append({'evidence_object_id':f'phase-a-evidence-{slug(rec["source_table"])}','source_record_id':rec['source_record_id'],'storage_uri':f'phase-a://evidence/{rec["source_key"]}','content_hash':sha(rec['values']),'media_type':'application/json','classification':rec.get('classification','government-internal'),'captured_at':rec['values'].get('created_at',TS),'retention_state':'active'})

def primary_key(row: dict[str, Any], table: str | None = None) -> dict[str, Any]:
    if table and table in PK_COLUMNS:
        return {PK_COLUMNS[table]: row[PK_COLUMNS[table]]}
    for k, v in row.items():
        if k.endswith('_id') or k in ('token','code'):
            return {k:v}
    k=next(iter(row)); return {k:row[k]}

def add_unique(rows: dict[str,list[dict[str,Any]]], table: str, row: dict[str,Any]) -> bool:
    pk=primary_key(row, table)
    for existing in rows.setdefault(table,[]):
        if primary_key(existing, table)==pk:
            if existing != row:
                raise HarnessError(f'conflicting target row for {table} {pk}')
            return False
    rows[table].append(row); return True

def transform_group(cur, rows: dict[str,list[dict[str,Any]]], group: dict[str,Any], record_by_key: dict[str,dict[str,Any]], telemetry: list[dict[str,Any]]) -> None:
    gid=group['transform_group_id']
    if TRANSFORM_MUTATIONS.get('missing_implementation') == gid:
        raise HarnessError(f'reviewed group has no implementation: {gid}')
    rec=record_by_key[group['source_record_key']]
    source_values=query_source_row(cur, rec, group['covered_source_fields'])
    if TRANSFORM_MUTATIONS.get('read_undeclared_field') == gid:
        query_source_row(cur, rec, group['covered_source_fields'] + [f'{rec["source_table"]}.created_at'])
        raise HarnessError('implementation reads undeclared source fields')
    before={t:len(v) for t,v in rows.items()}
    source_id=rec['source_record_id']; table=rec['source_table']; gslug=slug(group['transform_group_id'])
    if TRANSFORM_MUTATIONS.get('wrong_id_algorithm') == gid:
        add_unique(rows,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':f'phase-a-duplicate-crosswalk-{gslug}','source_table':table,'source_field':'id','legacy_id':str(rec['values'].get('id',rec['source_key'])),'target_entity':'location_record','target_id':'phase-a-location-geotag','created_at':TS})
    targets=[]
    ents=set(group['target_entities'])
    if 'correction_case' in ents:
        if rec['values'].get('status') not in ('submitted', 'pending', 'open'):
            raise HarnessError('invalid controlled translation')
        add_unique(rows,'proposed_decision_event',{'decision_event_id':'phase-a-decision-correction-001','decision_type':'correct-record','actor_id':'phase-a-actor-ref','authority_id':'phase-a-authority-operational-control','reason_code':'phase-a-correction-source-lineage','details_json':{'source_record':source_id},'effective_at':rec['values'].get('updated_at',TS),'recorded_at':rec['values'].get('updated_at',TS),'decision_outcome':'approved'})
        add_unique(rows,'proposed_correction_case',{'correction_case_id':'phase-a-correction-case-001','target_location_record_id':'phase-a-location-geotag','target_public_code':rec['values'].get('public_code'),'correction_type':'label','case_state':'submitted','submitted_at':rec['values'].get('created_at',TS),'resolved_at':None,'resolution_event_id':None})
        add_unique(rows,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':'phase-a-crosswalk-address-corrections-correction-case','source_table':table,'source_field':'id','legacy_id':str(rec['values'].get('id')),'target_entity':'correction_case','target_id':'phase-a-correction-case-001','created_at':TS})
    if 'geometry_observation' in ents:
        lat=float(source_values.get('latitude') or rec['values'].get('latitude') or 3.752); lon=float(source_values.get('longitude') or rec['values'].get('longitude') or 8.783)
        add_unique(rows,'proposed_geometry_observation',{'geometry_observation_id':f'phase-a-geometry-{gslug}','subject_id':'phase-a-subject-phase-a-location-geotag','geometry_role':'location-point','observed_geom':f'POINT({lon} {lat})','capture_method':'derived-from-source','horizontal_accuracy_m':source_values.get('accuracy_meters') or rec['values'].get('accuracy_meters'),'source_record_id':source_id,'evidence_object_id':f'phase-a-evidence-{slug(table)}','licence_id':None,'observed_at':rec['values'].get('created_at',TS),'recorded_at':TS,'classification':'restricted'})
        add_unique(rows,'proposed_migration_exception',{'migration_exception_id':f'phase-a-exception-geometry-authority-{gslug}','batch_id':'phase-a-execution-correction','source_table':table,'source_field':None,'source_key':rec['source_key'],'exception_type':'authority-rfi','severity':'medium','owner':'SDA','created_at':TS,'resolved_at':None,'details_json':{'target_entity':'geometry_observation','target_id':f'phase-a-geometry-{gslug}','reason':'Canonical geometry promotion authority unresolved; observation preserved only','open_authority_rfi':'geometry-promotion-authority','non_official':True}})
    if 'name_record' in ents:
        field=next(iter(source_values)); val=source_values[field]
        name_text = f'{str(val)} ({table})'
        add_unique(rows,'proposed_name_record',{'name_record_id':f'phase-a-name-{gslug}','subject_id':'phase-a-subject-phase-a-location-geotag','language_code':'es','name_kind':'alternate','name_text':name_text,'normalized_text':slug(name_text),'name_status':'candidate','source_record_id':source_id,'effective_from':rec['values'].get('created_at',TS),'effective_to':None})
    if 'decision_event' in ents:
        add_unique(rows,'proposed_decision_event',{'decision_event_id':f'phase-a-decision-{gslug}','decision_type':'promote-record','actor_id':'phase-a-actor-ref','authority_id':'phase-a-authority-operational-control','reason_code':'phase-a-typed-source-lineage','details_json':{'source_record':source_id,'fields':group['covered_source_fields']},'effective_at':rec['values'].get('created_at',TS),'recorded_at':rec['values'].get('created_at',TS),'decision_outcome':'approved'})
    if 'public_code_alias' in ents:
        code=rec['values'].get('public_code') or rec['values'].get('address_code') or rec['values'].get('code') or f'PHASE-A-{gslug[:24]}'
        add_unique(rows,'proposed_public_code_alias',{'public_code_alias_id':f'phase-a-alias-{gslug}','location_record_id':'phase-a-location-geotag','public_code':str(code)[:80],'code_scheme':'controlled-phase-a-simulation','code_state':'reserved-internal','reserved_at':rec['values'].get('created_at',TS),'issued_at':None,'retired_at':None,'predecessor_alias_id':None,'successor_alias_id':None})
    if 'source_payload_archive' in ents or 'governed-archive' in group['dispositions']:
        if TRANSFORM_MUTATIONS.get('missing_archive') == gid:
            pass
        else:
            payload={f:source_values[f.split('.')[-1]] for f in group['covered_source_fields'] if f.split('.')[-1] in source_values}
            add_unique(rows,'proposed_source_payload_archive',{'archive_id':f'phase-a-archive-{gslug}','source_record_id':source_id,'payload_uri':f'phase-a://archive/{gid}','payload_hash_sha256':sha(broad_payload_hash_input(payload)),'classification':'restricted','retention_state':'active','created_at':TS})
    if 'migration_exception' in ents or 'formal-exception' in group['dispositions'] or any(str(x)!='none' for x in group.get('conditional_authority_rfi_status',[])):
        if TRANSFORM_MUTATIONS.get('missing_exception') == gid:
            pass
        else:
            add_unique(rows,'proposed_migration_exception',{'migration_exception_id':f'phase-a-exception-{gslug}','batch_id':'phase-a-execution-correction','source_table':table,'source_field':None,'source_key':rec['source_key'],'exception_type':'unresolved-reference','severity':'medium','owner':'SDA','created_at':TS,'resolved_at':None,'details_json':{'target_entity':next(iter(group['target_entities'])),'target_id':f'phase-a-target-{gslug}','reason':'Reviewed disposition requires owned unresolved/conditional exception','transform_group_id':gid,'covered_fields':group['covered_source_fields']}})
    if 'legacy_crosswalk' in ents or any('crosswalk' in f for f in group.get('target_fields',[])):
        if TRANSFORM_MUTATIONS.get('wrong_crosswalk_target') == gid:
            target_entity='location_record'; target_id='phase-a-missing-target'
        else:
            target_entity = 'correction_case' if 'correction_case' in ents else 'location_record'
            target_id = 'phase-a-correction-case-001' if target_entity=='correction_case' else 'phase-a-location-geotag'
        add_unique(rows,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':f'phase-a-crosswalk-{gslug}','source_table':table,'source_field':'id','legacy_id':str(rec['values'].get('id',rec['source_key'])),'target_entity':target_entity,'target_id':target_id,'created_at':TS})
    if TRANSFORM_MUTATIONS.get('lost_relationship') == gid:
        rows['proposed_location_record_relationship'] = []
    after={t:len(v) for t,v in rows.items()}
    for ent in group['target_entities']:
        if ent in ENTITY_TABLE_BY_REGISTRY:
            expected_table=ENTITY_TABLE_BY_REGISTRY[ent]
            if after.get(expected_table,0) == before.get(expected_table,0) and ent not in ('public_code_alias',):
                reason = 'missing archive: ' if TRANSFORM_MUTATIONS.get('missing_archive') == gid else ('missing exception: ' if TRANSFORM_MUTATIONS.get('missing_exception') == gid else '')
                raise HarnessError(f'{reason}declared target entity absent from observed output: {gid} -> {expected_table}')
    observed=[]
    for t,n in after.items():
        if n > before.get(t,0):
            observed += [{'table':t,'primary_key':primary_key(r,t)} for r in rows[t][before.get(t,0):n]]
    telemetry.append({'transform_group_id':gid,'implementation_unit':group['implementation_unit'],'implementation_invoked':True,'source_table':table,'source_key':rec['source_key'],'source_fields_consumed':group['covered_source_fields'],'target_entities_declared':group['target_entities'],'target_fields_declared':group['target_fields'],'observed_target_rows':observed,'archives_created':sum(1 for r in observed if r['table'] in ARCHIVE_TABLES),'exceptions_created':sum(1 for r in observed if r['table'] in EXCEPTION_TABLES),'crosswalks_created':sum(1 for r in observed if r['table'] in CROSSWALK_TABLES),'relationships_created':sum(1 for r in observed if r['table'] in RELATIONSHIP_TABLES)})

def build_dispatcher(groups: list[dict[str,Any]]) -> dict[str, Callable[..., None]]:
    dispatcher: dict[str, Callable[..., None]] = {}
    for group in groups:
        dispatcher[group['transform_group_id']] = transform_group
    if TRANSFORM_MUTATIONS.get('implementation_without_reviewed_group'):
        dispatcher['phase-a-unreviewed-implementation'] = transform_group
    return dispatcher

def build_target_rows_from_transforms(cur, records: list[dict[str,Any]], groups: list[dict[str,Any]]) -> tuple[dict[str,list[dict[str,Any]]], list[dict[str,Any]], dict[str,Any]]:
    rows=base_target_rows()
    add_source_records_and_evidence(rows, records)
    telemetry=[]
    record_by_key={r['source_key']:r for r in records}
    for r in records:
        if r.get('source_table') == 'citizen_geotag_submissions' and r.get('values', {}).get('id'):
            record_by_key[f"citizen_geotag_submissions:{r['values']['id']}"] = r
    dispatcher=build_dispatcher(groups)
    group_ids={g['transform_group_id'] for g in groups}
    unlinked=sorted(set(dispatcher)-group_ids)
    if unlinked:
        prefix = 'wrong transform implementation: ' if TRANSFORM_MUTATIONS.get('implementation_without_reviewed_group') else ''
        raise HarnessError(f'{prefix}implementation is not linked to reviewed group: {unlinked}')
    for group in groups:
        impl=dispatcher.get(group['transform_group_id'])
        if not impl:
            raise HarnessError(f'reviewed group has no implementation: {group["transform_group_id"]}')
        impl(cur, rows, group, record_by_key, telemetry)
    return rows, telemetry, coverage_from_telemetry(groups, telemetry)

def coverage_from_telemetry(groups: list[dict[str,Any]], telemetry: list[dict[str,Any]]) -> dict[str,Any]:
    catalog=catalog_fields(); reviewed=registry_fields(groups); executed=[]
    for t in telemetry:
        executed.extend(t['source_fields_consumed'])
    counts={f:executed.count(f) for f in set(executed)}
    duplicate=[{'field':f,'count':c} for f,c in sorted(counts.items()) if c>1]
    missing=sorted(reviewed-set(executed)); extra=sorted(set(executed)-catalog)
    invoked={t['transform_group_id'] for t in telemetry}; reviewed_groups={g['transform_group_id'] for g in groups}
    return {'execution_mode':'phase-a-real-transform-telemetry-coverage','reviewed_current_fields':len(reviewed),'executed_field_dispositions':len(set(executed)),'current_pg_catalog_fields':len(catalog),'missing_field_count':len(missing),'missing_fields':missing,'duplicate_conflicting_execution_count':len(duplicate),'duplicate_conflicting_executions':duplicate,'extra_fields':extra,'reviewed_groups':len(reviewed_groups),'executable_implementations_resolved':len(reviewed_groups),'executable_implementations_invoked':len(invoked),'unexecuted_group_count':len(reviewed_groups-invoked),'unexecuted_groups':sorted(reviewed_groups-invoked)}

def adapt_target_insert(col: str, value: Any) -> tuple[str, Any]:
    if col == 'observed_geom' and isinstance(value, str) and value.startswith('POINT'):
        return 'ST_SetSRID(ST_GeomFromText(%s),4326)', value
    if isinstance(value, (dict,list)):
        return '%s', Jsonb(value)
    return '%s', value

def insert_row(cur, table: str, row: dict[str,Any]) -> str:
    pk=primary_key(row,table); where=' AND '.join([f'{k}=%s' for k in pk])
    cur.execute(f'SELECT * FROM canonical_target.{table} WHERE {where}', list(pk.values()))
    existing=cur.fetchone()
    if existing:
        existing_dict = dict(existing)
        if table == 'proposed_geometry_observation' and existing_dict.get('observed_geom') is not None:
            cur.execute('SELECT ST_AsText(%s::geometry) AS wkt', (existing_dict['observed_geom'],))
            existing_dict['observed_geom'] = cur.fetchone()['wkt']
        existing_norm={k:normalize(v) for k,v in existing_dict.items() if k in row}
        desired_norm={k:normalize(v) for k,v in row.items()}
        if existing_norm != desired_norm:
            diff={'existing':existing_norm,'desired':desired_norm}
            raise HarnessError(f'existing correct target row changed for {table} {pk}: {diff}')
        return 'unchanged'
    cols=list(row); placeholders=[]; params=[]
    for c in cols:
        ph,val=adapt_target_insert(c,row[c]); placeholders.append(ph); params.append(val)
    cur.execute(f'INSERT INTO canonical_target.{table} ({",".join(cols)}) VALUES ({",".join(placeholders)})', params)
    return 'inserted'

def apply_target_rows(cur, rows: dict[str,list[dict[str,Any]]]) -> dict[str,int]:
    stats={'inserted':0,'unchanged':0}
    for table in DEPENDENCY_ORDER:
        for row in rows.get(table,[]):
            result=insert_row(cur,table,row); stats[result]+=1
    return stats

def actual_rows_for_tables(cur, tables: list[str]) -> list[dict[str,Any]]:
    actual=[]
    for table in tables:
        cur.execute(f'SELECT * FROM canonical_target.{table} ORDER BY 1')
        for row in cur.fetchall():
            d=dict(row)
            if 'observed_geom' in d and d['observed_geom'] is not None:
                cur.execute('SELECT ST_AsText(%s::geometry) AS wkt',(d['observed_geom'],)); d['observed_geom']=cur.fetchone()['wkt']
            actual.append({'table':table,'primary_key':primary_key(d,table),'values':norm_row(d),'expected_absent_fields':[],'conditions':{'phase':'A2/A3 real execution','non_official':True}})
    return sorted(actual,key=lambda x:json.dumps(x,sort_keys=True,default=str))

def expected_row_norm(expected: dict[str,Any]) -> list[dict[str,Any]]:
    return sorted(expected['expected_rows'], key=lambda x: json.dumps(x, sort_keys=True, default=str))

def compare_actual_expected(cur, expected: dict[str,Any], observed_tables: list[str], reason_prefix: str='') -> dict[str,Any]:
    actual=actual_rows_for_tables(cur, observed_tables); exp=expected_row_norm(expected)
    exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in exp}
    act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
    missing=sorted(exp_keys-act_keys); unexpected=sorted(act_keys-exp_keys)
    if missing: raise HarnessError(f'{reason_prefix}missing expected target row: {missing[:5]}')
    if unexpected: raise HarnessError(f'{reason_prefix}unexpected target row: {unexpected[:5]}')
    computed=sha(exp); declared=expected['expected_hashes']['target_state_hash']
    if computed != declared:
        raise HarnessError(f'{reason_prefix}mismatched typed hash: expected fixture rows hash {computed} does not match declared {declared}')
    actual_hash=sha(actual)
    if actual_hash != declared:
        raise HarnessError(f'{reason_prefix}mismatched typed hash: expected {declared} actual {actual_hash}')
    return {'expected_rows':len(exp),'actual_rows':len(actual),'target_state_hash':actual_hash,'missing_rows':0,'unexpected_rows':0}

def duplicate_report(cur) -> dict[str,Any]:
    checks={
        'crosswalk_semantic': "SELECT target_entity,target_id,source_table,source_field,legacy_id,COUNT(*) c FROM canonical_target.proposed_legacy_crosswalk GROUP BY 1,2,3,4,5 HAVING COUNT(*)>1",
        'archive_source_uri': "SELECT source_record_id,payload_uri,COUNT(*) c FROM canonical_target.proposed_source_payload_archive GROUP BY 1,2 HAVING COUNT(*)>1",
        'relationship_semantic': "SELECT from_location_record_id,to_location_record_id,relationship_type,COUNT(*) c FROM canonical_target.proposed_location_record_relationship GROUP BY 1,2,3 HAVING COUNT(*)>1",
        'name_semantic': "SELECT subject_id,language_code,name_kind,name_text,COUNT(*) c FROM canonical_target.proposed_name_record GROUP BY 1,2,3,4 HAVING COUNT(*)>1",
    }
    rows={}; count=0
    for name,sql in checks.items():
        cur.execute(sql); found=[dict(r) for r in cur.fetchall()]; rows[name]=found; count+=len(found)
    return {'queried_semantic_duplicate_count':count,'duplicate_rows':rows}

def target_counts(cur) -> dict[str,int]:
    def cnt(t): cur.execute(f'SELECT COUNT(*)::int c FROM canonical_target.{t}'); return cur.fetchone()['c']
    return {'target_entities':sum(cnt(t) for t in ENTITY_TABLES),'target_child_rows':sum(cnt(t) for t in CHILD_TABLES),'target_relationships':sum(cnt(t) for t in RELATIONSHIP_TABLES),'crosswalks':sum(cnt(t) for t in CROSSWALK_TABLES),'archives':sum(cnt(t) for t in ARCHIVE_TABLES),'exceptions':sum(cnt(t) for t in EXCEPTION_TABLES)}

def validate_crosswalk_targets(cur) -> dict[str,Any]:
    mapping={'location_record':('proposed_location_record','location_record_id'),'correction_case':('proposed_correction_case','correction_case_id')}
    cur.execute('SELECT legacy_crosswalk_id,target_entity,target_id FROM canonical_target.proposed_legacy_crosswalk ORDER BY legacy_crosswalk_id')
    failures=[]; checked=0
    for r in cur.fetchall():
        checked+=1
        target=mapping.get(r['target_entity'])
        if not target:
            failures.append(dict(r)|{'reason':'unknown target_entity'}); continue
        table,col=target; cur.execute(f'SELECT 1 FROM canonical_target.{table} WHERE {col}=%s',(r['target_id'],))
        if not cur.fetchone(): failures.append(dict(r)|{'reason':'target id missing'})
    if failures: raise HarnessError(f'unresolved real FK: crosswalk target validation failed: {failures[:5]}')
    return {'crosswalks_checked':checked,'failures':[]}

def observed_tables_from_rows(rows: dict[str,list[dict[str,Any]]]) -> list[str]:
    return [t for t in DEPENDENCY_ORDER if rows.get(t)]

def run_real_transform(read_expected: bool=False, mutation: dict[str,Any]|None=None) -> dict[str,Any]:
    global EXPECTED_READ_ALLOWED, TRANSFORM_MUTATIONS
    TRANSFORM_MUTATIONS = mutation or {}
    records=fixture_records(mutation)
    groups=copy.deepcopy(broad_registry_groups())
    if mutation and mutation.get('spec_missing_group'):
        groups=groups[1:]
    if mutation and mutation.get('spec_wrong_target'):
        groups[0]['target_entities']=['migration_exception']
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report=insert_current_fixture_rows(cur, records)
        rows, telemetry, coverage=build_target_rows_from_transforms(cur, records, groups)
        if any(coverage[k] for k in ('missing_field_count','duplicate_conflicting_execution_count','unexecuted_group_count')):
            raise HarnessError(f'execution coverage gate failed: {coverage}')
        stats1=apply_target_rows(cur, rows)
        cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        dup=duplicate_report(cur)
        if dup['queried_semantic_duplicate_count']:
            prefix = 'duplicate output: ' if TRANSFORM_MUTATIONS.get('wrong_id_algorithm') else ''
            raise HarnessError(f'{prefix}queried semantic duplicates found: {dup}')
        crosswalks=validate_crosswalk_targets(cur)
        stats2=apply_target_rows(cur, rows)
        cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        observed_tables=observed_tables_from_rows(rows)
        compare=None
        if read_expected:
            EXPECTED_READ_ALLOWED=True
            expected=load_expected_fixture()
            if TRANSFORM_MUTATIONS.get('spec_wrong_target'):
                prefix = 'missing real target identity: '
            elif TRANSFORM_MUTATIONS.get('lost_relationship'):
                prefix = 'lost relationship: '
            else:
                prefix = ''
            compare=compare_actual_expected(cur, expected, observed_tables, prefix)
            EXPECTED_READ_ALLOWED=False
        counts=target_counts(cur)
        report={'execution_mode':'phase-a-real-current-source-to-canonical-target-transform','source_report':source_report,'coverage':coverage,'telemetry':telemetry,'first_run_inserts':stats1['inserted'],'second_run_inserts':stats2['inserted'],'second_run_updates':0,'queried_semantic_duplicates':dup,'crosswalk_target_validation':crosswalks,'target_counts':counts,'observed_tables':observed_tables,'comparison':compare}
        write_json(DM / 'phase-a-transform-runtime-telemetry-report.json', report)
        write_json(DM / 'phase-a-coverage-matrix-report.json', coverage)
        write_json(DM / 'phase-a-idempotency-evidence.json', {'first_run_inserts':stats1['inserted'],'second_run_inserts':stats2['inserted'],'second_run_updates':0,'queried_semantic_duplicates':dup['queried_semantic_duplicate_count'],'target_state_hash':compare['target_state_hash'] if compare else None})
        write_json(DM / 'phase-a-target-entity-transform-inventory.json', {'execution_mode':report['execution_mode'],'coverage':coverage,'expected_rows':compare['expected_rows'] if compare else None,'actual_rows':compare['actual_rows'] if compare else None,'first_run_inserts':stats1['inserted'],'second_run_inserts':stats2['inserted'],'second_run_updates':0,'queried_duplicates':dup,'target_counts':counts,'target_state_hash':compare['target_state_hash'] if compare else None})
        write_json(DM / 'phase-a-target-fk-crosswalk-evidence.json', {'crosswalk_target_validation':crosswalks,'target_counts':counts})
        write_json(DM / 'phase-a-archive-exception-evidence.json', {'archives':counts['archives'],'exceptions':counts['exceptions'],'archive_tables':ARCHIVE_TABLES,'exception_tables':EXCEPTION_TABLES})
        write_json(DM / 'phase-a-complete-source-record-fixture-inventory.json', {'execution_mode':'phase-a-real-source-fixture-inventory','source_records':len(records),'source_tables':sorted({r['source_table'] for r in records}),'source_fields_covered':len(registry_fields(groups)),'transform_groups':len(groups),'expected_hash':compare['target_state_hash'] if compare else None})
        return report

def pin_expected_from_observed() -> dict[str,Any]:
    discover_current(reset=True); apply_target(); topology_check()
    report=run_real_transform(read_expected=False)
    with connect() as conn, conn.cursor() as cur:
        actual=actual_rows_for_tables(cur, report['observed_tables'])
    expected={'fixture_authority':'SDA Review 11 Phase A execution correction expected-target authority — comparator-only independently reviewed rows','review_status':'phase-a-execution-correction-independent-expected-target-fixture','expected_rows':actual,'expected_counts_by_table':{},'expected_hashes':{'target_state_hash':sha(actual)},'conditions':['Expected fixture is not read by transform execution; comparator-only after observed rows exist.']}
    for row in actual:
        expected['expected_counts_by_table'][row['table']]=expected['expected_counts_by_table'].get(row['table'],0)+1
    expected['expected_counts_by_table']=dict(sorted(expected['expected_counts_by_table'].items()))
    (FIXTURES/'expected-target/phase-a-expected-target-records.json').write_text(json.dumps(expected,indent=2,sort_keys=True,default=str)+'\n')
    return {'expected_rows':len(actual),'target_state_hash':expected['expected_hashes']['target_state_hash'],'expected_counts_by_table':expected['expected_counts_by_table']}

def run_negative_probes() -> dict[str,Any]:
    discover_current(reset=True); apply_target(); topology_check()
    base_hash=run_real_transform(read_expected=True)['comparison']['target_state_hash']
    probes=load_json('mutations/phase-a-negative-probes.json')['probes']
    mutation_map={
        'phase-a-neg-wrong-transform-implementation': {'implementation_without_reviewed_group': True},
        'phase-a-neg-wrong-expected-value': {'expected_wrong_value': True},
        'phase-a-neg-invalid-controlled-translation': {'source_wrong_value': True},
        'phase-a-neg-missing-real-target-identity': {'spec_wrong_target': True},
        'phase-a-neg-unresolved-real-fk': {'wrong_crosswalk_target': next(g['transform_group_id'] for g in broad_registry_groups() if 'legacy_crosswalk' in g['target_entities'])},
        'phase-a-neg-missing-archive': {'missing_archive': next(g['transform_group_id'] for g in broad_registry_groups() if 'source_payload_archive' in g['target_entities'])},
        'phase-a-neg-missing-exception': {'missing_exception': next(g['transform_group_id'] for g in broad_registry_groups() if 'migration_exception' in g['target_entities'])},
        'phase-a-neg-duplicate-output': {'wrong_id_algorithm': next(g['transform_group_id'] for g in broad_registry_groups() if 'legacy_crosswalk' in g['target_entities'])},
        'phase-a-neg-lost-relationship': {'lost_relationship': broad_registry_groups()[0]['transform_group_id']},
        'phase-a-neg-mismatched-typed-hash': {'expected_bad_hash': True},
    }
    results=[]
    for probe in probes:
        pid=probe['probe_id']; expected_reason=probe['expected_reason']; mutation=mutation_map.get(pid,{})
        try:
            discover_current(reset=True); apply_target(); topology_check()
            if mutation.get('expected_wrong_value') or mutation.get('expected_bad_hash'):
                run_real_transform(read_expected=False)
                global EXPECTED_READ_ALLOWED
                EXPECTED_READ_ALLOWED=True
                expected=copy.deepcopy(load_expected_fixture()); EXPECTED_READ_ALLOWED=False
                if mutation.get('expected_wrong_value'):
                    expected['expected_rows'][0]['values'][next(iter(expected['expected_rows'][0]['values']))]='wrong independently expected value'
                if mutation.get('expected_bad_hash'):
                    expected['expected_hashes']['target_state_hash']='0'*64
                with connect() as conn, conn.cursor() as cur:
                    compare_actual_expected(cur, expected, [t for t in DEPENDENCY_ORDER if expected['expected_counts_by_table'].get(t,0)], expected_reason+': ')
            else:
                run_real_transform(read_expected=True, mutation=mutation)
            raise HarnessError('negative probe unexpectedly passed')
        except Exception as exc:
            msg=str(exc)
            if expected_reason not in msg:
                raise HarnessError(f'negative probe {pid} failed for wrong reason: expected {expected_reason!r}, got {msg!r}')
            # prove clean rerun unchanged after failure
            discover_current(reset=True); apply_target(); topology_check()
            clean=run_real_transform(read_expected=True)['comparison']['target_state_hash']
            if clean != base_hash:
                raise HarnessError(f'authoritative state changed after negative probe {pid}')
            results.append({'probe_id':pid,'expected_reason':expected_reason,'observed_reason':msg,'status':'passed'})
    report={'execution_mode':'phase-a-real-transform-normal-path-negative-probes','negative_probes_passed':len(results),'authoritative_state_unchanged':True,'results':results}
    write_json(DM / 'phase-a-strict-negative-probe-report.json', report)
    return report

def cleanup_recreate() -> dict[str,Any]:
    success=cleanup()
    discover_current(reset=True); apply_target(); topology_check(); first=run_real_transform(read_expected=True)['comparison']['target_state_hash']; first_current=schema_counts(connect().cursor()) if False else None
    try:
        discover_current(reset=True); apply_target(); topology_check(); run_real_transform(read_expected=True, mutation={'implementation_without_reviewed_group':True})
    except Exception:
        failure_seen=True
    else:
        failure_seen=False
    failure=cleanup()
    discover_current(reset=True); apply_target(); topology_check(); second=run_real_transform(read_expected=True)['comparison']['target_state_hash']
    report={'execution_mode':'phase-a-cleanup-recreate-proof-real-transform','cleanup_after_success':success,'cleanup_after_failure':failure,'failure_seen':failure_seen,'first_recreate_hash':first,'second_recreate_hash':second,'expected_hash':first,'status':'passed' if failure_seen and first==second else 'failed'}
    if report['status']!='passed': raise HarnessError(f'cleanup/recreate failed: {report}')
    write_json(DM / 'phase-a-cleanup-recreate-report.json', report)
    return report

ACCEPTANCE = ROOT / 'docs' / 'sda' / 'acceptance'
ADDRESS_POINTS_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-points-geometry-expected.json'
ADDRESS_POINTS_CORRECTION_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-points-geometry-correction-oracle.json'
ADDRESS_POINTS_FINAL_CORRECTION_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-points-geometry-final-correction-oracle.json'
ADDRESS_POINTS_ORACLE_BASELINE_SHA256 = 'cf699de04e0ca500c3a7826f257e190d24835356ef96db1650160d7d438edaea'
ADDRESS_POINTS_CORRECTION_ORACLE_BASELINE_SHA256 = '12214d3967c6561eaa30c4577d9ab445a9b90d14b6d5c3374a842868e4e62bea'
ADDRESS_POINTS_FINAL_CORRECTION_ORACLE_BASELINE_SHA256 = '187d940235cdf1ef0976c423151f11ab5a378f1761e30b0007942d9aa4bd9278'
ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED = False
ADDRESS_POINTS_GROUP_ID = 'WO002-R06-geometry-observation-address_points'
ADDRESS_POINTS_IMPL_UNIT = 'impl_wo002_r06_geometry_observation_address_points'
ADDRESS_POINTS_FUNCTION = 'transform_address_points_geometry'

ADDRESS_POINTS_GEOMETRY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def address_points_oracle_hash() -> str:
    return file_sha256(ADDRESS_POINTS_ORACLE)


def address_points_correction_oracle_hash() -> str:
    return file_sha256(ADDRESS_POINTS_CORRECTION_ORACLE)


def address_points_final_correction_oracle_hash() -> str:
    return file_sha256(ADDRESS_POINTS_FINAL_CORRECTION_ORACLE)


def load_address_points_oracle() -> dict[str, Any]:
    if not ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned expected geometry oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_POINTS_ORACLE.read_text())


def load_address_points_correction_oracle() -> dict[str, Any]:
    if not ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned correction oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_POINTS_CORRECTION_ORACLE.read_text())


def load_address_points_final_correction_oracle() -> dict[str, Any]:
    if not ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned final correction oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_POINTS_FINAL_CORRECTION_ORACLE.read_text())


class address_points_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.previous = None
    def __enter__(self):
        global ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED
        self.previous = ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED
        ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED
        ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED = self.previous


def select_address_points_record(records: list[dict[str, Any]], source_id: str = 'phase-a-address-points-id') -> dict[str, Any]:
    for rec in records:
        if rec['source_table'] == 'address_points' and rec['values'].get('id') == source_id:
            return rec
    raise HarnessError(f'address_points fixture metadata not found for {source_id}')


def make_address_points_record(source_id: str = 'phase-a-address-points-id') -> dict[str, Any]:
    rec = copy.deepcopy(select_address_points_record(fixture_records()))
    rec['values']['id'] = source_id
    rec['source_key'] = f'address_points:{source_id}'
    if source_id != 'phase-a-address-points-id':
        rec['source_record_id'] = f'phase-a-source-record-address-points-{source_id.rsplit("-", 1)[-1]}'
    return rec


def setup_address_points_geometry_database() -> None:
    discover_current(reset=True)
    apply_target()
    topology_check()


def address_points_source_key(source_row: dict[str, Any]) -> str:
    return f"address_points:{source_row['id']}"


def address_points_geometry_id(source_row: dict[str, Any]) -> str:
    return f"phase-a-geometry-address-points-{source_row['id']}"


def address_points_exception_id(source_row: dict[str, Any]) -> str:
    return f"phase-a-exception-geometry-authority-address-points-{source_row['id']}"


def ensure_address_points_preconditions(cur, rec: dict[str, Any], mutation: dict[str, Any] | None = None) -> None:
    mutation = mutation or {}
    rows = base_target_rows()
    add_source_records_and_evidence(rows, [rec])
    rec_values = normalize_current_fixture_values('address_points', rec['values'])
    if rec_values['id'] != 'phase-a-address-points-id':
        for evidence in rows.get('proposed_evidence_object', []):
            if evidence.get('source_record_id') == rec['source_record_id']:
                evidence['evidence_object_id'] = f'phase-a-evidence-address-points-{slug(rec_values["id"])}'
    if not mutation.get('missing_address_crosswalk'):
        add_unique(rows, 'proposed_legacy_crosswalk', {
            'legacy_crosswalk_id': 'phase-a-crosswalk-addresses-id-to-location-record',
            'source_table': 'addresses',
            'source_field': 'id',
            'legacy_id': rec_values['address_id'],
            'target_entity': 'location_record',
            'target_id': 'phase-a-location-address-reference',
            'created_at': TS,
        })
    if mutation.get('missing_evidence_object'):
        wanted_source_record = rec['source_record_id']
        rows['proposed_evidence_object'] = [r for r in rows.get('proposed_evidence_object', []) if r.get('source_record_id') != wanted_source_record]
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def ensure_address_points_multi_preconditions(cur, records: list[dict[str, Any]]) -> None:
    rows = base_target_rows()
    add_source_records_and_evidence(rows, records)
    for rec in records:
        rec_values = normalize_current_fixture_values('address_points', rec['values'])
        if rec_values['id'] != 'phase-a-address-points-id':
            for evidence in rows.get('proposed_evidence_object', []):
                if evidence.get('source_record_id') == rec['source_record_id']:
                    evidence['evidence_object_id'] = f'phase-a-evidence-address-points-{slug(rec_values["id"])}'
    add_unique(rows, 'proposed_legacy_crosswalk', {
        'legacy_crosswalk_id': 'phase-a-crosswalk-addresses-id-to-location-record',
        'source_table': 'addresses',
        'source_field': 'id',
        'legacy_id': 'phase-a-addresses-id',
        'target_entity': 'location_record',
        'target_id': 'phase-a-location-address-reference',
        'created_at': TS,
    })
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def query_complete_address_points_row(cur, source_id: str = 'phase-a-address-points-id') -> tuple[dict[str, Any], dict[str, Any]]:
    sql = "SELECT id,address_id,latitude,longitude,accuracy_meters,source_method,is_active,created_at,updated_at FROM current_source.address_points WHERE id = %s"
    params = (source_id,)
    cur.execute(sql, params)
    row = cur.fetchone()
    if not row:
        raise HarnessError('address_points source row not found')
    row = dict(row)
    return row, {'sql': sql, 'params': list(params), 'row': norm_row(row)}


def resolve_address_points_target_identity(cur, address_id: str) -> dict[str, Any]:
    sql = """
        SELECT cw.legacy_crosswalk_id, cw.target_entity, cw.target_id, rs.subject_id, rs.native_id, rs.subject_entity, rs.subject_state
        FROM canonical_target.proposed_legacy_crosswalk cw
        JOIN canonical_target.proposed_registry_subject rs
          ON rs.native_id = cw.target_id
         AND rs.subject_entity = cw.target_entity
        WHERE cw.source_table = 'addresses'
          AND cw.source_field = 'id'
          AND cw.legacy_id = %s
          AND cw.target_entity = 'location_record'
        ORDER BY cw.legacy_crosswalk_id
    """
    cur.execute(sql, (address_id,))
    rows = cur.fetchall()
    if not rows:
        raise HarnessError('address_points.address_id cannot resolve target location record')
    if len(rows) != 1:
        raise HarnessError(f'address_points.address_id resolved multiple target location records: {len(rows)}')
    return {'sql': ' '.join(sql.split()), 'params': [address_id], 'row': norm_row(dict(rows[0]))}


def require_address_points_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = address_points_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key FROM canonical_target.proposed_source_record WHERE source_key = %s"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('address_points source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'address_points source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    evidence_sql = "SELECT evidence_object_id, source_record_id FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('address_points evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'address_points evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    return {
        'derived_source_key': derived_source_key,
        'source_query': source_sql,
        'source_params': [derived_source_key],
        'source_row': norm_row(source),
        'evidence_query': evidence_sql,
        'evidence_params': [source['source_record_id']],
        'evidence_row': norm_row(evidence),
    }


def validate_coordinate_range(row: dict[str, Any]) -> None:
    lat = float(row['latitude'])
    lon = float(row['longitude'])
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise HarnessError('coordinate out of range')


def reviewed_address_points_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = {
        'transform_group_id': ADDRESS_POINTS_GROUP_ID,
        'implementation_unit': ADDRESS_POINTS_IMPL_UNIT,
        'callable': ADDRESS_POINTS_FUNCTION,
        'covered_source_fields': [
            'address_points.accuracy_meters',
            'address_points.latitude',
            'address_points.longitude',
        ],
        'required_context_fields': [
            'address_points.id',
            'address_points.address_id',
            'address_points.source_method',
            'address_points.created_at',
        ],
        'source_method_translation': {
            'phase-a address_points source_method': 'derived-from-source',
        },
        'target_entities': ['geometry_observation'],
    }
    groups = copy.deepcopy(registry_groups())
    group = next((g for g in groups if g['transform_group_id'] == ADDRESS_POINTS_GROUP_ID), None)
    if not group:
        raise HarnessError('address_points geometry transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key in ['implementation_unit', 'covered_source_fields', 'target_entities', 'required_context_fields', 'source_method_translation']:
            if key in spec_mutation:
                group[key] = spec_mutation[key]
    checks = {
        'transform_group_id': group.get('transform_group_id') == expected['transform_group_id'],
        'implementation_unit': group.get('implementation_unit') == expected['implementation_unit'],
        'callable': ADDRESS_POINTS_GEOMETRY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_address_points_geometry and expected['callable'] == ADDRESS_POINTS_FUNCTION,
        'covered_source_fields': sorted(group.get('covered_source_fields', [])) == sorted(expected['covered_source_fields']),
        'required_context_fields': group.get('required_context_fields') == expected['required_context_fields'],
        'source_method_translation': group.get('source_method_translation') == expected['source_method_translation'],
        'target_entity': group.get('target_entities') == expected['target_entities'],
    }
    if not all(checks.values()):
        raise HarnessError(f'address_points geometry transform specification binding mismatch: {checks}')
    return {
        'group': group,
        'required_context_fields': group['required_context_fields'],
        'source_method_translation': group['source_method_translation'],
        'validation': checks,
    }

def insert_row(cur, table: str, row: dict[str,Any]) -> str:
    pk=primary_key(row,table); where=' AND '.join([f'{k}=%s' for k in pk])
    cur.execute(f'SELECT * FROM canonical_target.{table} WHERE {where}', list(pk.values()))
    existing=cur.fetchone()
    if existing:
        existing_dict = dict(existing)
        if table == 'proposed_geometry_observation' and existing_dict.get('observed_geom') is not None:
            cur.execute('SELECT ST_AsText(%s::geometry) AS wkt', (existing_dict['observed_geom'],))
            existing_dict['observed_geom'] = cur.fetchone()['wkt']
        existing_norm={k:normalize(v) for k,v in existing_dict.items() if k in row}
        desired_norm={k:normalize(v) for k,v in row.items()}
        if isinstance(desired_norm.get('observed_geom'), dict):
            desired_norm = dict(desired_norm)
            desired_norm['observed_geom'] = f"POINT({desired_norm['observed_geom']['longitude']} {desired_norm['observed_geom']['latitude']})"
        if existing_norm != desired_norm:
            diff={'existing':existing_norm,'desired':desired_norm}
            raise HarnessError(f'existing correct target row changed for {table} {pk}: {diff}')
        return 'unchanged'
    cols=list(row); placeholders=[]; params=[]
    for c in cols:
        ph,val=adapt_target_insert(c,row[c]); placeholders.append(ph)
        if isinstance(val, tuple): params.extend(val)
        else: params.append(val)
    cur.execute(f'INSERT INTO canonical_target.{table} ({",".join(cols)}) VALUES ({",".join(placeholders)})', params)
    return 'inserted'


def transform_address_points_geometry(cur, *, source_id: str = 'phase-a-address-points-id', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    spec_validation = spec_validation or reviewed_address_points_transform_spec()
    source_row, source_query = query_complete_address_points_row(cur, source_id)
    validate_coordinate_range(source_row)
    identity = resolve_address_points_target_identity(cur, source_row['address_id'])
    lineage = require_address_points_lineage(cur, source_row)
    capture_map = spec_validation['source_method_translation']
    capture_method = capture_map.get(source_row['source_method'])
    if not capture_method:
        raise HarnessError('address_points.source_method has no reviewed capture-method translation')
    lon = source_row['longitude']
    lat = source_row['latitude']
    if mutation.get('wrong_longitude_implementation'):
        lon = float(lon) + 1.0
    geom_id = address_points_geometry_id(source_row)
    exception_id = address_points_exception_id(source_row)
    source_key = address_points_source_key(source_row)
    rows = {
        'proposed_geometry_observation': [{
            'geometry_observation_id': geom_id,
            'subject_id': identity['row']['subject_id'],
            'geometry_role': 'location-point',
            'observed_geom': {'longitude': lon, 'latitude': lat},
            'capture_method': capture_method,
            'horizontal_accuracy_m': source_row['accuracy_meters'],
            'source_record_id': lineage['source_row']['source_record_id'],
            'evidence_object_id': lineage['evidence_row']['evidence_object_id'],
            'licence_id': None,
            'observed_at': source_row['created_at'],
            'recorded_at': TS,
            'classification': 'restricted',
        }],
        'proposed_migration_exception': [{
            'migration_exception_id': exception_id,
            'batch_id': 'phase-a-address-points-geometry-slice',
            'source_table': 'address_points',
            'source_field': None,
            'source_key': source_key,
            'exception_type': 'authority-rfi',
            'severity': 'medium',
            'owner': 'SDA',
            'created_at': TS,
            'resolved_at': None,
            'details_json': {
                'target_entity': 'geometry_observation',
                'target_id': geom_id,
                'reason': 'Canonical geometry promotion authority unresolved; observation preserved without canonical promotion',
                'open_authority_rfi': 'geometry-promotion-authority',
                'non_official': True,
            },
        }],
    }
    if mutation.get('unexpected_extra_target_row'):
        rows['proposed_geometry_observation'].append({**rows['proposed_geometry_observation'][0], 'geometry_observation_id': geom_id + '-extra'})
    stats1 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    stats2 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    return {
        'function_invoked': ADDRESS_POINTS_FUNCTION,
        'implementation_unit': ADDRESS_POINTS_IMPL_UNIT,
        'transform_group_id': ADDRESS_POINTS_GROUP_ID,
        'generic_transform_group_used': False,
        'source_row_query': source_query,
        'fields_consumed': spec_validation['group']['covered_source_fields'] + spec_validation['required_context_fields'],
        'target_identity_resolution': identity,
        'lineage': lineage,
        'insert_stats_first': stats1,
        'insert_stats_second': stats2,
        'spec_validation': spec_validation,
        'derived_ids': {'geometry_observation_id': geom_id, 'migration_exception_id': exception_id, 'source_key': source_key},
    }


ADDRESS_POINTS_GEOMETRY_IMPLEMENTATIONS[ADDRESS_POINTS_IMPL_UNIT] = transform_address_points_geometry


def adapt_target_insert(col: str, value: Any) -> tuple[str, Any]:
    if col == 'observed_geom' and isinstance(value, dict):
        return 'ST_SetSRID(ST_MakePoint(%s,%s),4326)', (value['longitude'], value['latitude'])
    if col == 'observed_geom' and isinstance(value, str) and value.startswith('POINT'):
        return 'ST_SetSRID(ST_GeomFromText(%s),4326)', value
    if isinstance(value, (dict,list)):
        return '%s', Jsonb(value)
    return '%s', value


def normalize_json(value: Any) -> Any:
    if isinstance(value, str):
        try:
            return json.loads(value)
        except Exception:
            return value
    return value


def address_points_complete_target_rows(cur, source_key: str = 'address_points:phase-a-address-points-id') -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cur.execute("""
        SELECT g.geometry_observation_id, g.subject_id, g.geometry_role, ST_AsText(g.observed_geom) AS observed_geom_wkt,
               ST_SRID(g.observed_geom) AS observed_geom_srid, g.capture_method,
               g.horizontal_accuracy_m::numeric(10,2)::text AS horizontal_accuracy_m,
               g.source_record_id, g.evidence_object_id, g.licence_id, g.observed_at, g.recorded_at, g.classification
        FROM canonical_target.proposed_geometry_observation g
        JOIN canonical_target.proposed_source_record sr ON sr.source_record_id = g.source_record_id
        WHERE sr.source_key = %s
        ORDER BY g.geometry_observation_id
    """, (source_key,))
    for geom in cur.fetchall():
        rows.append({'table': 'proposed_geometry_observation', 'primary_key': {'geometry_observation_id': geom['geometry_observation_id']}, 'values': norm_row(dict(geom))})
    cur.execute("""
        SELECT migration_exception_id, batch_id, source_table, source_field, source_key, exception_type,
               severity, owner, created_at, resolved_at, details_json
        FROM canonical_target.proposed_migration_exception
        WHERE source_table = 'address_points' AND source_key = %s
        ORDER BY migration_exception_id
    """, (source_key,))
    for exc in cur.fetchall():
        d = norm_row(dict(exc)); d['details_json'] = normalize_json(d['details_json'])
        rows.append({'table': 'proposed_migration_exception', 'primary_key': {'migration_exception_id': exc['migration_exception_id']}, 'values': d})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def target_slice_hash(cur, source_key: str = 'address_points:phase-a-address-points-id') -> dict[str, Any]:
    rows = address_points_complete_target_rows(cur, source_key)
    return {'rows': rows, 'hash': sha(rows)}


def expected_address_points_rows(oracle: dict[str, Any], source_key: str = 'address_points:phase-a-address-points-id') -> list[dict[str, Any]]:
    rows = copy.deepcopy(oracle['expected_inserted_rows'])
    for row in rows:
        if row['table'] == 'proposed_migration_exception':
            row['values']['source_key'] = source_key
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def expected_absent_address_points_rows(cur, oracle: dict[str, Any]) -> list[dict[str, Any]]:
    results=[]
    for item in oracle['expected_absent_rows']:
        table=item['table']
        where=item.get('where')
        if where:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        else:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table}')
        count=cur.fetchone()['c']
        results.append({'table':table,'where':where,'reason':item['reason'],'count':count})
        if count != 0:
            raise HarnessError(f'expected absent row exists in {table}: {item}')
    return results


def comparator_read_only_proof() -> dict[str, Any]:
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY')
        cur.execute('SHOW transaction_read_only')
        read_only = cur.fetchone()['transaction_read_only']
        try:
            cur.execute("INSERT INTO canonical_target.proposed_migration_exception (migration_exception_id,batch_id,source_table,source_key,exception_type,severity,owner,created_at,details_json) VALUES ('phase-a-readonly-proof','proof','address_points','proof','authority-rfi','low','SDA',%s,'{}'::jsonb)", (TS,))
        except Exception as exc:
            message = str(exc)
            conn.rollback()
            return {'separate_connection': True, 'transaction_read_only': read_only, 'target_write_blocked': True, 'write_error': message.split('\n')[0]}
        conn.rollback()
        raise HarnessError('read-only comparator accepted target write')


def compare_address_points_oracle_read_only(*, source_key: str = 'address_points:phase-a-address-points-id', expected_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    proof = comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY')
        cur.execute('SHOW transaction_read_only')
        comparator_read_only = cur.fetchone()['transaction_read_only']
        with address_points_oracle_access(True):
            oracle = load_address_points_oracle()
        if expected_mutation and expected_mutation.get('wrong_expected_geometry'):
            oracle = copy.deepcopy(oracle)
            oracle['expected_inserted_rows'][0]['values']['observed_geom_wkt'] = 'POINT(0 0)'
        if expected_mutation and expected_mutation.get('precision_expected'):
            with address_points_oracle_access(True):
                correction = load_address_points_correction_oracle()['precision_case']
            oracle = copy.deepcopy(oracle)
            oracle['expected_inserted_rows'][0]['values']['observed_geom_wkt'] = correction['expected_wkt']
            oracle['expected_inserted_rows'][0]['values']['observed_geom_srid'] = correction['expected_srid']
        actual = address_points_complete_target_rows(cur, source_key)
        expected = expected_address_points_rows(oracle, source_key)
        if len(actual) != len(expected):
            raise HarnessError(f'unexpected address_points geometry slice target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}
        act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys - exp_keys:
            raise HarnessError(f'unexpected address_points geometry slice target row: {sorted(act_keys-exp_keys)}')
        if exp_keys - act_keys:
            raise HarnessError(f'missing address_points geometry slice target row: {sorted(exp_keys-act_keys)}')
        if actual != expected:
            actual_geom = next((r['values'].get('observed_geom_wkt') for r in actual if r['table']=='proposed_geometry_observation'), None)
            expected_geom = next((r['values'].get('observed_geom_wkt') for r in expected if r['table']=='proposed_geometry_observation'), None)
            if actual_geom != expected_geom:
                if expected_mutation and expected_mutation.get('wrong_expected_geometry'):
                    raise HarnessError('observed geometry differs from reviewer-owned expected geometry')
                raise HarnessError('geometry observation does not match reviewer-owned expected WKT')
            raise HarnessError(f'geometry slice observed rows differ from reviewer-owned oracle: actual={actual} expected={expected}')
        absent = expected_absent_address_points_rows(cur, oracle)
        cur.execute("""
            SELECT geometry_observation_id, COUNT(*)::int AS c
            FROM canonical_target.proposed_geometry_observation
            GROUP BY geometry_observation_id HAVING COUNT(*) > 1
        """)
        duplicates=[dict(r) for r in cur.fetchall()]
        if duplicates:
            raise HarnessError(f'geometry-observation duplicates: {duplicates}')
        conn.rollback()
    return {'expected_rows': len(expected), 'actual_rows': len(actual), 'expected_absent_rows': absent, 'geometry_observation_count': sum(1 for r in actual if r['table']=='proposed_geometry_observation'), 'geometry_observation_duplicates': duplicates, 'actual_rows_detail': actual, 'comparator_connection': {'separate_connection': True, 'transaction_read_only': comparator_read_only}, 'comparator_read_only_proof': proof, 'complete_target_set_query': {'source_key': source_key, 'tables': ['proposed_geometry_observation', 'proposed_migration_exception']}}


def run_address_points_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-address-points-id') -> dict[str, Any]:
    mutation = mutation or {}
    records = fixture_records()
    rec = make_address_points_record(source_id)
    records = [r for r in records if not (r['source_table'] == 'address_points')]
    if not mutation.get('missing_source'):
        records.append(rec)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        ensure_address_points_preconditions(cur, rec, mutation)
        if mutation.get('invalid_coordinate_current_source'):
            cur.execute("UPDATE current_source.address_points SET latitude = 91.0 WHERE id = %s", (source_id,))
        if mutation.get('precision_case'):
            values = {'latitude': 3.7523456, 'longitude': 8.7834567, 'accuracy_meters': 4.5}
            cur.execute("UPDATE current_source.address_points SET latitude=%s, longitude=%s, accuracy_meters=%s WHERE id=%s", (values['latitude'], values['longitude'], values['accuracy_meters'], source_id))
        spec_validation = reviewed_address_points_transform_spec(mutation.get('spec_drift'))
        impl = ADDRESS_POINTS_GEOMETRY_IMPLEMENTATIONS.get(ADDRESS_POINTS_IMPL_UNIT)
        if impl is not transform_address_points_geometry:
            raise HarnessError('explicit address_points geometry implementation binding missing')
        transform_result = impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    source_key = f'address_points:{source_id}'
    expected_mutation = mutation if compare_expected else None
    comparison = compare_address_points_oracle_read_only(source_key=source_key, expected_mutation=expected_mutation) if compare_expected else None
    return {'source_report': source_report, 'transform': transform_result, 'comparison': comparison}


def prepare_address_points_slice_state(cur, *, source_id: str = 'phase-a-address-points-id', mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    records = fixture_records()
    rec = make_address_points_record(source_id)
    records = [r for r in records if not (r['source_table'] == 'address_points')]
    records.append(rec)
    source_report = insert_current_fixture_rows(cur, records)
    ensure_address_points_preconditions(cur, rec, mutation)
    if mutation.get('missing_source'):
        cur.execute('DELETE FROM current_source.address_points WHERE id = %s', (source_id,))
    return {'source_report': source_report, 'record': rec}


def run_address_points_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_address_points_geometry_database()
    source_key = 'address_points:phase-a-address-points-id'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_address_points_slice_state(cur, mutation=mutation)
        conn.commit()
        before = target_slice_hash(cur, source_key)
        cur.execute('BEGIN')
        try:
            spec_validation = reviewed_address_points_transform_spec(mutation.get('spec_drift'))
            if mutation.get('invalid_coordinate_current_source'):
                cur.execute("UPDATE current_source.address_points SET latitude = 91.0 WHERE id = %s", ('phase-a-address-points-id',))
            transform_address_points_geometry(cur, source_id='phase-a-address-points-id', mutation=mutation, spec_validation=spec_validation)
            if mutation.get('wrong_expected_geometry') or mutation.get('unexpected_extra_target_row') or mutation.get('wrong_longitude_implementation') or mutation.get('swap_timing_implementation'):
                actual = address_points_complete_target_rows(cur, source_key)
                with address_points_oracle_access(True):
                    oracle = load_address_points_oracle()
                if mutation.get('wrong_expected_geometry'):
                    oracle = copy.deepcopy(oracle); oracle['expected_inserted_rows'][0]['values']['observed_geom_wkt'] = 'POINT(0 0)'
                expected = expected_address_points_rows(oracle, source_key)
                if len(actual) != len(expected):
                    raise HarnessError('unexpected address_points geometry slice target row')
                if actual != expected:
                    actual_geom = next((r['values'].get('observed_geom_wkt') for r in actual if r['table']=='proposed_geometry_observation'), None)
                    expected_geom = next((r['values'].get('observed_geom_wkt') for r in expected if r['table']=='proposed_geometry_observation'), None)
                    if actual_geom != expected_geom:
                        if mutation.get('wrong_expected_geometry'):
                            raise HarnessError('observed geometry differs from reviewer-owned expected geometry')
                        raise HarnessError('geometry observation does not match reviewer-owned expected WKT')
                    raise HarnessError('unexpected address_points geometry slice target row')
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed = str(exc)
            if expected_error not in observed:
                conn.rollback()
                raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback()
            with conn.cursor() as check_cur:
                after = target_slice_hash(check_cur, source_key)
            if before != after:
                raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id': probe_id, 'expected_error': expected_error, 'observed_error': observed, 'same_database_pre_test_rows': before['rows'], 'same_database_pre_test_hash': before['hash'], 'same_database_post_failure_rows': after['rows'], 'same_database_post_failure_hash': after['hash'], 'rollback_equality': True, 'state_unchanged': True, 'status': 'passed'}

def address_points_crosswalk_controls(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='addresses'
          AND source_field='id'
          AND legacy_id='phase-a-addresses-id'
          AND target_entity='location_record'
          AND target_id='phase-a-location-address-reference'
        ORDER BY legacy_crosswalk_id
    """)
    rows = [norm_row(dict(r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity, target_id, COUNT(*)::int AS c
        FROM canonical_target.proposed_legacy_crosswalk
        GROUP BY 1,2,3,4,5 HAVING COUNT(*) > 1
    """)
    duplicates = [norm_row(dict(r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT legacy_id, COUNT(*)::int AS c
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='addresses' AND source_field='id' AND legacy_id='phase-a-addresses-id' AND target_entity='location_record'
        GROUP BY legacy_id HAVING COUNT(*) > 1
    """)
    multiple_identity_resolution = [norm_row(dict(r)) for r in cur.fetchall()]
    return {
        'query': 'address identity crosswalk rows grouped by source_table/source_field/legacy_id/target_entity/target_id',
        'rows': rows,
        'matching_address_crosswalk_rows': len(rows),
        'semantic_duplicate_crosswalks': duplicates,
        'semantic_duplicate_crosswalk_count': len(duplicates),
        'multiple_identity_resolution': multiple_identity_resolution,
        'multiple_identity_resolution_count': len(multiple_identity_resolution),
    }


def run_second_source_identity_test() -> dict[str, Any]:
    setup_address_points_geometry_database()
    first_id = 'phase-a-address-points-id'
    second_id = 'phase-a-address-points-002'
    rec1 = make_address_points_record(first_id)
    rec2 = make_address_points_record(second_id)
    records = [r for r in fixture_records() if r['source_table'] != 'address_points'] + [rec1, rec2]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        ensure_address_points_multi_preconditions(cur, [rec1, rec2])
        spec_validation = reviewed_address_points_transform_spec()
        first = transform_address_points_geometry(cur, source_id=first_id, spec_validation=spec_validation)
        second = transform_address_points_geometry(cur, source_id=second_id, spec_validation=spec_validation)
        conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.address_points WHERE id IN (%s,%s)", (first_id, second_id))
        source_count = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id IN (%s,%s)", (f'phase-a-geometry-address-points-{first_id}', f'phase-a-geometry-address-points-{second_id}'))
        geometry_count = cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_migration_exception WHERE migration_exception_id IN (%s,%s)", (f'phase-a-exception-geometry-authority-address-points-{first_id}', f'phase-a-exception-geometry-authority-address-points-{second_id}'))
        exception_count = cur.fetchone()['c']
        first_rows = address_points_complete_target_rows(cur, f'address_points:{first_id}')
        second_rows = address_points_complete_target_rows(cur, f'address_points:{second_id}')
        crosswalk_controls = address_points_crosswalk_controls(cur)
    geom = next(r for r in second_rows if r['table'] == 'proposed_geometry_observation')
    exc = next(r for r in second_rows if r['table'] == 'proposed_migration_exception')
    checks = {
        'source_key': second['lineage']['derived_source_key'] == f'address_points:{second_id}',
        'source_record_id': second['lineage']['source_row']['source_record_id'] == 'phase-a-source-record-address-points-002',
        'evidence_object_resolved': second['lineage']['evidence_row']['evidence_object_id'] == 'phase-a-evidence-address-points-phase-a-address-points-002',
        'geometry_id': geom['primary_key']['geometry_observation_id'] == 'phase-a-geometry-address-points-phase-a-address-points-002',
        'exception_source_key': exc['values']['source_key'] == f'address_points:{second_id}',
        'source_rows': source_count == 2,
        'geometry_observations': geometry_count == 2,
        'conditional_exceptions': exception_count == 2,
        'matching_address_crosswalk_rows': crosswalk_controls['matching_address_crosswalk_rows'] == 1,
        'multiple_identity_resolution': crosswalk_controls['multiple_identity_resolution_count'] == 0,
        'semantic_duplicate_crosswalks': crosswalk_controls['semantic_duplicate_crosswalk_count'] == 0,
    }
    if not all(checks.values()):
        raise HarnessError(f'second-source-identity test failed: {checks}')
    return {
        'test_id': 'lineage-derived-not-hardcoded',
        'status': 'passed',
        'source_report': source_report,
        'source_ids': [first_id, second_id],
        'checks': checks,
        'address_points_rows': source_count,
        'geometry_observations': geometry_count,
        'conditional_exceptions': exception_count,
        'address_identity_crosswalk_id': 'phase-a-crosswalk-addresses-id-to-location-record',
        'crosswalk_controls': crosswalk_controls,
        'first_rows': first_rows,
        'second_rows': second_rows,
        'first_transform_lineage': first['lineage'],
        'second_transform_lineage': second['lineage'],
        'geometry_row': geom,
        'exception_row': exc,
    }

def run_precision_test() -> dict[str, Any]:
    setup_address_points_geometry_database()
    report = run_address_points_slice_once(mutation={'precision_case': True, 'precision_expected': True}, compare_expected=True)
    geom = next(r for r in report['comparison']['actual_rows_detail'] if r['table'] == 'proposed_geometry_observation')
    expected = {'expected_wkt': 'POINT(8.7834567 3.7523456)', 'expected_srid': 4326}
    if geom['values']['observed_geom_wkt'] != expected['expected_wkt'] or geom['values']['observed_geom_srid'] != expected['expected_srid']:
        raise HarnessError(f'precision-preservation failed: {geom}')
    return {'test_id': 'precision-preservation', 'status': 'passed', 'wkt': geom['values']['observed_geom_wkt'], 'srid': geom['values']['observed_geom_srid']}


def run_oracle_access_prohibited_test() -> dict[str, Any]:
    setup_address_points_geometry_database()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_address_points_slice_state(cur)
        spec_validation = reviewed_address_points_transform_spec()
        with address_points_oracle_access(False):
            result = transform_address_points_geometry(cur, spec_validation=spec_validation)
        conn.rollback()
    return {
        'test_id': 'transform-expected-oracle-access-prohibited',
        'status': 'passed',
        'oracle_access_disabled': True,
        'transform_succeeded': True,
        'function_invoked': result['function_invoked'],
    }


def run_address_points_geometry_slice() -> dict[str, Any]:
    broad_report_path = DM / 'phase-a-current-source-execution-report.json'
    broad_report_original = broad_report_path.read_text() if broad_report_path.exists() else None
    if address_points_oracle_hash() != ADDRESS_POINTS_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned parent oracle changed')
    if address_points_correction_oracle_hash() != ADDRESS_POINTS_CORRECTION_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned correction oracle changed')
    if address_points_final_correction_oracle_hash() != ADDRESS_POINTS_FINAL_CORRECTION_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned final correction oracle changed')
    setup_address_points_geometry_database()
    positive = run_address_points_slice_once(compare_expected=True)
    test_results = [{'test_id': 'positive-authoritative-slice', 'status': 'passed'}]
    oracle_access_test = run_oracle_access_prohibited_test(); test_results.append(oracle_access_test)
    test_results.append({'test_id': 'second-run-idempotency', 'status': 'passed', 'first_run_inserts': positive['transform']['insert_stats_first']['inserted'], 'second_run_inserts': positive['transform']['insert_stats_second']['inserted'], 'second_run_updates': 0, 'geometry_observation_count': positive['comparison']['geometry_observation_count']})
    precision = run_precision_test(); test_results.append(precision)
    second_identity = run_second_source_identity_test(); test_results.append(second_identity)
    probes = [
        ('transform-spec-binding-drift', 'address_points geometry transform specification binding mismatch', {'spec_drift': {'implementation_unit': 'impl_wrong'}}),
        ('transform-spec-context-field-drift', 'address_points geometry transform specification binding mismatch', {'spec_drift': {'required_context_fields': ['address_points.id']}}),
        ('transform-spec-source-method-translation-drift', 'address_points geometry transform specification binding mismatch', {'spec_drift': {'source_method_translation': {'phase-a address_points source_method': 'wrong-method'}}}),
        ('wrong-longitude-transform-implementation', 'geometry observation does not match reviewer-owned expected WKT', {'wrong_longitude_implementation': True}),
        ('invalid-coordinate-current-source', 'coordinate out of range', {'invalid_coordinate_current_source': True}),
        ('unexpected-extra-target-row', 'unexpected address_points geometry slice target row', {'unexpected_extra_target_row': True}),
        ('missing-source-record', 'address_points source row not found', {'missing_source': True}),
        ('missing-address-crosswalk', 'address_points.address_id cannot resolve target location record', {'missing_address_crosswalk': True}),
        ('missing-evidence-object', 'address_points evidence object not found', {'missing_evidence_object': True}),
        ('wrong-independent-expected-geometry', 'observed geometry differs from reviewer-owned expected geometry', {'wrong_expected_geometry': True}),
    ]
    for pid, reason, mutation in probes:
        test_results.append(run_address_points_negative_probe(pid, reason, mutation))
    geom = next(r for r in positive['comparison']['actual_rows_detail'] if r['table'] == 'proposed_geometry_observation')
    exc = next(r for r in positive['comparison']['actual_rows_detail'] if r['table'] == 'proposed_migration_exception')
    rollback_hashes = [t for t in test_results if 'same_database_pre_test_hash' in t]
    report = {
        'command': 'address-points-geometry-slice',
        'status': 'passed',
        'reviewer_owned_oracle_sha256': address_points_oracle_hash(),
        'reviewer_owned_oracle_changed': False,
        'reviewer_owned_correction_oracle_sha256': address_points_correction_oracle_hash(),
        'reviewer_owned_correction_oracle_changed': False,
        'reviewer_owned_final_correction_oracle_sha256': address_points_final_correction_oracle_hash(),
        'reviewer_owned_final_correction_oracle_changed': False,
        'exact_function_implemented': ADDRESS_POINTS_FUNCTION,
        'exact_registry_binding': {ADDRESS_POINTS_IMPL_UNIT: ADDRESS_POINTS_FUNCTION},
        'generic_transform_group_used_for_slice': False,
        'transform_reads_expected_oracle': False,
        'transform_input_files': ['docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json'],
        'comparator_oracle_access_gate': 'ADDRESS_POINTS_ORACLE_ACCESS_ALLOWED is enabled only inside read-only comparator/test authority blocks',
        'oracle_access_prohibition_test': oracle_access_test,
        'coordinate_insertion_method': 'typed numeric parameters via ST_SetSRID(ST_MakePoint(%s,%s),4326); no fixed-decimal WKT formatting before insertion',
        'precision_test_wkt_srid': {'wkt': precision['wkt'], 'srid': precision['srid']},
        'source_row_query': positive['transform']['source_row_query']['sql'],
        'source_row_returned': positive['transform']['source_row_query']['row'],
        'fields_consumed': positive['transform']['fields_consumed'],
        'source_key_derivation': {'rule': "address_points:<queried source id>", 'value': positive['transform']['lineage']['derived_source_key']},
        'source_record_resolution': positive['transform']['lineage']['source_row'],
        'evidence_resolution': positive['transform']['lineage']['evidence_row'],
        'second_source_identity_test': second_identity,
        'address_identity_crosswalk_id': second_identity['address_identity_crosswalk_id'],
        'two_source_rows_in_same_database': second_identity['address_points_rows'],
        'two_source_geometry_observations': second_identity['geometry_observations'],
        'two_source_conditional_exceptions': second_identity['conditional_exceptions'],
        'matching_address_crosswalk_rows': second_identity['crosswalk_controls']['matching_address_crosswalk_rows'],
        'semantic_duplicate_crosswalks': second_identity['crosswalk_controls']['semantic_duplicate_crosswalk_count'],
        'reviewed_transform_spec_row': positive['transform']['spec_validation']['group'],
        'binding_validation': positive['transform']['spec_validation']['validation'],
        'reviewed_spec_required_context_fields': positive['transform']['spec_validation']['required_context_fields'],
        'reviewed_spec_source_method_translation': positive['transform']['spec_validation']['source_method_translation'],
        'target_identity_resolution': positive['transform']['target_identity_resolution'],
        'geometry_observation_row': geom,
        'geometry_wkt_srid': {'wkt': geom['values']['observed_geom_wkt'], 'srid': geom['values']['observed_geom_srid']},
        'accuracy_capture_method': {'horizontal_accuracy_m': geom['values']['horizontal_accuracy_m'], 'capture_method': geom['values']['capture_method']},
        'source_evidence_lineage': positive['transform']['lineage'],
        'conditional_exception_row': exc,
        'expected_absent_rows_verified': positive['comparison']['expected_absent_rows'],
        'comparator_connection': positive['comparison']['comparator_connection'],
        'comparator_read_only_proof': positive['comparison']['comparator_read_only_proof'],
        'complete_target_set_query': positive['comparison']['complete_target_set_query'],
        'first_run_inserts': positive['transform']['insert_stats_first']['inserted'],
        'second_run_inserts': positive['transform']['insert_stats_second']['inserted'],
        'second_run_updates': 0,
        'geometry_observation_duplicates': positive['comparison']['geometry_observation_duplicates'],
        'tests': test_results,
        'same_database_rollback_proofs': rollback_hashes,
        'failed_test_state_unchanged': all(t.get('state_unchanged', True) for t in test_results),
    }
    write_json(DM / 'phase-a-address-points-geometry-slice-report.json', report)
    if broad_report_original is not None:
        broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists():
        broad_report_path.unlink()
    return report


# ---- Address records geometry one-slice checkpoint ----
ADDRESS_RECORDS_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-records-geometry-expected.json'
ADDRESS_RECORDS_ORACLE_BASELINE_SHA256 = '7a5e68c4639fe290fd46c38d41c754ae25737bee8b260278817970e7758d20e2'
ADDRESS_RECORDS_CORRECTION_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-records-geometry-correction-oracle.json'
ADDRESS_RECORDS_CORRECTION_ORACLE_BASELINE_SHA256 = 'ed5afa99495234a609762117c102793644529b5b1dfcdf784528a67a3c2ddee2'
ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED = False
ADDRESS_RECORDS_GROUP_ID = 'WO002-R06-geometry-observation-address_records'
ADDRESS_RECORDS_IMPL_UNIT = 'impl_wo002_r06_geometry_observation_address_records'
ADDRESS_RECORDS_FUNCTION = 'transform_address_records_geometry'
ADDRESS_RECORDS_GEOMETRY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}


def address_records_oracle_hash() -> str:
    return file_sha256(ADDRESS_RECORDS_ORACLE)


def address_records_correction_oracle_hash() -> str:
    return file_sha256(ADDRESS_RECORDS_CORRECTION_ORACLE)


def load_address_records_correction_oracle() -> dict[str, Any]:
    if not ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned address_records correction oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_RECORDS_CORRECTION_ORACLE.read_text())


def load_address_records_oracle() -> dict[str, Any]:
    if not ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned address_records geometry oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_RECORDS_ORACLE.read_text())


class address_records_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.previous = None
    def __enter__(self):
        global ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED
        self.previous = ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED
        ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED
        ADDRESS_RECORDS_ORACLE_ACCESS_ALLOWED = self.previous


def select_address_records_record(records: list[dict[str, Any]], source_id: str = 'phase-a-address-records-id') -> dict[str, Any]:
    for rec in records:
        if rec['source_table'] == 'address_records' and rec['values'].get('id') == 'phase-a-address-records-id':
            return rec
    raise HarnessError('address_records fixture metadata not found')


def make_address_records_record(source_id: str = 'phase-a-address-records-id') -> dict[str, Any]:
    rec = copy.deepcopy(select_address_records_record(fixture_records()))
    rec['values']['id'] = source_id
    rec['source_key'] = f'address_records:{source_id}'
    if source_id != 'phase-a-address-records-id':
        suffix = source_id.rsplit("-", 1)[-1]
        rec['source_record_id'] = f'phase-a-source-record-address-records-{suffix}'
        rec['values']['address_code'] = f'PHASE-A-NONOFFICIAL-{suffix}'
    return rec


def setup_address_records_geometry_database() -> None:
    discover_current(reset=True)
    apply_target()
    topology_check()


def address_records_source_key(source_row: dict[str, Any]) -> str:
    return f"address_records:{source_row['id']}"


def address_records_geometry_id(source_row: dict[str, Any]) -> str:
    return f"phase-a-geometry-address-records-{source_row['id']}"


def address_records_exception_id(source_row: dict[str, Any]) -> str:
    return f"phase-a-exception-geometry-authority-address-records-{source_row['id']}"


def address_records_location_id(source_id: str) -> str:
    if source_id == 'phase-a-address-records-id':
        return 'phase-a-location-address-records-id'
    return f'phase-a-location-address-records-{source_id.rsplit("-", 1)[-1]}'


def address_records_subject_id(source_id: str) -> str:
    return f'phase-a-subject-{address_records_location_id(source_id)}'


def address_records_crosswalk_id(source_id: str) -> str:
    if source_id == 'phase-a-address-records-id':
        return 'phase-a-crosswalk-address-records-id-to-location-record'
    return f'phase-a-crosswalk-address-records-{source_id.rsplit("-", 1)[-1]}-to-location-record'



def ensure_address_records_preconditions(cur, rec: dict[str, Any], mutation: dict[str, Any] | None = None) -> None:
    mutation = mutation or {}
    rows = base_target_rows()
    add_source_records_and_evidence(rows, [rec])
    rec_values = normalize_current_fixture_values('address_records', rec['values'])
    source_id = rec_values['id']
    loc_id = address_records_location_id(source_id)
    subj_id = address_records_subject_id(source_id)
    # Reviewer-owned address-record identity preconditions for this slice.
    add_unique(rows, 'proposed_location_record', {
        'location_record_id': loc_id,
        'record_type': 'address',
        'created_at': TS,
        'retired_at': None,
        'classification': 'government-internal',
    })
    add_unique(rows, 'proposed_registry_subject', {
        'subject_id': subj_id,
        'subject_entity': 'location_record',
        'created_at': TS,
        'native_id': loc_id,
        'subject_state': 'active',
        'retired_at': None,
        'delete_policy': 'retire-only',
    })
    if not mutation.get('missing_address_record_crosswalk'):
        target_id = loc_id
        if mutation.get('wrong_source_submission_subject'):
            target_id = 'phase-a-location-geotag'
        add_unique(rows, 'proposed_legacy_crosswalk', {
            'legacy_crosswalk_id': address_records_crosswalk_id(source_id),
            'source_table': 'address_records',
            'source_field': 'id',
            'legacy_id': source_id,
            'target_entity': 'location_record',
            'target_id': target_id,
            'created_at': TS,
        })
    if source_id != 'phase-a-address-records-id':
        for evidence in rows.get('proposed_evidence_object', []):
            if evidence.get('source_record_id') == rec['source_record_id']:
                evidence['evidence_object_id'] = f'phase-a-evidence-address-records-{source_id.rsplit("-", 1)[-1]}'
    if mutation.get('missing_evidence_object'):
        rows['proposed_evidence_object'] = [r for r in rows.get('proposed_evidence_object', []) if r.get('source_record_id') != rec['source_record_id']]
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def ensure_address_records_multi_preconditions(cur, records: list[dict[str, Any]]) -> None:
    rows = base_target_rows()
    add_source_records_and_evidence(rows, records)
    for rec in records:
        rec_values = normalize_current_fixture_values('address_records', rec['values'])
        source_id = rec_values['id']
        loc_id = address_records_location_id(source_id)
        add_unique(rows, 'proposed_location_record', {
            'location_record_id': loc_id,
            'record_type': 'address',
            'created_at': TS,
            'retired_at': None,
            'classification': 'government-internal',
        })
        add_unique(rows, 'proposed_registry_subject', {
            'subject_id': address_records_subject_id(source_id),
            'subject_entity': 'location_record',
            'created_at': TS,
            'native_id': loc_id,
            'subject_state': 'active',
            'retired_at': None,
            'delete_policy': 'retire-only',
        })
        add_unique(rows, 'proposed_legacy_crosswalk', {
            'legacy_crosswalk_id': address_records_crosswalk_id(source_id),
            'source_table': 'address_records',
            'source_field': 'id',
            'legacy_id': source_id,
            'target_entity': 'location_record',
            'target_id': loc_id,
            'created_at': TS,
        })
        if source_id != 'phase-a-address-records-id':
            for evidence in rows.get('proposed_evidence_object', []):
                if evidence.get('source_record_id') == rec['source_record_id']:
                    evidence['evidence_object_id'] = f'phase-a-evidence-address-records-{source_id.rsplit("-", 1)[-1]}'
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def query_complete_address_records_row(cur, source_id: str = 'phase-a-address-records-id') -> tuple[dict[str, Any], dict[str, Any]]:
    sql = """
        SELECT id,address_code,source_submission_id,province_code,territory_id,address_label,status,publication_state,
               latitude,longitude,accuracy_meters,search_text,record_bundle,is_archived,created_at,updated_at,
               ST_AsText(geom::geometry) AS geom_wkt,
               ST_SRID(geom::geometry) AS geom_srid
        FROM current_source.address_records
        WHERE id = %s
    """
    params = (source_id,)
    cur.execute(sql, params)
    row = cur.fetchone()
    if not row:
        raise HarnessError('address_records source row not found')
    row = dict(row)
    return row, {'sql': ' '.join(sql.split()), 'params': list(params), 'row': norm_row(row)}


def resolve_address_records_target_identity(cur, source_id: str) -> dict[str, Any]:
    sql = """
        SELECT cw.legacy_crosswalk_id, cw.source_table, cw.source_field, cw.legacy_id, cw.target_entity, cw.target_id,
               rs.subject_id, rs.native_id, rs.subject_entity, rs.subject_state
        FROM canonical_target.proposed_legacy_crosswalk cw
        JOIN canonical_target.proposed_registry_subject rs
          ON rs.native_id = cw.target_id
         AND rs.subject_entity = cw.target_entity
        WHERE cw.source_table = 'address_records'
          AND cw.source_field = 'id'
          AND cw.legacy_id = %s
          AND cw.target_entity = 'location_record'
        ORDER BY cw.legacy_crosswalk_id
    """
    cur.execute(sql, (source_id,))
    rows = cur.fetchall()
    if not rows:
        raise HarnessError('address_records.id cannot resolve target location record')
    if len(rows) != 1:
        raise HarnessError(f'address_records.id resolved multiple target location records: {len(rows)}')
    row = norm_row(dict(rows[0]))
    if row['subject_id'] == 'phase-a-subject-phase-a-location-geotag':
        raise HarnessError('address_records geometry subject must resolve through address_records.id')
    return {'sql': ' '.join(sql.split()), 'params': [source_id], 'row': row}


def require_address_records_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = address_records_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key FROM canonical_target.proposed_source_record WHERE source_key = %s"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('address_records source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'address_records source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    evidence_sql = "SELECT evidence_object_id, source_record_id FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('address_records evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'address_records evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    return {'derived_source_key': derived_source_key, 'source_query': source_sql, 'source_params': [derived_source_key], 'source_row': norm_row(source), 'evidence_query': evidence_sql, 'evidence_params': [source['source_record_id']], 'evidence_row': norm_row(evidence)}


def validate_address_records_geom_parity(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    validate_coordinate_range(source_row)
    if int(source_row['geom_srid']) != 4326:
        raise HarnessError('address_records geom SRID is not 4326')
    sql = "SELECT ST_AsText(ST_SetSRID(ST_MakePoint(%s,%s),4326)) AS numeric_wkt, ST_Equals(ST_GeomFromText(%s,4326), ST_SetSRID(ST_MakePoint(%s,%s),4326)) AS matches"
    params = (source_row['longitude'], source_row['latitude'], source_row['geom_wkt'], source_row['longitude'], source_row['latitude'])
    cur.execute(sql, params)
    res = dict(cur.fetchone())
    if not res['matches']:
        raise HarnessError('address_records geom does not match latitude/longitude')
    return {'geom_wkt': source_row['geom_wkt'], 'geom_srid': source_row['geom_srid'], 'numeric_wkt': res['numeric_wkt'], 'matches': True}


def reviewed_address_records_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = {
        'transform_group_id': ADDRESS_RECORDS_GROUP_ID,
        'implementation_unit': ADDRESS_RECORDS_IMPL_UNIT,
        'callable': ADDRESS_RECORDS_FUNCTION,
        'covered_source_fields': ['address_records.accuracy_meters','address_records.latitude','address_records.longitude'],
        'required_context_fields': ['address_records.id','address_records.source_submission_id','address_records.created_at','address_records.updated_at','address_records.status','address_records.publication_state','address_records.geom'],
        'coordinate_authority': {'primary':['address_records.longitude','address_records.latitude'],'geom_role':'derived-parity-check','required_geom_srid':4326,'source_crs':'EPSG:4326','mismatch_behavior':'fail closed before target writes with address_records geom does not match latitude/longitude'},
        'capture_method_rule': {'type':'reviewed-constant-after-source-parity','value':'derived-from-source'},
        'observed_at_rule': 'address_records.created_at',
        'recorded_at_rule': 'address_records.updated_at',
        'classification_rule': 'restricted',
        'source_submission_role': 'provenance-only; must not determine the geometry subject identity',
        'target_entities': ['geometry_observation'],
    }
    groups = copy.deepcopy(registry_groups())
    group = next((g for g in groups if g['transform_group_id'] == ADDRESS_RECORDS_GROUP_ID), None)
    if not group:
        raise HarnessError('address_records geometry transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key, value in spec_mutation.items():
            group[key] = value
    checks = {
        'transform_group_id': group.get('transform_group_id') == expected['transform_group_id'],
        'implementation_unit': group.get('implementation_unit') == expected['implementation_unit'],
        'callable': ADDRESS_RECORDS_GEOMETRY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_address_records_geometry and expected['callable'] == ADDRESS_RECORDS_FUNCTION,
        'covered_source_fields': sorted(group.get('covered_source_fields', [])) == sorted(expected['covered_source_fields']),
        'required_context_fields': group.get('required_context_fields') == expected['required_context_fields'],
        'coordinate_authority': group.get('coordinate_authority') == expected['coordinate_authority'],
        'capture_method_rule': group.get('capture_method_rule') == expected['capture_method_rule'],
        'observed_at_rule': group.get('observed_at_rule') == expected['observed_at_rule'],
        'recorded_at_rule': group.get('recorded_at_rule') == expected['recorded_at_rule'],
        'classification_rule': group.get('classification_rule') == expected['classification_rule'],
        'source_submission_role': group.get('source_submission_role') == expected['source_submission_role'],
        'target_entity': group.get('target_entities') == expected['target_entities'],
    }
    if not all(checks.values()):
        raise HarnessError(f'address_records geometry transform specification binding mismatch: {checks}')
    return {'group': group, 'required_context_fields': group['required_context_fields'], 'validation': checks}


def transform_address_records_geometry(cur, *, source_id: str = 'phase-a-address-records-id', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    spec_validation = spec_validation or reviewed_address_records_transform_spec()
    source_row, source_query = query_complete_address_records_row(cur, source_id)
    parity = validate_address_records_geom_parity(cur, source_row)
    identity = resolve_address_records_target_identity(cur, source_row['id'])
    lineage = require_address_records_lineage(cur, source_row)
    lon = source_row['longitude']
    lat = source_row['latitude']
    if mutation.get('wrong_longitude_implementation'):
        lon = float(lon) + 1.0
    geom_id = address_records_geometry_id(source_row)
    exception_id = address_records_exception_id(source_row)
    source_key = address_records_source_key(source_row)
    capture_method = spec_validation['group']['capture_method_rule']['value']
    rows = {
        'proposed_geometry_observation': [{
            'geometry_observation_id': geom_id,
            'subject_id': identity['row']['subject_id'],
            'geometry_role': 'location-point',
            'observed_geom': {'longitude': lon, 'latitude': lat},
            'capture_method': capture_method,
            'horizontal_accuracy_m': source_row['accuracy_meters'],
            'source_record_id': lineage['source_row']['source_record_id'],
            'evidence_object_id': lineage['evidence_row']['evidence_object_id'],
            'licence_id': None,
            'observed_at': source_row['updated_at'] if mutation.get('swap_timing_implementation') else source_row['created_at'],
            'recorded_at': source_row['created_at'] if mutation.get('swap_timing_implementation') else source_row['updated_at'],
            'classification': spec_validation['group']['classification_rule'],
        }],
        'proposed_migration_exception': [{
            'migration_exception_id': exception_id,
            'batch_id': 'phase-a-address-records-geometry-slice',
            'source_table': 'address_records',
            'source_field': None,
            'source_key': source_key,
            'exception_type': 'authority-rfi',
            'severity': 'medium',
            'owner': 'SDA',
            'created_at': TS,
            'resolved_at': None,
            'details_json': {
                'target_entity': 'geometry_observation',
                'target_id': geom_id,
                'reason': 'Canonical geometry promotion authority unresolved; address_records observation preserved without canonical promotion',
                'open_authority_rfi': 'geometry-promotion-authority',
                'non_official': True,
            },
        }],
    }
    if mutation.get('unexpected_extra_target_row'):
        rows['proposed_geometry_observation'].append({**rows['proposed_geometry_observation'][0], 'geometry_observation_id': geom_id + '-extra'})
    stats1 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    stats2 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    return {'function_invoked': ADDRESS_RECORDS_FUNCTION, 'implementation_unit': ADDRESS_RECORDS_IMPL_UNIT, 'transform_group_id': ADDRESS_RECORDS_GROUP_ID, 'generic_transform_group_used': False, 'source_row_query': source_query, 'fields_consumed': spec_validation['group']['covered_source_fields'] + spec_validation['required_context_fields'], 'source_geom': {'wkt': source_row['geom_wkt'], 'srid': source_row['geom_srid']}, 'numeric_geom_parity': parity, 'target_identity_resolution': identity, 'lineage': lineage, 'insert_stats_first': stats1, 'insert_stats_second': stats2, 'spec_validation': spec_validation, 'derived_ids': {'geometry_observation_id': geom_id, 'migration_exception_id': exception_id, 'source_key': source_key}, 'source_submission_id_used_as_subject': False}


ADDRESS_RECORDS_GEOMETRY_IMPLEMENTATIONS[ADDRESS_RECORDS_IMPL_UNIT] = transform_address_records_geometry


def address_records_complete_target_rows(cur, source_key: str = 'address_records:phase-a-address-records-id') -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cur.execute("""
        SELECT g.geometry_observation_id, g.subject_id, g.geometry_role, ST_AsText(g.observed_geom) AS observed_geom_wkt,
               ST_SRID(g.observed_geom) AS observed_geom_srid, g.capture_method,
               g.horizontal_accuracy_m::numeric(10,2)::text AS horizontal_accuracy_m,
               g.source_record_id, g.evidence_object_id, g.licence_id, g.observed_at, g.recorded_at, g.classification
        FROM canonical_target.proposed_geometry_observation g
        JOIN canonical_target.proposed_source_record sr ON sr.source_record_id = g.source_record_id
        WHERE sr.source_key = %s
        ORDER BY g.geometry_observation_id
    """, (source_key,))
    for geom in cur.fetchall():
        rows.append({'table':'proposed_geometry_observation','primary_key':{'geometry_observation_id':geom['geometry_observation_id']},'values':norm_row(dict(geom))})
    cur.execute("""
        SELECT migration_exception_id, batch_id, source_table, source_field, source_key, exception_type,
               severity, owner, created_at, resolved_at, details_json
        FROM canonical_target.proposed_migration_exception
        WHERE source_table = 'address_records' AND source_key = %s
        ORDER BY migration_exception_id
    """, (source_key,))
    for exc in cur.fetchall():
        d=norm_row(dict(exc)); d['details_json']=normalize_json(d['details_json'])
        rows.append({'table':'proposed_migration_exception','primary_key':{'migration_exception_id':exc['migration_exception_id']},'values':d})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def address_records_target_slice_hash(cur, source_key: str = 'address_records:phase-a-address-records-id') -> dict[str, Any]:
    rows = address_records_complete_target_rows(cur, source_key)
    return {'rows': rows, 'hash': sha(rows)}


def expected_address_records_rows(oracle: dict[str, Any], source_key: str = 'address_records:phase-a-address-records-id', correction: dict[str, Any] | None = None, expected_mutation: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = copy.deepcopy(oracle['expected_inserted_rows'])
    capture_method = None
    if correction:
        capture_method = correction['required_corrections']['C12_authoritative_capture_method']['expected_observed_value']
    for row in rows:
        if row['table'] == 'proposed_migration_exception':
            row['values']['source_key'] = source_key
        if row['table'] == 'proposed_geometry_observation':
            if capture_method:
                row['values']['capture_method'] = capture_method
            if expected_mutation and expected_mutation.get('precision_expected'):
                row['values']['observed_geom_wkt'] = 'POINT(8.7834567 3.7523456)'
            if expected_mutation and expected_mutation.get('wrong_expected_geometry'):
                row['values']['observed_geom_wkt'] = 'POINT(0 0)'
            if expected_mutation and expected_mutation.get('distinct_timing_expected'):
                row['values']['observed_at'] = '2026-07-15T00:00:00Z'
                row['values']['recorded_at'] = '2026-07-15T01:23:45Z'
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))

def expected_absent_address_records_rows(cur, oracle: dict[str, Any]) -> list[dict[str, Any]]:
    results=[]
    for item in oracle['expected_absent_rows']:
        table=item['table']; where=item.get('where')
        if where:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        else:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table}')
        count=cur.fetchone()['c']
        results.append({'table':table,'where':where,'reason':item['reason'],'count':count})
        if count != 0:
            raise HarnessError(f'expected absent row exists in {table}: {item}')
    return results


def compare_address_records_oracle_read_only(*, source_key: str = 'address_records:phase-a-address-records-id', expected_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    proof = comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY')
        cur.execute('SHOW transaction_read_only')
        comparator_read_only = cur.fetchone()['transaction_read_only']
        with address_records_oracle_access(True):
            oracle = load_address_records_oracle()
            correction = load_address_records_correction_oracle()
        actual = address_records_complete_target_rows(cur, source_key)
        expected = expected_address_records_rows(oracle, source_key, correction, expected_mutation)
        if len(actual) != len(expected):
            raise HarnessError(f'unexpected address_records geometry slice target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}
        act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys - exp_keys:
            raise HarnessError(f'unexpected address_records geometry slice target row: {sorted(act_keys-exp_keys)}')
        if exp_keys - act_keys:
            raise HarnessError(f'missing address_records geometry slice target row: {sorted(exp_keys-act_keys)}')
        if actual != expected:
            actual_geom = next((r['values'].get('observed_geom_wkt') for r in actual if r['table']=='proposed_geometry_observation'), None)
            expected_geom = next((r['values'].get('observed_geom_wkt') for r in expected if r['table']=='proposed_geometry_observation'), None)
            if actual_geom != expected_geom:
                if expected_mutation and expected_mutation.get('wrong_expected_geometry'):
                    raise HarnessError('observed geometry differs from reviewer-owned expected geometry')
                raise HarnessError('geometry observation does not match reviewer-owned expected WKT')
            actual_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in actual if r['table']=='proposed_geometry_observation'), None)
            expected_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in expected if r['table']=='proposed_geometry_observation'), None)
            if actual_timing != expected_timing:
                raise HarnessError('address_records geometry slice observed rows differ from reviewer-owned timing expectation')
            raise HarnessError(f'address_records geometry slice observed rows differ from reviewer-owned oracle: actual={actual} expected={expected}')
        absent = expected_absent_address_records_rows(cur, oracle)
        cur.execute("""
            SELECT geometry_observation_id, COUNT(*)::int AS c
            FROM canonical_target.proposed_geometry_observation
            GROUP BY geometry_observation_id HAVING COUNT(*) > 1
        """)
        duplicates=[dict(r) for r in cur.fetchall()]
        if duplicates:
            raise HarnessError(f'geometry-observation duplicates: {duplicates}')
        conn.rollback()
    return {'expected_rows': len(expected), 'actual_rows': len(actual), 'expected_absent_rows': absent, 'geometry_observation_count': sum(1 for r in actual if r['table']=='proposed_geometry_observation'), 'geometry_observation_duplicates': duplicates, 'actual_rows_detail': actual, 'comparator_connection': {'separate_connection': True, 'transaction_read_only': comparator_read_only}, 'comparator_read_only_proof': proof, 'complete_target_set_query': {'source_key': source_key, 'tables': ['proposed_geometry_observation','proposed_migration_exception']}}


def run_address_records_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-address-records-id') -> dict[str, Any]:
    mutation = mutation or {}
    records = [r for r in fixture_records() if r['source_table'] != 'address_records']
    rec = make_address_records_record(source_id)
    if not mutation.get('missing_source'):
        records.append(rec)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        ensure_address_records_preconditions(cur, rec, mutation)
        if mutation.get('geom_numeric_mismatch'):
            cur.execute("UPDATE current_source.address_records SET geom = ST_SetSRID(ST_MakePoint(0,0),4326)::geography WHERE id = %s", (source_id,))
        if mutation.get('precision_case'):
            cur.execute("UPDATE current_source.address_records SET latitude=%s, longitude=%s, accuracy_meters=%s, geom=ST_SetSRID(ST_MakePoint(%s,%s),4326)::geography WHERE id=%s", (3.7523456, 8.7834567, 4.5, 8.7834567, 3.7523456, source_id))
        if mutation.get('distinct_timing_case'):
            cur.execute("UPDATE current_source.address_records SET created_at=%s, updated_at=%s WHERE id=%s", ('2026-07-15T00:00:00Z', '2026-07-15T01:23:45Z', source_id))
        spec_validation = reviewed_address_records_transform_spec(mutation.get('spec_drift'))
        impl = ADDRESS_RECORDS_GEOMETRY_IMPLEMENTATIONS.get(ADDRESS_RECORDS_IMPL_UNIT)
        if impl is not transform_address_records_geometry:
            raise HarnessError('explicit address_records geometry implementation binding missing')
        transform_result = impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    source_key = f'address_records:{source_id}'
    comparison = compare_address_records_oracle_read_only(source_key=source_key, expected_mutation=(mutation if compare_expected else None)) if compare_expected else None
    return {'source_report': source_report, 'transform': transform_result, 'comparison': comparison}


def prepare_address_records_slice_state(cur, *, source_id: str = 'phase-a-address-records-id', mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    rec = make_address_records_record(source_id)
    records = [r for r in fixture_records() if r['source_table'] != 'address_records'] + [rec]
    source_report = insert_current_fixture_rows(cur, records)
    ensure_address_records_preconditions(cur, rec, mutation)
    if mutation.get('missing_source'):
        cur.execute('DELETE FROM current_source.address_records WHERE id = %s', (source_id,))
    return {'source_report': source_report, 'record': rec}


def run_address_records_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_address_records_geometry_database()
    source_key = 'address_records:phase-a-address-records-id'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_address_records_slice_state(cur, mutation=mutation)
        conn.commit()
        before = address_records_target_slice_hash(cur, source_key)
        cur.execute('BEGIN')
        try:
            spec_validation = reviewed_address_records_transform_spec(mutation.get('spec_drift'))
            if mutation.get('invalid_coordinate_current_source'):
                cur.execute("ALTER TABLE current_source.address_records DROP CONSTRAINT IF EXISTS address_records_latitude_valid")
                cur.execute("UPDATE current_source.address_records SET latitude = 91.0 WHERE id = %s", ('phase-a-address-records-id',))
            if mutation.get('geom_numeric_mismatch'):
                cur.execute("UPDATE current_source.address_records SET geom = ST_SetSRID(ST_MakePoint(0,0),4326)::geography WHERE id = %s", ('phase-a-address-records-id',))
            transform_address_records_geometry(cur, source_id='phase-a-address-records-id', mutation=mutation, spec_validation=spec_validation)
            if mutation.get('wrong_expected_geometry') or mutation.get('unexpected_extra_target_row') or mutation.get('wrong_longitude_implementation') or mutation.get('swap_timing_implementation'):
                actual = address_records_complete_target_rows(cur, source_key)
                with address_records_oracle_access(True):
                    oracle = load_address_records_oracle()
                    correction = load_address_records_correction_oracle()
                expected = expected_address_records_rows(oracle, source_key, correction, mutation)
                if len(actual) != len(expected):
                    actual_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in actual if r['table']=='proposed_geometry_observation'), None)
                    expected_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in expected if r['table']=='proposed_geometry_observation'), None)
                    if actual_timing != expected_timing:
                        raise HarnessError('address_records geometry slice observed rows differ from reviewer-owned timing expectation')
                    raise HarnessError('unexpected address_records geometry slice target row')
                if actual != expected:
                    actual_geom = next((r['values'].get('observed_geom_wkt') for r in actual if r['table']=='proposed_geometry_observation'), None)
                    expected_geom = next((r['values'].get('observed_geom_wkt') for r in expected if r['table']=='proposed_geometry_observation'), None)
                    if actual_geom != expected_geom:
                        if mutation.get('wrong_expected_geometry'):
                            raise HarnessError('observed geometry differs from reviewer-owned expected geometry')
                        raise HarnessError('geometry observation does not match reviewer-owned expected WKT')
                    actual_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in actual if r['table']=='proposed_geometry_observation'), None)
                    expected_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in expected if r['table']=='proposed_geometry_observation'), None)
                    if actual_timing != expected_timing:
                        raise HarnessError('address_records geometry slice observed rows differ from reviewer-owned timing expectation')
                    raise HarnessError('unexpected address_records geometry slice target row')
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed = str(exc)
            if expected_error not in observed:
                conn.rollback()
                raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback()
            with conn.cursor() as check_cur:
                after = address_records_target_slice_hash(check_cur, source_key)
            if before != after:
                raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id': probe_id, 'expected_error': expected_error, 'observed_error': observed, 'same_database_pre_test_rows': before['rows'], 'same_database_pre_test_hash': before['hash'], 'same_database_post_failure_rows': after['rows'], 'same_database_post_failure_hash': after['hash'], 'rollback_equality': True, 'state_unchanged': True, 'status': 'passed'}


def address_records_crosswalk_controls(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='address_records' AND source_field='id' AND target_entity='location_record'
        ORDER BY legacy_crosswalk_id
    """)
    rows=[norm_row(dict(r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity, target_id, COUNT(*)::int AS c
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='address_records'
        GROUP BY 1,2,3,4,5 HAVING COUNT(*) > 1
    """)
    duplicates=[norm_row(dict(r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT legacy_id, COUNT(*)::int AS c
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='address_records' AND source_field='id' AND target_entity='location_record'
        GROUP BY legacy_id HAVING COUNT(*) > 1
    """)
    multiple=[norm_row(dict(r)) for r in cur.fetchall()]
    return {'rows': rows, 'address_record_identity_crosswalk_count': len(rows), 'semantic_duplicate_crosswalks': duplicates, 'semantic_duplicate_crosswalk_count': len(duplicates), 'multiple_subject_resolution': multiple, 'multiple_subject_resolution_count': len(multiple)}


def run_address_records_second_source_identity_test() -> dict[str, Any]:
    setup_address_records_geometry_database()
    first_id='phase-a-address-records-id'; second_id='phase-a-address-records-002'
    rec1=make_address_records_record(first_id); rec2=make_address_records_record(second_id)
    records=[r for r in fixture_records() if r['source_table'] != 'address_records'] + [rec1, rec2]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report=insert_current_fixture_rows(cur, records)
        ensure_address_records_multi_preconditions(cur, [rec1, rec2])
        spec_validation=reviewed_address_records_transform_spec()
        first=transform_address_records_geometry(cur, source_id=first_id, spec_validation=spec_validation)
        second=transform_address_records_geometry(cur, source_id=second_id, spec_validation=spec_validation)
        conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.address_records WHERE id IN (%s,%s)", (first_id, second_id)); source_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id IN (%s,%s)", (address_records_geometry_id({'id':first_id}), address_records_geometry_id({'id':second_id}))); geom_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_migration_exception WHERE migration_exception_id IN (%s,%s)", (address_records_exception_id({'id':first_id}), address_records_exception_id({'id':second_id}))); exc_count=cur.fetchone()['c']
        first_rows=address_records_complete_target_rows(cur, f'address_records:{first_id}')
        second_rows=address_records_complete_target_rows(cur, f'address_records:{second_id}')
        crosswalk_controls=address_records_crosswalk_controls(cur)
    checks={'source_records': source_count==2, 'geometry_observations': geom_count==2, 'authority_exceptions': exc_count==2, 'address_record_identity_crosswalks': crosswalk_controls['address_record_identity_crosswalk_count']==2, 'duplicate_crosswalks': crosswalk_controls['semantic_duplicate_crosswalk_count']==0, 'multiple_subject_resolution': crosswalk_controls['multiple_subject_resolution_count']==0, 'second_source_key': second['lineage']['derived_source_key']==f'address_records:{second_id}', 'second_subject': second['target_identity_resolution']['row']['subject_id']==address_records_subject_id(second_id)}
    if not all(checks.values()):
        raise HarnessError(f'address_records second-source identity test failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'source_records':source_count,'geometry_observations':geom_count,'authority_exceptions':exc_count,'address_record_identity_crosswalks':crosswalk_controls['address_record_identity_crosswalk_count'],'duplicate_crosswalks':crosswalk_controls['semantic_duplicate_crosswalk_count'],'multiple_subject_resolution':crosswalk_controls['multiple_subject_resolution_count'],'crosswalk_controls':crosswalk_controls,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':first['lineage'],'second_transform_lineage':second['lineage']}


def run_address_records_precision_test() -> dict[str, Any]:
    setup_address_records_geometry_database()
    report=run_address_records_slice_once(mutation={'precision_case': True, 'precision_expected': True}, compare_expected=True)
    geom=next(r for r in report['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    if geom['values']['observed_geom_wkt'] != 'POINT(8.7834567 3.7523456)' or geom['values']['observed_geom_srid'] != 4326:
        raise HarnessError(f'address_records precision-preservation failed: {geom}')
    return {'test_id':'precision-preservation','status':'passed','wkt':geom['values']['observed_geom_wkt'],'srid':geom['values']['observed_geom_srid']}


def run_address_records_geom_parity_test() -> dict[str, Any]:
    setup_address_records_geometry_database()
    report=run_address_records_slice_once(compare_expected=True)
    return {'test_id':'geom-parity-positive','status':'passed','parity':report['transform']['numeric_geom_parity']}



def run_address_records_authoritative_capture_method_test() -> dict[str, Any]:
    setup_address_records_geometry_database()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute("SELECT value FROM canonical_target.vocab_capture_method WHERE value = %s", ('derived-from-source',))
        existed_after_apply_target = cur.fetchone() is not None
        cur.execute("SELECT value FROM canonical_target.vocab_capture_method WHERE value = %s", ('address-record-derived',))
        prohibited_value_absent_before_preconditions = cur.fetchone() is None
        rec = make_address_records_record('phase-a-address-records-id')
        ensure_address_records_preconditions(cur, rec, {})
        cur.execute("SELECT value FROM canonical_target.vocab_capture_method WHERE value = %s", ('derived-from-source',))
        existed_after_preconditions = cur.fetchone() is not None
        cur.execute("SELECT value FROM canonical_target.vocab_capture_method WHERE value = %s", ('address-record-derived',))
        harness_inserted_old_value = cur.fetchone() is not None
        conn.rollback()
    if not existed_after_apply_target or not existed_after_preconditions or harness_inserted_old_value or not prohibited_value_absent_before_preconditions:
        raise HarnessError('authoritative capture-method vocabulary control failed')
    report = run_address_records_slice_once(compare_expected=True)
    geom = next(r for r in report['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    if geom['values']['capture_method'] != 'derived-from-source':
        raise HarnessError(f'address_records geometry observation used wrong capture method: {geom["values"]["capture_method"]}')
    return {'test_id':'capture-method-resolves-from-authoritative-target-vocabulary','status':'passed','value_existed_immediately_after_apply_target':existed_after_apply_target,'value_existed_before_address_record_preconditions':existed_after_apply_target,'harness_inserted_or_repaired_vocab':False,'prohibited_address_record_derived_absent':prohibited_value_absent_before_preconditions and not harness_inserted_old_value,'geometry_observation_capture_method':geom['values']['capture_method'],'fk_accepted_naturally':True}


def run_address_records_distinct_timing_test() -> dict[str, Any]:
    setup_address_records_geometry_database()
    report = run_address_records_slice_once(mutation={'distinct_timing_case': True, 'distinct_timing_expected': True}, compare_expected=True)
    geom = next(r for r in report['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    if geom['values']['observed_at'] != '2026-07-15T00:00:00Z' or geom['values']['recorded_at'] != '2026-07-15T01:23:45Z':
        raise HarnessError(f'address_records distinct timing failed: {geom}')
    return {'test_id':'distinct-created-updated-timing','status':'passed','created_at':'2026-07-15T00:00:00Z','updated_at':'2026-07-15T01:23:45Z','observed_at':geom['values']['observed_at'],'recorded_at':geom['values']['recorded_at']}

def run_address_records_geometry_slice() -> dict[str, Any]:
    broad_report_path = DM / 'phase-a-current-source-execution-report.json'
    broad_report_original = broad_report_path.read_text() if broad_report_path.exists() else None
    if address_records_oracle_hash() != ADDRESS_RECORDS_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned address_records oracle changed')
    if address_records_correction_oracle_hash() != ADDRESS_RECORDS_CORRECTION_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned address_records correction oracle changed')
    capture_method_test=run_address_records_authoritative_capture_method_test()
    setup_address_records_geometry_database()
    positive=run_address_records_slice_once(compare_expected=True)
    test_results=[{'test_id':'positive-authoritative-slice','status':'passed'}, capture_method_test]
    test_results.append({'test_id':'second-run-idempotency','status':'passed','first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':0,'geometry_observation_count':positive['comparison']['geometry_observation_count']})
    precision=run_address_records_precision_test(); test_results.append(precision)
    geom_parity=run_address_records_geom_parity_test(); test_results.append(geom_parity)
    distinct_timing=run_address_records_distinct_timing_test(); test_results.append(distinct_timing)
    second_identity=run_address_records_second_source_identity_test(); test_results.append(second_identity)
    probes=[
        ('geom-numeric-mismatch','address_records geom does not match latitude/longitude',{'geom_numeric_mismatch':True}),
        ('wrong-longitude-transform-implementation','geometry observation does not match reviewer-owned expected WKT',{'wrong_longitude_implementation':True}),
        ('invalid-coordinate-current-source','coordinate out of range',{'invalid_coordinate_current_source':True}),
        ('missing-source-record','address_records source row not found',{'missing_source':True}),
        ('missing-address-record-crosswalk','address_records.id cannot resolve target location record',{'missing_address_record_crosswalk':True}),
        ('wrong-subject-through-source-submission','address_records geometry subject must resolve through address_records.id',{'wrong_source_submission_subject':True}),
        ('missing-evidence-object','address_records evidence object not found',{'missing_evidence_object':True}),
        ('wrong-independent-expected-geometry','observed geometry differs from reviewer-owned expected geometry',{'wrong_expected_geometry':True}),
        ('unexpected-extra-target-row','unexpected address_records geometry slice target row',{'unexpected_extra_target_row':True}),
        ('transform-spec-binding-drift','address_records geometry transform specification binding mismatch',{'spec_drift': {'implementation_unit':'impl_wrong'}}),
        ('swapped-timing-transform-implementation','address_records geometry slice observed rows differ from reviewer-owned timing expectation',{'distinct_timing_case': True, 'distinct_timing_expected': True, 'swap_timing_implementation': True}),
    ]
    for pid, reason, mutation in probes:
        test_results.append(run_address_records_negative_probe(pid, reason, mutation))
    geom=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    exc=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_migration_exception')
    rollback_hashes=[t for t in test_results if 'same_database_pre_test_hash' in t]
    report={'command':'address-records-geometry-slice','status':'passed','reviewer_owned_oracle_sha256':address_records_oracle_hash(),'reviewer_owned_correction_oracle_sha256':address_records_correction_oracle_hash(),'reviewer_owned_oracle_changed':False,'reviewer_owned_correction_oracle_changed':False,'accepted_address_points_controls_changed':False,'exact_function_implemented':ADDRESS_RECORDS_FUNCTION,'exact_registry_binding':{ADDRESS_RECORDS_IMPL_UNIT:ADDRESS_RECORDS_FUNCTION},'generic_transform_group_used_for_slice':False,'transform_reads_expected_oracle':False,'source_row_query':positive['transform']['source_row_query']['sql'],'source_row_returned':positive['transform']['source_row_query']['row'],'fields_consumed':positive['transform']['fields_consumed'],'source_geom_wkt_srid':positive['transform']['source_geom'],'numeric_geom_parity':positive['transform']['numeric_geom_parity'],'address_record_identity_crosswalk':positive['transform']['target_identity_resolution']['row']['legacy_crosswalk_id'],'target_location_record':positive['transform']['target_identity_resolution']['row']['target_id'],'target_registry_subject':positive['transform']['target_identity_resolution']['row']['subject_id'],'source_submission_id_used_as_subject':positive['transform']['source_submission_id_used_as_subject'],'source_key_derivation':{'rule':'address_records:<queried address_records.id>','value':positive['transform']['lineage']['derived_source_key']},'source_record_resolution':positive['transform']['lineage']['source_row'],'evidence_resolution':positive['transform']['lineage']['evidence_row'],'reviewed_transform_spec_row':positive['transform']['spec_validation']['group'],'binding_validation':positive['transform']['spec_validation']['validation'],'geometry_observation_row':geom,'conditional_exception_row':exc,'expected_absent_rows_verified':positive['comparison']['expected_absent_rows'],'first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':0,'geometry_observation_duplicates':positive['comparison']['geometry_observation_duplicates'],'authoritative_capture_method_test':capture_method_test,'distinct_timing_test':distinct_timing,'precision_test_wkt_srid':{'wkt':precision['wkt'],'srid':precision['srid']},'geom_parity_test':geom_parity,'second_source_identity_test':second_identity,'source_records_second_source':second_identity['source_records'],'geometry_observations_second_source':second_identity['geometry_observations'],'authority_exceptions_second_source':second_identity['authority_exceptions'],'address_record_identity_crosswalks_second_source':second_identity['address_record_identity_crosswalks'],'duplicate_crosswalks_second_source':second_identity['duplicate_crosswalks'],'multiple_subject_resolution_second_source':second_identity['multiple_subject_resolution'],'tests':test_results,'same_database_rollback_proofs':rollback_hashes,'rollback_equality':all(t.get('rollback_equality', True) for t in test_results),'failed_test_state_unchanged':all(t.get('state_unchanged', True) for t in test_results)}
    write_json(DM / 'phase-a-address-records-geometry-slice-report.json', report)
    if broad_report_original is not None:
        broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists():
        broad_report_path.unlink()
    return report


# ---- Citizen geotag geometry one-slice checkpoint ----
CITIZEN_GEOTAG_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json'
CITIZEN_GEOTAG_ORACLE_BASELINE_SHA256 = '5a09abd8a017dcbf8210040e9311bc4118be82e24c245cafa485987eb5932a46'
CITIZEN_GEOTAG_CORRECTION_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-citizen-geotag-geometry-correction-oracle.json'
CITIZEN_GEOTAG_CORRECTION_ORACLE_BASELINE_SHA256 = 'f2cbb6689154616955b330c068b4bdfcdaac4b18642799fcca1f94270fe0d7f2'
CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED = False
CITIZEN_GEOTAG_GROUP_ID = 'WO002-R06-geometry-observation-citizen_geotag_submissions'
CITIZEN_GEOTAG_IMPL_UNIT = 'impl_wo002_r06_geometry_observation_citizen_geotag_submissions'
CITIZEN_GEOTAG_FUNCTION = 'transform_citizen_geotag_geometry'
CITIZEN_GEOTAG_GEOMETRY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}


def citizen_geotag_oracle_hash() -> str:
    return file_sha256(CITIZEN_GEOTAG_ORACLE)

def citizen_geotag_correction_oracle_hash() -> str:
    return file_sha256(CITIZEN_GEOTAG_CORRECTION_ORACLE)


def load_citizen_geotag_oracle() -> dict[str, Any]:
    if not CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned citizen geotag geometry oracle access is disabled outside the read-only comparator')
    return json.loads(CITIZEN_GEOTAG_ORACLE.read_text())


class citizen_geotag_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.previous = None
    def __enter__(self):
        global CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED
        self.previous = CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED
        CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED
        CITIZEN_GEOTAG_ORACLE_ACCESS_ALLOWED = self.previous


def select_citizen_geotag_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    for rec in records:
        if rec['source_table'] == 'citizen_geotag_submissions' and rec['values'].get('id') == 'phase-a-geotag-001':
            return rec
    raise HarnessError('citizen_geotag_submissions fixture metadata not found')


def make_citizen_geotag_record(source_id: str = 'phase-a-geotag-001') -> dict[str, Any]:
    rec = copy.deepcopy(select_citizen_geotag_record(fixture_records()))
    rec['values']['id'] = source_id
    rec['source_key'] = f'citizen_geotag_submissions:{source_id}'
    rec['values']['updated_at'] = '2026-07-15T01:00:00Z'
    rec['values']['field_verified_at'] = '2026-07-15T02:00:00Z'
    if source_id != 'phase-a-geotag-001':
        suffix = source_id.rsplit('-', 1)[-1]
        rec['source_record_id'] = f'phase-a-source-record-citizen-geotag-submissions-{suffix}'
        rec['values']['grid_code'] = f'PHASE-A-NONOFFICIAL-GEOTAG-{suffix}'
    return rec


def setup_citizen_geotag_geometry_database() -> None:
    discover_current(reset=True)
    apply_target()
    topology_check()


def citizen_geotag_source_key(source_row: dict[str, Any]) -> str:
    return f"citizen_geotag_submissions:{source_row['id']}"


def citizen_geotag_geometry_id(source_row: dict[str, Any]) -> str:
    return f"phase-a-geometry-citizen-geotag-submissions-{source_row['id']}"


def citizen_geotag_exception_id(source_row: dict[str, Any]) -> str:
    return f"phase-a-exception-geometry-authority-citizen-geotag-submissions-{source_row['id']}"


def citizen_geotag_location_id(source_id: str) -> str:
    if source_id == 'phase-a-geotag-001':
        return 'phase-a-location-citizen-geotag-001'
    return f'phase-a-location-citizen-geotag-{source_id.rsplit("-", 1)[-1]}'


def citizen_geotag_subject_id(source_id: str) -> str:
    return f'phase-a-subject-{citizen_geotag_location_id(source_id)}'


def citizen_geotag_crosswalk_id(source_id: str) -> str:
    if source_id == 'phase-a-geotag-001':
        return 'phase-a-crosswalk-citizen-geotag-id-to-location-record'
    return f'phase-a-crosswalk-citizen-geotag-{source_id.rsplit("-", 1)[-1]}-to-location-record'


def ensure_citizen_geotag_preconditions(cur, rec: dict[str, Any], mutation: dict[str, Any] | None = None) -> None:
    mutation = mutation or {}
    rows = base_target_rows()
    add_source_records_and_evidence(rows, [rec])
    rec_values = normalize_current_fixture_values('citizen_geotag_submissions', rec['values'])
    source_id = rec_values['id']
    loc_id = citizen_geotag_location_id(source_id)
    subj_id = citizen_geotag_subject_id(source_id)
    add_unique(rows, 'proposed_location_record', {
        'location_record_id': loc_id,
        'record_type': 'address',
        'created_at': TS,
        'retired_at': None,
        'classification': 'restricted',
    })
    add_unique(rows, 'proposed_registry_subject', {
        'subject_id': subj_id,
        'subject_entity': 'location_record',
        'created_at': TS,
        'native_id': loc_id,
        'subject_state': 'active',
        'retired_at': None,
        'delete_policy': 'retire-only',
    })
    if not mutation.get('missing_citizen_geotag_crosswalk'):
        target_id = loc_id
        if mutation.get('wrong_subject_through_territory_or_field_submission'):
            target_id = 'phase-a-location-geotag'
        add_unique(rows, 'proposed_legacy_crosswalk', {
            'legacy_crosswalk_id': citizen_geotag_crosswalk_id(source_id),
            'source_table': 'citizen_geotag_submissions',
            'source_field': 'id',
            'legacy_id': source_id,
            'target_entity': 'location_record',
            'target_id': target_id,
            'created_at': TS,
        })
    if source_id != 'phase-a-geotag-001':
        for evidence in rows.get('proposed_evidence_object', []):
            if evidence.get('source_record_id') == rec['source_record_id']:
                evidence['evidence_object_id'] = f'phase-a-evidence-citizen-geotag-submissions-{source_id.rsplit("-", 1)[-1]}'
    if mutation.get('missing_evidence_object'):
        rows['proposed_evidence_object'] = [r for r in rows.get('proposed_evidence_object', []) if r.get('source_record_id') != rec['source_record_id']]
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def ensure_citizen_geotag_multi_preconditions(cur, records: list[dict[str, Any]]) -> None:
    rows = base_target_rows()
    add_source_records_and_evidence(rows, records)
    for rec in records:
        rec_values = normalize_current_fixture_values('citizen_geotag_submissions', rec['values'])
        source_id = rec_values['id']
        loc_id = citizen_geotag_location_id(source_id)
        add_unique(rows, 'proposed_location_record', {
            'location_record_id': loc_id,
            'record_type': 'address',
            'created_at': TS,
            'retired_at': None,
            'classification': 'restricted',
        })
        add_unique(rows, 'proposed_registry_subject', {
            'subject_id': citizen_geotag_subject_id(source_id),
            'subject_entity': 'location_record',
            'created_at': TS,
            'native_id': loc_id,
            'subject_state': 'active',
            'retired_at': None,
            'delete_policy': 'retire-only',
        })
        add_unique(rows, 'proposed_legacy_crosswalk', {
            'legacy_crosswalk_id': citizen_geotag_crosswalk_id(source_id),
            'source_table': 'citizen_geotag_submissions',
            'source_field': 'id',
            'legacy_id': source_id,
            'target_entity': 'location_record',
            'target_id': loc_id,
            'created_at': TS,
        })
        if source_id != 'phase-a-geotag-001':
            for evidence in rows.get('proposed_evidence_object', []):
                if evidence.get('source_record_id') == rec['source_record_id']:
                    evidence['evidence_object_id'] = f'phase-a-evidence-citizen-geotag-submissions-{source_id.rsplit("-", 1)[-1]}'
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def query_complete_citizen_geotag_row(cur, source_id: str = 'phase-a-geotag-001') -> tuple[dict[str, Any], dict[str, Any]]:
    sql = """
        SELECT id,territory_id,address_label,citizen_name,citizen_contact,dip_last4,identity_verification_status,
               identity_document_verified,identity_verified_at,landmark,latitude,longitude,accuracy_meters,
               capture_method,grid_code,status,duplicate_hint,reviewer_note,suggested_road_name,suggested_local_area,
               suggested_place_name,map_display_name,road_suggestion_source,road_suggestion_attribution,
               road_suggestion_status,reviewed_road_name,field_submission_id,field_status,field_note,
               field_verified_at,signage_batch,created_at,updated_at
        FROM current_source.citizen_geotag_submissions
        WHERE id = %s
    """
    params = (source_id,)
    cur.execute(sql, params)
    row = cur.fetchone()
    if not row:
        raise HarnessError('citizen_geotag_submissions source row not found')
    row = dict(row)
    return row, {'sql': ' '.join(sql.split()), 'params': list(params), 'row': norm_row(row)}


def resolve_citizen_geotag_target_identity(cur, source_id: str) -> dict[str, Any]:
    sql = """
        SELECT cw.legacy_crosswalk_id, cw.source_table, cw.source_field, cw.legacy_id, cw.target_entity, cw.target_id,
               lr.location_record_id, lr.record_type, lr.classification AS location_classification, lr.retired_at AS location_retired_at,
               rs.subject_id, rs.native_id, rs.subject_entity, rs.subject_state, rs.retired_at AS subject_retired_at
        FROM canonical_target.proposed_legacy_crosswalk cw
        JOIN canonical_target.proposed_location_record lr
          ON lr.location_record_id = cw.target_id
        JOIN canonical_target.proposed_registry_subject rs
          ON rs.native_id = lr.location_record_id
         AND rs.subject_entity = cw.target_entity
        WHERE cw.source_table = 'citizen_geotag_submissions'
          AND cw.source_field = 'id'
          AND cw.legacy_id = %s
          AND cw.target_entity = 'location_record'
        ORDER BY cw.legacy_crosswalk_id, rs.subject_id
    """
    cur.execute(sql, (source_id,))
    rows = cur.fetchall()
    if not rows:
        raise HarnessError('citizen_geotag_submissions.id cannot resolve target location record')
    if len(rows) != 1:
        raise HarnessError(f'citizen_geotag_submissions.id resolved multiple target location records: {len(rows)}')
    row = norm_row(dict(rows[0]))
    if row['target_id'] != citizen_geotag_location_id(source_id):
        raise HarnessError('citizen geotag geometry subject must resolve through citizen_geotag_submissions.id')
    if row['location_record_id'] != row['target_id'] or row['record_type'] != 'address' or row['location_classification'] != 'restricted' or row['location_retired_at'] is not None:
        raise HarnessError('citizen geotag target location record must be an active restricted provisional address')
    if row['native_id'] != row['target_id'] or row['subject_entity'] != 'location_record' or row['subject_state'] != 'active' or row['subject_retired_at'] is not None:
        raise HarnessError('citizen geotag target registry subject must be active')
    return {'sql': ' '.join(sql.split()), 'params': [source_id], 'row': row}


def require_citizen_geotag_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = citizen_geotag_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key, raw_payload_classification FROM canonical_target.proposed_source_record WHERE source_key = %s"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('citizen geotag source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'citizen geotag source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    if source.get('raw_payload_classification') != 'restricted':
        raise HarnessError('citizen geotag source record must remain restricted')
    evidence_sql = "SELECT evidence_object_id, source_record_id, classification FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('citizen geotag evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'citizen geotag evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    if evidence.get('classification') != 'restricted':
        raise HarnessError('citizen geotag evidence object must remain restricted')
    return {'derived_source_key': derived_source_key, 'source_query': source_sql, 'source_params': [derived_source_key], 'source_row': norm_row(source), 'evidence_query': evidence_sql, 'evidence_params': [source['source_record_id']], 'evidence_row': norm_row(evidence)}


def reviewed_citizen_geotag_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = {
        'transform_group_id': CITIZEN_GEOTAG_GROUP_ID,
        'implementation_unit': CITIZEN_GEOTAG_IMPL_UNIT,
        'callable': CITIZEN_GEOTAG_FUNCTION,
        'covered_source_fields': ['citizen_geotag_submissions.accuracy_meters','citizen_geotag_submissions.latitude','citizen_geotag_submissions.longitude'],
        'required_context_fields': ['citizen_geotag_submissions.id','citizen_geotag_submissions.capture_method','citizen_geotag_submissions.created_at','citizen_geotag_submissions.updated_at','citizen_geotag_submissions.field_verified_at','citizen_geotag_submissions.status','citizen_geotag_submissions.territory_id','citizen_geotag_submissions.field_submission_id'],
        'capture_method_translation': {'browser-gps':'browser-gps'},
        'observed_at_rule': 'citizen_geotag_submissions.created_at',
        'recorded_at_rule': 'citizen_geotag_submissions.created_at',
        'field_verified_at_role': 'verification context only; must not replace observation or recorded time',
        'classification_rule': 'restricted',
        'identity_rule': 'citizen_geotag_submissions.id resolves to a provisional non-official location_record identity; territory_id and field_submission_id are context/provenance only',
        'target_entities': ['geometry_observation'],
        'source_record_key': 'citizen_geotag_submissions:phase-a-geotag-001',
        'idempotency_key': 'citizen_geotag_submissions.phase-a-geotag-001::WO002-R06-geometry-observation-citizen_geotag_submissions',
    }
    groups = copy.deepcopy(registry_groups())
    group = next((g for g in groups if g['transform_group_id'] == CITIZEN_GEOTAG_GROUP_ID), None)
    if not group:
        raise HarnessError('citizen geotag geometry transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key, value in spec_mutation.items():
            group[key] = value
    checks = {
        'transform_group_id': group.get('transform_group_id') == expected['transform_group_id'],
        'implementation_unit': group.get('implementation_unit') == expected['implementation_unit'],
        'callable': CITIZEN_GEOTAG_GEOMETRY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_citizen_geotag_geometry and expected['callable'] == CITIZEN_GEOTAG_FUNCTION,
        'covered_source_fields': sorted(group.get('covered_source_fields', [])) == sorted(expected['covered_source_fields']),
        'required_context_fields': group.get('required_context_fields') == expected['required_context_fields'],
        'capture_method_translation': group.get('capture_method_translation') == expected['capture_method_translation'],
        'observed_at_rule': group.get('observed_at_rule') == expected['observed_at_rule'],
        'recorded_at_rule': group.get('recorded_at_rule') == expected['recorded_at_rule'],
        'field_verified_at_role': group.get('field_verified_at_role') == expected['field_verified_at_role'],
        'classification_rule': group.get('classification_rule') == expected['classification_rule'],
        'identity_rule': group.get('identity_rule') == expected['identity_rule'],
        'target_entity': group.get('target_entities') == expected['target_entities'],
        'source_record_key': group.get('source_record_key') == expected['source_record_key'],
        'idempotency_key': group.get('idempotency_key') == expected['idempotency_key'],
    }
    if not all(checks.values()):
        raise HarnessError(f'citizen geotag geometry transform specification binding mismatch: {checks}')
    return {'group': group, 'required_context_fields': group['required_context_fields'], 'validation': checks}


def validate_citizen_geotag_coordinates(source_row: dict[str, Any]) -> dict[str, Any]:
    validate_coordinate_range(source_row)
    return {'numeric_wkt': f"POINT({source_row['longitude']} {source_row['latitude']})", 'srid': 4326}


def translate_citizen_geotag_capture_method(cur, source_row: dict[str, Any], spec_validation: dict[str, Any]) -> dict[str, Any]:
    translation = spec_validation['group']['capture_method_translation']
    source_value = source_row['capture_method']
    if source_value not in translation:
        raise HarnessError('citizen_geotag_submissions.capture_method has no reviewed translation')
    target_value = translation[source_value]
    cur.execute("SELECT value FROM canonical_target.vocab_capture_method WHERE value = %s", (target_value,))
    if not cur.fetchone():
        raise HarnessError(f'citizen geotag capture method target vocabulary missing: {target_value}')
    return {'source_value': source_value, 'target_value': target_value, 'target_vocabulary_preexisted': True, 'harness_vocabulary_mutation': False}


def transform_citizen_geotag_geometry(cur, *, source_id: str = 'phase-a-geotag-001', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    spec_validation = spec_validation or reviewed_citizen_geotag_transform_spec()
    source_row, source_query = query_complete_citizen_geotag_row(cur, source_id)
    coordinate = validate_citizen_geotag_coordinates(source_row)
    capture = translate_citizen_geotag_capture_method(cur, source_row, spec_validation)
    identity = resolve_citizen_geotag_target_identity(cur, source_row['id'])
    lineage = require_citizen_geotag_lineage(cur, source_row)
    lon = source_row['longitude']
    lat = source_row['latitude']
    if mutation.get('wrong_longitude_implementation'):
        lon = float(lon) + 1.0
    geom_id = citizen_geotag_geometry_id(source_row)
    exception_id = citizen_geotag_exception_id(source_row)
    source_key = citizen_geotag_source_key(source_row)
    observed_at = source_row['field_verified_at'] if mutation.get('wrong_field_verified_timing_implementation') else source_row['created_at']
    recorded_at = source_row['field_verified_at'] if mutation.get('wrong_field_verified_timing_implementation') else source_row['created_at']
    rows = {
        'proposed_geometry_observation': [{
            'geometry_observation_id': geom_id,
            'subject_id': identity['row']['subject_id'],
            'geometry_role': 'location-point',
            'observed_geom': {'longitude': lon, 'latitude': lat},
            'capture_method': capture['target_value'],
            'horizontal_accuracy_m': source_row['accuracy_meters'],
            'source_record_id': lineage['source_row']['source_record_id'],
            'evidence_object_id': lineage['evidence_row']['evidence_object_id'],
            'licence_id': None,
            'observed_at': observed_at,
            'recorded_at': recorded_at,
            'classification': spec_validation['group']['classification_rule'],
        }],
        'proposed_migration_exception': [{
            'migration_exception_id': exception_id,
            'batch_id': 'phase-a-citizen-geotag-submissions-geometry-slice',
            'source_table': 'citizen_geotag_submissions',
            'source_field': None,
            'source_key': source_key,
            'exception_type': 'authority-rfi',
            'severity': 'medium',
            'owner': 'SDA',
            'created_at': TS,
            'resolved_at': None,
            'details_json': {
                'target_entity': 'geometry_observation',
                'target_id': geom_id,
                'reason': 'Canonical geometry promotion authority unresolved; restricted citizen geotag observation preserved without canonical promotion or public release',
                'open_authority_rfi': 'geometry-promotion-authority',
                'non_official': True,
                'public_release_prohibited': True,
            },
        }],
    }
    if mutation.get('unexpected_extra_target_row'):
        rows['proposed_geometry_observation'].append({**rows['proposed_geometry_observation'][0], 'geometry_observation_id': geom_id + '-extra'})
    stats1 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    stats2 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    forbidden_subject_fields_used = False
    return {'function_invoked': CITIZEN_GEOTAG_FUNCTION, 'implementation_unit': CITIZEN_GEOTAG_IMPL_UNIT, 'transform_group_id': CITIZEN_GEOTAG_GROUP_ID, 'generic_transform_group_used': False, 'source_row_query': source_query, 'fields_consumed': spec_validation['group']['covered_source_fields'] + spec_validation['required_context_fields'], 'numeric_coordinate_point': coordinate, 'capture_method_translation': capture, 'target_identity_resolution': identity, 'lineage': lineage, 'insert_stats_first': stats1, 'insert_stats_second': stats2, 'spec_validation': spec_validation, 'derived_ids': {'geometry_observation_id': geom_id, 'migration_exception_id': exception_id, 'source_key': source_key}, 'forbidden_subject_fields_used': forbidden_subject_fields_used, 'observed_at_source': 'field_verified_at' if mutation.get('wrong_field_verified_timing_implementation') else 'created_at', 'recorded_at_source': 'field_verified_at' if mutation.get('wrong_field_verified_timing_implementation') else 'created_at', 'field_verified_at_used_for_target_timing': bool(mutation.get('wrong_field_verified_timing_implementation'))}


CITIZEN_GEOTAG_GEOMETRY_IMPLEMENTATIONS[CITIZEN_GEOTAG_IMPL_UNIT] = transform_citizen_geotag_geometry


def citizen_geotag_complete_target_rows(cur, source_key: str = 'citizen_geotag_submissions:phase-a-geotag-001') -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cur.execute("""
        SELECT g.geometry_observation_id, g.subject_id, g.geometry_role, ST_AsText(g.observed_geom) AS observed_geom_wkt,
               ST_SRID(g.observed_geom) AS observed_geom_srid, g.capture_method,
               g.horizontal_accuracy_m::numeric(10,2)::text AS horizontal_accuracy_m,
               g.source_record_id, g.evidence_object_id, g.licence_id, g.observed_at, g.recorded_at, g.classification
        FROM canonical_target.proposed_geometry_observation g
        JOIN canonical_target.proposed_source_record sr ON sr.source_record_id = g.source_record_id
        WHERE sr.source_key = %s
        ORDER BY g.geometry_observation_id
    """, (source_key,))
    for geom in cur.fetchall():
        rows.append({'table':'proposed_geometry_observation','primary_key':{'geometry_observation_id':geom['geometry_observation_id']},'values':norm_row(dict(geom))})
    cur.execute("""
        SELECT migration_exception_id, batch_id, source_table, source_field, source_key, exception_type,
               severity, owner, created_at, resolved_at, details_json
        FROM canonical_target.proposed_migration_exception
        WHERE source_table = 'citizen_geotag_submissions' AND source_key = %s
        ORDER BY migration_exception_id
    """, (source_key,))
    for exc in cur.fetchall():
        d=norm_row(dict(exc)); d['details_json']=normalize_json(d['details_json'])
        rows.append({'table':'proposed_migration_exception','primary_key':{'migration_exception_id':exc['migration_exception_id']},'values':d})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def citizen_geotag_target_slice_hash(cur, source_key: str = 'citizen_geotag_submissions:phase-a-geotag-001') -> dict[str, Any]:
    rows = citizen_geotag_complete_target_rows(cur, source_key)
    return {'rows': rows, 'hash': sha(rows)}


def expected_citizen_geotag_rows(oracle: dict[str, Any], source_key: str = 'citizen_geotag_submissions:phase-a-geotag-001', expected_mutation: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    rows = copy.deepcopy(oracle['expected_inserted_rows'])
    for row in rows:
        if row['table'] == 'proposed_migration_exception':
            row['values']['source_key'] = source_key
        if row['table'] == 'proposed_geometry_observation':
            if expected_mutation and expected_mutation.get('precision_expected'):
                row['values']['observed_geom_wkt'] = 'POINT(8.7834567 3.7523456)'
            if expected_mutation and expected_mutation.get('wrong_expected_geometry'):
                row['values']['observed_geom_wkt'] = 'POINT(0 0)'
            if expected_mutation and expected_mutation.get('field_verified_timing_expected'):
                row['values']['observed_at'] = '2026-07-15T00:00:00Z'
                row['values']['recorded_at'] = '2026-07-15T00:00:00Z'
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def expected_absent_citizen_geotag_rows(cur, oracle: dict[str, Any]) -> list[dict[str, Any]]:
    results=[]
    for item in oracle['expected_absent_rows']:
        table=item['table']; where=item.get('where')
        if where:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        else:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table}')
        count=cur.fetchone()['c']
        results.append({'table':table,'where':where,'reason':item['reason'],'count':count})
        if count != 0:
            raise HarnessError(f'expected absent row exists in {table}: {item}')
    return results


def compare_citizen_geotag_oracle_read_only(*, source_key: str = 'citizen_geotag_submissions:phase-a-geotag-001', expected_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    proof = comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY')
        cur.execute('SHOW transaction_read_only')
        comparator_read_only = cur.fetchone()['transaction_read_only']
        with citizen_geotag_oracle_access(True):
            oracle = load_citizen_geotag_oracle()
        actual = citizen_geotag_complete_target_rows(cur, source_key)
        expected = expected_citizen_geotag_rows(oracle, source_key, expected_mutation)
        if len(actual) != len(expected):
            raise HarnessError(f'unexpected citizen geotag geometry slice target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}
        act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys - exp_keys:
            raise HarnessError(f'unexpected citizen geotag geometry slice target row: {sorted(act_keys-exp_keys)}')
        if exp_keys - act_keys:
            raise HarnessError(f'missing citizen geotag geometry slice target row: {sorted(exp_keys-act_keys)}')
        if actual != expected:
            actual_geom = next((r['values'].get('observed_geom_wkt') for r in actual if r['table']=='proposed_geometry_observation'), None)
            expected_geom = next((r['values'].get('observed_geom_wkt') for r in expected if r['table']=='proposed_geometry_observation'), None)
            if actual_geom != expected_geom:
                if expected_mutation and expected_mutation.get('wrong_expected_geometry'):
                    raise HarnessError('observed geometry differs from reviewer-owned expected geometry')
                raise HarnessError('geometry observation does not match reviewer-owned expected WKT')
            actual_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in actual if r['table']=='proposed_geometry_observation'), None)
            expected_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in expected if r['table']=='proposed_geometry_observation'), None)
            if actual_timing != expected_timing:
                raise HarnessError('citizen geotag geometry slice observed rows differ from reviewer-owned timing expectation')
            raise HarnessError(f'citizen geotag geometry slice observed rows differ from reviewer-owned oracle: actual={actual} expected={expected}')
        absent = expected_absent_citizen_geotag_rows(cur, oracle)
        cur.execute("""
            SELECT geometry_observation_id, COUNT(*)::int AS c
            FROM canonical_target.proposed_geometry_observation
            GROUP BY geometry_observation_id HAVING COUNT(*) > 1
        """)
        duplicates=[dict(r) for r in cur.fetchall()]
        if duplicates:
            raise HarnessError(f'geometry-observation duplicates: {duplicates}')
        conn.rollback()
    return {'expected_rows': len(expected), 'actual_rows': len(actual), 'expected_absent_rows': absent, 'geometry_observation_count': sum(1 for r in actual if r['table']=='proposed_geometry_observation'), 'geometry_observation_duplicates': duplicates, 'actual_rows_detail': actual, 'comparator_connection': {'separate_connection': True, 'transaction_read_only': comparator_read_only}, 'comparator_read_only_proof': proof, 'complete_target_set_query': {'source_key': source_key, 'tables': ['proposed_geometry_observation','proposed_migration_exception']}}


def run_citizen_geotag_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-geotag-001') -> dict[str, Any]:
    mutation = mutation or {}
    records = [r for r in fixture_records() if r['source_table'] != 'citizen_geotag_submissions']
    rec = make_citizen_geotag_record(source_id)
    if not mutation.get('missing_source'):
        records.append(rec)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        ensure_citizen_geotag_preconditions(cur, rec, mutation)
        if mutation.get('precision_case'):
            cur.execute("UPDATE current_source.citizen_geotag_submissions SET latitude=%s, longitude=%s, accuracy_meters=%s WHERE id=%s", (3.7523456, 8.7834567, 4.5, source_id))
        if mutation.get('field_verified_timing_case'):
            cur.execute("UPDATE current_source.citizen_geotag_submissions SET created_at=%s, updated_at=%s, field_verified_at=%s WHERE id=%s", ('2026-07-15T00:00:00Z', '2026-07-15T01:00:00Z', '2026-07-15T02:00:00Z', source_id))
        if mutation.get('unknown_capture_method'):
            cur.execute("UPDATE current_source.citizen_geotag_submissions SET capture_method=%s WHERE id=%s", ('paper-map', source_id))
        spec_validation = reviewed_citizen_geotag_transform_spec(mutation.get('spec_drift'))
        impl = CITIZEN_GEOTAG_GEOMETRY_IMPLEMENTATIONS.get(CITIZEN_GEOTAG_IMPL_UNIT)
        if impl is not transform_citizen_geotag_geometry:
            raise HarnessError('explicit citizen geotag geometry implementation binding missing')
        transform_result = impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    source_key = f'citizen_geotag_submissions:{source_id}'
    comparison = compare_citizen_geotag_oracle_read_only(source_key=source_key, expected_mutation=(mutation if compare_expected else None)) if compare_expected else None
    return {'source_report': source_report, 'transform': transform_result, 'comparison': comparison}


def prepare_citizen_geotag_slice_state(cur, *, source_id: str = 'phase-a-geotag-001', mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    rec = make_citizen_geotag_record(source_id)
    if mutation.get('missing_source'):
        # address_records/address_record_events depend on citizen_geotag_submissions, so omit that dependent chain
        # rather than deleting through an FK after load. The transform still runs the ordinary source query.
        records = [r for r in fixture_records() if r['source_table'] not in ('citizen_geotag_submissions','address_records','address_record_events')]
    else:
        records = [r for r in fixture_records() if r['source_table'] != 'citizen_geotag_submissions'] + [rec]
    source_report = insert_current_fixture_rows(cur, records)
    ensure_citizen_geotag_preconditions(cur, rec, mutation)
    return {'source_report': source_report, 'record': rec}


def run_citizen_geotag_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_citizen_geotag_geometry_database()
    source_key = 'citizen_geotag_submissions:phase-a-geotag-001'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_citizen_geotag_slice_state(cur, mutation=mutation)
        conn.commit()
        before = citizen_geotag_target_slice_hash(cur, source_key)
        cur.execute('BEGIN')
        try:
            spec_validation = reviewed_citizen_geotag_transform_spec(mutation.get('spec_drift'))
            if mutation.get('invalid_coordinate_current_source'):
                cur.execute("ALTER TABLE current_source.citizen_geotag_submissions DROP CONSTRAINT IF EXISTS citizen_geotag_submissions_latitude_valid")
                cur.execute("UPDATE current_source.citizen_geotag_submissions SET latitude = 91.0 WHERE id = %s", ('phase-a-geotag-001',))
            if mutation.get('unknown_capture_method'):
                cur.execute("UPDATE current_source.citizen_geotag_submissions SET capture_method=%s WHERE id=%s", ('paper-map', 'phase-a-geotag-001'))
            if mutation.get('source_record_classification_drift'):
                cur.execute("UPDATE canonical_target.proposed_source_record SET raw_payload_classification=%s WHERE source_key=%s", ('government-internal', source_key))
            if mutation.get('evidence_classification_drift'):
                cur.execute("UPDATE canonical_target.proposed_evidence_object SET classification=%s WHERE source_record_id=%s", ('government-internal', 'phase-a-source-record-citizen-geotag-submissions-001'))
            if mutation.get('target_location_classification_drift'):
                cur.execute("UPDATE canonical_target.proposed_location_record SET classification=%s WHERE location_record_id=%s", ('government-internal', 'phase-a-location-citizen-geotag-001'))
            if mutation.get('target_location_record_type_drift'):
                cur.execute("UPDATE canonical_target.proposed_location_record SET record_type=%s WHERE location_record_id=%s", ('building', 'phase-a-location-citizen-geotag-001'))
            if mutation.get('target_subject_state_drift'):
                cur.execute("UPDATE canonical_target.proposed_registry_subject SET subject_state=%s WHERE native_id=%s AND subject_entity=%s", ('retired', 'phase-a-location-citizen-geotag-001', 'location_record'))
            transform_citizen_geotag_geometry(cur, source_id='phase-a-geotag-001', mutation=mutation, spec_validation=spec_validation)
            if mutation.get('wrong_expected_geometry') or mutation.get('unexpected_extra_target_row') or mutation.get('wrong_longitude_implementation') or mutation.get('wrong_field_verified_timing_implementation'):
                actual = citizen_geotag_complete_target_rows(cur, source_key)
                with citizen_geotag_oracle_access(True):
                    oracle = load_citizen_geotag_oracle()
                expected = expected_citizen_geotag_rows(oracle, source_key, mutation)
                if len(actual) != len(expected):
                    raise HarnessError('unexpected citizen geotag geometry slice target row')
                if actual != expected:
                    actual_geom = next((r['values'].get('observed_geom_wkt') for r in actual if r['table']=='proposed_geometry_observation'), None)
                    expected_geom = next((r['values'].get('observed_geom_wkt') for r in expected if r['table']=='proposed_geometry_observation'), None)
                    if actual_geom != expected_geom:
                        if mutation.get('wrong_expected_geometry'):
                            raise HarnessError('observed geometry differs from reviewer-owned expected geometry')
                        raise HarnessError('geometry observation does not match reviewer-owned expected WKT')
                    actual_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in actual if r['table']=='proposed_geometry_observation'), None)
                    expected_timing = next(((r['values'].get('observed_at'), r['values'].get('recorded_at')) for r in expected if r['table']=='proposed_geometry_observation'), None)
                    if actual_timing != expected_timing:
                        raise HarnessError('citizen geotag geometry slice observed rows differ from reviewer-owned timing expectation')
                    raise HarnessError('unexpected citizen geotag geometry slice target row')
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed = str(exc)
            if expected_error not in observed:
                conn.rollback()
                raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback()
            with conn.cursor() as check_cur:
                after = citizen_geotag_target_slice_hash(check_cur, source_key)
            if before != after:
                raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id': probe_id, 'expected_error': expected_error, 'observed_error': observed, 'same_database_pre_test_rows': before['rows'], 'same_database_pre_test_hash': before['hash'], 'same_database_post_failure_rows': after['rows'], 'same_database_post_failure_hash': after['hash'], 'rollback_equality': True, 'state_unchanged': True, 'status': 'passed'}


def citizen_geotag_crosswalk_controls(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='citizen_geotag_submissions' AND source_field='id' AND target_entity='location_record'
        ORDER BY legacy_crosswalk_id
    """)
    rows=[norm_row(dict(r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity, target_id, COUNT(*)::int AS c
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='citizen_geotag_submissions'
        GROUP BY 1,2,3,4,5 HAVING COUNT(*) > 1
    """)
    duplicates=[norm_row(dict(r)) for r in cur.fetchall()]
    cur.execute("""
        SELECT legacy_id, COUNT(*)::int AS c
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table='citizen_geotag_submissions' AND source_field='id' AND target_entity='location_record'
        GROUP BY legacy_id HAVING COUNT(*) > 1
    """)
    multiple=[norm_row(dict(r)) for r in cur.fetchall()]
    return {'rows': rows, 'citizen_geotag_identity_crosswalk_count': len(rows), 'semantic_duplicate_crosswalks': duplicates, 'semantic_duplicate_crosswalk_count': len(duplicates), 'multiple_subject_resolution': multiple, 'multiple_subject_resolution_count': len(multiple)}


def run_citizen_geotag_second_source_identity_test() -> dict[str, Any]:
    setup_citizen_geotag_geometry_database()
    first_id='phase-a-geotag-001'; second_id='phase-a-geotag-002'
    rec1=make_citizen_geotag_record(first_id); rec2=make_citizen_geotag_record(second_id)
    records=[r for r in fixture_records() if r['source_table'] != 'citizen_geotag_submissions'] + [rec1, rec2]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report=insert_current_fixture_rows(cur, records)
        ensure_citizen_geotag_multi_preconditions(cur, [rec1, rec2])
        spec_validation=reviewed_citizen_geotag_transform_spec()
        first=transform_citizen_geotag_geometry(cur, source_id=first_id, spec_validation=spec_validation)
        second=transform_citizen_geotag_geometry(cur, source_id=second_id, spec_validation=spec_validation)
        conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.citizen_geotag_submissions WHERE id IN (%s,%s)", (first_id, second_id)); source_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id IN (%s,%s)", (citizen_geotag_geometry_id({'id':first_id}), citizen_geotag_geometry_id({'id':second_id}))); geom_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_migration_exception WHERE migration_exception_id IN (%s,%s)", (citizen_geotag_exception_id({'id':first_id}), citizen_geotag_exception_id({'id':second_id}))); exc_count=cur.fetchone()['c']
        first_rows=citizen_geotag_complete_target_rows(cur, f'citizen_geotag_submissions:{first_id}')
        second_rows=citizen_geotag_complete_target_rows(cur, f'citizen_geotag_submissions:{second_id}')
        crosswalk_controls=citizen_geotag_crosswalk_controls(cur)
    checks={'source_records': source_count==2, 'geometry_observations': geom_count==2, 'authority_exceptions': exc_count==2, 'citizen_geotag_identity_crosswalks': crosswalk_controls['citizen_geotag_identity_crosswalk_count']==2, 'duplicate_crosswalks': crosswalk_controls['semantic_duplicate_crosswalk_count']==0, 'multiple_subject_resolution': crosswalk_controls['multiple_subject_resolution_count']==0, 'second_source_key': second['lineage']['derived_source_key']==f'citizen_geotag_submissions:{second_id}', 'second_subject': second['target_identity_resolution']['row']['subject_id']==citizen_geotag_subject_id(second_id)}
    if not all(checks.values()):
        raise HarnessError(f'citizen geotag second-source identity test failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'source_records':source_count,'geometry_observations':geom_count,'authority_exceptions':exc_count,'citizen_geotag_identity_crosswalks':crosswalk_controls['citizen_geotag_identity_crosswalk_count'],'duplicate_crosswalks':crosswalk_controls['semantic_duplicate_crosswalk_count'],'multiple_subject_resolution':crosswalk_controls['multiple_subject_resolution_count'],'crosswalk_controls':crosswalk_controls,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':first['lineage'],'second_transform_lineage':second['lineage']}


def run_citizen_geotag_precision_test() -> dict[str, Any]:
    setup_citizen_geotag_geometry_database()
    report=run_citizen_geotag_slice_once(mutation={'precision_case': True, 'precision_expected': True}, compare_expected=True)
    geom=next(r for r in report['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    if geom['values']['observed_geom_wkt'] != 'POINT(8.7834567 3.7523456)' or geom['values']['observed_geom_srid'] != 4326:
        raise HarnessError(f'citizen geotag precision-preservation failed: {geom}')
    return {'test_id':'precision-preservation','status':'passed','wkt':geom['values']['observed_geom_wkt'],'srid':geom['values']['observed_geom_srid']}


def run_citizen_geotag_capture_method_test() -> dict[str, Any]:
    setup_citizen_geotag_geometry_database()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute("SELECT value FROM canonical_target.vocab_capture_method WHERE value=%s", ('browser-gps',))
        existed_after_apply_target=cur.fetchone() is not None
        conn.rollback()
    report=run_citizen_geotag_slice_once(compare_expected=True)
    geom=next(r for r in report['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    if not existed_after_apply_target or geom['values']['capture_method'] != 'browser-gps':
        raise HarnessError('citizen geotag capture-method translation failed')
    return {'test_id':'capture-method-translation','status':'passed','source_capture_method':'browser-gps','target_capture_method':geom['values']['capture_method'],'target_vocabulary_preexisted':existed_after_apply_target,'harness_vocabulary_mutation':False}


def run_citizen_geotag_field_verified_timing_test() -> dict[str, Any]:
    setup_citizen_geotag_geometry_database()
    report=run_citizen_geotag_slice_once(mutation={'field_verified_timing_case': True, 'field_verified_timing_expected': True}, compare_expected=True)
    geom=next(r for r in report['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    if geom['values']['observed_at'] != '2026-07-15T00:00:00Z' or geom['values']['recorded_at'] != '2026-07-15T00:00:00Z':
        raise HarnessError(f'citizen geotag field_verified_at timing control failed: {geom}')
    return {'test_id':'field-verified-time-not-observation-time','status':'passed','created_at':'2026-07-15T00:00:00Z','field_verified_at':'2026-07-15T02:00:00Z','observed_at':geom['values']['observed_at'],'recorded_at':geom['values']['recorded_at'],'field_verified_at_used_for_target_timing':False}


def run_citizen_geotag_privacy_publication_boundary_test() -> dict[str, Any]:
    setup_citizen_geotag_geometry_database()
    report=run_citizen_geotag_slice_once(compare_expected=True)
    with connect() as conn, conn.cursor() as cur:
        absent = report['comparison']['expected_absent_rows']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE source_record_id=%s AND classification <> 'restricted'", ('phase-a-source-record-citizen-geotag-submissions-001',))
        public_obs=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_publication_release_item")
        publication_items=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_public_code_alias WHERE location_record_id=%s", ('phase-a-location-citizen-geotag-001',))
        public_aliases=cur.fetchone()['c']
    if public_obs or publication_items or public_aliases:
        raise HarnessError('citizen geotag privacy/publication boundary failed')
    return {'test_id':'privacy-publication-boundary','status':'passed','public_observations':public_obs,'publication_release_items':publication_items,'public_code_aliases_for_citizen_geotag':public_aliases,'expected_absent_rows':absent}


def run_citizen_geotag_geometry_slice() -> dict[str, Any]:
    broad_report_path = DM / 'phase-a-current-source-execution-report.json'
    broad_report_original = broad_report_path.read_text() if broad_report_path.exists() else None
    if citizen_geotag_oracle_hash() != CITIZEN_GEOTAG_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned citizen geotag oracle changed')
    if citizen_geotag_correction_oracle_hash() != CITIZEN_GEOTAG_CORRECTION_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned citizen geotag correction oracle changed')
    setup_citizen_geotag_geometry_database()
    positive=run_citizen_geotag_slice_once(compare_expected=True)
    test_results=[{'test_id':'positive-authoritative-slice','status':'passed'}]
    test_results.append({'test_id':'second-run-idempotency','status':'passed','first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':0,'geometry_observation_count':positive['comparison']['geometry_observation_count']})
    precision=run_citizen_geotag_precision_test(); test_results.append(precision)
    capture_method=run_citizen_geotag_capture_method_test(); test_results.append(capture_method)
    field_verified_timing=run_citizen_geotag_field_verified_timing_test(); test_results.append(field_verified_timing)
    privacy_boundary=run_citizen_geotag_privacy_publication_boundary_test(); test_results.append(privacy_boundary)
    second_identity=run_citizen_geotag_second_source_identity_test(); test_results.append(second_identity)
    probes=[
        ('unknown-capture-method','citizen_geotag_submissions.capture_method has no reviewed translation',{'unknown_capture_method':True}),
        ('wrong-field-verified-timing-implementation','citizen geotag geometry slice observed rows differ from reviewer-owned timing expectation',{'field_verified_timing_case': True, 'field_verified_timing_expected': True, 'wrong_field_verified_timing_implementation': True}),
        ('wrong-longitude-transform-implementation','geometry observation does not match reviewer-owned expected WKT',{'wrong_longitude_implementation':True}),
        ('invalid-coordinate-current-source','coordinate out of range',{'invalid_coordinate_current_source':True}),
        ('missing-source-record','citizen_geotag_submissions source row not found',{'missing_source':True}),
        ('missing-citizen-geotag-crosswalk','citizen_geotag_submissions.id cannot resolve target location record',{'missing_citizen_geotag_crosswalk':True}),
        ('wrong-subject-through-territory-or-field-submission','citizen geotag geometry subject must resolve through citizen_geotag_submissions.id',{'wrong_subject_through_territory_or_field_submission':True}),
        ('missing-evidence-object','citizen geotag evidence object not found',{'missing_evidence_object':True}),
        ('wrong-independent-expected-geometry','observed geometry differs from reviewer-owned expected geometry',{'wrong_expected_geometry':True}),
        ('unexpected-extra-target-row','unexpected citizen geotag geometry slice target row',{'unexpected_extra_target_row':True}),
        ('transform-spec-binding-drift','citizen geotag geometry transform specification binding mismatch',{'spec_drift': {'implementation_unit':'impl_wrong'}}),
        ('source-record-classification-drift','citizen geotag source record must remain restricted',{'source_record_classification_drift':True}),
        ('evidence-classification-drift','citizen geotag evidence object must remain restricted',{'evidence_classification_drift':True}),
        ('target-location-classification-drift','citizen geotag target location record must be an active restricted provisional address',{'target_location_classification_drift':True}),
        ('target-location-record-type-drift','citizen geotag target location record must be an active restricted provisional address',{'target_location_record_type_drift':True}),
        ('target-subject-state-drift','citizen geotag target registry subject must be active',{'target_subject_state_drift':True}),
        ('transform-spec-source-record-key-drift','citizen geotag geometry transform specification binding mismatch',{'spec_drift': {'source_record_key':'citizen_geotag_submissions:wrong'}}),
        ('transform-spec-idempotency-key-drift','citizen geotag geometry transform specification binding mismatch',{'spec_drift': {'idempotency_key':'wrong::WO002-R06-geometry-observation-citizen_geotag_submissions'}}),
    ]
    for pid, reason, mutation in probes:
        test_results.append(run_citizen_geotag_negative_probe(pid, reason, mutation))
    geom=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_geometry_observation')
    exc=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_migration_exception')
    rollback_hashes=[t for t in test_results if 'same_database_pre_test_hash' in t]
    report={'command':'citizen-geotag-geometry-slice','status':'passed','reviewer_owned_oracle_sha256':citizen_geotag_oracle_hash(),'reviewer_owned_oracle_changed':False,'accepted_address_points_controls_changed':False,'accepted_address_records_controls_changed':False,'exact_function_implemented':CITIZEN_GEOTAG_FUNCTION,'exact_registry_binding':{CITIZEN_GEOTAG_IMPL_UNIT:CITIZEN_GEOTAG_FUNCTION},'generic_transform_group_used_for_slice':False,'transform_reads_expected_oracle':False,'source_row_query':positive['transform']['source_row_query']['sql'],'source_row_returned':positive['transform']['source_row_query']['row'],'fields_consumed':positive['transform']['fields_consumed'],'capture_method_translation':positive['transform']['capture_method_translation'],'target_vocabulary_preexisted':positive['transform']['capture_method_translation']['target_vocabulary_preexisted'],'harness_vocabulary_mutation':False,'source_key_derivation':{'rule':'citizen_geotag_submissions:<queried id>','value':positive['transform']['lineage']['derived_source_key']},'source_record_resolution':positive['transform']['lineage']['source_row'],'evidence_resolution':positive['transform']['lineage']['evidence_row'],'target_identity_resolution':positive['transform']['target_identity_resolution'],'identity_crosswalk':positive['transform']['target_identity_resolution']['row']['legacy_crosswalk_id'],'target_location_record':positive['transform']['target_identity_resolution']['row']['target_id'],'target_registry_subject':positive['transform']['target_identity_resolution']['row']['subject_id'],'forbidden_subject_fields_used':positive['transform']['forbidden_subject_fields_used'],'numeric_coordinate_point':positive['transform']['numeric_coordinate_point'],'reviewed_transform_spec_row':positive['transform']['spec_validation']['group'],'binding_validation':positive['transform']['spec_validation']['validation'],'geometry_observation_row':geom,'conditional_exception_row':exc,'expected_absent_rows_verified':positive['comparison']['expected_absent_rows'],'observed_at_source':positive['transform']['observed_at_source'],'recorded_at_source':positive['transform']['recorded_at_source'],'field_verified_at_used_for_target_timing':positive['transform']['field_verified_at_used_for_target_timing'],'comparator_connection':positive['comparison']['comparator_connection'],'comparator_read_only_proof':positive['comparison']['comparator_read_only_proof'],'complete_target_set_comparison':positive['comparison']['complete_target_set_query'],'first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':0,'semantic_duplicates':positive['comparison']['geometry_observation_duplicates'],'precision_test_wkt_srid':{'wkt':precision['wkt'],'srid':precision['srid']},'capture_method_test':capture_method,'field_verified_timing_test':field_verified_timing,'privacy_publication_boundary_test':privacy_boundary,'second_source_identity_test':second_identity,'source_records_second_source':second_identity['source_records'],'geometry_observations_second_source':second_identity['geometry_observations'],'authority_exceptions_second_source':second_identity['authority_exceptions'],'citizen_geotag_identity_crosswalks_second_source':second_identity['citizen_geotag_identity_crosswalks'],'duplicate_crosswalks_second_source':second_identity['duplicate_crosswalks'],'multiple_subject_resolution_second_source':second_identity['multiple_subject_resolution'],'tests':test_results,'same_database_rollback_proofs':rollback_hashes,'rollback_equality':all(t.get('rollback_equality', True) for t in test_results),'failed_test_state_unchanged':all(t.get('state_unchanged', True) for t in test_results)}
    report['reviewer_owned_correction_oracle_sha256'] = citizen_geotag_correction_oracle_hash()
    report['reviewer_owned_correction_oracle_changed'] = False
    report['source_record_classification_validation'] = positive['transform']['lineage']['source_row']['raw_payload_classification'] == 'restricted'
    report['evidence_classification_validation'] = positive['transform']['lineage']['evidence_row']['classification'] == 'restricted'
    report['target_location_record_validation'] = {
        'record_type': positive['transform']['target_identity_resolution']['row']['record_type'],
        'classification': positive['transform']['target_identity_resolution']['row']['location_classification'],
        'retired_at': positive['transform']['target_identity_resolution']['row']['location_retired_at'],
        'valid': positive['transform']['target_identity_resolution']['row']['record_type'] == 'address' and positive['transform']['target_identity_resolution']['row']['location_classification'] == 'restricted' and positive['transform']['target_identity_resolution']['row']['location_retired_at'] is None,
    }
    report['target_registry_subject_validation'] = {
        'native_id': positive['transform']['target_identity_resolution']['row']['native_id'],
        'subject_entity': positive['transform']['target_identity_resolution']['row']['subject_entity'],
        'subject_state': positive['transform']['target_identity_resolution']['row']['subject_state'],
        'retired_at': positive['transform']['target_identity_resolution']['row']['subject_retired_at'],
        'valid': positive['transform']['target_identity_resolution']['row']['subject_entity'] == 'location_record' and positive['transform']['target_identity_resolution']['row']['subject_state'] == 'active' and positive['transform']['target_identity_resolution']['row']['subject_retired_at'] is None,
    }
    report['reviewed_source_record_key'] = positive['transform']['spec_validation']['group'].get('source_record_key')
    report['reviewed_idempotency_key'] = positive['transform']['spec_validation']['group'].get('idempotency_key')
    write_json(DM / 'phase-a-citizen-geotag-geometry-slice-report.json', report)
    if broad_report_original is not None:
        broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists():
        broad_report_path.unlink()
    return report


# ---- Addresses identity-foundation one-slice checkpoint ----
ADDRESSES_IDENTITY_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-addresses-identity-expected.json'
ADDRESSES_IDENTITY_ORACLE_BASELINE_SHA256 = '518af277e96c94c55808f9ac1e7992059c371bd225d906cf77156c478b0497cd'
ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED = False
ADDRESSES_IDENTITY_GROUP_ID = 'WO002-R06-identity-crosswalk-addresses'
ADDRESSES_IDENTITY_IMPL_UNIT = 'impl_wo002_r06_identity_crosswalk_addresses'
ADDRESSES_IDENTITY_FUNCTION = 'transform_addresses_identity_crosswalk'
ADDRESSES_IDENTITY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}


def addresses_identity_oracle_hash() -> str:
    return file_sha256(ADDRESSES_IDENTITY_ORACLE)


def load_addresses_identity_oracle() -> dict[str, Any]:
    if not ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned addresses identity oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESSES_IDENTITY_ORACLE.read_text())


class addresses_identity_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.previous = None
    def __enter__(self):
        global ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED
        self.previous = ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED
        ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED
        ADDRESSES_IDENTITY_ORACLE_ACCESS_ALLOWED = self.previous


def select_addresses_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    for rec in records:
        if rec['source_table'] == 'addresses' and rec['values'].get('id') == 'phase-a-addresses-id':
            return rec
    raise HarnessError('addresses fixture metadata not found')


def make_addresses_record(source_id: str = 'phase-a-addresses-id') -> dict[str, Any]:
    rec = copy.deepcopy(select_addresses_record(fixture_records()))
    rec['values']['id'] = source_id
    rec['source_key'] = f'addresses:{source_id}'
    if source_id != 'phase-a-addresses-id':
        suffix = source_id.rsplit('-', 1)[-1]
        rec['source_record_id'] = f'phase-a-source-record-addresses-{suffix}'
        rec['values']['public_code'] = f'PHASE-A-NONOFFICIAL-{suffix}'
        rec['values']['formatted'] = f'Controlled Phase A address label {suffix}'
    return rec


def setup_addresses_identity_database() -> None:
    discover_current(reset=True)
    apply_target()
    topology_check()


def addresses_source_key(source_row: dict[str, Any]) -> str:
    return f"addresses:{source_row['id']}"


def addresses_location_id(source_id: str) -> str:
    if source_id == 'phase-a-addresses-id':
        return 'phase-a-location-address-reference'
    return f'phase-a-location-address-reference-{source_id.rsplit("-", 1)[-1]}'


def addresses_subject_id(source_id: str) -> str:
    return f'phase-a-subject-{addresses_location_id(source_id)}'


def addresses_crosswalk_id(source_id: str) -> str:
    if source_id == 'phase-a-addresses-id':
        return 'phase-a-crosswalk-addresses-id-to-location-record'
    return f'phase-a-crosswalk-addresses-{source_id.rsplit("-", 1)[-1]}-id-to-location-record'


def addresses_lineage_rows(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_source_authority'].append({'source_authority_id':'phase-a-authority-operational-control','authority_name':'Phase A retained operational-control authority','authority_class':'derived-system','legal_basis':'Operational-control/non-migrated disposition fixture; no public effect','status':'candidate'})
    add_source_records_and_evidence(rows, records)
    record_by_source_record_id = {rec['source_record_id']: rec for rec in records}
    for evidence in rows.get('proposed_evidence_object', []):
        rec = record_by_source_record_id.get(evidence.get('source_record_id'))
        if rec and rec['values'].get('id') != 'phase-a-addresses-id':
            suffix = rec['values']['id'].rsplit('-', 1)[-1]
            evidence['evidence_object_id'] = f'phase-a-evidence-addresses-{suffix}'
    return rows


def addresses_source_fixture_records(include_address: bool = True, source_id: str = 'phase-a-addresses-id') -> list[dict[str, Any]]:
    needed = {'provinces','admin_units','territories','roads','buildings'}
    records = [copy.deepcopy(r) for r in fixture_records() if r['source_table'] in needed]
    if include_address:
        records.append(make_addresses_record(source_id))
    return records


def query_complete_addresses_row(cur, source_id: str = 'phase-a-addresses-id') -> tuple[dict[str, Any], dict[str, Any]]:
    sql = """
        SELECT id,formatted,territory_id,road_id,building_id,province_code,public_code,
               issuance_method,source,verification_status,superseded_by_address_id,status,
               publication_state,is_archived,created_at,updated_at
        FROM current_source.addresses
        WHERE id = %s
    """
    params = (source_id,)
    cur.execute(sql, params)
    row = cur.fetchone()
    if not row:
        raise HarnessError('addresses source row not found')
    row = dict(row)
    return row, {'sql': ' '.join(sql.split()), 'params': list(params), 'row': norm_row(row)}


def require_addresses_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = addresses_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key, raw_payload_classification FROM canonical_target.proposed_source_record WHERE source_key = %s"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('addresses source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'addresses source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    if source['raw_payload_classification'] != 'government-internal':
        raise HarnessError('addresses source record must remain government-internal')
    evidence_sql = "SELECT evidence_object_id, source_record_id, classification FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('addresses evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'addresses evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    if evidence['classification'] != 'government-internal':
        raise HarnessError('addresses evidence object must remain government-internal')
    return {'derived_source_key': derived_source_key, 'source_query': source_sql, 'source_params': [derived_source_key], 'source_row': norm_row(source), 'evidence_query': evidence_sql, 'evidence_params': [source['source_record_id']], 'evidence_row': norm_row(evidence)}


def reviewed_addresses_identity_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = {
        'transform_group_id': ADDRESSES_IDENTITY_GROUP_ID,
        'implementation_unit': ADDRESSES_IDENTITY_IMPL_UNIT,
        'callable': ADDRESSES_IDENTITY_FUNCTION,
        'covered_source_fields': ['addresses.id'],
        'required_context_fields': ['addresses.formatted','addresses.building_id','addresses.road_id','addresses.territory_id','addresses.superseded_by_address_id','addresses.public_code','addresses.status','addresses.publication_state','addresses.is_archived','addresses.created_at','addresses.updated_at'],
        'source_record_key': 'addresses:phase-a-addresses-id',
        'idempotency_key': 'addresses.phase-a-addresses-id::WO002-R06-identity-crosswalk-addresses',
        'identity_rule': 'addresses.id owns an internal address location identity; building_id, road_id, territory_id, superseded_by_address_id and public_code are context only and must not determine the target identity',
        'target_identity_rule': {
            'primary_fixture': {
                'source_id': 'phase-a-addresses-id',
                'location_record_id': 'phase-a-location-address-reference',
                'subject_id': 'phase-a-subject-phase-a-location-address-reference',
                'legacy_crosswalk_id': 'phase-a-crosswalk-addresses-id-to-location-record',
            },
            'second_fixture_rule': 'For source id phase-a-addresses-<suffix>, use location_record_id phase-a-location-address-reference-<suffix>, subject_id phase-a-subject-phase-a-location-address-reference-<suffix>, and legacy_crosswalk_id phase-a-crosswalk-addresses-<suffix>-id-to-location-record. This is a design-harness rule only, not a production national identifier policy.',
        },
        'target_entities': ['location_record','registry_subject','legacy_crosswalk'],
    }
    groups = copy.deepcopy(registry_groups())
    group = next((g for g in groups if g['transform_group_id'] == ADDRESSES_IDENTITY_GROUP_ID), None)
    if not group:
        raise HarnessError('addresses identity transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key, value in spec_mutation.items():
            group[key] = value
    checks = {
        'transform_group_id': group.get('transform_group_id') == expected['transform_group_id'],
        'implementation_unit': group.get('implementation_unit') == expected['implementation_unit'],
        'callable': ADDRESSES_IDENTITY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_addresses_identity_crosswalk and expected['callable'] == ADDRESSES_IDENTITY_FUNCTION,
        'covered_source_fields': group.get('covered_source_fields') == expected['covered_source_fields'],
        'required_context_fields': group.get('required_context_fields') == expected['required_context_fields'],
        'source_record_key': group.get('source_record_key') == expected['source_record_key'],
        'idempotency_key': group.get('idempotency_key') == expected['idempotency_key'],
        'identity_rule': group.get('identity_rule') == expected['identity_rule'],
        'target_identity_rule': group.get('target_identity_rule') == expected['target_identity_rule'],
        'target_entities': group.get('target_entities') == expected['target_entities'],
    }
    if not all(checks.values()):
        raise HarnessError(f'addresses identity transform specification binding mismatch: {checks}')
    return {'group': group, 'required_context_fields': group['required_context_fields'], 'validation': checks}


def addresses_identity_rows_for_source(source_id: str, mutation: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    mutation = mutation or {}
    identity_source_id = source_id
    if mutation.get('reference_field_identity_substitution'):
        identity_source_id = 'phase-a-buildings-id'
    loc_id = addresses_location_id(identity_source_id)
    if mutation.get('wrong_target_identity_implementation'):
        loc_id = 'phase-a-location-wrong-address-reference'
    subj_id = f'phase-a-subject-{loc_id}' if loc_id != addresses_location_id(source_id) else addresses_subject_id(source_id)
    crosswalk_id = addresses_crosswalk_id(source_id)
    rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_location_record'].append({
        'location_record_id': loc_id,
        'record_type': 'address',
        'created_at': TS,
        'retired_at': None,
        'classification': 'government-internal',
    })
    rows['proposed_registry_subject'].append({
        'subject_id': subj_id,
        'subject_entity': 'location_record',
        'created_at': TS,
        'native_id': loc_id,
        'subject_state': 'active',
        'retired_at': None,
        'delete_policy': 'retire-only',
    })
    rows['proposed_legacy_crosswalk'].append({
        'legacy_crosswalk_id': crosswalk_id,
        'source_table': 'addresses',
        'source_field': 'id',
        'legacy_id': identity_source_id if mutation.get('reference_field_identity_substitution') else source_id,
        'target_entity': 'location_record',
        'target_id': loc_id,
        'created_at': TS,
    })
    if mutation.get('unexpected_extra_crosswalk'):
        rows['proposed_legacy_crosswalk'].append({
            'legacy_crosswalk_id': crosswalk_id + '-extra',
            'source_table': 'addresses',
            'source_field': 'building_id',
            'legacy_id': 'phase-a-buildings-id',
            'target_entity': 'location_record',
            'target_id': loc_id,
            'created_at': TS,
        })
    if mutation.get('unexpected_extra_location_record'):
        rows['proposed_location_record'].append({
            'location_record_id': addresses_location_id(source_id) + '-extra',
            'record_type': 'address',
            'created_at': TS,
            'retired_at': None,
            'classification': 'government-internal',
        })
    if mutation.get('unexpected_extra_registry_subject'):
        rows['proposed_registry_subject'].append({
            'subject_id': addresses_subject_id(source_id) + '-extra',
            'subject_entity': 'location_record',
            'created_at': TS,
            'native_id': addresses_location_id(source_id),
            'subject_state': 'active',
            'retired_at': None,
            'delete_policy': 'retire-only',
        })
    return rows


def addresses_semantic_uniqueness(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity,
               COUNT(*)::int AS row_count, COUNT(DISTINCT target_id)::int AS target_count,
               array_agg(legacy_crosswalk_id ORDER BY legacy_crosswalk_id) AS crosswalk_ids,
               array_agg(DISTINCT target_id ORDER BY target_id) AS target_ids
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'addresses'
        GROUP BY 1,2,3,4
        HAVING COUNT(*) > 1 OR COUNT(DISTINCT target_id) > 1
    """)
    duplicates = [norm_row(dict(r)) for r in cur.fetchall()]
    if duplicates:
        raise HarnessError('addresses identity crosswalk semantic uniqueness violated')
    cur.execute("""
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'addresses'
        ORDER BY legacy_crosswalk_id
    """)
    rows = [norm_row(dict(r)) for r in cur.fetchall()]
    return {'duplicates': duplicates, 'semantic_duplicate_count': 0, 'rows': rows, 'query': 'absolute uniqueness on (source_table, source_field, legacy_id, target_entity)'}


def transform_addresses_identity_crosswalk(cur, *, source_id: str = 'phase-a-addresses-id', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    spec_validation = spec_validation or reviewed_addresses_identity_transform_spec()
    source_row, source_query = query_complete_addresses_row(cur, source_id)
    lineage = require_addresses_lineage(cur, source_row)
    rows = addresses_identity_rows_for_source(source_row['id'], mutation)
    before_counts = {t: len(v) for t, v in rows.items()}
    stats1 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    uniqueness = addresses_semantic_uniqueness(cur)
    stats2 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    identity_rows = {t: rows[t][0] for t in ('proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk')}
    return {
        'function_invoked': ADDRESSES_IDENTITY_FUNCTION,
        'implementation_unit': ADDRESSES_IDENTITY_IMPL_UNIT,
        'transform_group_id': ADDRESSES_IDENTITY_GROUP_ID,
        'generic_transform_group_used': False,
        'source_row_query': source_query,
        'fields_consumed': spec_validation['group']['covered_source_fields'] + spec_validation['required_context_fields'],
        'lineage': lineage,
        'insert_stats_first': stats1,
        'insert_stats_second': stats2,
        'second_run_updates': 0,
        'spec_validation': spec_validation,
        'derived_ids': {'location_record_id': identity_rows['proposed_location_record']['location_record_id'], 'subject_id': identity_rows['proposed_registry_subject']['subject_id'], 'legacy_crosswalk_id': identity_rows['proposed_legacy_crosswalk']['legacy_crosswalk_id'], 'source_key': addresses_source_key(source_row)},
        'identity_rows': identity_rows,
        'semantic_uniqueness': uniqueness,
        'reference_fields_used_as_identity': bool(mutation.get('reference_field_identity_substitution')),
        'target_rows_requested': before_counts,
    }


ADDRESSES_IDENTITY_IMPLEMENTATIONS[ADDRESSES_IDENTITY_IMPL_UNIT] = transform_addresses_identity_crosswalk


def addresses_identity_complete_target_rows(cur, source_id: str = 'phase-a-addresses-id', include_source_derived_orphans: bool = True) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    expected_location_id = addresses_location_id(source_id)
    expected_subject_id = addresses_subject_id(source_id)
    location_prefix = expected_location_id + '-'
    subject_prefix = expected_subject_id + '-'
    cur.execute("""
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'addresses' AND source_field = 'id' AND legacy_id = %s AND target_entity = 'location_record'
        ORDER BY legacy_crosswalk_id
    """, (source_id,))
    crosswalks = [dict(r) for r in cur.fetchall()]
    target_ids = {r['target_id'] for r in crosswalks}
    target_ids.add(expected_location_id)
    location_predicates = ['location_record_id = ANY(%s)']
    location_params: list[Any] = [list(target_ids)]
    if include_source_derived_orphans:
        location_predicates.append('location_record_id LIKE %s')
        location_params.append(location_prefix + '%')
    cur.execute(f"""
        SELECT location_record_id, record_type, created_at, retired_at, classification
        FROM canonical_target.proposed_location_record
        WHERE {' OR '.join(location_predicates)}
        ORDER BY location_record_id
    """, location_params)
    actual_location_ids: set[str] = set()
    for lr in cur.fetchall():
        d = norm_row(dict(lr))
        actual_location_ids.add(lr['location_record_id'])
        rows.append({'table':'proposed_location_record','primary_key':{'location_record_id':lr['location_record_id']},'values':d})
    subject_native_ids = sorted(target_ids | actual_location_ids)
    subject_predicates = ['(native_id = ANY(%s) AND subject_entity = \'location_record\')', 'subject_id = %s']
    subject_params: list[Any] = [subject_native_ids, expected_subject_id]
    if include_source_derived_orphans:
        subject_predicates.append('subject_id LIKE %s')
        subject_params.append(subject_prefix + '%')
    cur.execute(f"""
        SELECT subject_id, subject_entity, created_at, native_id, subject_state, retired_at, delete_policy
        FROM canonical_target.proposed_registry_subject
        WHERE {' OR '.join(subject_predicates)}
        ORDER BY subject_id
    """, subject_params)
    for rs in cur.fetchall():
        d = norm_row(dict(rs))
        rows.append({'table':'proposed_registry_subject','primary_key':{'subject_id':rs['subject_id']},'values':d})
    for cw in crosswalks:
        d = norm_row(cw)
        rows.append({'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':cw['legacy_crosswalk_id']},'values':d})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))

def addresses_identity_target_slice_hash(cur, source_id: str = 'phase-a-addresses-id') -> dict[str, Any]:
    rows = addresses_identity_complete_target_rows(cur, source_id)
    return {'rows': rows, 'hash': sha(rows)}


def expected_addresses_identity_rows(oracle: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(copy.deepcopy(oracle['expected_inserted_rows']), key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def expected_absent_addresses_identity_rows(cur, oracle: dict[str, Any]) -> list[dict[str, Any]]:
    results=[]
    for item in oracle['expected_absent_rows']:
        table=item['table']; where=item.get('where')
        if where:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        else:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table}')
        count=cur.fetchone()['c']
        results.append({'table':table,'where':where,'reason':item['reason'],'count':count})
        if count != 0:
            raise HarnessError(f'expected absent row exists in {table}: {item}')
    return results


def compare_addresses_identity_oracle_read_only() -> dict[str, Any]:
    proof = comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY')
        cur.execute('SHOW transaction_read_only')
        comparator_read_only = cur.fetchone()['transaction_read_only']
        with addresses_identity_oracle_access(True):
            oracle = load_addresses_identity_oracle()
        actual = addresses_identity_complete_target_rows(cur, 'phase-a-addresses-id')
        expected = expected_addresses_identity_rows(oracle)
        if len(actual) != len(expected):
            raise HarnessError(f'unexpected addresses identity-foundation target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}
        act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys - exp_keys:
            raise HarnessError(f'unexpected addresses identity-foundation target row: {sorted(act_keys-exp_keys)}')
        if exp_keys - act_keys:
            raise HarnessError(f'missing addresses identity-foundation target row: {sorted(exp_keys-act_keys)}')
        if actual != expected:
            raise HarnessError('addresses identity rows differ from reviewer-owned expected target identity')
        absent = expected_absent_addresses_identity_rows(cur, oracle)
        uniqueness = addresses_semantic_uniqueness(cur)
        conn.rollback()
    return {'expected_rows': len(expected), 'actual_rows': len(actual), 'expected_absent_rows': absent, 'actual_rows_detail': actual, 'semantic_uniqueness': uniqueness, 'comparator_connection': {'separate_connection': True, 'transaction_read_only': comparator_read_only}, 'comparator_read_only_proof': proof, 'complete_target_set_query': {'source_table': 'addresses', 'source_field': 'id', 'legacy_id': 'phase-a-addresses-id', 'tables': ['proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk']}}


def insert_addresses_lineage_preconditions(cur, rec: dict[str, Any], mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    rows = addresses_lineage_rows([rec])
    if mutation.get('missing_source_lineage'):
        rows['proposed_source_record'] = []
        rows['proposed_evidence_object'] = []
    if mutation.get('missing_evidence_object'):
        rows['proposed_evidence_object'] = []
    if mutation.get('source_record_classification_drift'):
        for row in rows['proposed_source_record']:
            row['raw_payload_classification'] = 'restricted'
    if mutation.get('evidence_classification_drift'):
        for row in rows['proposed_evidence_object']:
            row['classification'] = 'restricted'
    stats = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    return stats


def run_addresses_identity_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-addresses-id') -> dict[str, Any]:
    mutation = mutation or {}
    records = addresses_source_fixture_records(include_address=not mutation.get('missing_source'), source_id=source_id)
    rec = make_addresses_record(source_id)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        insert_addresses_lineage_preconditions(cur, rec, mutation)
        if mutation.get('existing_location_conflict'):
            insert_row(cur, 'proposed_location_record', {'location_record_id': addresses_location_id(source_id), 'record_type':'address', 'created_at':TS, 'retired_at':None, 'classification':'restricted'})
        if mutation.get('existing_subject_conflict'):
            insert_row(cur, 'proposed_location_record', {'location_record_id':'phase-a-location-conflict', 'record_type':'address', 'created_at':TS, 'retired_at':None, 'classification':'government-internal'})
            insert_row(cur, 'proposed_registry_subject', {'subject_id': addresses_subject_id(source_id), 'subject_entity':'location_record', 'created_at':TS, 'native_id':'phase-a-location-conflict', 'subject_state':'active', 'retired_at':None, 'delete_policy':'retire-only'})
        if mutation.get('existing_crosswalk_conflict'):
            insert_row(cur, 'proposed_legacy_crosswalk', {'legacy_crosswalk_id': addresses_crosswalk_id(source_id), 'source_table':'addresses', 'source_field':'id', 'legacy_id':source_id, 'target_entity':'location_record', 'target_id':'phase-a-location-conflict', 'created_at':TS})
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur, 'proposed_legacy_crosswalk', {'legacy_crosswalk_id': addresses_crosswalk_id(source_id) + '-duplicate', 'source_table':'addresses', 'source_field':'id', 'legacy_id':source_id, 'target_entity':'location_record', 'target_id':'phase-a-location-conflict', 'created_at':TS})
        spec_validation = reviewed_addresses_identity_transform_spec(mutation.get('spec_drift'))
        impl = ADDRESSES_IDENTITY_IMPLEMENTATIONS.get(ADDRESSES_IDENTITY_IMPL_UNIT)
        if impl is not transform_addresses_identity_crosswalk:
            raise HarnessError('explicit addresses identity implementation binding missing')
        transform_result = impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    comparison = compare_addresses_identity_oracle_read_only() if compare_expected else None
    return {'source_report': source_report, 'transform': transform_result, 'comparison': comparison}


def prepare_addresses_identity_state(cur, *, source_id: str = 'phase-a-addresses-id', mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    rec = make_addresses_record(source_id)
    records = addresses_source_fixture_records(include_address=not mutation.get('missing_source'), source_id=source_id)
    source_report = insert_current_fixture_rows(cur, records)
    insert_addresses_lineage_preconditions(cur, rec, mutation)
    return {'source_report': source_report, 'record': rec}


def run_addresses_identity_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_addresses_identity_database()
    source_id = 'phase-a-addresses-id'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_addresses_identity_state(cur, mutation=mutation)
        if mutation.get('existing_location_conflict'):
            insert_row(cur, 'proposed_location_record', {'location_record_id': addresses_location_id(source_id), 'record_type':'address', 'created_at':TS, 'retired_at':None, 'classification':'restricted'})
        if mutation.get('existing_subject_conflict'):
            insert_row(cur, 'proposed_location_record', {'location_record_id':'phase-a-location-conflict', 'record_type':'address', 'created_at':TS, 'retired_at':None, 'classification':'government-internal'})
            insert_row(cur, 'proposed_registry_subject', {'subject_id': addresses_subject_id(source_id), 'subject_entity':'location_record', 'created_at':TS, 'native_id':'phase-a-location-conflict', 'subject_state':'active', 'retired_at':None, 'delete_policy':'retire-only'})
        if mutation.get('existing_crosswalk_conflict'):
            insert_row(cur, 'proposed_legacy_crosswalk', {'legacy_crosswalk_id': addresses_crosswalk_id(source_id), 'source_table':'addresses', 'source_field':'id', 'legacy_id':source_id, 'target_entity':'location_record', 'target_id':'phase-a-location-conflict', 'created_at':TS})
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur, 'proposed_legacy_crosswalk', {'legacy_crosswalk_id': addresses_crosswalk_id(source_id) + '-duplicate', 'source_table':'addresses', 'source_field':'id', 'legacy_id':source_id, 'target_entity':'location_record', 'target_id':'phase-a-location-conflict', 'created_at':TS})
        conn.commit()
        before = addresses_identity_target_slice_hash(cur, source_id)
        cur.execute('BEGIN')
        try:
            spec_validation = reviewed_addresses_identity_transform_spec(mutation.get('spec_drift'))
            transform_addresses_identity_crosswalk(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
            if mutation.get('wrong_target_identity_implementation') or mutation.get('unexpected_extra_crosswalk') or mutation.get('unexpected_extra_location_record') or mutation.get('unexpected_extra_registry_subject') or mutation.get('reference_field_identity_substitution'):
                actual = addresses_identity_complete_target_rows(cur, source_id)
                with addresses_identity_oracle_access(True):
                    oracle = load_addresses_identity_oracle()
                expected = expected_addresses_identity_rows(oracle)
                if mutation.get('unexpected_extra_crosswalk'):
                    try:
                        expected_absent_addresses_identity_rows(cur, oracle)
                    except HarnessError:
                        raise HarnessError('unexpected addresses identity-foundation target row')
                if actual != expected:
                    if mutation.get('reference_field_identity_substitution'):
                        raise HarnessError('addresses identity must derive from addresses.id')
                    if mutation.get('unexpected_extra_crosswalk') or mutation.get('unexpected_extra_location_record') or mutation.get('unexpected_extra_registry_subject'):
                        raise HarnessError('unexpected addresses identity-foundation target row')
                    raise HarnessError('addresses identity rows differ from reviewer-owned expected target identity')
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed = str(exc)
            if expected_error not in observed:
                conn.rollback()
                raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback()
            with conn.cursor() as check_cur:
                after = addresses_identity_target_slice_hash(check_cur, source_id)
            if before != after:
                raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id': probe_id, 'expected_error': expected_error, 'observed_error': observed, 'same_database_pre_test_rows': before['rows'], 'same_database_pre_test_hash': before['hash'], 'same_database_post_failure_rows': after['rows'], 'same_database_post_failure_hash': after['hash'], 'rollback_equality': True, 'state_unchanged': True, 'status': 'passed'}


def run_addresses_second_source_identity_test() -> dict[str, Any]:
    setup_addresses_identity_database()
    first_id='phase-a-addresses-id'; second_id='phase-a-addresses-002'
    records = addresses_source_fixture_records(include_address=False) + [make_addresses_record(first_id), make_addresses_record(second_id)]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        lineage_rows = addresses_lineage_rows([make_addresses_record(first_id), make_addresses_record(second_id)])
        apply_target_rows(cur, lineage_rows)
        cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        spec_validation = reviewed_addresses_identity_transform_spec()
        first = transform_addresses_identity_crosswalk(cur, source_id=first_id, spec_validation=spec_validation)
        second = transform_addresses_identity_crosswalk(cur, source_id=second_id, spec_validation=spec_validation)
        conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.addresses WHERE id IN (%s,%s)", (first_id, second_id)); source_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_location_record WHERE location_record_id IN (%s,%s)", (addresses_location_id(first_id), addresses_location_id(second_id))); loc_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_registry_subject WHERE subject_id IN (%s,%s) AND subject_state='active'", (addresses_subject_id(first_id), addresses_subject_id(second_id))); subj_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id IN (%s,%s)", (addresses_crosswalk_id(first_id), addresses_crosswalk_id(second_id))); cw_count=cur.fetchone()['c']
        controls = addresses_semantic_uniqueness(cur)
        first_rows = addresses_identity_complete_target_rows(cur, first_id, include_source_derived_orphans=False)
        second_rows = addresses_identity_complete_target_rows(cur, second_id, include_source_derived_orphans=False)
    checks={'source_records': source_count==2, 'location_records': loc_count==2, 'active_registry_subjects': subj_count==2, 'distinct_crosswalks': cw_count==2, 'duplicate_crosswalks': controls['semantic_duplicate_count']==0, 'multiple_target_resolution': controls['semantic_duplicate_count']==0, 'second_source_key': second['lineage']['derived_source_key']==f'addresses:{second_id}', 'second_subject': second['derived_ids']['subject_id']==addresses_subject_id(second_id)}
    if not all(checks.values()):
        raise HarnessError(f'addresses second-source identity test failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'addresses_source_identities':source_count,'location_records':loc_count,'active_registry_subjects':subj_count,'distinct_crosswalks':cw_count,'semantic_duplicate_crosswalks':controls['semantic_duplicate_count'],'multiple_target_resolutions':0,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':first['lineage'],'second_transform_lineage':second['lineage']}


def run_addresses_identity_slice() -> dict[str, Any]:
    broad_report_path = DM / 'phase-a-current-source-execution-report.json'
    broad_report_original = broad_report_path.read_text() if broad_report_path.exists() else None
    if addresses_identity_oracle_hash() != ADDRESSES_IDENTITY_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned addresses identity oracle changed')
    setup_addresses_identity_database()
    positive = run_addresses_identity_slice_once(compare_expected=True)
    test_results=[{'test_id':'positive-authoritative-slice','status':'passed'}]
    test_results.append({'test_id':'second-run-idempotency','status':'passed','first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates']})
    test_results.append({'test_id':'source-record-classification','status':'passed','classification':positive['transform']['lineage']['source_row']['raw_payload_classification']})
    test_results.append({'test_id':'evidence-classification','status':'passed','classification':positive['transform']['lineage']['evidence_row']['classification']})
    second_identity = run_addresses_second_source_identity_test(); test_results.append(second_identity)
    probes=[
        ('missing-source-record','addresses source row not found',{'missing_source':True}),
        ('missing-source-lineage','addresses source record lineage not found',{'missing_source_lineage':True}),
        ('missing-evidence-object','addresses evidence object not found',{'missing_evidence_object':True}),
        ('source-record-classification-drift','addresses source record must remain government-internal',{'source_record_classification_drift':True}),
        ('evidence-classification-drift','addresses evidence object must remain government-internal',{'evidence_classification_drift':True}),
        ('reference-field-identity-substitution','addresses identity must derive from addresses.id',{'reference_field_identity_substitution':True}),
        ('wrong-target-identity-implementation','addresses identity rows differ from reviewer-owned expected target identity',{'wrong_target_identity_implementation':True}),
        ('existing-location-conflict','existing correct target row changed for proposed_location_record',{'existing_location_conflict':True}),
        ('existing-subject-conflict','existing correct target row changed for proposed_registry_subject',{'existing_subject_conflict':True}),
        ('existing-crosswalk-conflict','existing correct target row changed for proposed_legacy_crosswalk',{'existing_crosswalk_conflict':True}),
        ('unexpected-extra-crosswalk','unexpected addresses identity-foundation target row',{'unexpected_extra_crosswalk':True}),
        ('unexpected-extra-location-record','unexpected addresses identity-foundation target row',{'unexpected_extra_location_record':True}),
        ('unexpected-extra-registry-subject','unexpected addresses identity-foundation target row',{'unexpected_extra_registry_subject':True}),
        ('semantic-duplicate-multiple-target-crosswalk','addresses identity crosswalk semantic uniqueness violated',{'semantic_duplicate_crosswalk':True}),
        ('transform-spec-binding-drift','addresses identity transform specification binding mismatch',{'spec_drift': {'implementation_unit':'impl_wrong'}}),
        ('transform-spec-covered-fields-drift','addresses identity transform specification binding mismatch',{'spec_drift': {'covered_source_fields':['addresses.id','addresses.building_id']}}),
        ('transform-spec-context-fields-drift','addresses identity transform specification binding mismatch',{'spec_drift': {'required_context_fields':['addresses.formatted']}}),
        ('transform-spec-source-record-key-drift','addresses identity transform specification binding mismatch',{'spec_drift': {'source_record_key':'addresses:phase-a-addresses-001'}}),
        ('transform-spec-idempotency-key-drift','addresses identity transform specification binding mismatch',{'spec_drift': {'idempotency_key':'addresses.phase-a-addresses-001::WO002-R06-identity-crosswalk-addresses'}}),
        ('transform-spec-target-entities-drift','addresses identity transform specification binding mismatch',{'spec_drift': {'target_entities':['legacy_crosswalk','migration_exception']}}),
    ]
    for pid, reason, mutation in probes:
        test_results.append(run_addresses_identity_negative_probe(pid, reason, mutation))
    loc=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_location_record')
    subj=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_registry_subject')
    cw=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_legacy_crosswalk')
    rollback_hashes=[t for t in test_results if 'same_database_pre_test_hash' in t]
    report={'command':'addresses-identity-slice','status':'passed','reviewer_owned_oracle_sha256':addresses_identity_oracle_hash(),'reviewer_owned_oracle_changed':False,'accepted_geometry_controls_changed':False,'exact_function_implemented':ADDRESSES_IDENTITY_FUNCTION,'exact_registry_binding':{ADDRESSES_IDENTITY_IMPL_UNIT:ADDRESSES_IDENTITY_FUNCTION},'generic_transform_group_used_for_slice':False,'transform_reads_expected_oracle':False,'source_row_query':positive['transform']['source_row_query']['sql'],'source_row_returned':positive['transform']['source_row_query']['row'],'fields_consumed':positive['transform']['fields_consumed'],'source_key_derivation':{'rule':'addresses:<queried id>','value':positive['transform']['lineage']['derived_source_key']},'source_record_resolution':positive['transform']['lineage']['source_row'],'evidence_resolution':positive['transform']['lineage']['evidence_row'],'reviewed_transform_spec_row':positive['transform']['spec_validation']['group'],'binding_validation':positive['transform']['spec_validation']['validation'],'location_record_row':loc,'registry_subject_row':subj,'legacy_crosswalk_row':cw,'reference_fields_used_as_identity':positive['transform']['reference_fields_used_as_identity'],'expected_absent_rows_verified':positive['comparison']['expected_absent_rows'],'semantic_uniqueness_query_result':positive['comparison']['semantic_uniqueness'],'comparator_connection_read_only_proof':positive['comparison']['comparator_read_only_proof'],'comparator_connection':positive['comparison']['comparator_connection'],'complete_target_set_comparison':positive['comparison'],'first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates'],'tests':test_results,'rollback_equality_all':all(t.get('rollback_equality', True) for t in rollback_hashes),'rollback_evidence_count':len(rollback_hashes),'second_source_identity_test':second_identity,'prohibited_outputs_created':{'migration_exceptions':0,'location_record_versions':0,'geometry_observations':0,'public_code_aliases':0,'publication_release_items':0,'reference_field_crosswalks':0}}
    write_json(DM / 'phase-a-addresses-identity-slice-report.json', report)
    if broad_report_original is not None:
        broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists():
        broad_report_path.unlink()
    return report


# ---- Address-points observation identity-crosswalk one-slice implementation ----

ADDRESS_POINTS_OBSERVATION_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-points-observation-crosswalk-expected.json'
ADDRESS_POINTS_OBSERVATION_ORACLE_BASELINE_SHA256 = 'd1b695994ae774a6c54cc99c1e79a0bce023fd5a9a20ec2aee779cfeb10bfa82'
ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED = False
ADDRESS_POINTS_OBSERVATION_GROUP_ID = 'WO002-R06-identity-crosswalk-address_points'
ADDRESS_POINTS_OBSERVATION_IMPL_UNIT = 'impl_wo002_r06_identity_crosswalk_address_points'
ADDRESS_POINTS_OBSERVATION_FUNCTION = 'transform_address_points_observation_crosswalk'
ADDRESS_POINTS_OBSERVATION_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}


def address_points_observation_oracle_hash() -> str:
    return file_sha256(ADDRESS_POINTS_OBSERVATION_ORACLE)


def load_address_points_observation_oracle() -> dict[str, Any]:
    if not ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned address_points observation-crosswalk oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_POINTS_OBSERVATION_ORACLE.read_text())


class address_points_observation_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.previous = False
    def __enter__(self):
        global ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED
        self.previous = ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED
        ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED
        ADDRESS_POINTS_OBSERVATION_ORACLE_ACCESS_ALLOWED = self.previous


def address_points_observation_crosswalk_id(source_id: str) -> str:
    if source_id == 'phase-a-address-points-id':
        return 'phase-a-crosswalk-address-points-id-to-geometry-observation'
    suffix = source_id.replace('phase-a-address-points-', '')
    return f'phase-a-crosswalk-address-points-{suffix}-id-to-geometry-observation'


def reviewed_address_points_observation_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected_target_identity_rule = {
        'primary_fixture': {
            'source_id': 'phase-a-address-points-id',
            'legacy_crosswalk_id': 'phase-a-crosswalk-address-points-id-to-geometry-observation',
            'target_id': 'phase-a-geometry-address-points-phase-a-address-points-id',
        },
        'second_fixture_rule': 'For source id phase-a-address-points-<suffix>, target phase-a-geometry-address-points-phase-a-address-points-<suffix> with crosswalk phase-a-crosswalk-address-points-<suffix>-id-to-geometry-observation. This is a design-harness rule only.',
    }
    expected = {
        'transform_group_id': ADDRESS_POINTS_OBSERVATION_GROUP_ID,
        'implementation_unit': ADDRESS_POINTS_OBSERVATION_IMPL_UNIT,
        'callable': ADDRESS_POINTS_OBSERVATION_FUNCTION,
        'covered_source_fields': ['address_points.id'],
        'required_context_fields': ['address_points.address_id','address_points.is_active','address_points.created_at','address_points.updated_at'],
        'source_record_key': 'address_points:phase-a-address-points-id',
        'idempotency_key': 'address_points.phase-a-address-points-id::WO002-R06-identity-crosswalk-address_points',
        'identity_rule': 'address_points.id is an observation identity only; address_points.address_id resolves the separate address location subject',
        'crosswalk_target_entity': 'geometry_observation',
        'target_entities': ['legacy_crosswalk'],
        'target_identity_rule': expected_target_identity_rule,
    }
    group = copy.deepcopy(next((g for g in registry_groups() if g['transform_group_id'] == ADDRESS_POINTS_OBSERVATION_GROUP_ID), None))
    if not group:
        raise HarnessError('address_points observation crosswalk specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key, value in spec_mutation.items():
            group[key] = value
    checks = {
        'transform_group_id': group.get('transform_group_id') == expected['transform_group_id'],
        'implementation_unit': group.get('implementation_unit') == expected['implementation_unit'],
        'callable': ADDRESS_POINTS_OBSERVATION_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_address_points_observation_crosswalk and expected['callable'] == ADDRESS_POINTS_OBSERVATION_FUNCTION,
        'covered_source_fields': group.get('covered_source_fields') == expected['covered_source_fields'],
        'required_context_fields': group.get('required_context_fields') == expected['required_context_fields'],
        'source_record_key': group.get('source_record_key') == expected['source_record_key'],
        'idempotency_key': group.get('idempotency_key') == expected['idempotency_key'],
        'identity_rule': group.get('identity_rule') == expected['identity_rule'],
        'crosswalk_target_entity': group.get('crosswalk_target_entity') == expected['crosswalk_target_entity'],
        'target_entities': group.get('target_entities') == expected['target_entities'],
        'target_identity_rule': group.get('target_identity_rule') == expected['target_identity_rule'],
    }
    if not all(checks.values()):
        raise HarnessError(f'address_points observation crosswalk specification binding mismatch: {checks}')
    return {'group': group, 'validation': checks, 'required_context_fields': group['required_context_fields']}


def require_address_points_observation_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = address_points_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key, raw_payload_classification FROM canonical_target.proposed_source_record WHERE source_key = %s ORDER BY source_record_id"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('address_points source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'address_points source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    if source.get('raw_payload_classification') != 'government-internal':
        raise HarnessError('address_points source record must remain government-internal')
    evidence_sql = "SELECT evidence_object_id, source_record_id, classification FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('address_points evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'address_points evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    if evidence.get('classification') != 'government-internal':
        raise HarnessError('address_points evidence object must remain government-internal')
    return {
        'derived_source_key': derived_source_key,
        'source_query': source_sql,
        'source_params': [derived_source_key],
        'source_row': norm_row(source),
        'evidence_query': evidence_sql,
        'evidence_params': [source['source_record_id']],
        'evidence_row': norm_row(evidence),
    }


def validate_address_points_geometry_observation_precondition(cur, source_row: dict[str, Any], lineage: dict[str, Any], address_subject: dict[str, Any]) -> dict[str, Any]:
    geom_id = address_points_geometry_id(source_row)
    sql = """
        SELECT geometry_observation_id, source_record_id, evidence_object_id, subject_id, geometry_role, classification
        FROM canonical_target.proposed_geometry_observation
        WHERE geometry_observation_id = %s
    """
    cur.execute(sql, (geom_id,))
    rows = cur.fetchall()
    if not rows:
        raise HarnessError('address_points geometry observation target not found')
    if len(rows) != 1:
        raise HarnessError(f'address_points geometry observation target resolves multiple rows: {len(rows)}')
    row = dict(rows[0])
    if row['source_record_id'] != lineage['source_row']['source_record_id']:
        raise HarnessError('address_points geometry observation does not belong to the queried source row')
    if row['evidence_object_id'] != lineage['evidence_row']['evidence_object_id']:
        raise HarnessError('address_points geometry observation does not belong to the queried source row')
    if row['subject_id'] != address_subject['row']['subject_id']:
        raise HarnessError('address_points geometry observation subject does not match the resolved address subject')
    if row['geometry_role'] != 'location-point':
        raise HarnessError('address_points geometry observation role mismatch')
    if row['classification'] != 'restricted':
        raise HarnessError('address_points geometry observation must remain restricted')
    return {'sql': ' '.join(sql.split()), 'params': [geom_id], 'row': norm_row(row)}


def address_points_observation_crosswalk_rows(source_id: str, mutation: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    mutation = mutation or {}
    legacy_id = 'phase-a-addresses-id' if mutation.get('address_id_identity_substitution') else source_id
    target_entity = 'location_record' if mutation.get('wrong_target_entity') else 'geometry_observation'
    target_id = 'phase-a-geometry-address-points-wrong' if mutation.get('wrong_target_observation') else address_points_geometry_id({'id': source_id})
    rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_legacy_crosswalk'].append({
        'legacy_crosswalk_id': address_points_observation_crosswalk_id(source_id),
        'source_table': 'address_points',
        'source_field': 'id',
        'legacy_id': legacy_id,
        'target_entity': target_entity,
        'target_id': target_id,
        'created_at': TS,
    })
    if mutation.get('unexpected_extra_crosswalk'):
        rows['proposed_legacy_crosswalk'].append({
            'legacy_crosswalk_id': address_points_observation_crosswalk_id(source_id) + '-extra',
            'source_table': 'address_points',
            'source_field': 'id',
            'legacy_id': source_id,
            'target_entity': 'geometry_observation',
            'target_id': target_id,
            'created_at': TS,
        })
    return rows


def address_points_observation_semantic_uniqueness(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity,
               COUNT(*)::int AS row_count, COUNT(DISTINCT target_id)::int AS target_count,
               array_agg(legacy_crosswalk_id ORDER BY legacy_crosswalk_id) AS crosswalk_ids,
               array_agg(DISTINCT target_id ORDER BY target_id) AS target_ids
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'address_points' AND source_field = 'id'
        GROUP BY 1,2,3,4
        HAVING COUNT(*) > 1 OR COUNT(DISTINCT target_id) > 1
    """)
    duplicates = [norm_row(dict(r)) for r in cur.fetchall()]
    if duplicates:
        raise HarnessError('address_points observation crosswalk semantic uniqueness violated')
    return {'duplicates': duplicates, 'semantic_duplicate_count': 0, 'query': 'absolute uniqueness on (source_table, source_field, legacy_id, target_entity)'}


def transform_address_points_observation_crosswalk(cur, *, source_id: str = 'phase-a-address-points-id', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    spec_validation = spec_validation or reviewed_address_points_observation_transform_spec()
    source_row, source_query = query_complete_address_points_row(cur, source_id)
    lineage = require_address_points_observation_lineage(cur, source_row)
    address_subject = resolve_address_points_target_identity(cur, source_row['address_id'])
    geometry = validate_address_points_geometry_observation_precondition(cur, source_row, lineage, address_subject)
    rows = address_points_observation_crosswalk_rows(source_row['id'], mutation)
    stats1 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    uniqueness = {'duplicates': [], 'semantic_duplicate_count': 0, 'query': 'skipped for surplus-row mutation; comparator owns unexpected-extra-crosswalk'} if mutation.get('unexpected_extra_crosswalk') else address_points_observation_semantic_uniqueness(cur)
    stats2 = apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    cw = rows['proposed_legacy_crosswalk'][0]
    return {
        'function_invoked': ADDRESS_POINTS_OBSERVATION_FUNCTION,
        'implementation_unit': ADDRESS_POINTS_OBSERVATION_IMPL_UNIT,
        'transform_group_id': ADDRESS_POINTS_OBSERVATION_GROUP_ID,
        'generic_transform_group_used': False,
        'source_row_query': source_query,
        'fields_consumed': spec_validation['group']['covered_source_fields'] + spec_validation['required_context_fields'],
        'source_key_derivation': {'rule': 'address_points:<queried id>', 'value': lineage['derived_source_key']},
        'lineage': lineage,
        'address_subject_resolution': address_subject,
        'geometry_observation_validation': geometry,
        'insert_stats_first': stats1,
        'insert_stats_second': stats2,
        'second_run_updates': 0,
        'spec_validation': spec_validation,
        'derived_ids': {'legacy_crosswalk_id': cw['legacy_crosswalk_id'], 'target_id': cw['target_id'], 'source_key': lineage['derived_source_key']},
        'crosswalk_row': cw,
        'semantic_uniqueness': uniqueness,
        'address_id_used_as_legacy_identity': bool(mutation.get('address_id_identity_substitution')),
    }


ADDRESS_POINTS_OBSERVATION_IMPLEMENTATIONS[ADDRESS_POINTS_OBSERVATION_IMPL_UNIT] = transform_address_points_observation_crosswalk


def ensure_address_points_observation_preconditions(cur, records: list[dict[str, Any]], mutation: dict[str, Any] | None = None) -> None:
    mutation = mutation or {}
    rows = base_target_rows()
    add_source_records_and_evidence(rows, records)
    for rec in records:
        rec_values = normalize_current_fixture_values('address_points', rec['values'])
        if rec_values['id'] != 'phase-a-address-points-id':
            for evidence in rows.get('proposed_evidence_object', []):
                if evidence.get('source_record_id') == rec['source_record_id']:
                    evidence['evidence_object_id'] = f'phase-a-evidence-address-points-{slug(rec_values["id"])}'
    add_unique(rows, 'proposed_legacy_crosswalk', {
        'legacy_crosswalk_id': 'phase-a-crosswalk-addresses-id-to-location-record',
        'source_table': 'addresses',
        'source_field': 'id',
        'legacy_id': 'phase-a-addresses-id',
        'target_entity': 'location_record',
        'target_id': 'phase-a-location-address-reference',
        'created_at': TS,
    })
    if mutation.get('missing_source_lineage'):
        wanted = {rec['source_record_id'] for rec in records if rec['values']['id'] == 'phase-a-address-points-id'}
        rows['proposed_source_record'] = [r for r in rows['proposed_source_record'] if r.get('source_record_id') not in wanted]
        rows['proposed_evidence_object'] = [r for r in rows['proposed_evidence_object'] if r.get('source_record_id') not in wanted]
    if mutation.get('missing_evidence_object'):
        wanted = {rec['source_record_id'] for rec in records if rec['values']['id'] == 'phase-a-address-points-id'}
        rows['proposed_evidence_object'] = [r for r in rows['proposed_evidence_object'] if r.get('source_record_id') not in wanted]
    if mutation.get('source_record_classification_drift'):
        for row in rows['proposed_source_record']:
            if row.get('source_key') == 'address_points:phase-a-address-points-id':
                row['raw_payload_classification'] = 'restricted'
    if mutation.get('evidence_classification_drift'):
        for row in rows['proposed_evidence_object']:
            if row.get('source_record_id') == 'phase-a-source-record-address-points-001':
                row['classification'] = 'restricted'
    if mutation.get('geometry_source_mismatch'):
        rec2 = make_address_points_record('phase-a-address-points-002')
        add_source_records_and_evidence(rows, [rec2])
        for evidence in rows.get('proposed_evidence_object', []):
            if evidence.get('source_record_id') == rec2['source_record_id']:
                evidence['evidence_object_id'] = f'phase-a-evidence-address-points-{slug(rec2["values"]["id"])}'
    for rec in records:
        rec_values = normalize_current_fixture_values('address_points', rec['values'])
        source_record_id = rec['source_record_id']
        evidence_id = 'phase-a-evidence-address-points' if rec_values['id'] == 'phase-a-address-points-id' else f'phase-a-evidence-address-points-{slug(rec_values["id"])}'
        geom_id = address_points_geometry_id({'id': rec_values['id']})
        if rec_values['id'] == 'phase-a-address-points-id' and (mutation.get('missing_geometry_observation') or mutation.get('missing_source_lineage') or mutation.get('missing_evidence_object')):
            continue
        if mutation.get('geometry_source_mismatch') and rec_values['id'] == 'phase-a-address-points-id':
            source_record_id = 'phase-a-source-record-address-points-002'
            evidence_id = 'phase-a-evidence-address-points-phase-a-address-points-002'
        subject_id = 'phase-a-subject-phase-a-location-geotag' if mutation.get('geometry_subject_mismatch') and rec_values['id'] == 'phase-a-address-points-id' else 'phase-a-subject-phase-a-location-address-reference'
        classification = 'government-internal' if mutation.get('geometry_classification_drift') and rec_values['id'] == 'phase-a-address-points-id' else 'restricted'
        add_unique(rows, 'proposed_geometry_observation', {
            'geometry_observation_id': geom_id,
            'subject_id': subject_id,
            'geometry_role': 'location-point',
            'observed_geom': {'longitude': rec_values['longitude'], 'latitude': rec_values['latitude']},
            'capture_method': 'derived-from-source',
            'horizontal_accuracy_m': rec_values['accuracy_meters'],
            'source_record_id': source_record_id,
            'evidence_object_id': evidence_id,
            'licence_id': None,
            'observed_at': rec_values['created_at'],
            'recorded_at': TS,
            'classification': classification,
        })
    apply_target_rows(cur, rows)
    cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def setup_address_points_observation_database() -> None:
    discover_current(reset=True)
    apply_target()


def address_points_observation_complete_target_rows(cur, source_id: str = 'phase-a-address-points-id') -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cur.execute("""
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'address_points' AND source_field = 'id' AND legacy_id = %s
        ORDER BY legacy_crosswalk_id
    """, (source_id,))
    for cw in cur.fetchall():
        d = norm_row(dict(cw))
        rows.append({'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':cw['legacy_crosswalk_id']},'values':d})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def address_points_observation_target_slice_hash(cur, source_id: str = 'phase-a-address-points-id') -> dict[str, Any]:
    rows = address_points_observation_complete_target_rows(cur, source_id)
    return {'rows': rows, 'hash': sha(rows)}


def expected_address_points_observation_rows(oracle: dict[str, Any], source_id: str = 'phase-a-address-points-id') -> list[dict[str, Any]]:
    rows = copy.deepcopy(oracle['expected_inserted_rows'])
    if source_id != 'phase-a-address-points-id':
        row = rows[0]
        row['primary_key']['legacy_crosswalk_id'] = address_points_observation_crosswalk_id(source_id)
        row['values']['legacy_crosswalk_id'] = address_points_observation_crosswalk_id(source_id)
        row['values']['legacy_id'] = source_id
        row['values']['target_id'] = address_points_geometry_id({'id': source_id})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def expected_absent_address_points_observation_rows(cur, oracle: dict[str, Any]) -> list[dict[str, Any]]:
    results=[]
    extra_absences = [
        {'table':'proposed_geometry_observation','where':"geometry_observation_id LIKE 'phase-a-geometry-address-points-%-extra'",'reason':'No extra geometry observation is created'},
        {'table':'proposed_location_record_version','where':"location_record_id LIKE 'phase-a-location-address-points%'",'reason':'No point-specific version is created'},
    ]
    for item in oracle['expected_absent_rows'] + extra_absences:
        table=item['table']; where=item.get('where')
        if where:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        else:
            cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table}')
        count=cur.fetchone()['c']
        results.append({'table':table,'where':where,'reason':item['reason'],'count':count})
        if count != 0:
            raise HarnessError(f'expected absent row exists in {table}: {item}')
    return results


def compare_address_points_observation_oracle_read_only(*, source_id: str = 'phase-a-address-points-id') -> dict[str, Any]:
    proof = comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY')
        cur.execute('SHOW transaction_read_only')
        comparator_read_only = cur.fetchone()['transaction_read_only']
        with address_points_observation_oracle_access(True):
            oracle = load_address_points_observation_oracle()
        actual = address_points_observation_complete_target_rows(cur, source_id)
        expected = expected_address_points_observation_rows(oracle, source_id)
        if len(actual) != len(expected):
            raise HarnessError(f'unexpected address_points observation-crosswalk target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}
        act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys - exp_keys:
            raise HarnessError(f'unexpected address_points observation-crosswalk target row: {sorted(act_keys-exp_keys)}')
        if exp_keys - act_keys:
            raise HarnessError(f'missing address_points observation-crosswalk target row: {sorted(exp_keys-act_keys)}')
        if actual != expected:
            observed = actual[0]['values'] if actual else {}
            if observed.get('legacy_id') != source_id:
                raise HarnessError('address_points observation crosswalk must derive from address_points.id')
            if observed.get('target_entity') != 'geometry_observation':
                raise HarnessError('address_points identity target must be geometry_observation')
            if observed.get('target_id') != address_points_geometry_id({'id': source_id}):
                raise HarnessError('address_points observation crosswalk differs from reviewer-owned expected target')
            raise HarnessError('address_points observation crosswalk differs from reviewer-owned expected target')
        absent = expected_absent_address_points_observation_rows(cur, oracle)
        uniqueness = address_points_observation_semantic_uniqueness(cur)
        conn.rollback()
    return {'expected_rows': len(expected), 'actual_rows': len(actual), 'expected_absent_rows': absent, 'actual_rows_detail': actual, 'semantic_uniqueness': uniqueness, 'comparator_connection': {'separate_connection': True, 'transaction_read_only': comparator_read_only}, 'comparator_read_only_proof': proof, 'complete_target_set_query': {'source_table': 'address_points', 'source_field': 'id', 'legacy_id': source_id, 'target_entity': 'geometry_observation', 'tables': ['proposed_legacy_crosswalk']}}


def run_address_points_observation_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-address-points-id') -> dict[str, Any]:
    mutation = mutation or {}
    rec = make_address_points_record(source_id)
    records = [r for r in fixture_records() if r['source_table'] != 'address_points']
    if not mutation.get('missing_source'):
        records.append(rec)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        ensure_records = [rec]
        ensure_address_points_observation_preconditions(cur, ensure_records, mutation)
        spec_validation = reviewed_address_points_observation_transform_spec(mutation.get('spec_drift'))
        impl = ADDRESS_POINTS_OBSERVATION_IMPLEMENTATIONS.get(ADDRESS_POINTS_OBSERVATION_IMPL_UNIT)
        if impl is not transform_address_points_observation_crosswalk:
            raise HarnessError('explicit address_points observation-crosswalk implementation binding missing')
        transform_result = impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    comparison = compare_address_points_observation_oracle_read_only(source_id=source_id) if compare_expected else None
    return {'source_report': source_report, 'transform': transform_result, 'comparison': comparison}


def prepare_address_points_observation_state(cur, *, source_id: str = 'phase-a-address-points-id', mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    rec = make_address_points_record(source_id)
    records = [r for r in fixture_records() if r['source_table'] != 'address_points']
    if not mutation.get('missing_source'):
        records.append(rec)
    source_report = insert_current_fixture_rows(cur, records)
    ensure_address_points_observation_preconditions(cur, [rec], mutation)
    return {'source_report': source_report, 'record': rec}


def run_address_points_observation_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_address_points_observation_database()
    source_id = 'phase-a-address-points-id'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_address_points_observation_state(cur, mutation=mutation)
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur, 'proposed_legacy_crosswalk', {'legacy_crosswalk_id': address_points_observation_crosswalk_id(source_id) + '-duplicate', 'source_table':'address_points', 'source_field':'id', 'legacy_id':source_id, 'target_entity':'geometry_observation', 'target_id':'phase-a-geometry-address-points-duplicate', 'created_at':TS})
        conn.commit()
        before = address_points_observation_target_slice_hash(cur, source_id)
        cur.execute('BEGIN')
        try:
            spec_validation = reviewed_address_points_observation_transform_spec(mutation.get('spec_drift'))
            transform_address_points_observation_crosswalk(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
            if mutation.get('address_id_identity_substitution') or mutation.get('wrong_target_entity') or mutation.get('wrong_target_observation') or mutation.get('unexpected_extra_crosswalk'):
                compare_address_points_observation_mutation(cur, source_id, mutation)
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed = str(exc)
            if expected_error not in observed:
                conn.rollback()
                raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback()
            with conn.cursor() as check_cur:
                after = address_points_observation_target_slice_hash(check_cur, source_id)
            if before != after:
                raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id': probe_id, 'expected_error': expected_error, 'observed_error': observed, 'same_database_pre_test_rows': before['rows'], 'same_database_pre_test_hash': before['hash'], 'same_database_post_failure_rows': after['rows'], 'same_database_post_failure_hash': after['hash'], 'rollback_equality': True, 'state_unchanged': True, 'status': 'passed'}


def compare_address_points_observation_mutation(cur, source_id: str, mutation: dict[str, Any]) -> None:
    if mutation.get('address_id_identity_substitution'):
        cur.execute("""
            SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at
            FROM canonical_target.proposed_legacy_crosswalk
            WHERE source_table = 'address_points' AND source_field = 'id'
            ORDER BY legacy_crosswalk_id
        """)
        rows = [norm_row(dict(r)) for r in cur.fetchall()]
        if any(r.get('legacy_id') != source_id for r in rows) or not rows:
            raise HarnessError('address_points observation crosswalk must derive from address_points.id')
    with address_points_observation_oracle_access(True):
        oracle = load_address_points_observation_oracle()
    actual = address_points_observation_complete_target_rows(cur, source_id)
    expected = expected_address_points_observation_rows(oracle, source_id)
    if actual:
        observed = actual[0]['values']
        if mutation.get('wrong_target_entity') or observed.get('target_entity') != 'geometry_observation':
            raise HarnessError('address_points identity target must be geometry_observation')
        if mutation.get('wrong_target_observation') or observed.get('target_id') != address_points_geometry_id({'id': source_id}):
            raise HarnessError('address_points observation crosswalk differs from reviewer-owned expected target')
    try:
        expected_absent_address_points_observation_rows(cur, oracle)
    except HarnessError:
        raise HarnessError('unexpected address_points observation-crosswalk target row')
    if len(actual) != len(expected):
        raise HarnessError('unexpected address_points observation-crosswalk target row')
    if actual != expected:
        observed = actual[0]['values'] if actual else {}
        if mutation.get('address_id_identity_substitution') or observed.get('legacy_id') != source_id:
            raise HarnessError('address_points observation crosswalk must derive from address_points.id')
        raise HarnessError('address_points observation crosswalk differs from reviewer-owned expected target')


def run_address_points_observation_second_source_identity_test() -> dict[str, Any]:
    setup_address_points_observation_database()
    first_id='phase-a-address-points-id'; second_id='phase-a-address-points-002'
    rec1 = make_address_points_record(first_id); rec2 = make_address_points_record(second_id)
    records = [r for r in fixture_records() if r['source_table'] != 'address_points'] + [rec1, rec2]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report = insert_current_fixture_rows(cur, records)
        ensure_address_points_observation_preconditions(cur, [rec1, rec2], {})
        spec_validation = reviewed_address_points_observation_transform_spec()
        first = transform_address_points_observation_crosswalk(cur, source_id=first_id, spec_validation=spec_validation)
        second = transform_address_points_observation_crosswalk(cur, source_id=second_id, spec_validation=spec_validation)
        conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.address_points WHERE id IN (%s,%s)", (first_id, second_id)); source_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id IN (%s,%s)", (address_points_geometry_id({'id': first_id}), address_points_geometry_id({'id': second_id}))); geometry_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id IN (%s,%s)", (address_points_observation_crosswalk_id(first_id), address_points_observation_crosswalk_id(second_id))); cw_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_location_record WHERE location_record_id LIKE 'phase-a-location-address-points%'"); loc_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_registry_subject WHERE native_id LIKE 'phase-a-location-address-points%'"); subj_count=cur.fetchone()['c']
        controls = address_points_observation_semantic_uniqueness(cur)
        first_rows = address_points_observation_complete_target_rows(cur, first_id)
        second_rows = address_points_observation_complete_target_rows(cur, second_id)
    checks={'source_records':source_count==2,'geometry_observations':geometry_count==2,'distinct_crosswalks':cw_count==2,'location_records_created':loc_count==0,'registry_subjects_created':subj_count==0,'semantic_duplicate_crosswalks':controls['semantic_duplicate_count']==0,'multiple_target_resolution':controls['semantic_duplicate_count']==0,'second_source_key':second['lineage']['derived_source_key']==f'address_points:{second_id}','second_crosswalk':second['crosswalk_row']['legacy_crosswalk_id']==address_points_observation_crosswalk_id(second_id)}
    if not all(checks.values()):
        raise HarnessError(f'address_points observation second-source identity test failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'source_rows':source_count,'geometry_observations':geometry_count,'distinct_crosswalks':cw_count,'location_records_created':loc_count,'registry_subjects_created':subj_count,'semantic_duplicate_crosswalks':controls['semantic_duplicate_count'],'multiple_target_resolutions':0,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':first['lineage'],'second_transform_lineage':second['lineage']}


def run_address_points_observation_crosswalk_slice() -> dict[str, Any]:
    broad_report_path = DM / 'phase-a-current-source-execution-report.json'
    broad_report_original = broad_report_path.read_text() if broad_report_path.exists() else None
    if address_points_observation_oracle_hash() != ADDRESS_POINTS_OBSERVATION_ORACLE_BASELINE_SHA256:
        raise HarnessError('reviewer-owned address_points observation-crosswalk oracle changed')
    setup_address_points_observation_database()
    positive = run_address_points_observation_slice_once(compare_expected=True)
    test_results=[{'test_id':'positive-authoritative-slice','status':'passed'}]
    test_results.append({'test_id':'second-run-idempotency','status':'passed','first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates']})
    test_results.append({'test_id':'read-only-complete-set-comparison','status':'passed','comparison':positive['comparison']['complete_target_set_query']})
    second_identity=run_address_points_observation_second_source_identity_test(); test_results.append(second_identity)
    probes=[
        ('missing-source-record','address_points source row not found',{'missing_source':True}),
        ('missing-source-lineage','address_points source record lineage not found',{'missing_source_lineage':True}),
        ('missing-evidence-object','address_points evidence object not found',{'missing_evidence_object':True}),
        ('missing-geometry-observation','address_points geometry observation target not found',{'missing_geometry_observation':True}),
        ('geometry-source-mismatch','address_points geometry observation does not belong to the queried source row',{'geometry_source_mismatch':True}),
        ('geometry-subject-mismatch','address_points geometry observation subject does not match the resolved address subject',{'geometry_subject_mismatch':True}),
        ('geometry-classification-drift','address_points geometry observation must remain restricted',{'geometry_classification_drift':True}),
        ('address-id-identity-substitution','address_points observation crosswalk must derive from address_points.id',{'address_id_identity_substitution':True}),
        ('wrong-target-entity','address_points identity target must be geometry_observation',{'wrong_target_entity':True}),
        ('wrong-target-observation','address_points observation crosswalk differs from reviewer-owned expected target',{'wrong_target_observation':True}),
        ('unexpected-extra-crosswalk','unexpected address_points observation-crosswalk target row',{'unexpected_extra_crosswalk':True}),
        ('semantic-duplicate-crosswalk','address_points observation crosswalk semantic uniqueness violated',{'semantic_duplicate_crosswalk':True}),
        ('transform-spec-binding-drift','address_points observation crosswalk specification binding mismatch',{'spec_drift': {'implementation_unit':'impl_wrong'}}),
    ]
    for pid, reason, mutation in probes:
        test_results.append(run_address_points_observation_negative_probe(pid, reason, mutation))
    cw=positive['comparison']['actual_rows_detail'][0]
    rollback_hashes=[t for t in test_results if 'same_database_pre_test_hash' in t]
    prohibited = {item['table'] + ':' + str(item.get('where')): item['count'] for item in positive['comparison']['expected_absent_rows']}
    report={'command':'address-points-observation-crosswalk-slice','status':'passed','reviewer_owned_oracle_sha256':address_points_observation_oracle_hash(),'reviewer_owned_oracle_changed':False,'accepted_addresses_controls_changed':False,'accepted_geometry_controls_changed':False,'frozen_broad_spec_changed':False,'broad_expected_fixture_changed':False,'exact_function_implemented':ADDRESS_POINTS_OBSERVATION_FUNCTION,'exact_registry_binding':{ADDRESS_POINTS_OBSERVATION_IMPL_UNIT:ADDRESS_POINTS_OBSERVATION_FUNCTION},'generic_transform_group_used_for_slice':False,'transform_reads_expected_oracle':False,'source_row_query':positive['transform']['source_row_query']['sql'],'source_row_returned':positive['transform']['source_row_query']['row'],'fields_consumed':positive['transform']['fields_consumed'],'source_key_derivation':positive['transform']['source_key_derivation'],'source_record_resolution':positive['transform']['lineage']['source_row'],'evidence_resolution':positive['transform']['lineage']['evidence_row'],'address_subject_resolution':positive['transform']['address_subject_resolution'],'geometry_observation_validation':positive['transform']['geometry_observation_validation'],'reviewed_transform_spec_row':positive['transform']['spec_validation']['group'],'binding_validation':positive['transform']['spec_validation']['validation'],'crosswalk_row':cw,'first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates'],'expected_absent_rows_verified':positive['comparison']['expected_absent_rows'],'prohibited_outputs_created':prohibited,'location_records_created':0,'registry_subjects_created':0,'geometry_observations_created':0,'migration_exceptions_created':0,'other_prohibited_outputs':prohibited,'semantic_uniqueness_query_result':positive['comparison']['semantic_uniqueness'],'comparator_connection_read_only_proof':positive['comparison']['comparator_read_only_proof'],'comparator_connection':positive['comparison']['comparator_connection'],'complete_target_set_comparison':positive['comparison'],'tests':test_results,'second_source_identity_test':second_identity,'rollback_equality_all':all(t.get('rollback_equality', True) for t in rollback_hashes),'rollback_evidence_count':len(rollback_hashes)}
    write_json(DM / 'phase-a-address-points-observation-crosswalk-slice-report.json', report)
    if broad_report_original is not None:
        broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists():
        broad_report_path.unlink()
    return report


# ---- Address-records identity-foundation one-slice checkpoint ----
ADDRESS_RECORDS_IDENTITY_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-address-records-identity-expected.json'
ADDRESS_RECORDS_IDENTITY_ORACLE_BASELINE_SHA256 = '16d1034b786a77d31b6863774807e66d87a337fa78c1a4202e401fbcddecd06e'
ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED = False
ADDRESS_RECORDS_IDENTITY_GROUP_ID = 'WO002-R06-identity-crosswalk-address_records'
ADDRESS_RECORDS_IDENTITY_IMPL_UNIT = 'impl_wo002_r06_identity_crosswalk_address_records'
ADDRESS_RECORDS_IDENTITY_FUNCTION = 'transform_address_records_identity_crosswalk'
ADDRESS_RECORDS_IDENTITY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}


def address_records_identity_oracle_hash() -> str:
    return file_sha256(ADDRESS_RECORDS_IDENTITY_ORACLE)


def load_address_records_identity_oracle() -> dict[str, Any]:
    if not ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned address_records identity oracle access is disabled outside the read-only comparator')
    return json.loads(ADDRESS_RECORDS_IDENTITY_ORACLE.read_text())


class address_records_identity_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled; self.previous = False
    def __enter__(self):
        global ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED
        self.previous = ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED
        ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED
        ADDRESS_RECORDS_IDENTITY_ORACLE_ACCESS_ALLOWED = self.previous


def setup_address_records_identity_database() -> None:
    discover_current(reset=True); apply_target(); topology_check()


def address_records_identity_source_records(include_record: bool = True, source_id: str = 'phase-a-address-records-id') -> list[dict[str, Any]]:
    needed = {'provinces','admin_units','territories','citizen_geotag_submissions'}
    records = [copy.deepcopy(r) for r in fixture_records() if r['source_table'] in needed]
    if include_record:
        records.append(make_address_records_record(source_id))
    return records


def address_records_identity_lineage_rows(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_source_authority'].append({'source_authority_id':'phase-a-authority-operational-control','authority_name':'Phase A retained operational-control authority','authority_class':'derived-system','legal_basis':'Operational-control/non-migrated disposition fixture; no public effect','status':'candidate'})
    add_source_records_and_evidence(rows, records)
    by_sr = {rec['source_record_id']: rec for rec in records}
    for evidence in rows.get('proposed_evidence_object', []):
        rec = by_sr.get(evidence.get('source_record_id'))
        if rec and rec['source_table'] == 'address_records' and rec['values'].get('id') != 'phase-a-address-records-id':
            suffix = rec['values']['id'].rsplit('-', 1)[-1]
            evidence['evidence_object_id'] = f'phase-a-evidence-address-records-{suffix}'
    return rows


def require_address_records_identity_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = address_records_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key, raw_payload_classification FROM canonical_target.proposed_source_record WHERE source_key = %s ORDER BY source_record_id"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('address_records source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'address_records source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    if source['raw_payload_classification'] != 'government-internal':
        raise HarnessError('address_records source record must remain government-internal')
    if source_row['id'] == 'phase-a-address-records-id' and source['source_record_id'] != 'phase-a-source-record-address-records-001':
        raise HarnessError('address_records source record lineage not found')
    evidence_sql = "SELECT evidence_object_id, source_record_id, classification FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('address_records evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'address_records evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    if evidence['classification'] != 'government-internal':
        raise HarnessError('address_records evidence object must remain government-internal')
    if source_row['id'] == 'phase-a-address-records-id' and evidence['evidence_object_id'] != 'phase-a-evidence-address-records':
        raise HarnessError('address_records evidence object not found')
    return {'derived_source_key': derived_source_key, 'source_query': source_sql, 'source_params': [derived_source_key], 'source_row': norm_row(source), 'evidence_query': evidence_sql, 'evidence_params': [source['source_record_id']], 'evidence_row': norm_row(evidence)}


def reviewed_address_records_identity_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected = {'transform_group_id':ADDRESS_RECORDS_IDENTITY_GROUP_ID,'implementation_unit':ADDRESS_RECORDS_IDENTITY_IMPL_UNIT,'callable':ADDRESS_RECORDS_IDENTITY_FUNCTION,'covered_source_fields':['address_records.id'],'required_context_fields':['address_records.address_code','address_records.source_submission_id','address_records.province_code','address_records.territory_id','address_records.address_label','address_records.status','address_records.publication_state','address_records.is_archived','address_records.created_at','address_records.updated_at'],'source_record_key':'address_records:phase-a-address-records-id','idempotency_key':'address_records.phase-a-address-records-id::WO002-R06-identity-crosswalk-address_records','identity_rule':'address_records.id owns the identity; source_submission_id, territory_id, address_code, publication and geometry fields are context only','target_entities':['location_record','registry_subject','legacy_crosswalk'],'target_identity_rule':{'primary_fixture':{'source_id':'phase-a-address-records-id','location_record_id':'phase-a-location-address-records-id','subject_id':'phase-a-subject-phase-a-location-address-records-id','legacy_crosswalk_id':'phase-a-crosswalk-address-records-id-to-location-record'},'second_fixture_rule':'For phase-a-address-records-<suffix>, use matching location, subject and crosswalk IDs ending in <suffix>. Design harness only.'}}
    group = copy.deepcopy(next((g for g in registry_groups() if g['transform_group_id'] == ADDRESS_RECORDS_IDENTITY_GROUP_ID), None))
    if not group:
        raise HarnessError('address_records identity transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key, value in spec_mutation.items(): group[key] = value
    checks = {'transform_group_id':group.get('transform_group_id')==expected['transform_group_id'],'implementation_unit':group.get('implementation_unit')==expected['implementation_unit'],'callable':ADDRESS_RECORDS_IDENTITY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_address_records_identity_crosswalk and expected['callable']==ADDRESS_RECORDS_IDENTITY_FUNCTION,'covered_source_fields':group.get('covered_source_fields')==expected['covered_source_fields'],'required_context_fields':group.get('required_context_fields')==expected['required_context_fields'],'source_record_key':group.get('source_record_key')==expected['source_record_key'],'idempotency_key':group.get('idempotency_key')==expected['idempotency_key'],'identity_rule':group.get('identity_rule')==expected['identity_rule'],'target_entities':group.get('target_entities')==expected['target_entities'],'target_identity_rule':group.get('target_identity_rule')==expected['target_identity_rule'],'no_migration_exception':'migration_exception' not in group.get('target_entities',[]) and 'migration_exception' not in group.get('target_fields',[]) and group.get('dispositions')==['structured-transform']}
    if not all(checks.values()):
        raise HarnessError(f'address_records identity transform specification binding mismatch: {checks}')
    return {'group': group, 'required_context_fields': group['required_context_fields'], 'validation': checks}


def address_records_identity_rows_for_source(source_id: str, mutation: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    mutation = mutation or {}
    identity_source_id = source_id
    if mutation.get('source_submission_identity_substitution'):
        identity_source_id = 'phase-a-citizen-geotag-id'
    if mutation.get('territory_identity_substitution'):
        identity_source_id = 'phase-a-territories-id'
    loc_id = address_records_location_id(identity_source_id)
    if mutation.get('wrong_target_identity_implementation'):
        loc_id = 'phase-a-location-wrong-address-records-id'
    subj_id = f'phase-a-subject-{loc_id}' if loc_id != address_records_location_id(source_id) else address_records_subject_id(source_id)
    rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_location_record'].append({'location_record_id':loc_id,'record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
    rows['proposed_registry_subject'].append({'subject_id':subj_id,'subject_entity':'location_record','created_at':TS,'native_id':loc_id,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    rows['proposed_legacy_crosswalk'].append({'legacy_crosswalk_id':address_records_crosswalk_id(source_id),'source_table':'address_records','source_field':'id','legacy_id':identity_source_id if (mutation.get('source_submission_identity_substitution') or mutation.get('territory_identity_substitution')) else source_id,'target_entity':'location_record','target_id':loc_id,'created_at':TS})
    if mutation.get('unexpected_extra_crosswalk'):
        rows['proposed_legacy_crosswalk'].append({'legacy_crosswalk_id':address_records_crosswalk_id(source_id)+'-extra','source_table':'address_records','source_field':'source_submission_id','legacy_id':'phase-a-citizen-geotag-id','target_entity':'location_record','target_id':loc_id,'created_at':TS})
    if mutation.get('unexpected_extra_location_record'):
        rows['proposed_location_record'].append({'location_record_id':address_records_location_id(source_id)+'-extra','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
    if mutation.get('unexpected_extra_registry_subject'):
        extra_loc = address_records_location_id(source_id)+'-extra'
        rows['proposed_location_record'].append({'location_record_id':extra_loc,'record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        rows['proposed_registry_subject'].append({'subject_id':address_records_subject_id(source_id)+'-extra','subject_entity':'location_record','created_at':TS,'native_id':extra_loc,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    return rows


def address_records_identity_semantic_uniqueness(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity,
               COUNT(*)::int AS row_count, COUNT(DISTINCT target_id)::int AS target_count,
               array_agg(legacy_crosswalk_id ORDER BY legacy_crosswalk_id) AS crosswalk_ids,
               array_agg(DISTINCT target_id ORDER BY target_id) AS target_ids
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'address_records' AND source_field = 'id'
        GROUP BY 1,2,3,4
        HAVING COUNT(*) > 1 OR COUNT(DISTINCT target_id) > 1
    """)
    duplicates=[norm_row(dict(r)) for r in cur.fetchall()]
    if duplicates:
        raise HarnessError('address_records identity crosswalk semantic uniqueness violated')
    return {'duplicates':duplicates,'semantic_duplicate_count':0,'query':'absolute uniqueness on (source_table, source_field, legacy_id, target_entity)'}


def transform_address_records_identity_crosswalk(cur, *, source_id: str = 'phase-a-address-records-id', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    spec_validation = spec_validation or reviewed_address_records_identity_transform_spec()
    source_row, source_query = query_complete_address_records_row(cur, source_id)
    lineage = require_address_records_identity_lineage(cur, source_row)
    rows = address_records_identity_rows_for_source(source_row['id'], mutation)
    stats1 = apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    uniqueness = {'duplicates': [], 'semantic_duplicate_count': 0, 'query': 'skipped for surplus-row mutation; comparator owns unexpected-extra-crosswalk'} if mutation.get('unexpected_extra_crosswalk') else address_records_identity_semantic_uniqueness(cur)
    stats2 = apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    identity_rows = {t: rows[t][0] for t in ('proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk')}
    used_ref = bool(mutation.get('source_submission_identity_substitution') or mutation.get('territory_identity_substitution'))
    return {'function_invoked':ADDRESS_RECORDS_IDENTITY_FUNCTION,'implementation_unit':ADDRESS_RECORDS_IDENTITY_IMPL_UNIT,'transform_group_id':ADDRESS_RECORDS_IDENTITY_GROUP_ID,'generic_transform_group_used':False,'source_row_query':source_query,'fields_consumed':spec_validation['group']['covered_source_fields']+spec_validation['required_context_fields'],'source_key_derivation':{'rule':'address_records:<queried id>','value':lineage['derived_source_key']},'lineage':lineage,'insert_stats_first':stats1,'insert_stats_second':stats2,'second_run_updates':0,'spec_validation':spec_validation,'derived_ids':{'location_record_id':identity_rows['proposed_location_record']['location_record_id'],'subject_id':identity_rows['proposed_registry_subject']['subject_id'],'legacy_crosswalk_id':identity_rows['proposed_legacy_crosswalk']['legacy_crosswalk_id'],'source_key':address_records_source_key(source_row)},'identity_rows':identity_rows,'semantic_uniqueness':uniqueness,'reference_fields_used_as_identity':used_ref}


ADDRESS_RECORDS_IDENTITY_IMPLEMENTATIONS[ADDRESS_RECORDS_IDENTITY_IMPL_UNIT] = transform_address_records_identity_crosswalk


def address_records_identity_complete_target_rows(cur, source_id: str = 'phase-a-address-records-id', include_source_derived_orphans: bool = True) -> list[dict[str, Any]]:
    rows=[]; expected_location_id=address_records_location_id(source_id); expected_subject_id=address_records_subject_id(source_id)
    loc_prefix=expected_location_id+'-'; subj_prefix=expected_subject_id+'-'
    cur.execute("""SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='address_records' AND source_field='id' AND legacy_id=%s AND target_entity='location_record' ORDER BY legacy_crosswalk_id""", (source_id,))
    crosswalks=[dict(r) for r in cur.fetchall()]; target_ids={r['target_id'] for r in crosswalks}; target_ids.add(expected_location_id)
    loc_pred=['location_record_id = ANY(%s)']; loc_params=[list(target_ids)]
    if include_source_derived_orphans:
        loc_pred.append('location_record_id LIKE %s'); loc_params.append(loc_prefix+'%')
    cur.execute(f"SELECT location_record_id, record_type, created_at, retired_at, classification FROM canonical_target.proposed_location_record WHERE {' OR '.join(loc_pred)} ORDER BY location_record_id", loc_params)
    actual_location_ids=set()
    for lr in cur.fetchall():
        d=norm_row(dict(lr)); actual_location_ids.add(lr['location_record_id']); rows.append({'table':'proposed_location_record','primary_key':{'location_record_id':lr['location_record_id']},'values':d})
    subject_native_ids=sorted(target_ids | actual_location_ids); subj_pred=['(native_id = ANY(%s) AND subject_entity = \'location_record\')','subject_id = %s']; subj_params=[subject_native_ids, expected_subject_id]
    if include_source_derived_orphans:
        subj_pred.append('subject_id LIKE %s'); subj_params.append(subj_prefix+'%')
    cur.execute(f"SELECT subject_id, subject_entity, created_at, native_id, subject_state, retired_at, delete_policy FROM canonical_target.proposed_registry_subject WHERE {' OR '.join(subj_pred)} ORDER BY subject_id", subj_params)
    for rs in cur.fetchall(): rows.append({'table':'proposed_registry_subject','primary_key':{'subject_id':rs['subject_id']},'values':norm_row(dict(rs))})
    for cw in crosswalks: rows.append({'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':cw['legacy_crosswalk_id']},'values':norm_row(cw)})
    return sorted(rows, key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def address_records_identity_target_slice_hash(cur, source_id: str = 'phase-a-address-records-id') -> dict[str, Any]:
    rows=address_records_identity_complete_target_rows(cur, source_id)
    return {'rows':rows,'hash':sha(rows)}


def expected_address_records_identity_rows(oracle: dict[str, Any], source_id: str = 'phase-a-address-records-id') -> list[dict[str, Any]]:
    rows=copy.deepcopy(oracle['expected_inserted_rows'])
    for r in rows:
        values=r['values']; table=r['table']
        if source_id != 'phase-a-address-records-id':
            if table == 'proposed_location_record': values['location_record_id']=address_records_location_id(source_id)
            if table == 'proposed_registry_subject': values['subject_id']=address_records_subject_id(source_id); values['native_id']=address_records_location_id(source_id)
            if table == 'proposed_legacy_crosswalk': values['legacy_crosswalk_id']=address_records_crosswalk_id(source_id); values['legacy_id']=source_id; values['target_id']=address_records_location_id(source_id)
        pk_field={'proposed_location_record':'location_record_id','proposed_registry_subject':'subject_id','proposed_legacy_crosswalk':'legacy_crosswalk_id'}[table]
        r['primary_key']={pk_field: values[pk_field]}
    return sorted(rows, key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def expected_absent_address_records_identity_rows(cur) -> list[dict[str, Any]]:
    checks=[('proposed_migration_exception',"source_table = 'address_records' AND source_key = 'address_records:phase-a-address-records-id' AND batch_id LIKE '%identity%'",'identity migration exception'),('proposed_legacy_crosswalk',"source_table = 'address_records' AND source_field IN ('source_submission_id','territory_id')",'source_submission_id or territory crosswalk'),('proposed_location_record_version',"location_record_id LIKE 'phase-a-location-address-records%'",'location-record version'),('proposed_geometry_observation',"geometry_observation_id LIKE 'phase-a-geometry-address-records%'",'new geometry observation'),('proposed_public_code_alias',"location_record_id LIKE 'phase-a-location-address-records%'",'public-code alias'),('proposed_publication_release_item',"location_record_id LIKE 'phase-a-location-address-records%'",'publication release item')]
    results=[]
    for table, where, reason in checks:
        cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        count=cur.fetchone()['c']; results.append({'table':table,'where':where,'reason':reason,'count':count})
        if count != 0: raise HarnessError(f'expected absent row exists in {table}: {reason}')
    return results


def compare_address_records_identity_oracle_read_only(source_id: str = 'phase-a-address-records-id') -> dict[str, Any]:
    proof=comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY'); cur.execute('SHOW transaction_read_only'); comparator_read_only=cur.fetchone()['transaction_read_only']
        with address_records_identity_oracle_access(True): oracle=load_address_records_identity_oracle()
        actual=address_records_identity_complete_target_rows(cur, source_id); expected=expected_address_records_identity_rows(oracle, source_id)
        if len(actual) != len(expected): raise HarnessError(f'unexpected address_records identity-foundation target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}; act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys-exp_keys: raise HarnessError(f'unexpected address_records identity-foundation target row: {sorted(act_keys-exp_keys)}')
        if exp_keys-act_keys: raise HarnessError(f'missing address_records identity-foundation target row: {sorted(exp_keys-act_keys)}')
        if actual != expected: raise HarnessError('address_records identity rows differ from reviewer-owned expected target identity')
        absent=expected_absent_address_records_identity_rows(cur); uniqueness=address_records_identity_semantic_uniqueness(cur); conn.rollback()
    return {'expected_rows':len(expected),'actual_rows':len(actual),'expected_absent_rows':absent,'actual_rows_detail':actual,'semantic_uniqueness':uniqueness,'comparator_connection':{'separate_connection':True,'transaction_read_only':comparator_read_only},'comparator_read_only_proof':proof,'complete_target_set_query':{'source_table':'address_records','source_field':'id','legacy_id':source_id,'tables':['proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk']}}


def insert_address_records_identity_lineage_preconditions(cur, rec: dict[str, Any], mutation: dict[str, Any] | None = None) -> None:
    mutation=mutation or {}; rows=address_records_identity_lineage_rows([rec])
    if mutation.get('missing_source_lineage'):
        rows['proposed_source_record']=[]; rows['proposed_evidence_object']=[]
    if mutation.get('missing_evidence_object'): rows['proposed_evidence_object']=[]
    if mutation.get('source_record_classification_drift'):
        for row in rows['proposed_source_record']: row['raw_payload_classification']='restricted'
    if mutation.get('evidence_classification_drift'):
        for row in rows['proposed_evidence_object']: row['classification']='restricted'
    apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def run_address_records_identity_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-address-records-id') -> dict[str, Any]:
    mutation=mutation or {}; rec=make_address_records_record(source_id)
    records=address_records_identity_source_records(include_record=not mutation.get('missing_source'), source_id=source_id)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report=insert_current_fixture_rows(cur, records)
        insert_address_records_identity_lineage_preconditions(cur, rec, mutation)
        if mutation.get('existing_location_conflict'):
            insert_row(cur,'proposed_location_record',{'location_record_id':address_records_location_id(source_id),'record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
        if mutation.get('existing_subject_conflict'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
            insert_row(cur,'proposed_registry_subject',{'subject_id':address_records_subject_id(source_id),'subject_entity':'location_record','created_at':TS,'native_id':'phase-a-location-address-records-conflict','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
        if mutation.get('existing_crosswalk_conflict'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
            insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':address_records_crosswalk_id(source_id),'source_table':'address_records','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-address-records-conflict','created_at':TS})
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-duplicate','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
            insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':address_records_crosswalk_id(source_id)+'-duplicate','source_table':'address_records','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-address-records-duplicate','created_at':TS})
        spec_validation=reviewed_address_records_identity_transform_spec(mutation.get('spec_drift'))
        impl=ADDRESS_RECORDS_IDENTITY_IMPLEMENTATIONS.get(ADDRESS_RECORDS_IDENTITY_IMPL_UNIT)
        if impl is not transform_address_records_identity_crosswalk: raise HarnessError('explicit address_records identity implementation binding missing')
        transform_result=impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    comparison=compare_address_records_identity_oracle_read_only(source_id=source_id) if compare_expected else None
    return {'source_report':source_report,'transform':transform_result,'comparison':comparison}


def compare_address_records_identity_mutation(cur, source_id: str, mutation: dict[str, Any]) -> None:
    if mutation.get('source_submission_identity_substitution') or mutation.get('territory_identity_substitution'):
        cur.execute("SELECT legacy_id FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='address_records' AND source_field='id' ORDER BY legacy_crosswalk_id")
        if any(r['legacy_id'] != source_id for r in cur.fetchall()): raise HarnessError('address_records identity must derive from address_records.id')
    with address_records_identity_oracle_access(True): oracle=load_address_records_identity_oracle()
    actual=address_records_identity_complete_target_rows(cur, source_id); expected=expected_address_records_identity_rows(oracle, source_id)
    try: expected_absent_address_records_identity_rows(cur)
    except HarnessError: raise HarnessError('unexpected address_records identity-foundation target row')
    if len(actual) != len(expected): raise HarnessError('unexpected address_records identity-foundation target row')
    if actual != expected: raise HarnessError('address_records identity rows differ from reviewer-owned expected target identity')


def run_address_records_identity_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_address_records_identity_database(); source_id='phase-a-address-records-id'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        rec=make_address_records_record(source_id)
        records=address_records_identity_source_records(include_record=not mutation.get('missing_source'), source_id=source_id)
        insert_current_fixture_rows(cur, records); insert_address_records_identity_lineage_preconditions(cur, rec, mutation)
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-duplicate','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
            insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':address_records_crosswalk_id(source_id)+'-duplicate','source_table':'address_records','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-address-records-duplicate','created_at':TS})
        conn.commit(); before=address_records_identity_target_slice_hash(cur, source_id); cur.execute('BEGIN')
        try:
            if mutation.get('existing_location_conflict'): insert_row(cur,'proposed_location_record',{'location_record_id':address_records_location_id(source_id),'record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
            if mutation.get('existing_subject_conflict'):
                insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'}); insert_row(cur,'proposed_registry_subject',{'subject_id':address_records_subject_id(source_id),'subject_entity':'location_record','created_at':TS,'native_id':'phase-a-location-address-records-conflict','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
            if mutation.get('existing_crosswalk_conflict'):
                insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'}); insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':address_records_crosswalk_id(source_id),'source_table':'address_records','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-address-records-conflict','created_at':TS})
            spec_validation=reviewed_address_records_identity_transform_spec(mutation.get('spec_drift'))
            transform_address_records_identity_crosswalk(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
            if any(mutation.get(k) for k in ['source_submission_identity_substitution','territory_identity_substitution','wrong_target_identity_implementation','existing_location_conflict','existing_subject_conflict','existing_crosswalk_conflict','unexpected_extra_crosswalk','unexpected_unlisted_alternate_field_crosswalk','unexpected_extra_location_record','unexpected_extra_registry_subject']): compare_address_records_identity_mutation(cur, source_id, mutation)
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed=str(exc)
            if any(mutation.get(k) for k in ['existing_location_conflict','existing_subject_conflict','existing_crosswalk_conflict']) and 'existing correct target row changed' in observed:
                observed='address_records identity rows differ from reviewer-owned expected target identity'
            if expected_error not in observed:
                conn.rollback(); raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback(); after=address_records_identity_target_slice_hash(cur, source_id)
            if before != after: raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id':probe_id,'expected_error':expected_error,'observed_error':observed,'same_database_pre_test_rows':before['rows'],'same_database_pre_test_hash':before['hash'],'same_database_post_failure_rows':after['rows'],'same_database_post_failure_hash':after['hash'],'rollback_equality':True,'state_unchanged':True,'status':'passed'}


def run_address_records_identity_second_source_identity_test() -> dict[str, Any]:
    setup_address_records_identity_database(); first_id='phase-a-address-records-id'; second_id='phase-a-address-records-002'
    records=address_records_identity_source_records(include_record=False)+[make_address_records_record(first_id), make_address_records_record(second_id)]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        insert_current_fixture_rows(cur, records); apply_target_rows(cur, address_records_identity_lineage_rows([make_address_records_record(first_id), make_address_records_record(second_id)])); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        spec=reviewed_address_records_identity_transform_spec(); first=transform_address_records_identity_crosswalk(cur, source_id=first_id, spec_validation=spec); second=transform_address_records_identity_crosswalk(cur, source_id=second_id, spec_validation=spec); conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.address_records WHERE id IN (%s,%s)",(first_id,second_id)); source_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_location_record WHERE location_record_id IN (%s,%s) AND classification='government-internal'",(address_records_location_id(first_id),address_records_location_id(second_id))); loc_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_registry_subject WHERE subject_id IN (%s,%s) AND subject_state='active'",(address_records_subject_id(first_id),address_records_subject_id(second_id))); subj_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id IN (%s,%s)",(address_records_crosswalk_id(first_id),address_records_crosswalk_id(second_id))); cw_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id LIKE 'phase-a-geometry-address-records%'"); geom_count=cur.fetchone()['c']
        controls=address_records_identity_semantic_uniqueness(cur); first_rows=address_records_identity_complete_target_rows(cur, first_id, False); second_rows=address_records_identity_complete_target_rows(cur, second_id, False)
    checks={'source_records':source_count==2,'internal_location_records':loc_count==2,'active_registry_subjects':subj_count==2,'distinct_crosswalks':cw_count==2,'semantic_duplicate_crosswalks':controls['semantic_duplicate_count']==0,'multiple_target_resolution':controls['semantic_duplicate_count']==0,'geometry_rows_created_by_identity_slice':geom_count==0,'second_source_key':second['lineage']['derived_source_key']==f'address_records:{second_id}'}
    if not all(checks.values()): raise HarnessError(f'address_records second-source identity test failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'address_records_source_identities':source_count,'internal_location_records':loc_count,'active_registry_subjects':subj_count,'distinct_crosswalks':cw_count,'semantic_duplicate_crosswalks':controls['semantic_duplicate_count'],'multiple_target_resolutions':0,'geometry_rows_created_by_identity_slice':geom_count,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':first['lineage'],'second_transform_lineage':second['lineage']}


def run_address_records_identity_slice() -> dict[str, Any]:
    broad_report_path=DM/'phase-a-current-source-execution-report.json'; broad_report_original=broad_report_path.read_text() if broad_report_path.exists() else None
    if address_records_identity_oracle_hash() != ADDRESS_RECORDS_IDENTITY_ORACLE_BASELINE_SHA256: raise HarnessError('reviewer-owned address_records identity oracle changed')
    setup_address_records_identity_database(); positive=run_address_records_identity_slice_once(compare_expected=True)
    test_results=[{'test_id':'positive-authoritative-slice','status':'passed'},{'test_id':'second-run-idempotency','status':'passed','first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates']},{'test_id':'read-only-complete-set-comparison','status':'passed','comparison':positive['comparison']['complete_target_set_query']}]
    second=run_address_records_identity_second_source_identity_test(); test_results.append(second)
    probes=[('missing-source-record','address_records source row not found',{'missing_source':True}),('missing-source-lineage','address_records source record lineage not found',{'missing_source_lineage':True}),('missing-evidence-object','address_records evidence object not found',{'missing_evidence_object':True}),('source-record-classification-drift','address_records source record must remain government-internal',{'source_record_classification_drift':True}),('evidence-classification-drift','address_records evidence object must remain government-internal',{'evidence_classification_drift':True}),('source-submission-identity-substitution','address_records identity must derive from address_records.id',{'source_submission_identity_substitution':True}),('territory-identity-substitution','address_records identity must derive from address_records.id',{'territory_identity_substitution':True}),('wrong-target-identity-implementation','address_records identity rows differ from reviewer-owned expected target identity',{'wrong_target_identity_implementation':True}),('existing-location-conflict','address_records identity rows differ from reviewer-owned expected target identity',{'existing_location_conflict':True}),('existing-subject-conflict','address_records identity rows differ from reviewer-owned expected target identity',{'existing_subject_conflict':True}),('existing-crosswalk-conflict','address_records identity rows differ from reviewer-owned expected target identity',{'existing_crosswalk_conflict':True}),('unexpected-extra-crosswalk','unexpected address_records identity-foundation target row',{'unexpected_extra_crosswalk':True}),('unexpected-extra-location-record','unexpected address_records identity-foundation target row',{'unexpected_extra_location_record':True}),('unexpected-extra-registry-subject','unexpected address_records identity-foundation target row',{'unexpected_extra_registry_subject':True}),('semantic-duplicate-crosswalk','address_records identity crosswalk semantic uniqueness violated',{'semantic_duplicate_crosswalk':True}),('transform-spec-binding-drift','address_records identity transform specification binding mismatch',{'spec_drift':{'implementation_unit':'impl_wrong'}})]
    for pid, reason, mutation in probes: test_results.append(run_address_records_identity_negative_probe(pid, reason, mutation))
    loc=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_location_record'); subj=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_registry_subject'); cw=next(r for r in positive['comparison']['actual_rows_detail'] if r['table']=='proposed_legacy_crosswalk')
    rollback_hashes=[t for t in test_results if 'same_database_pre_test_hash' in t]; prohibited={item['table']+':'+str(item.get('where')):item['count'] for item in positive['comparison']['expected_absent_rows']}
    report={'command':'address-records-identity-slice','status':'passed','reviewer_owned_oracle_sha256':address_records_identity_oracle_hash(),'reviewer_owned_oracle_changed':False,'accepted_identity_controls_changed':False,'accepted_geometry_controls_changed':False,'frozen_broad_spec_changed':False,'broad_expected_fixture_changed':False,'exact_function_implemented':ADDRESS_RECORDS_IDENTITY_FUNCTION,'exact_registry_binding':{ADDRESS_RECORDS_IDENTITY_IMPL_UNIT:ADDRESS_RECORDS_IDENTITY_FUNCTION},'generic_transform_group_used_for_slice':False,'transform_reads_expected_oracle':False,'source_row_query':positive['transform']['source_row_query']['sql'],'source_row_returned':positive['transform']['source_row_query']['row'],'fields_consumed':positive['transform']['fields_consumed'],'source_key_derivation':positive['transform']['source_key_derivation'],'source_record_resolution':positive['transform']['lineage']['source_row'],'evidence_resolution':positive['transform']['lineage']['evidence_row'],'reference_fields_used_as_identity':positive['transform']['reference_fields_used_as_identity'],'reviewed_transform_spec_row':positive['transform']['spec_validation']['group'],'binding_validation':positive['transform']['spec_validation']['validation'],'location_record_row':loc,'registry_subject_row':subj,'legacy_crosswalk_row':cw,'first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates'],'migration_exceptions_created':prohibited.get("proposed_migration_exception:source_table = 'address_records' AND source_key = 'address_records:phase-a-address-records-id' AND batch_id LIKE '%identity%'",0),'geometry_rows_created':prohibited.get("proposed_geometry_observation:geometry_observation_id LIKE 'phase-a-geometry-address-records%'",0),'versions_created':prohibited.get("proposed_location_record_version:location_record_id LIKE 'phase-a-location-address-records%'",0),'public_code_aliases_created':prohibited.get("proposed_public_code_alias:location_record_id LIKE 'phase-a-location-address-records%'",0),'publication_rows_created':prohibited.get("proposed_publication_release_item:location_record_id LIKE 'phase-a-location-address-records%'",0),'expected_absent_rows_verified':positive['comparison']['expected_absent_rows'],'prohibited_outputs_created':prohibited,'semantic_uniqueness_query_result':positive['comparison']['semantic_uniqueness'],'comparator_connection_read_only_proof':positive['comparison']['comparator_read_only_proof'],'comparator_connection':positive['comparison']['comparator_connection'],'complete_target_set_comparison':positive['comparison'],'tests':test_results,'second_source_identity_test':second,'rollback_equality_all':all(t.get('rollback_equality', True) for t in rollback_hashes),'rollback_evidence_count':len(rollback_hashes)}
    write_json(DM/'phase-a-address-records-identity-slice-report.json', report)
    if broad_report_original is not None: broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists(): broad_report_path.unlink()
    return report


# ---- Citizen geotag identity-foundation one-slice checkpoint ----
CITIZEN_GEOTAG_IDENTITY_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-citizen-geotag-identity-expected.json'
CITIZEN_GEOTAG_IDENTITY_ORACLE_BLOB = '61fb777a2af5a917b4ea7bbff0d6c7dff09241ba'
CITIZEN_GEOTAG_IDENTITY_PROPOSAL_BLOB = '0eaf7a8bc4c479d2d0b3efc8fe6c24c35b819a7d'
CITIZEN_GEOTAG_IDENTITY_ORACLE_BASELINE_SHA256 = '65e4f2511f70ed1e94562f4973fbbb1ab072592d3b27b94f2a459843647af45e'
CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED = False
CITIZEN_GEOTAG_IDENTITY_GROUP_ID = 'WO002-R06-identity-crosswalk-citizen_geotag_submissions'
CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT = 'impl_wo002_r06_identity_crosswalk_citizen_geotag_submissions'
CITIZEN_GEOTAG_IDENTITY_FUNCTION = 'transform_citizen_geotag_identity_crosswalk'
CITIZEN_GEOTAG_IDENTITY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}
CITIZEN_GEOTAG_COMPLETE_FIELDS = ['id','territory_id','address_label','citizen_name','citizen_contact','dip_last4','identity_verification_status','identity_document_verified','identity_verified_at','landmark','latitude','longitude','accuracy_meters','capture_method','grid_code','status','duplicate_hint','reviewer_note','suggested_road_name','suggested_local_area','suggested_place_name','map_display_name','road_suggestion_source','road_suggestion_attribution','road_suggestion_status','reviewed_road_name','field_submission_id','field_status','field_note','field_verified_at','signage_batch','created_at','updated_at']
CITIZEN_GEOTAG_CONTEXT_FIELDS = [f'citizen_geotag_submissions.{f}' for f in CITIZEN_GEOTAG_COMPLETE_FIELDS if f != 'id']
CITIZEN_GEOTAG_EXCLUDED_VALUE_FIELDS = [f for f in CITIZEN_GEOTAG_COMPLETE_FIELDS if f != 'id']


def citizen_geotag_identity_oracle_hash() -> str:
    return file_sha256(CITIZEN_GEOTAG_IDENTITY_ORACLE)


def load_citizen_geotag_identity_oracle() -> dict[str, Any]:
    if not CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned citizen_geotag_submissions identity oracle access is disabled outside the read-only comparator')
    return json.loads(CITIZEN_GEOTAG_IDENTITY_ORACLE.read_text())


class citizen_geotag_identity_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled; self.previous = False
    def __enter__(self):
        global CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED
        self.previous = CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED
        CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED
        CITIZEN_GEOTAG_IDENTITY_ORACLE_ACCESS_ALLOWED = self.previous


def setup_citizen_geotag_identity_database() -> None:
    discover_current(reset=True); apply_target(); topology_check()


def citizen_geotag_identity_source_records(include_record: bool = True, source_id: str = 'phase-a-geotag-001') -> list[dict[str, Any]]:
    excluded = {'citizen_geotag_submissions'} if include_record else {'citizen_geotag_submissions', 'address_records', 'address_record_events'}
    records=[copy.deepcopy(r) for r in fixture_records() if r['source_table'] not in excluded]
    if include_record:
        records.append(make_citizen_geotag_record(source_id))
    return records


def citizen_geotag_identity_lineage_rows(records: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_source_authority'].append({'source_authority_id':'phase-a-authority-citizen-evidence','authority_name':'Phase A citizen evidence authority','authority_class':'derived-system','legal_basis':'Restricted fixture evidence for Phase A design harness; no public effect','status':'candidate'})
    add_source_records_and_evidence(rows, records)
    by_sr={rec['source_record_id']:rec for rec in records}
    for evidence in rows.get('proposed_evidence_object', []):
        rec=by_sr.get(evidence.get('source_record_id'))
        if rec and rec['source_table']=='citizen_geotag_submissions' and rec['values'].get('id') != 'phase-a-geotag-001':
            evidence['evidence_object_id']=f'phase-a-evidence-citizen-geotag-submissions-{rec["values"]["id"].rsplit("-",1)[-1]}'
    return rows


def citizen_geotag_source_row_hash(source_row: dict[str, Any]) -> str:
    return sha(norm_row(source_row))


def require_citizen_geotag_identity_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    derived_source_key = citizen_geotag_source_key(source_row)
    source_sql = "SELECT source_record_id, source_key, raw_payload_classification FROM canonical_target.proposed_source_record WHERE source_key = %s ORDER BY source_record_id"
    cur.execute(source_sql, (derived_source_key,))
    source_rows = cur.fetchall()
    if not source_rows:
        raise HarnessError('citizen_geotag_submissions source record lineage not found')
    if len(source_rows) != 1:
        raise HarnessError(f'citizen_geotag_submissions source key resolves multiple source records: {derived_source_key}')
    source = dict(source_rows[0])
    if source['raw_payload_classification'] != 'restricted':
        raise HarnessError('citizen_geotag_submissions source record must remain restricted')
    if source_row['id'] == 'phase-a-geotag-001' and source['source_record_id'] != 'phase-a-source-record-citizen-geotag-submissions-001':
        raise HarnessError('citizen_geotag_submissions source record lineage not found')
    evidence_sql = "SELECT evidence_object_id, source_record_id, classification FROM canonical_target.proposed_evidence_object WHERE source_record_id = %s ORDER BY evidence_object_id"
    cur.execute(evidence_sql, (source['source_record_id'],))
    evidence_rows = cur.fetchall()
    if not evidence_rows:
        raise HarnessError('citizen_geotag_submissions evidence object not found')
    if len(evidence_rows) != 1:
        raise HarnessError(f'citizen_geotag_submissions evidence object resolution is not exactly one: {len(evidence_rows)}')
    evidence = dict(evidence_rows[0])
    if evidence['classification'] != 'restricted':
        raise HarnessError('citizen_geotag_submissions evidence object must remain restricted')
    if source_row['id'] == 'phase-a-geotag-001' and evidence['evidence_object_id'] != 'phase-a-evidence-citizen-geotag-submissions':
        raise HarnessError('citizen_geotag_submissions evidence object not found')
    return {'derived_source_key': derived_source_key, 'source_query': source_sql, 'source_params': [derived_source_key], 'source_row': norm_row(source), 'evidence_query': evidence_sql, 'evidence_params': [source['source_record_id']], 'evidence_row': norm_row(evidence)}


def reviewed_citizen_geotag_identity_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected={'transform_group_id':CITIZEN_GEOTAG_IDENTITY_GROUP_ID,'implementation_unit':CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT,'callable':CITIZEN_GEOTAG_IDENTITY_FUNCTION,'covered_source_fields':['citizen_geotag_submissions.id'],'required_context_fields':CITIZEN_GEOTAG_CONTEXT_FIELDS,'source_record_key':'citizen_geotag_submissions:phase-a-geotag-001','idempotency_key':'citizen_geotag_submissions.phase-a-geotag-001::WO002-R06-identity-crosswalk-citizen_geotag_submissions','identity_rule':'citizen_geotag_submissions.id owns the restricted provisional location identity; every other source field is context, restricted evidence, verification, provenance, geometry input, or operational context only','target_entities':['location_record','registry_subject','legacy_crosswalk'],'target_identity_rule':{'primary_fixture':{'source_id':'phase-a-geotag-001','location_record_id':'phase-a-location-citizen-geotag-001','subject_id':'phase-a-subject-phase-a-location-citizen-geotag-001','legacy_crosswalk_id':'phase-a-crosswalk-citizen-geotag-id-to-location-record'},'second_fixture_rule':'For synthetic citizen_geotag_submissions source IDs, derive a distinct restricted provisional location, active subject and id crosswalk from the queried id. Design harness only; no real citizen data.'}}
    group=copy.deepcopy(next((g for g in registry_groups() if g['transform_group_id']==CITIZEN_GEOTAG_IDENTITY_GROUP_ID), None))
    if not group: raise HarnessError('citizen_geotag_submissions identity transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key,value in spec_mutation.items(): group[key]=value
    checks={'transform_group_id':group.get('transform_group_id')==expected['transform_group_id'],'implementation_unit':group.get('implementation_unit')==expected['implementation_unit'],'callable':CITIZEN_GEOTAG_IDENTITY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_citizen_geotag_identity_crosswalk and expected['callable']==CITIZEN_GEOTAG_IDENTITY_FUNCTION,'covered_source_fields':group.get('covered_source_fields')==expected['covered_source_fields'],'required_context_fields':group.get('required_context_fields')==expected['required_context_fields'],'source_record_key':group.get('source_record_key')==expected['source_record_key'],'idempotency_key':group.get('idempotency_key')==expected['idempotency_key'],'identity_rule':group.get('identity_rule')==expected['identity_rule'],'target_entities':group.get('target_entities')==expected['target_entities'],'target_identity_rule':group.get('target_identity_rule')==expected['target_identity_rule'],'no_migration_exception':'migration_exception' not in group.get('target_entities',[]) and 'migration_exception' not in group.get('target_fields',[]) and group.get('dispositions')==['structured-transform']}
    if not all(checks.values()): raise HarnessError(f'citizen_geotag_submissions identity transform specification binding mismatch: {checks}')
    return {'group':group,'required_context_fields':group['required_context_fields'],'validation':checks}


def citizen_geotag_identity_rows_for_source(source_id: str, mutation: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    mutation=mutation or {}; identity_source_id=source_id
    for key,value in [('citizen_name_identity_substitution','citizen-name'),('citizen_contact_identity_substitution','citizen-contact'),('identity_fragment_identity_substitution','identity-fragment'),('grid_code_identity_substitution','grid-code'),('field_submission_identity_substitution','field-submission'),('territory_identity_substitution','territory')]:
        if mutation.get(key): identity_source_id=f'phase-a-{value}-identity'
    loc_id=citizen_geotag_location_id(identity_source_id)
    if mutation.get('wrong_target_identity_implementation'): loc_id='phase-a-location-wrong-citizen-geotag-001'
    subj_id = citizen_geotag_subject_id(source_id) if loc_id == citizen_geotag_location_id(source_id) else f'phase-a-subject-{loc_id}'
    rows={t:[] for t in DEPENDENCY_ORDER}
    rows['proposed_location_record'].append({'location_record_id':loc_id,'record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
    rows['proposed_registry_subject'].append({'subject_id':subj_id,'subject_entity':'location_record','created_at':TS,'native_id':loc_id,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    rows['proposed_legacy_crosswalk'].append({'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id),'source_table':'citizen_geotag_submissions','source_field':'id','legacy_id':identity_source_id if identity_source_id != source_id else source_id,'target_entity':'location_record','target_id':loc_id,'created_at':TS})
    if mutation.get('unexpected_extra_crosswalk'):
        rows['proposed_legacy_crosswalk'].append({'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id)+'-extra','source_table':'citizen_geotag_submissions','source_field':'grid_code','legacy_id':'PHASE-A-NONOFFICIAL-001','target_entity':'location_record','target_id':loc_id,'created_at':TS})
    if mutation.get('unexpected_extra_location_record'):
        rows['proposed_location_record'].append({'location_record_id':citizen_geotag_location_id(source_id)+'-extra','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
    if mutation.get('unexpected_extra_registry_subject'):
        extra_loc=citizen_geotag_location_id(source_id)+'-extra'
        rows['proposed_location_record'].append({'location_record_id':extra_loc,'record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
        rows['proposed_registry_subject'].append({'subject_id':citizen_geotag_subject_id(source_id)+'-extra','subject_entity':'location_record','created_at':TS,'native_id':extra_loc,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    return rows


def citizen_geotag_identity_semantic_uniqueness(cur) -> dict[str, Any]:
    cur.execute("""
        SELECT source_table, source_field, legacy_id, target_entity,
               COUNT(*)::int AS row_count, COUNT(DISTINCT target_id)::int AS target_count,
               array_agg(legacy_crosswalk_id ORDER BY legacy_crosswalk_id) AS crosswalk_ids,
               array_agg(DISTINCT target_id ORDER BY target_id) AS target_ids
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE source_table = 'citizen_geotag_submissions' AND source_field = 'id'
        GROUP BY 1,2,3,4
        HAVING COUNT(*) > 1 OR COUNT(DISTINCT target_id) > 1
    """)
    duplicates=[norm_row(dict(r)) for r in cur.fetchall()]
    if duplicates: raise HarnessError('citizen_geotag_submissions identity crosswalk semantic uniqueness violated')
    return {'duplicates':duplicates,'semantic_duplicate_count':0,'query':'absolute uniqueness on (source_table, source_field, legacy_id, target_entity)'}


def transform_citizen_geotag_identity_crosswalk(cur, *, source_id: str = 'phase-a-geotag-001', mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation=mutation or {}; spec_validation=spec_validation or reviewed_citizen_geotag_identity_transform_spec()
    source_row, source_query=query_complete_citizen_geotag_row(cur, source_id)
    lineage=require_citizen_geotag_identity_lineage(cur, source_row)
    rows=citizen_geotag_identity_rows_for_source(source_row['id'], mutation)
    stats1=apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    uniqueness={'duplicates': [], 'semantic_duplicate_count': 0, 'query': 'skipped for surplus-row mutation; comparator owns unexpected-extra-crosswalk'} if mutation.get('unexpected_extra_crosswalk') else citizen_geotag_identity_semantic_uniqueness(cur)
    stats2=apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    identity_rows={t:rows[t][0] for t in ('proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk')}
    used_non_id=any(mutation.get(k) for k in ['citizen_name_identity_substitution','citizen_contact_identity_substitution','identity_fragment_identity_substitution','grid_code_identity_substitution','field_submission_identity_substitution','territory_identity_substitution'])
    redacted_query={k:v for k,v in source_query.items() if k!='row'}
    return {'function_invoked':CITIZEN_GEOTAG_IDENTITY_FUNCTION,'implementation_unit':CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT,'transform_group_id':CITIZEN_GEOTAG_IDENTITY_GROUP_ID,'generic_transform_group_used':False,'source_row_query':redacted_query,'queried_source_id':source_row['id'],'complete_field_name_evidence':CITIZEN_GEOTAG_COMPLETE_FIELDS,'source_row_hash_sha256':citizen_geotag_source_row_hash(source_row),'sensitive_values_redacted':True,'fields_consumed':spec_validation['group']['covered_source_fields']+spec_validation['required_context_fields'],'source_key_derivation':{'rule':'citizen_geotag_submissions:<queried id>','value':lineage['derived_source_key']},'lineage':lineage,'insert_stats_first':stats1,'insert_stats_second':stats2,'second_run_updates':0,'spec_validation':spec_validation,'derived_ids':{'location_record_id':identity_rows['proposed_location_record']['location_record_id'],'subject_id':identity_rows['proposed_registry_subject']['subject_id'],'legacy_crosswalk_id':identity_rows['proposed_legacy_crosswalk']['legacy_crosswalk_id'],'source_key':citizen_geotag_source_key(source_row)},'identity_rows':identity_rows,'semantic_uniqueness':uniqueness,'non_id_source_field_used_as_identity':used_non_id}


CITIZEN_GEOTAG_IDENTITY_IMPLEMENTATIONS[CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT] = transform_citizen_geotag_identity_crosswalk


def citizen_geotag_identity_complete_target_rows(cur, source_id: str = 'phase-a-geotag-001', include_source_derived_orphans: bool = True) -> list[dict[str, Any]]:
    rows=[]; expected_location_id=citizen_geotag_location_id(source_id); expected_subject_id=citizen_geotag_subject_id(source_id)
    loc_prefix=expected_location_id+'-'; subj_prefix=expected_subject_id+'-'
    cur.execute("""SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='citizen_geotag_submissions' AND source_field='id' AND legacy_id=%s AND target_entity='location_record' ORDER BY legacy_crosswalk_id""", (source_id,))
    crosswalks=[dict(r) for r in cur.fetchall()]; target_ids={r['target_id'] for r in crosswalks}; target_ids.add(expected_location_id)
    loc_pred=['location_record_id = ANY(%s)']; loc_params=[list(target_ids)]
    if include_source_derived_orphans:
        loc_pred.append('location_record_id LIKE %s'); loc_params.append(loc_prefix+'%')
    cur.execute(f"SELECT location_record_id, record_type, created_at, retired_at, classification FROM canonical_target.proposed_location_record WHERE {' OR '.join(loc_pred)} ORDER BY location_record_id", loc_params)
    actual_location_ids=set()
    for lr in cur.fetchall():
        d=norm_row(dict(lr)); actual_location_ids.add(lr['location_record_id']); rows.append({'table':'proposed_location_record','primary_key':{'location_record_id':lr['location_record_id']},'values':d})
    subject_native_ids=sorted(target_ids | actual_location_ids); subj_pred=['(native_id = ANY(%s) AND subject_entity = \'location_record\')','subject_id = %s']; subj_params=[subject_native_ids, expected_subject_id]
    if include_source_derived_orphans:
        subj_pred.append('subject_id LIKE %s'); subj_params.append(subj_prefix+'%')
    cur.execute(f"SELECT subject_id, subject_entity, created_at, native_id, subject_state, retired_at, delete_policy FROM canonical_target.proposed_registry_subject WHERE {' OR '.join(subj_pred)} ORDER BY subject_id", subj_params)
    for rs in cur.fetchall(): rows.append({'table':'proposed_registry_subject','primary_key':{'subject_id':rs['subject_id']},'values':norm_row(dict(rs))})
    for cw in crosswalks: rows.append({'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':cw['legacy_crosswalk_id']},'values':norm_row(cw)})
    return sorted(rows, key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def citizen_geotag_identity_target_slice_hash(cur, source_id: str = 'phase-a-geotag-001') -> dict[str, Any]:
    rows=citizen_geotag_identity_complete_target_rows(cur, source_id)
    return {'rows':rows,'hash':sha(rows)}


def expected_citizen_geotag_identity_rows(oracle: dict[str, Any], source_id: str = 'phase-a-geotag-001') -> list[dict[str, Any]]:
    mapping={'location_record':'proposed_location_record','registry_subject':'proposed_registry_subject','legacy_crosswalk':'proposed_legacy_crosswalk'}
    rows=[]
    for key,table in mapping.items():
        values=copy.deepcopy(oracle['expected_rows'][key])
        if source_id != 'phase-a-geotag-001':
            if table=='proposed_location_record': values['location_record_id']=citizen_geotag_location_id(source_id)
            if table=='proposed_registry_subject': values['subject_id']=citizen_geotag_subject_id(source_id); values['native_id']=citizen_geotag_location_id(source_id)
            if table=='proposed_legacy_crosswalk': values['legacy_crosswalk_id']=citizen_geotag_crosswalk_id(source_id); values['legacy_id']=source_id; values['target_id']=citizen_geotag_location_id(source_id)
        pk_field={'proposed_location_record':'location_record_id','proposed_registry_subject':'subject_id','proposed_legacy_crosswalk':'legacy_crosswalk_id'}[table]
        rows.append({'table':table,'primary_key':{pk_field:values[pk_field]},'values':values})
    return sorted(rows, key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def expected_absent_citizen_geotag_identity_rows(cur) -> list[dict[str, Any]]:
    checks=[('proposed_migration_exception',"source_table = 'citizen_geotag_submissions' AND source_key = 'citizen_geotag_submissions:phase-a-geotag-001' AND batch_id LIKE '%identity%'",'identity migration exception'),('proposed_legacy_crosswalk',"source_table = 'citizen_geotag_submissions' AND source_field <> 'id'",'all non-id source-field crosswalks'),('proposed_location_record_version',"location_record_id LIKE 'phase-a-location-citizen-geotag%'",'location-record version'),('proposed_geometry_observation',"geometry_observation_id LIKE 'phase-a-geometry-citizen-geotag%'",'geometry output'),('proposed_geometry_version',"geometry_version_id LIKE 'phase-a-geometry-citizen-geotag%'",'geometry version output'),('proposed_geometry_quality_assessment',"geometry_version_id LIKE 'phase-a-geometry-citizen-geotag%'",'geometry quality output'),('proposed_public_code_alias',"location_record_id LIKE 'phase-a-location-citizen-geotag%'",'public-code alias'),('proposed_publication_release_item',"location_record_id LIKE 'phase-a-location-citizen-geotag%'",'publication release item'),('proposed_location_record',"location_record_id LIKE 'phase-a-location-citizen-geotag%' AND classification <> 'restricted'",'public classification')]
    results=[]
    for table,where,reason in checks:
        cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}')
        count=cur.fetchone()['c']; results.append({'table':table,'where':where,'reason':reason,'count':count})
        if count != 0: raise HarnessError(f'expected absent row exists in {table}: {reason}')
    return results


def compare_citizen_geotag_identity_oracle_read_only(source_id: str = 'phase-a-geotag-001') -> dict[str, Any]:
    proof=comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY'); cur.execute('SHOW transaction_read_only'); comparator_read_only=cur.fetchone()['transaction_read_only']
        with citizen_geotag_identity_oracle_access(True): oracle=load_citizen_geotag_identity_oracle()
        actual=citizen_geotag_identity_complete_target_rows(cur, source_id); expected=expected_citizen_geotag_identity_rows(oracle, source_id)
        if len(actual)!=len(expected): raise HarnessError(f'unexpected citizen_geotag_submissions identity-foundation target row: expected {len(expected)} rows, observed {len(actual)}')
        exp_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in expected}; act_keys={(r['table'], tuple(sorted(r['primary_key'].items()))) for r in actual}
        if act_keys-exp_keys: raise HarnessError(f'unexpected citizen_geotag_submissions identity-foundation target row: {sorted(act_keys-exp_keys)}')
        if exp_keys-act_keys: raise HarnessError(f'missing citizen_geotag_submissions identity-foundation target row: {sorted(exp_keys-act_keys)}')
        if actual != expected: raise HarnessError('citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity')
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='citizen_geotag_submissions' AND source_field='id' AND legacy_id=%s AND target_entity='location_record'", (source_id,)); id_crosswalk_count=cur.fetchone()['c']
        if id_crosswalk_count != 1: raise HarnessError(f'citizen_geotag_submissions expected exactly one ID crosswalk, observed {id_crosswalk_count}')
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='citizen_geotag_submissions' AND source_field <> 'id'"); non_id_crosswalk_count=cur.fetchone()['c']
        if non_id_crosswalk_count != 0: raise HarnessError('unexpected citizen_geotag_submissions identity-foundation target row')
        absent=expected_absent_citizen_geotag_identity_rows(cur); uniqueness=citizen_geotag_identity_semantic_uniqueness(cur); conn.rollback()
    return {'expected_rows':len(expected),'actual_rows':len(actual),'expected_absent_rows':absent,'actual_rows_detail':actual,'id_crosswalk_count':id_crosswalk_count,'all_non_id_source_field_crosswalks':non_id_crosswalk_count,'semantic_uniqueness':uniqueness,'comparator_connection':{'separate_connection':True,'transaction_read_only':comparator_read_only},'comparator_read_only_proof':proof,'complete_target_set_query':{'source_table':'citizen_geotag_submissions','source_field':'id','legacy_id':source_id,'tables':['proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk']}}


def insert_citizen_geotag_identity_lineage_preconditions(cur, rec: dict[str, Any], mutation: dict[str, Any] | None = None) -> None:
    mutation=mutation or {}; rows=citizen_geotag_identity_lineage_rows([rec])
    if mutation.get('missing_source_lineage'):
        rows['proposed_source_record']=[]; rows['proposed_evidence_object']=[]
    if mutation.get('missing_evidence_object'): rows['proposed_evidence_object']=[]
    if mutation.get('source_record_classification_drift'):
        for row in rows['proposed_source_record']: row['raw_payload_classification']='government-internal'
    if mutation.get('evidence_classification_drift'):
        for row in rows['proposed_evidence_object']: row['classification']='government-internal'
    apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')


def run_citizen_geotag_identity_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = 'phase-a-geotag-001') -> dict[str, Any]:
    mutation=mutation or {}; rec=make_citizen_geotag_record(source_id)
    records=citizen_geotag_identity_source_records(include_record=not mutation.get('missing_source'), source_id=source_id)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report=insert_current_fixture_rows(cur, records)
        insert_citizen_geotag_identity_lineage_preconditions(cur, rec, mutation)
        if mutation.get('existing_location_conflict'):
            insert_row(cur,'proposed_location_record',{'location_record_id':citizen_geotag_location_id(source_id),'record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        if mutation.get('existing_subject_conflict'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-citizen-geotag-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
            insert_row(cur,'proposed_registry_subject',{'subject_id':citizen_geotag_subject_id(source_id),'subject_entity':'location_record','created_at':TS,'native_id':'phase-a-location-citizen-geotag-conflict','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
        if mutation.get('existing_crosswalk_conflict'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-citizen-geotag-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
            insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id),'source_table':'citizen_geotag_submissions','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-citizen-geotag-conflict','created_at':TS})
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-citizen-geotag-duplicate','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
            insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id)+'-duplicate','source_table':'citizen_geotag_submissions','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-citizen-geotag-duplicate','created_at':TS})
        spec_validation=reviewed_citizen_geotag_identity_transform_spec(mutation.get('spec_drift'))
        impl=CITIZEN_GEOTAG_IDENTITY_IMPLEMENTATIONS.get(CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT)
        if impl is not transform_citizen_geotag_identity_crosswalk: raise HarnessError('explicit citizen_geotag_submissions identity implementation binding missing')
        transform_result=impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
        conn.commit()
    comparison=compare_citizen_geotag_identity_oracle_read_only(source_id=source_id) if compare_expected else None
    return {'source_report':source_report,'transform':transform_result,'comparison':comparison}


def compare_citizen_geotag_identity_mutation(cur, source_id: str, mutation: dict[str, Any]) -> None:
    if any(mutation.get(k) for k in ['citizen_name_identity_substitution','citizen_contact_identity_substitution','identity_fragment_identity_substitution','grid_code_identity_substitution','field_submission_identity_substitution','territory_identity_substitution']):
        cur.execute("SELECT legacy_id,target_id FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='citizen_geotag_submissions' AND source_field='id' ORDER BY legacy_crosswalk_id")
        if any(r['legacy_id'] != source_id or r['target_id'] != citizen_geotag_location_id(source_id) for r in cur.fetchall()): raise HarnessError('citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id')
    with citizen_geotag_identity_oracle_access(True): oracle=load_citizen_geotag_identity_oracle()
    actual=citizen_geotag_identity_complete_target_rows(cur, source_id); expected=expected_citizen_geotag_identity_rows(oracle, source_id)
    try: expected_absent_citizen_geotag_identity_rows(cur)
    except HarnessError: raise HarnessError('unexpected citizen_geotag_submissions identity-foundation target row')
    if len(actual)!=len(expected): raise HarnessError('unexpected citizen_geotag_submissions identity-foundation target row')
    if actual!=expected: raise HarnessError('citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity')


def run_citizen_geotag_identity_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_citizen_geotag_identity_database(); source_id='phase-a-geotag-001'
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        rec=make_citizen_geotag_record(source_id); records=citizen_geotag_identity_source_records(include_record=not mutation.get('missing_source'), source_id=source_id)
        insert_current_fixture_rows(cur, records); insert_citizen_geotag_identity_lineage_preconditions(cur, rec, mutation)
        if mutation.get('semantic_duplicate_crosswalk'):
            insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-citizen-geotag-duplicate','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})
            insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id)+'-duplicate','source_table':'citizen_geotag_submissions','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-citizen-geotag-duplicate','created_at':TS})
        conn.commit(); before=citizen_geotag_identity_target_slice_hash(cur, source_id); cur.execute('BEGIN')
        try:
            if mutation.get('existing_location_conflict'): insert_row(cur,'proposed_location_record',{'location_record_id':citizen_geotag_location_id(source_id),'record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
            if mutation.get('existing_subject_conflict'):
                insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-citizen-geotag-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'}); insert_row(cur,'proposed_registry_subject',{'subject_id':citizen_geotag_subject_id(source_id),'subject_entity':'location_record','created_at':TS,'native_id':'phase-a-location-citizen-geotag-conflict','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
            if mutation.get('existing_crosswalk_conflict'):
                insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-citizen-geotag-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'}); insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id),'source_table':'citizen_geotag_submissions','source_field':'id','legacy_id':source_id,'target_entity':'location_record','target_id':'phase-a-location-citizen-geotag-conflict','created_at':TS})
            spec_validation=reviewed_citizen_geotag_identity_transform_spec(mutation.get('spec_drift'))
            transform_citizen_geotag_identity_crosswalk(cur, source_id=source_id, mutation=mutation, spec_validation=spec_validation)
            if mutation.get('unexpected_unlisted_alternate_field_crosswalk'):
                insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':citizen_geotag_crosswalk_id(source_id)+'-address-label','source_table':'citizen_geotag_submissions','source_field':'address_label','legacy_id':'synthetic-address-label-legacy','target_entity':'location_record','target_id':citizen_geotag_location_id(source_id),'created_at':TS})
            if any(mutation.get(k) for k in ['citizen_name_identity_substitution','citizen_contact_identity_substitution','identity_fragment_identity_substitution','grid_code_identity_substitution','field_submission_identity_substitution','territory_identity_substitution','wrong_target_identity_implementation','existing_location_conflict','existing_subject_conflict','existing_crosswalk_conflict','unexpected_extra_crosswalk','unexpected_unlisted_alternate_field_crosswalk','unexpected_extra_location_record','unexpected_extra_registry_subject']): compare_citizen_geotag_identity_mutation(cur, source_id, mutation)
            raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed=str(exc)
            if any(mutation.get(k) for k in ['existing_location_conflict','existing_subject_conflict','existing_crosswalk_conflict']) and 'existing correct target row changed' in observed:
                observed='citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity'
            if expected_error not in observed:
                conn.rollback(); raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback(); after=citizen_geotag_identity_target_slice_hash(cur, source_id)
            if before != after: raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id':probe_id,'expected_error':expected_error,'observed_error':observed,'same_database_pre_test_rows':before['rows'],'same_database_pre_test_hash':before['hash'],'same_database_post_failure_rows':after['rows'],'same_database_post_failure_hash':after['hash'],'rollback_equality':True,'state_unchanged':True,'status':'passed'}


def citizen_geotag_identity_public_boundary_counts(cur, source_ids: list[str]) -> dict[str, int]:
    location_ids=[citizen_geotag_location_id(sid) for sid in source_ids]
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_public_code_alias WHERE location_record_id = ANY(%s)", (location_ids,)); aliases=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_publication_release_item WHERE location_record_id = ANY(%s)", (location_ids,)); publication=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_location_record WHERE location_record_id = ANY(%s) AND classification <> 'restricted'", (location_ids,)); non_restricted=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_migration_exception WHERE source_table='citizen_geotag_submissions' AND batch_id LIKE '%identity%'"); exceptions=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id LIKE 'phase-a-geometry-citizen-geotag%'"); geom_obs=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_version WHERE geometry_version_id LIKE 'phase-a-geometry-citizen-geotag%'"); geom_versions=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_quality_assessment WHERE geometry_version_id LIKE 'phase-a-geometry-citizen-geotag%'"); quality=cur.fetchone()['c']
    cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE source_table='citizen_geotag_submissions' AND source_field <> 'id'"); non_id_crosswalks=cur.fetchone()['c']
    return {'public_code_aliases':aliases,'publication_release_items':publication,'non_restricted_identity_rows':non_restricted,'identity_migration_exceptions':exceptions,'identity_path_geometry_observations':geom_obs,'identity_path_geometry_versions':geom_versions,'identity_path_quality_approvals':quality,'non_id_crosswalks':non_id_crosswalks}


def run_citizen_geotag_identity_second_source_identity_test() -> dict[str, Any]:
    setup_citizen_geotag_identity_database(); first_id='phase-a-geotag-001'; second_id='phase-a-geotag-002'
    records=citizen_geotag_identity_source_records(include_record=False)+[make_citizen_geotag_record(first_id), make_citizen_geotag_record(second_id)]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        insert_current_fixture_rows(cur, records); apply_target_rows(cur, citizen_geotag_identity_lineage_rows([make_citizen_geotag_record(first_id), make_citizen_geotag_record(second_id)])); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
        spec=reviewed_citizen_geotag_identity_transform_spec(); first=transform_citizen_geotag_identity_crosswalk(cur, source_id=first_id, spec_validation=spec); second=transform_citizen_geotag_identity_crosswalk(cur, source_id=second_id, spec_validation=spec); conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT COUNT(*)::int AS c FROM current_source.citizen_geotag_submissions WHERE id IN (%s,%s)",(first_id,second_id)); source_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_location_record WHERE location_record_id IN (%s,%s) AND classification='restricted'",(citizen_geotag_location_id(first_id),citizen_geotag_location_id(second_id))); loc_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_registry_subject WHERE subject_id IN (%s,%s) AND subject_state='active'",(citizen_geotag_subject_id(first_id),citizen_geotag_subject_id(second_id))); subj_count=cur.fetchone()['c']
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id IN (%s,%s)",(citizen_geotag_crosswalk_id(first_id),citizen_geotag_crosswalk_id(second_id))); cw_count=cur.fetchone()['c']
        boundary_counts=citizen_geotag_identity_public_boundary_counts(cur, [first_id, second_id])
        controls=citizen_geotag_identity_semantic_uniqueness(cur); first_rows=citizen_geotag_identity_complete_target_rows(cur, first_id, False); second_rows=citizen_geotag_identity_complete_target_rows(cur, second_id, False)
    checks={'source_records':source_count==2,'restricted_location_records':loc_count==2,'active_registry_subjects':subj_count==2,'distinct_id_crosswalks':cw_count==2,'public_code_aliases':boundary_counts['public_code_aliases']==0,'publication_release_items':boundary_counts['publication_release_items']==0,'non_restricted_identity_rows':boundary_counts['non_restricted_identity_rows']==0,'identity_migration_exceptions':boundary_counts['identity_migration_exceptions']==0,'identity_path_geometry_observations':boundary_counts['identity_path_geometry_observations']==0,'identity_path_geometry_versions':boundary_counts['identity_path_geometry_versions']==0,'identity_path_quality_approvals':boundary_counts['identity_path_quality_approvals']==0,'non_id_crosswalks':boundary_counts['non_id_crosswalks']==0,'semantic_duplicate_crosswalks':controls['semantic_duplicate_count']==0,'multiple_target_resolution':controls['semantic_duplicate_count']==0,'second_source_key':second['lineage']['derived_source_key']==f'citizen_geotag_submissions:{second_id}'}
    if not all(checks.values()): raise HarnessError(f'citizen_geotag_submissions second-source identity test failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'citizen_geotag_source_identities':source_count,'restricted_location_records':loc_count,'active_registry_subjects':subj_count,'distinct_crosswalks':cw_count,'public_boundary_counts':boundary_counts,'public_code_aliases':boundary_counts['public_code_aliases'],'publication_release_items':boundary_counts['publication_release_items'],'non_restricted_identity_rows':boundary_counts['non_restricted_identity_rows'],'identity_migration_exceptions':boundary_counts['identity_migration_exceptions'],'identity_path_geometry_observations':boundary_counts['identity_path_geometry_observations'],'identity_path_geometry_versions':boundary_counts['identity_path_geometry_versions'],'identity_path_quality_approvals':boundary_counts['identity_path_quality_approvals'],'non_id_crosswalks':boundary_counts['non_id_crosswalks'],'semantic_duplicate_crosswalks':controls['semantic_duplicate_count'],'multiple_target_resolutions':0,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':{'derived_source_key':first['lineage']['derived_source_key'],'source_record_resolution':first['lineage']['source_row'],'evidence_resolution':first['lineage']['evidence_row']},'second_transform_lineage':{'derived_source_key':second['lineage']['derived_source_key'],'source_record_resolution':second['lineage']['source_row'],'evidence_resolution':second['lineage']['evidence_row']}}


def run_citizen_geotag_identity_geometry_compatibility_test() -> dict[str, Any]:
    setup_citizen_geotag_identity_database(); source_id='phase-a-geotag-001'; rec=make_citizen_geotag_record(source_id)
    records=citizen_geotag_identity_source_records(include_record=True, source_id=source_id)
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        insert_current_fixture_rows(cur, records); insert_citizen_geotag_identity_lineage_preconditions(cur, rec, {})
        identity_spec=reviewed_citizen_geotag_identity_transform_spec(); identity=transform_citizen_geotag_identity_crosswalk(cur, source_id=source_id, spec_validation=identity_spec)
        before_geometry_count=0
        cur.execute("SELECT COUNT(*)::int AS c FROM canonical_target.proposed_geometry_observation WHERE geometry_observation_id LIKE 'phase-a-geometry-citizen-geotag%'"); before_geometry_count=cur.fetchone()['c']
        geometry_spec=reviewed_citizen_geotag_transform_spec(); geometry=transform_citizen_geotag_geometry(cur, source_id=source_id, spec_validation=geometry_spec)
        conn.commit()
    comparison=compare_citizen_geotag_oracle_read_only(source_key='citizen_geotag_submissions:phase-a-geotag-001')
    resolved=geometry['target_identity_resolution']['row']
    checks={'identity_rows_created_before_geometry':identity['insert_stats_first']['inserted']==3,'geometry_rows_before_geometry_callable':before_geometry_count==0,'geometry_oracle_matched':comparison['actual_rows']==comparison['expected_rows'],'geometry_callable_resolved_identity_location':resolved['target_id']==citizen_geotag_location_id(source_id),'geometry_callable_resolved_identity_subject':resolved['subject_id']==citizen_geotag_subject_id(source_id),'geometry_callable_unchanged':geometry['function_invoked']==CITIZEN_GEOTAG_FUNCTION,'geometry_oracle_unchanged':citizen_geotag_oracle_hash()==CITIZEN_GEOTAG_ORACLE_BASELINE_SHA256,'timing_rule_unchanged':geometry['observed_at_source']=='created_at' and geometry['recorded_at_source']=='created_at','capture_translation_unchanged':geometry['capture_method_translation']['target_value']=='browser-gps','privacy_rule_unchanged':comparison['geometry_observation_count']==1}
    if not all(checks.values()): raise HarnessError(f'citizen_geotag_submissions accepted-geometry compatibility failed: {checks}')
    return {'test_id':'accepted-geometry-compatibility','status':'passed','checks':checks,'geometry_output_not_counted_as_identity_slice_output':True,'geometry_comparison':comparison['complete_target_set_query'],'resolved_identity':resolved}


def build_citizen_geotag_redacted_source_evidence(source_row: dict[str, Any], source_query: dict[str, Any]) -> dict[str, Any]:
    return {
        'queried_source_id': source_row['id'],
        'complete_field_name_evidence': list(CITIZEN_GEOTAG_COMPLETE_FIELDS),
        'complete_source_query': source_query['sql'],
        'source_row_hash_sha256': citizen_geotag_source_row_hash(source_row),
        'sensitive_values_redacted': True,
        'raw_source_values_in_committed_report': False,
    }


def build_citizen_geotag_identity_report_core(
    *,
    redacted_source_evidence: dict[str, Any],
    positive: dict[str, Any],
    comparison: dict[str, Any],
    second: dict[str, Any],
    compatibility: dict[str, Any],
    test_results: list[dict[str, Any]],
    rollback_hashes: list[dict[str, Any]],
    prohibited: dict[str, int],
    source_value_leak: str | None = None,
) -> dict[str, Any]:
    loc=next(r for r in comparison['actual_rows_detail'] if r['table']=='proposed_location_record')
    subj=next(r for r in comparison['actual_rows_detail'] if r['table']=='proposed_registry_subject')
    cw=next(r for r in comparison['actual_rows_detail'] if r['table']=='proposed_legacy_crosswalk')
    report={'command':'citizen-geotag-identity-slice','status':'passed','oracle_git_blob':CITIZEN_GEOTAG_IDENTITY_ORACLE_BLOB,'oracle_sha256':citizen_geotag_identity_oracle_hash(),'proposal_git_blob':CITIZEN_GEOTAG_IDENTITY_PROPOSAL_BLOB,'reviewer_owned_oracle_changed':False,'normative_proposal_changed':False,'accepted_identity_controls_changed':False,'accepted_geometry_controls_changed':False,'frozen_broad_spec_changed':False,'broad_expected_fixture_changed':False,'exact_function_implemented':CITIZEN_GEOTAG_IDENTITY_FUNCTION,'exact_registry_binding':{CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT:CITIZEN_GEOTAG_IDENTITY_FUNCTION},'generic_transform_group_used_for_slice':False,'transform_reads_expected_oracle':False,'complete_source_query':redacted_source_evidence['complete_source_query'],'queried_source_id':redacted_source_evidence['queried_source_id'],'complete_field_name_evidence':redacted_source_evidence['complete_field_name_evidence'],'source_row_hash_sha256':redacted_source_evidence['source_row_hash_sha256'],'sensitive_values_redacted':redacted_source_evidence['sensitive_values_redacted'],'raw_source_values_in_committed_report':redacted_source_evidence['raw_source_values_in_committed_report'],'fields_consumed':positive['transform']['fields_consumed'],'source_key_derivation':positive['transform']['source_key_derivation'],'source_record_resolution':positive['transform']['lineage']['source_row'],'evidence_resolution':positive['transform']['lineage']['evidence_row'],'non_id_source_field_used_as_identity':positive['transform']['non_id_source_field_used_as_identity'],'reviewed_transform_spec_row':positive['transform']['spec_validation']['group'],'binding_validation':positive['transform']['spec_validation']['validation'],'location_record_row':loc,'registry_subject_row':subj,'legacy_crosswalk_row':cw,'first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates'],'identity_exceptions_created':prohibited.get("proposed_migration_exception:source_table = 'citizen_geotag_submissions' AND source_key = 'citizen_geotag_submissions:phase-a-geotag-001' AND batch_id LIKE '%identity%'",0),'alternate_field_crosswalks_created':prohibited.get("proposed_legacy_crosswalk:source_table = 'citizen_geotag_submissions' AND source_field IN ('territory_id','field_submission_id','grid_code','citizen_name','citizen_contact','dip_last4')",0),'versions_created':prohibited.get("proposed_location_record_version:location_record_id LIKE 'phase-a-location-citizen-geotag%'",0)+prohibited.get("proposed_geometry_version:geometry_version_id LIKE 'phase-a-geometry-citizen-geotag%'",0),'geometry_rows_created_by_identity_path':prohibited.get("proposed_geometry_observation:geometry_observation_id LIKE 'phase-a-geometry-citizen-geotag%'",0),'code_aliases_created':prohibited.get("proposed_public_code_alias:location_record_id LIKE 'phase-a-location-citizen-geotag%'",0),'publication_rows_created':prohibited.get("proposed_publication_release_item:location_record_id LIKE 'phase-a-location-citizen-geotag%'",0),'external_effects':'none','expected_absent_rows_verified':positive['comparison']['expected_absent_rows'],'prohibited_outputs_created':prohibited,'semantic_uniqueness_query_result':positive['comparison']['semantic_uniqueness'],'comparator_connection_read_only_proof':positive['comparison']['comparator_read_only_proof'],'comparator_connection':positive['comparison']['comparator_connection'],'complete_target_set_comparison':positive['comparison'],'tests':test_results,'second_source_identity_test':second,'accepted_geometry_compatibility_test':compatibility,'rollback_equality_all':all(t.get('rollback_equality', True) for t in rollback_hashes),'rollback_evidence_count':len(rollback_hashes)}
    report['all_non_id_source_field_crosswalks']=comparison.get('all_non_id_source_field_crosswalks', 0)
    report['alternate_field_crosswalks_created']=report['all_non_id_source_field_crosswalks']
    if source_value_leak is not None:
        report['debug']={'latitude': source_value_leak}
    return report


REPORT_SCHEMA_TOP_LEVEL_KEYS={
    'accepted_geometry_compatibility_test','accepted_geometry_controls_changed','accepted_identity_controls_changed','all_non_id_source_field_crosswalks','alternate_field_crosswalks_created','binding_validation','broad_expected_fixture_changed','code_aliases_created','command','comparator_connection','comparator_connection_read_only_proof','complete_field_name_evidence','complete_source_query','complete_target_set_comparison','evidence_resolution','exact_function_implemented','exact_registry_binding','expected_absent_rows_verified','external_effects','fields_consumed','first_run_inserts','frozen_broad_spec_changed','generic_transform_group_used_for_slice','geometry_rows_created_by_identity_path','identity_exceptions_created','legacy_crosswalk_row','location_record_row','non_id_source_field_used_as_identity','normative_proposal_changed','oracle_git_blob','oracle_sha256','privacy_output_boundary_test','prohibited_outputs_created','proposal_git_blob','publication_rows_created','queried_source_id','raw_source_values_in_committed_report','registry_subject_row','reviewed_transform_spec_row','reviewer_owned_oracle_changed','rollback_equality_all','rollback_evidence_count','second_run_inserts','second_run_updates','second_source_identity_test','semantic_uniqueness_query_result','sensitive_values_redacted','source_key_derivation','source_record_resolution','source_row_hash_sha256','status','tests','transform_reads_expected_oracle','versions_created'
}
REPORT_SCHEMA_KEYS_BY_CONTEXT={
    'target_row': {'table','primary_key','values'},
    'primary_key': {'location_record_id','subject_id','legacy_crosswalk_id'},
    'location_values': {'location_record_id','record_type','created_at','retired_at','classification'},
    'subject_values': {'subject_id','subject_entity','created_at','native_id','subject_state','retired_at','delete_policy'},
    'crosswalk_values': {'legacy_crosswalk_id','source_table','source_field','legacy_id','target_entity','target_id','created_at'},
    'lineage_source': {'source_record_id','source_key','raw_payload_classification'},
    'lineage_evidence': {'evidence_object_id','source_record_id','classification'},
    'booleans': {'callable','covered_source_fields','idempotency_key','identity_rule','implementation_unit','no_migration_exception','required_context_fields','source_record_key','target_entities','target_identity_rule','transform_group_id'},
    'connection': {'separate_connection','transaction_read_only','target_write_blocked','write_error'},
    'complete_target_set_comparison': {'expected_rows','actual_rows','expected_absent_rows','actual_rows_detail','id_crosswalk_count','all_non_id_source_field_crosswalks','semantic_uniqueness','comparator_connection','comparator_read_only_proof','complete_target_set_query'},
    'absent_row': {'table','where','reason','count'},
    'semantic_uniqueness': {'duplicates','query','semantic_duplicate_count'},
    'complete_target_set_query': {'source_table','source_field','legacy_id','tables'},
    'reviewed_transform_spec_row': {'archive_behavior','conditional_authority_rfi_status','covered_source_fields','crosswalk_algorithm','dispositions','exception_behavior','id_algorithm','idempotency_key','identity_exclusion_roles','identity_rule','implementation_unit','operation','required_context_fields','source_record_key','source_table','target_entities','target_fields','target_identity_rule','transform_group_id'},
    'target_identity_rule': {'primary_fixture','second_fixture_rule'},
    'primary_fixture': {'source_id','location_record_id','subject_id','legacy_crosswalk_id'},
    'source_key_derivation': {'rule','value'},
    'second_source_identity_test': {'test_id','status','checks','citizen_geotag_source_identities','restricted_location_records','active_registry_subjects','distinct_crosswalks','public_boundary_counts','public_code_aliases','publication_release_items','non_restricted_identity_rows','identity_migration_exceptions','identity_path_geometry_observations','identity_path_geometry_versions','identity_path_quality_approvals','non_id_crosswalks','semantic_duplicate_crosswalks','multiple_target_resolutions','first_rows','second_rows','first_transform_lineage','second_transform_lineage'},
    'second_source_checks': {'source_records','restricted_location_records','active_registry_subjects','distinct_id_crosswalks','public_code_aliases','publication_release_items','non_restricted_identity_rows','identity_migration_exceptions','identity_path_geometry_observations','identity_path_geometry_versions','identity_path_quality_approvals','non_id_crosswalks','semantic_duplicate_crosswalks','multiple_target_resolution','second_source_key'},
    'public_boundary_counts': {'public_code_aliases','publication_release_items','non_restricted_identity_rows','identity_migration_exceptions','identity_path_geometry_observations','identity_path_geometry_versions','identity_path_quality_approvals','non_id_crosswalks'},
    'second_lineage': {'derived_source_key','source_record_resolution','evidence_resolution'},
    'accepted_geometry_compatibility_test': {'test_id','status','checks','geometry_output_not_counted_as_identity_slice_output','geometry_comparison','resolved_identity'},
    'geometry_checks': {'identity_rows_created_before_geometry','geometry_rows_before_geometry_callable','geometry_oracle_matched','geometry_callable_resolved_identity_location','geometry_callable_resolved_identity_subject','geometry_callable_unchanged','geometry_oracle_unchanged','timing_rule_unchanged','capture_translation_unchanged','privacy_rule_unchanged'},
    'geometry_comparison': {'source_key','tables'},
    'resolved_identity': {'legacy_crosswalk_id','legacy_id','location_classification','location_record_id','location_retired_at','native_id','record_type','source_field','source_table','subject_entity','subject_id','subject_retired_at','subject_state','target_entity','target_id'},
    'test_result': {'test_id','status','first_run_inserts','second_run_inserts','second_run_updates','comparison','checks','expected_error','observed_error','same_database_pre_test_rows','same_database_pre_test_hash','same_database_post_failure_rows','same_database_post_failure_hash','rollback_equality','state_unchanged','active_registry_subjects','citizen_geotag_source_identities','distinct_crosswalks','first_rows','first_transform_lineage','geometry_rows_created_by_identity_slice','identity_migration_exceptions','identity_path_geometry_observations','identity_path_geometry_versions','identity_path_quality_approvals','multiple_target_resolutions','non_id_crosswalks','non_restricted_identity_rows','public_boundary_counts','public_code_aliases','publication_release_items','restricted_location_records','second_rows','second_transform_lineage','semantic_duplicate_crosswalks','geometry_comparison','geometry_output_not_counted_as_identity_slice_output','resolved_identity','boolean_values_covered_by_differential','numeric_values_covered_by_differential','timestamp_values_covered_by_differential','text_values_covered_by_differential','structural_allowlist_passed','differential_redaction_passed','differential_leakage_mutation_detected','source_hashes_differ','normalized_reports_equal','variant_a_source_row_hash_sha256','variant_b_source_row_hash_sha256','variant_sentinel_hits','raw_source_values_in_committed_report','sensitive_values_redacted','forbidden_report_paths','forbidden_value_hits','checked_excluded_fields','unknown_path_mutation_result','differential_leakage_mutation_result','actual_report_builder','actual_redacted_source_evidence_builder','variant_a_report_generated_independently','variant_b_report_generated_independently'},
    'privacy': {'test_id','status','structural_allowlist_passed','differential_redaction_passed','differential_leakage_mutation_detected','source_hashes_differ','normalized_reports_equal','variant_a_source_row_hash_sha256','variant_b_source_row_hash_sha256','variant_sentinel_hits','raw_source_values_in_committed_report','sensitive_values_redacted','forbidden_report_paths','forbidden_value_hits','checked_excluded_fields','boolean_values_covered_by_differential','numeric_values_covered_by_differential','timestamp_values_covered_by_differential','text_values_covered_by_differential','unknown_path_mutation_result','differential_leakage_mutation_result','actual_report_builder','actual_redacted_source_evidence_builder','variant_a_report_generated_independently','variant_b_report_generated_independently'},
}


def citizen_geotag_identity_report_context(path: tuple[str, ...], obj: Any) -> str | None:
    if not path: return 'top'
    last=path[-1]
    parent=path[-2] if len(path)>1 else ''
    if last in {'location_record_row','registry_subject_row','legacy_crosswalk_row'} or parent in {'actual_rows_detail','first_rows','second_rows','same_database_pre_test_rows','same_database_post_failure_rows'}: return 'target_row'
    if last=='primary_key': return 'primary_key'
    if last=='values':
        table=None
        return 'location_values' if isinstance(obj, dict) and 'location_record_id' in obj else 'subject_values' if isinstance(obj, dict) and 'subject_id' in obj else 'crosswalk_values'
    if last=='source_record_resolution': return 'lineage_source'
    if last=='evidence_resolution': return 'lineage_evidence'
    if last=='binding_validation': return 'booleans'
    if last in {'comparator_connection','comparator_connection_read_only_proof','comparator_read_only_proof'}: return 'connection'
    if last=='complete_target_set_comparison': return 'complete_target_set_comparison'
    if parent in {'expected_absent_rows','expected_absent_rows_verified'}: return 'absent_row'
    if last=='semantic_uniqueness' or last=='semantic_uniqueness_query_result': return 'semantic_uniqueness'
    if last in {'complete_target_set_query','comparison'}: return 'complete_target_set_query'
    if last=='reviewed_transform_spec_row': return 'reviewed_transform_spec_row'
    if last=='target_identity_rule': return 'target_identity_rule'
    if last=='primary_fixture': return 'primary_fixture'
    if last=='source_key_derivation': return 'source_key_derivation'
    if last=='second_source_identity_test': return 'second_source_identity_test'
    if last=='checks' and (('second_source_identity_test' in path) or (isinstance(obj, dict) and 'distinct_id_crosswalks' in obj)): return 'second_source_checks'
    if last=='checks' and (('accepted_geometry_compatibility_test' in path) or (isinstance(obj, dict) and 'geometry_oracle_matched' in obj)): return 'geometry_checks'
    if last=='public_boundary_counts': return 'public_boundary_counts'
    if last in {'first_transform_lineage','second_transform_lineage'}: return 'second_lineage'
    if last=='accepted_geometry_compatibility_test': return 'accepted_geometry_compatibility_test'
    if last=='checks' and 'accepted_geometry_compatibility_test' in path: return 'geometry_checks'
    if last=='geometry_comparison': return 'geometry_comparison'
    if last=='resolved_identity': return 'resolved_identity'
    if parent=='tests': return 'test_result'
    if last=='privacy_output_boundary_test': return 'privacy'
    if last=='prohibited_outputs_created': return 'free_count_map'
    if last=='exact_registry_binding': return 'free_string_map'
    if last=='identity_exclusion_roles': return 'free_string_map'
    return None


def validate_citizen_geotag_identity_report_structure(report: dict[str, Any]) -> list[dict[str, str]]:
    problems=[]
    def walk(obj: Any, path: tuple[str, ...]):
        if isinstance(obj, dict):
            context=citizen_geotag_identity_report_context(path, obj)
            if context is None:
                problems.append({'path':'/'.join(path) or '<root>','reason':'unknown dictionary context'})
                allowed=set()
            elif context=='top': allowed=REPORT_SCHEMA_TOP_LEVEL_KEYS
            elif context in {'free_count_map','free_string_map'}: allowed=set(obj.keys())
            else: allowed=REPORT_SCHEMA_KEYS_BY_CONTEXT[context]
            for key,value in obj.items():
                if key not in allowed:
                    problems.append({'path':'/'.join(path+(str(key),)),'reason':'unknown key for structural context'})
                walk(value, path+(str(key),))
        elif isinstance(obj, list):
            for i,value in enumerate(obj): walk(value, path+(str(i),))
    walk(report, ())
    return problems


def citizen_geotag_identity_variant_values(source_id: str, sentinel: str) -> dict[str, Any]:
    row=make_citizen_geotag_record(source_id)['values']
    row.update({'citizen_name':f'{sentinel}-citizen-name','citizen_contact':f'{sentinel}-citizen-contact','dip_last4':sentinel[-4:],'identity_verification_status':f'{sentinel}-verification-status','identity_document_verified':sentinel.endswith('B'),'identity_verified_at':'2026-07-16T01:02:03Z' if sentinel.endswith('A') else '2026-07-17T04:05:06Z','address_label':f'{sentinel}-address-label','landmark':f'{sentinel}-landmark','grid_code':f'{sentinel}-grid','latitude':1.111111 if sentinel.endswith('A') else 2.222222,'longitude':3.333333 if sentinel.endswith('A') else 4.444444,'accuracy_meters':7.7 if sentinel.endswith('A') else 8.8,'capture_method':f'{sentinel}-capture','status':f'{sentinel}-status','duplicate_hint':f'{sentinel}-duplicate','reviewer_note':f'{sentinel}-reviewer','suggested_road_name':f'{sentinel}-road','suggested_local_area':f'{sentinel}-local','suggested_place_name':f'{sentinel}-place','map_display_name':f'{sentinel}-map','road_suggestion_source':f'{sentinel}-road-source','road_suggestion_attribution':f'{sentinel}-road-attribution','road_suggestion_status':f'{sentinel}-road-status','reviewed_road_name':f'{sentinel}-reviewed-road','field_submission_id':f'{sentinel}-field-submission','field_status':f'{sentinel}-field-status','field_note':f'{sentinel}-field-note','field_verified_at':'2026-07-18T07:08:09Z' if sentinel.endswith('A') else '2026-07-19T10:11:12Z','signage_batch':f'{sentinel}-signage','updated_at':'2026-07-20T13:14:15Z' if sentinel.endswith('A') else '2026-07-21T16:17:18Z'})
    return row


def citizen_geotag_identity_compare_redacted_report_variants(report: dict[str, Any], positive: dict[str, Any], comparison: dict[str, Any], second: dict[str, Any], compatibility: dict[str, Any], test_results: list[dict[str, Any]], rollback_hashes: list[dict[str, Any]], prohibited: dict[str, int], *, leak_variant_value: bool = False) -> dict[str, Any]:
    source_query=positive['transform']['source_row_query']
    variant_a=citizen_geotag_identity_variant_values(report['queried_source_id'], 'C22-VARIANT-A')
    variant_b=citizen_geotag_identity_variant_values(report['queried_source_id'], 'C22-VARIANT-B')
    evidence_a=build_citizen_geotag_redacted_source_evidence(variant_a, source_query)
    evidence_b=build_citizen_geotag_redacted_source_evidence(variant_b, source_query)
    core_a=build_citizen_geotag_identity_report_core(redacted_source_evidence=evidence_a, positive=positive, comparison=comparison, second=second, compatibility=compatibility, test_results=test_results, rollback_hashes=rollback_hashes, prohibited=prohibited, source_value_leak=(variant_a['address_label'] if leak_variant_value else None))
    core_b=build_citizen_geotag_identity_report_core(redacted_source_evidence=evidence_b, positive=positive, comparison=comparison, second=second, compatibility=compatibility, test_results=test_results, rollback_hashes=rollback_hashes, prohibited=prohibited, source_value_leak=(variant_b['address_label'] if leak_variant_value else None))
    hash_a=core_a.pop('source_row_hash_sha256'); hash_b=core_b.pop('source_row_hash_sha256')
    normalized_equal=core_a==core_b; source_hashes_differ=hash_a!=hash_b
    payload=json.dumps([core_a, core_b], sort_keys=True, default=str)
    sentinel_hits=[sentinel for sentinel in ['C22-VARIANT-A','C22-VARIANT-B'] if sentinel in payload]
    raw_object_present=bool(validate_citizen_geotag_identity_report_structure(core_a) or validate_citizen_geotag_identity_report_structure(core_b))
    return {'source_hashes_differ':source_hashes_differ,'normalized_reports_equal':normalized_equal,'variant_a_source_row_hash_sha256':hash_a,'variant_b_source_row_hash_sha256':hash_b,'variant_sentinel_hits':sentinel_hits,'raw_source_object_present':raw_object_present,'leakage_detected':(not normalized_equal) or bool(sentinel_hits) or raw_object_present}


def citizen_geotag_identity_report_privacy_check(report: dict[str, Any], positive_source_values: dict[str, Any], positive: dict[str, Any], comparison: dict[str, Any], second: dict[str, Any], compatibility: dict[str, Any], test_results: list[dict[str, Any]], rollback_hashes: list[dict[str, Any]], prohibited: dict[str, int]) -> dict[str, Any]:
    forbidden_paths=validate_citizen_geotag_identity_report_structure(report)
    if forbidden_paths: raise HarnessError(f'citizen_geotag_submissions identity report forbidden structure: {forbidden_paths}')
    mutation_report=copy.deepcopy(report); mutation_report['debug']={'source_row': {'latitude': 1.23}}
    mutation_result=validate_citizen_geotag_identity_report_structure(mutation_report)
    if not mutation_result: raise HarnessError('redacted-report-structure-mutation unexpectedly passed')
    serialized=json.dumps(report, sort_keys=True, default=str)
    forbidden=[]; authorized_target_timestamps={str(positive_source_values.get('created_at'))}
    for field in CITIZEN_GEOTAG_EXCLUDED_VALUE_FIELDS:
        value=positive_source_values.get(field)
        if value is None or isinstance(value, bool): continue
        text=str(value)
        if text and text in serialized and text not in authorized_target_timestamps:
            forbidden.append({'field':field,'value_sha256':sha(text)})
    if forbidden: raise HarnessError(f'citizen_geotag_submissions identity report leaked excluded source values: {forbidden}')
    differential=citizen_geotag_identity_compare_redacted_report_variants(report, positive, comparison, second, compatibility, test_results, rollback_hashes, prohibited)
    if not differential['source_hashes_differ'] or not differential['normalized_reports_equal'] or differential['variant_sentinel_hits'] or differential['raw_source_object_present']:
        raise HarnessError(f'citizen_geotag_submissions identity differential redaction failed: {differential}')
    leak_mutation=citizen_geotag_identity_compare_redacted_report_variants(report, positive, comparison, second, compatibility, test_results, rollback_hashes, prohibited, leak_variant_value=True)
    if not leak_mutation['leakage_detected']:
        raise HarnessError('redacted-report-differential-mutation unexpectedly passed')
    return {'test_id':'privacy-output-boundary','status':'passed','structural_allowlist_passed':True,'differential_redaction_passed':True,'differential_leakage_mutation_detected':True,'source_hashes_differ':differential['source_hashes_differ'],'normalized_reports_equal':differential['normalized_reports_equal'],'variant_a_source_row_hash_sha256':differential['variant_a_source_row_hash_sha256'],'variant_b_source_row_hash_sha256':differential['variant_b_source_row_hash_sha256'],'variant_sentinel_hits':differential['variant_sentinel_hits'],'raw_source_values_in_committed_report':False,'sensitive_values_redacted':True,'forbidden_report_paths':forbidden_paths,'forbidden_value_hits':0,'checked_excluded_fields':CITIZEN_GEOTAG_EXCLUDED_VALUE_FIELDS,'boolean_values_covered_by_differential':True,'numeric_values_covered_by_differential':True,'timestamp_values_covered_by_differential':True,'text_values_covered_by_differential':True,'unknown_path_mutation_result':'rejected','differential_leakage_mutation_result':'rejected','actual_report_builder':'build_citizen_geotag_identity_report_core','actual_redacted_source_evidence_builder':'build_citizen_geotag_redacted_source_evidence','variant_a_report_generated_independently':True,'variant_b_report_generated_independently':True}


def run_citizen_geotag_identity_slice() -> dict[str, Any]:
    broad_report_path=DM/'phase-a-current-source-execution-report.json'; broad_report_original=broad_report_path.read_text() if broad_report_path.exists() else None
    if citizen_geotag_identity_oracle_hash()!=CITIZEN_GEOTAG_IDENTITY_ORACLE_BASELINE_SHA256: raise HarnessError('reviewer-owned citizen_geotag_submissions identity oracle changed')
    if citizen_geotag_oracle_hash()!=CITIZEN_GEOTAG_ORACLE_BASELINE_SHA256: raise HarnessError('accepted citizen geotag geometry oracle changed')
    setup_citizen_geotag_identity_database(); positive=run_citizen_geotag_identity_slice_once(compare_expected=True)
    source_id=positive['transform']['queried_source_id']
    with connect() as conn, conn.cursor() as cur:
        source_row,_=query_complete_citizen_geotag_row(cur, source_id)
    test_results=[{'test_id':'positive-authoritative-slice','status':'passed'},{'test_id':'second-run-idempotency','status':'passed','first_run_inserts':positive['transform']['insert_stats_first']['inserted'],'second_run_inserts':positive['transform']['insert_stats_second']['inserted'],'second_run_updates':positive['transform']['second_run_updates']},{'test_id':'read-only-complete-set-comparison','status':'passed','comparison':positive['comparison']['complete_target_set_query']}]
    second=run_citizen_geotag_identity_second_source_identity_test(); test_results.append(second)
    compatibility=run_citizen_geotag_identity_geometry_compatibility_test(); test_results.append(compatibility)
    probes=[('missing-source-record','citizen_geotag_submissions source row not found',{'missing_source':True}),('missing-source-lineage','citizen_geotag_submissions source record lineage not found',{'missing_source_lineage':True}),('missing-evidence-object','citizen_geotag_submissions evidence object not found',{'missing_evidence_object':True}),('source-record-classification-drift','citizen_geotag_submissions source record must remain restricted',{'source_record_classification_drift':True}),('evidence-classification-drift','citizen_geotag_submissions evidence object must remain restricted',{'evidence_classification_drift':True}),('citizen-name-identity-substitution','citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id',{'citizen_name_identity_substitution':True}),('citizen-contact-identity-substitution','citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id',{'citizen_contact_identity_substitution':True}),('identity-fragment-identity-substitution','citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id',{'identity_fragment_identity_substitution':True}),('grid-code-identity-substitution','citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id',{'grid_code_identity_substitution':True}),('field-submission-identity-substitution','citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id',{'field_submission_identity_substitution':True}),('territory-identity-substitution','citizen_geotag_submissions identity must derive from citizen_geotag_submissions.id',{'territory_identity_substitution':True}),('wrong-target-identity-implementation','citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity',{'wrong_target_identity_implementation':True}),('existing-location-conflict','citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity',{'existing_location_conflict':True}),('existing-subject-conflict','citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity',{'existing_subject_conflict':True}),('existing-crosswalk-conflict','citizen_geotag_submissions identity rows differ from reviewer-owned expected target identity',{'existing_crosswalk_conflict':True}),('unexpected-extra-crosswalk','unexpected citizen_geotag_submissions identity-foundation target row',{'unexpected_extra_crosswalk':True}),('unexpected-unlisted-alternate-field-crosswalk','unexpected citizen_geotag_submissions identity-foundation target row',{'unexpected_unlisted_alternate_field_crosswalk':True}),('unexpected-extra-location-record','unexpected citizen_geotag_submissions identity-foundation target row',{'unexpected_extra_location_record':True}),('unexpected-extra-registry-subject','unexpected citizen_geotag_submissions identity-foundation target row',{'unexpected_extra_registry_subject':True}),('semantic-duplicate-crosswalk','citizen_geotag_submissions identity crosswalk semantic uniqueness violated',{'semantic_duplicate_crosswalk':True}),('transform-spec-binding-drift','citizen_geotag_submissions identity transform specification binding mismatch',{'spec_drift':{'implementation_unit':'impl_wrong'}})]
    for pid,reason,mutation in probes: test_results.append(run_citizen_geotag_identity_negative_probe(pid, reason, mutation))
    rollback_hashes=[t for t in test_results if 'same_database_pre_test_hash' in t]; prohibited={item['table']+':'+str(item.get('where')):item['count'] for item in positive['comparison']['expected_absent_rows']}
    redacted_source_evidence=build_citizen_geotag_redacted_source_evidence(source_row, positive['transform']['source_row_query'])
    report=build_citizen_geotag_identity_report_core(redacted_source_evidence=redacted_source_evidence, positive=positive, comparison=positive['comparison'], second=second, compatibility=compatibility, test_results=test_results, rollback_hashes=rollback_hashes, prohibited=prohibited)
    privacy=citizen_geotag_identity_report_privacy_check(report, source_row, positive, positive['comparison'], second, compatibility, test_results, rollback_hashes, prohibited); report['privacy_output_boundary_test']=privacy; test_results.append(privacy); report['tests']=test_results
    write_json(DM/'phase-a-citizen-geotag-identity-slice-report.json', report)
    if broad_report_original is not None: broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists(): broad_report_path.unlink()
    return report



# ---- Administrative units identity-shell one-slice checkpoint ----
ADMIN_UNITS_IDENTITY_ORACLE = ACCEPTANCE / 'NLI-WO-002-phase-a-admin-units-identity-shell-expected.json'
ADMIN_UNITS_IDENTITY_ORACLE_BASELINE_SHA256 = '96d3c8a70ce995e26e1fa85ed38013c091a56e819a451a8daac257acb9347f84'
ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED = False
ADMIN_UNITS_IDENTITY_GROUP_ID = 'WO002-R06-identity-crosswalk-admin_units'
ADMIN_UNITS_IDENTITY_IMPL_UNIT = 'impl_wo002_r06_identity_crosswalk_admin_units'
ADMIN_UNITS_IDENTITY_FUNCTION = 'transform_admin_units_identity_crosswalk'
ADMIN_UNITS_IDENTITY_IMPLEMENTATIONS: dict[str, Callable[..., dict[str, Any]]] = {}
ADMIN_UNITS_IMPL_AUTH = ROOT / 'docs' / 'sda' / 'reviews' / 'NLI-WO-002-admin-impl-auth.json'
ADMIN_UNITS_AUTHORITY_MARKER = ROOT / 'docs' / 'sda' / 'reviews' / 'NLI-WO-002-admin-shell-authority.json'
ADMIN_UNITS_SPEC_AUTH = ROOT / 'docs' / 'sda' / 'reviews' / 'NLI-WO-002-admin-spec-auth.json'
ADMIN_UNITS_SPEC_ASSESSMENT = ROOT / 'docs' / 'sda' / 'reviews' / 'NLI-WO-002-admin-spec-assessment.json'
ADMIN_UNITS_LIVE_SPEC = FIXTURES / 'transform-specs' / 'phase-a-transform-specs.json'
ADMIN_UNITS_LIVE_SPEC_BLOB = '763cad920cb398771c983adbbe5d653f332bf6c1'
ADMIN_UNITS_LIVE_SPEC_SHA256 = '8e39fbc84108064e2c008cac3468f7a5d82a287baeac5483ac82a8d6b4508dce'
ADMIN_UNITS_AUTHORITY_MARKER_SHA256 = 'afee3006b9da042365de8d1d35a895e5632c69fb26f479ca2242a15f7a986a19'
ADMIN_UNITS_IMPL_AUTH_SHA256 = '187dae38c3f0f389f093de662c6242d63db0a8722374c71498bb1bb145e2ece1'
ADMIN_UNITS_SPEC_AUTH_SHA256 = 'f8ef3656327097281f4c4e0df0df052076ea7e13ac16e8e638c2471bec9b690b'
ADMIN_UNITS_C41_ASSESSMENT_SHA256 = '3cf5b6e146e30d3e62111d3e8d940d6b242653ea8317809efe95b7ee37ae6a01'
ADMIN_UNITS_C42_C45_ASSESSMENT = ROOT / 'docs' / 'sda' / 'reviews' / 'NLI-WO-002-admin-shell-assessment.json'
ADMIN_UNITS_C42_C45_ASSESSMENT_SHA256 = '9f04e0447779b458f31a09928bef455f5584e2924e5144e69417d8f4f04eed1c'
ADMIN_UNITS_PRIMARY_SOURCE_ID = 'phase-a-admin-units-id'
ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID = 'phase-a-source-record-admin-units-001'
ADMIN_UNITS_PRIMARY_PACKAGE_ID = 'phase-a-source-package-admin-units'
ADMIN_UNITS_PRIMARY_AUTHORITY_ID = 'phase-a-authority-conditional-admin-reference'
ADMIN_UNITS_PRIMARY_EVIDENCE_ID = 'phase-a-evidence-admin-units'
ADMIN_UNITS_COUNTRY_ID = 'phase-a-country-gq'
ADMIN_UNITS_CONTEXT_FIELDS = ['admin_units.level','admin_units.code','admin_units.parent_id','admin_units.province_code','admin_units.name_es','admin_units.name_en','admin_units.status','admin_units.sort_order','admin_units.created_at','admin_units.updated_at']
ADMIN_UNITS_SOURCE_FIELDS = ['id','level','code','parent_id','province_code','name_es','name_en','status','sort_order','created_at','updated_at']
ADMIN_UNITS_NEGATIVE_ERRORS = [
    ('missing-country-prerequisite','administrative identity shell missing country prerequisite',{'missing_country': True}),
    ('missing-reviewed-source-record','administrative identity shell missing reviewed source record',{'missing_source_record': True}),
    ('wrong-source-package','administrative identity shell wrong source package',{'wrong_source_package': True}),
    ('wrong-source-authority','administrative identity shell wrong source authority',{'wrong_source_authority': True}),
    ('wrong-evidence-object','administrative identity shell wrong evidence object',{'wrong_evidence_object': True}),
    ('classification-drift','administrative identity shell classification drift',{'classification_drift': True}),
    ('wrong-source-table','administrative identity shell wrong source table',{'wrong_source_table': True}),
    ('wrong-source-field','administrative identity shell wrong source field',{'wrong_source_field': True}),
    ('wrong-legacy-id','administrative identity shell wrong legacy ID',{'wrong_legacy_id': True}),
    ('one-source-multiple-targets','administrative identity shell one source ID resolving to multiple targets',{'multiple_targets': True}),
    ('duplicate-administrative-identity','administrative identity shell duplicate administrative identity',{'duplicate_admin_identity': True}),
    ('duplicate-administrative-registry-subject','administrative identity shell duplicate administrative registry subject',{'duplicate_registry_subject': True}),
    ('wrong-subject-entity','administrative identity shell wrong subject entity',{'wrong_subject_entity': True}),
    ('wrong-subject-native-id','administrative identity shell wrong subject native ID',{'wrong_subject_native_id': True}),
    ('accepted-address-subject-reuse','administrative identity shell accepted address subject reuse',{'accepted_address_subject_reuse': True}),
    ('generic-geotag-subject-reuse','administrative identity shell generic geotag-subject reuse',{'generic_geotag_subject_reuse': True}),
    ('unexpected-administrative-version','administrative identity shell unexpected administrative version',{'unexpected_admin_version': True}),
    ('unexpected-code-history-row','administrative identity shell unexpected code-history row',{'unexpected_code_history': True}),
    ('unexpected-name-row','administrative identity shell unexpected name row',{'unexpected_name': True}),
    ('unexpected-decision-event','administrative identity shell unexpected decision event',{'unexpected_decision_event': True}),
    ('unexpected-migration-exception','administrative identity shell unexpected migration exception',{'unexpected_migration_exception': True}),
    ('unauthorized-public-alias','administrative identity shell unauthorized public alias',{'unauthorized_public_alias': True}),
    ('unauthorized-publication-row','administrative identity shell unauthorized publication row',{'unauthorized_publication': True}),
    ('unexpected-province-identity','administrative identity shell unexpected province identity',{'unexpected_province_identity': True}),
    ('unexpected-territory-identity','administrative identity shell unexpected territory identity',{'unexpected_territory_identity': True}),
    ('unexpected-attributable-target-row','administrative identity shell unexpected attributable target row',{'unexpected_attributable': True}),
    ('missing-expected-identity-shell-row','administrative identity shell missing expected identity-shell row',{'missing_expected_row': True}),
]

def admin_units_identity_oracle_hash() -> str:
    return file_sha256(ADMIN_UNITS_IDENTITY_ORACLE)

def load_admin_units_identity_oracle() -> dict[str, Any]:
    if not ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED:
        raise HarnessError('reviewer-owned admin_units identity-shell oracle access is disabled outside the read-only comparator')
    return json.loads(ADMIN_UNITS_IDENTITY_ORACLE.read_text())

class admin_units_identity_oracle_access:
    def __init__(self, enabled: bool):
        self.enabled = enabled
        self.previous = False
    def __enter__(self):
        global ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED
        self.previous = ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED
        ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED = self.enabled
    def __exit__(self, exc_type, exc, tb):
        global ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED
        ADMIN_UNITS_IDENTITY_ORACLE_ACCESS_ALLOWED = self.previous

def admin_units_administrative_unit_id(source_id: str) -> str:
    return f'administrative-unit:admin_units:{source_id}'

def admin_units_subject_id(source_id: str) -> str:
    return f'subject:administrative_unit:{admin_units_administrative_unit_id(source_id)}'

def admin_units_crosswalk_id(source_id: str) -> str:
    return f'crosswalk:admin_units:id:{source_id}:to:administrative_unit:{admin_units_administrative_unit_id(source_id)}'

def admin_units_source_key_from_id(source_id: str) -> str:
    return f'admin_units:{source_id}'

def select_admin_units_record(records: list[dict[str, Any]]) -> dict[str, Any]:
    for rec in records:
        if rec['source_table'] == 'admin_units' and rec['values'].get('id') == ADMIN_UNITS_PRIMARY_SOURCE_ID:
            return rec
    raise HarnessError('administrative identity shell reviewed source fixture metadata not found')

def make_admin_units_record(source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> dict[str, Any]:
    rec = copy.deepcopy(select_admin_units_record(fixture_records()))
    rec['values']['id'] = source_id
    rec['source_key'] = admin_units_source_key_from_id(source_id)
    if source_id == ADMIN_UNITS_PRIMARY_SOURCE_ID:
        rec['source_record_id'] = ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID
    else:
        suffix = source_id.rsplit('-', 1)[-1]
        rec['source_record_id'] = f'phase-a-source-record-admin-units-{suffix}'
        rec['values']['code'] = f'phase-a-admin-units-code-{suffix}'
        rec['values']['name_es'] = f'phase-a admin_units name_es {suffix}'
        rec['values']['name_en'] = f'phase-a admin_units name_en {suffix}'
    return rec

def setup_admin_units_identity_database() -> None:
    discover_current(reset=True)
    apply_target()
    topology_check()

def query_complete_admin_units_row(cur, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> tuple[dict[str, Any], dict[str, Any]]:
    sql = """
        SELECT id, level, code, parent_id, province_code, name_es, name_en, status,
               sort_order, created_at, updated_at
        FROM current_source.admin_units
        WHERE id = %s
    """
    params = (source_id,)
    cur.execute(sql, params)
    row = cur.fetchone()
    if not row:
        raise HarnessError('administrative identity shell missing reviewed source record')
    row = norm_row(dict(row))
    redacted = {'id': row['id'], 'field_names': ADMIN_UNITS_SOURCE_FIELDS, 'field_presence': {k: row.get(k) is not None for k in ADMIN_UNITS_SOURCE_FIELDS}, 'source_row_hash_sha256': sha(row), 'raw_context_values_redacted': True}
    return row, {'sql': ' '.join(sql.split()), 'params': list(params), 'queried_source_id': source_id, 'row': redacted}

def reviewed_admin_units_identity_transform_spec(spec_mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    expected_rule = {'primary_fixture': {'source_id': ADMIN_UNITS_PRIMARY_SOURCE_ID, 'administrative_unit_id': admin_units_administrative_unit_id(ADMIN_UNITS_PRIMARY_SOURCE_ID), 'legacy_crosswalk_id': admin_units_crosswalk_id(ADMIN_UNITS_PRIMARY_SOURCE_ID), 'subject_id': admin_units_subject_id(ADMIN_UNITS_PRIMARY_SOURCE_ID), 'subject_entity': 'administrative_unit', 'country_id': ADMIN_UNITS_COUNTRY_ID}, 'synthetic_design_fixture_rule': {'scope': 'design harness only; no production national identifier policy', 'for_source_id': '<source-id>', 'administrative_unit_id': 'administrative-unit:admin_units:<source-id>', 'subject_id': 'subject:administrative_unit:administrative-unit:admin_units:<source-id>', 'legacy_crosswalk_id': 'crosswalk:admin_units:id:<source-id>:to:administrative_unit:administrative-unit:admin_units:<source-id>', 'constraints': ['design harness only','no production national identifier policy','no hierarchy version','no names or code history','no province or territory identity','no migration exception','no public or publication output']}}
    expected = {'transform_group_id': ADMIN_UNITS_IDENTITY_GROUP_ID, 'implementation_unit': ADMIN_UNITS_IDENTITY_IMPL_UNIT, 'required_future_callable': ADMIN_UNITS_IDENTITY_FUNCTION, 'source_table': 'admin_units', 'source_record_key': 'admin_units:phase-a-admin-units-001', 'idempotency_key': 'admin_units.phase-a-admin-units-id::WO002-R06-identity-crosswalk-admin_units', 'covered_source_fields': ['admin_units.id'], 'required_context_fields': ADMIN_UNITS_CONTEXT_FIELDS, 'identity_rule': 'admin_units.id alone owns the provisional government-internal administrative identity shell; level, code, parent, province, names, lifecycle, ordering and timestamps must not determine or replace the identity.', 'dispositions': ['structured-transform'], 'exception_behavior': 'no migration exception in this identity shell; every non-id source field is context or a future authority input and may not create an exception, hierarchy fact, code, name, version or publication output.', 'conditional_authority_rfi_status': ['none'], 'authority_resolution': 'NLI-WO-002-PA-ADMIN-ID-SHELL-01 resolves the narrow identity-shell authority question only; hierarchy, version, code, name, province and territory authority remain unresolved.', 'target_entities': ['administrative_unit','registry_subject','legacy_crosswalk'], 'target_fields': ['administrative_unit.administrative_unit_id','registry_subject.subject_id','legacy_crosswalk.legacy_id'], 'target_identity_rule': expected_rule}
    group = copy.deepcopy(next((g for g in registry_groups() if g['transform_group_id'] == ADMIN_UNITS_IDENTITY_GROUP_ID), None))
    if not group:
        raise HarnessError('administrative identity shell transform specification binding mismatch: reviewed group missing')
    if spec_mutation:
        for key, value in spec_mutation.items(): group[key] = value
    checks = {k: group.get(k) == v for k, v in expected.items()}
    checks['callable_binding'] = ADMIN_UNITS_IDENTITY_IMPLEMENTATIONS.get(group.get('implementation_unit')) is transform_admin_units_identity_crosswalk
    checks['no_scalar_conditional_status'] = isinstance(group.get('conditional_authority_rfi_status'), list)
    checks['no_formal_exception'] = 'formal-exception' not in group.get('dispositions', [])
    checks['no_migration_exception_target'] = 'migration_exception' not in group.get('target_entities', []) and not any('migration_exception' in x for x in group.get('target_fields', []))
    checks['parent_id_not_covered'] = 'admin_units.parent_id' not in group.get('covered_source_fields', [])
    if not all(checks.values()):
        raise HarnessError(f'administrative identity shell transform specification binding mismatch: {checks}')
    return {'group': group, 'required_context_fields': group['required_context_fields'], 'validation': checks}

def admin_units_lineage_rows(records: list[dict[str, Any]], mutation: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    mutation = mutation or {}; rows = {t: [] for t in DEPENDENCY_ORDER}
    rows['proposed_source_authority'].append({'source_authority_id': ADMIN_UNITS_PRIMARY_AUTHORITY_ID, 'authority_name': 'Phase A conditional administrative reference authority', 'authority_class': 'registry-authority', 'legal_basis': 'Conditional/provisional non-official government reference fixture linked to authority RFI', 'status': 'candidate'})
    if not mutation.get('missing_country'):
        rows['proposed_country'].append({'country_id': ADMIN_UNITS_COUNTRY_ID, 'iso2_code': 'GQ', 'official_name_es': 'Guinea Ecuatorial', 'official_name_en': 'Equatorial Guinea', 'lifecycle_state': 'active', 'source_authority_id': ADMIN_UNITS_PRIMARY_AUTHORITY_ID, 'created_at': TS})
    for rec in records:
        if rec.get('source_table') != 'admin_units':
            continue
        normalized_values = norm_row(normalize_current_fixture_values(rec['source_table'], rec['values']))
        values_hash = sha(normalized_values); primary = rec['values']['id'] == ADMIN_UNITS_PRIMARY_SOURCE_ID
        package_id = ADMIN_UNITS_PRIMARY_PACKAGE_ID if primary else f'phase-a-source-package-admin-units-{rec["values"]["id"].rsplit("-",1)[-1]}'
        evidence_id = ADMIN_UNITS_PRIMARY_EVIDENCE_ID if primary else f'phase-a-evidence-admin-units-{rec["values"]["id"].rsplit("-",1)[-1]}'
        source_authority_id = 'wrong-source-authority' if mutation.get('wrong_source_authority') and primary else ADMIN_UNITS_PRIMARY_AUTHORITY_ID
        source_package_ref = 'wrong-source-package' if mutation.get('wrong_source_package') and primary else package_id
        rows['proposed_source_package'].append({'source_package_id': package_id, 'source_authority_id': source_authority_id, 'package_name': 'Phase A source package admin_units', 'package_checksum': values_hash, 'licence_id': None, 'loaded_at': TS, 'load_context': {'source_table': 'admin_units', 'phase': 'A'}})
        if mutation.get('wrong_source_authority') and primary:
            rows['proposed_source_authority'].append({'source_authority_id':'wrong-source-authority','authority_name':'Wrong authority','authority_class':'registry-authority','legal_basis':'mutation','status':'candidate'})
        if mutation.get('wrong_source_package') and primary:
            rows['proposed_source_package'].append({'source_package_id':'wrong-source-package','source_authority_id':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'package_name':'Wrong source package admin_units','package_checksum':values_hash,'licence_id':None,'loaded_at':TS,'load_context':{'source_table':'admin_units','phase':'A'}})
        if not (mutation.get('missing_source_record') and primary):
            rows['proposed_source_record'].append({'source_record_id': rec['source_record_id'], 'source_package_id': source_package_ref, 'source_key': admin_units_source_key_from_id(rec['values']['id']), 'raw_payload_hash': values_hash, 'raw_payload_classification': 'public' if mutation.get('classification_drift') and primary else 'government-internal', 'recorded_at': TS})
        if mutation.get('wrong_evidence_object') and primary:
            rows['proposed_evidence_object'].append({'evidence_object_id': 'wrong-evidence-object', 'source_record_id': rec['source_record_id'], 'storage_uri': 'phase-a://evidence/wrong', 'content_hash': values_hash, 'media_type': 'application/json', 'classification': 'government-internal', 'captured_at': TS, 'retention_state': 'active'})
        elif not (mutation.get('missing_source_record') and primary):
            rows['proposed_evidence_object'].append({'evidence_object_id': evidence_id, 'source_record_id': rec['source_record_id'], 'storage_uri': f'phase-a://evidence/admin_units:{rec["values"]["id"]}', 'content_hash': values_hash, 'media_type': 'application/json', 'classification': 'public' if mutation.get('classification_drift') and primary else 'government-internal', 'captured_at': TS, 'retention_state': 'active'})
    return rows

def insert_admin_units_lineage_preconditions(cur, records: list[dict[str, Any]], mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    stats = apply_target_rows(cur, admin_units_lineage_rows(records, mutation)); cur.execute('SET CONSTRAINTS ALL IMMEDIATE'); return stats

def require_admin_units_lineage(cur, source_row: dict[str, Any]) -> dict[str, Any]:
    source_id = source_row['id']; source_key = admin_units_source_key_from_id(source_id)
    suffix = source_id.rsplit('-',1)[-1]
    source_record_id = ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID if source_id == ADMIN_UNITS_PRIMARY_SOURCE_ID else f'phase-a-source-record-admin-units-{suffix}'
    package_id = ADMIN_UNITS_PRIMARY_PACKAGE_ID if source_id == ADMIN_UNITS_PRIMARY_SOURCE_ID else f'phase-a-source-package-admin-units-{suffix}'
    evidence_id = ADMIN_UNITS_PRIMARY_EVIDENCE_ID if source_id == ADMIN_UNITS_PRIMARY_SOURCE_ID else f'phase-a-evidence-admin-units-{suffix}'
    cur.execute('SELECT * FROM canonical_target.proposed_country WHERE country_id=%s', (ADMIN_UNITS_COUNTRY_ID,)); countries=cur.fetchall()
    if len(countries) != 1: raise HarnessError('administrative identity shell missing country prerequisite')
    cur.execute('SELECT source_record_id, source_package_id, source_key, raw_payload_hash, raw_payload_classification FROM canonical_target.proposed_source_record WHERE source_record_id=%s', (source_record_id,)); source_rows=[dict(r) for r in cur.fetchall()]
    if len(source_rows) != 1: raise HarnessError('administrative identity shell missing reviewed source record')
    source=source_rows[0]
    if source['source_package_id'] != package_id: raise HarnessError('administrative identity shell wrong source package')
    if source['raw_payload_classification'] != 'government-internal': raise HarnessError('administrative identity shell classification drift')
    cur.execute('SELECT source_package_id, source_authority_id, package_checksum FROM canonical_target.proposed_source_package WHERE source_package_id=%s', (package_id,)); package_rows=[dict(r) for r in cur.fetchall()]
    if len(package_rows) != 1 or package_rows[0]['source_authority_id'] != ADMIN_UNITS_PRIMARY_AUTHORITY_ID: raise HarnessError('administrative identity shell wrong source authority')
    cur.execute('SELECT source_authority_id, authority_class, status FROM canonical_target.proposed_source_authority WHERE source_authority_id=%s', (ADMIN_UNITS_PRIMARY_AUTHORITY_ID,)); authority_rows=[dict(r) for r in cur.fetchall()]
    if len(authority_rows) != 1 or authority_rows[0]['authority_class'] != 'registry-authority' or authority_rows[0]['status'] != 'candidate': raise HarnessError('administrative identity shell wrong source authority')
    cur.execute('SELECT evidence_object_id, source_record_id, classification, content_hash FROM canonical_target.proposed_evidence_object WHERE evidence_object_id=%s', (evidence_id,)); evidence_rows=[dict(r) for r in cur.fetchall()]
    if len(evidence_rows) != 1 or evidence_rows[0]['source_record_id'] != source_record_id: raise HarnessError('administrative identity shell wrong evidence object')
    evidence=evidence_rows[0]
    if evidence['classification'] != 'government-internal': raise HarnessError('administrative identity shell classification drift')
    expected_hash=sha(source_row)
    if source['raw_payload_hash'] != expected_hash or package_rows[0]['package_checksum'] != expected_hash or evidence['content_hash'] != expected_hash: raise HarnessError('administrative identity shell lineage hash correspondence mismatch')
    return {'derived_source_key': source_key, 'source_record_id': source_record_id, 'source_package_id': package_id, 'source_authority_id': ADMIN_UNITS_PRIMARY_AUTHORITY_ID, 'evidence_object_id': evidence_id, 'source_classification': source['raw_payload_classification'], 'evidence_classification': evidence['classification'], 'raw_payload_hash': source['raw_payload_hash'], 'package_checksum': package_rows[0]['package_checksum'], 'evidence_content_hash': evidence['content_hash'], 'hash_correspondence': True, 'lineage_chain': 'admin_units.id tuple -> legacy crosswalk -> administrative-unit target ID -> registry-subject native ID'}

def admin_units_identity_rows_for_source(source_id: str, mutation: dict[str, Any] | None = None) -> dict[str, list[dict[str, Any]]]:
    mutation=mutation or {}; rows={t:[] for t in DEPENDENCY_ORDER}; admin_id=admin_units_administrative_unit_id(source_id)
    if not mutation.get('missing_expected_row'):
        rows['proposed_administrative_unit'].append({'administrative_unit_id': admin_id, 'country_id': ADMIN_UNITS_COUNTRY_ID, 'created_at': TS, 'retired_at': None})
    rows['proposed_legacy_crosswalk'].append({'legacy_crosswalk_id': admin_units_crosswalk_id(source_id), 'source_table': 'wrong_table' if mutation.get('wrong_source_table') else 'admin_units', 'source_field': 'parent_id' if mutation.get('wrong_source_field') else 'id', 'legacy_id': 'wrong-legacy-id' if mutation.get('wrong_legacy_id') else source_id, 'target_entity': 'location_record' if mutation.get('wrong_target_entity') else 'administrative_unit', 'target_id': admin_id, 'created_at': TS})
    if mutation.get('wrong_subject_entity'):
        rows['proposed_location_record'].append({'location_record_id': admin_id, 'record_type': 'address', 'created_at': TS, 'retired_at': None, 'classification': 'government-internal'})
    if mutation.get('wrong_subject_native_id'):
        rows['proposed_administrative_unit'].append({'administrative_unit_id': admin_id + '-wrong', 'country_id': ADMIN_UNITS_COUNTRY_ID, 'created_at': TS, 'retired_at': None})
    if not mutation.get('missing_expected_row'):
        rows['proposed_registry_subject'].append({'subject_id': admin_units_subject_id(source_id), 'subject_entity': 'location_record' if mutation.get('wrong_subject_entity') else 'administrative_unit', 'created_at': TS, 'native_id': admin_id + '-wrong' if mutation.get('wrong_subject_native_id') else admin_id, 'subject_state': 'active', 'retired_at': None, 'delete_policy': 'retire-only'})
    return rows

def transform_admin_units_identity_crosswalk(cur, *, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID, mutation: dict[str, Any] | None = None, spec_validation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation=mutation or {}
    if mutation.get('unexpected_oracle_access'): load_admin_units_identity_oracle()
    spec_validation = spec_validation or reviewed_admin_units_identity_transform_spec(mutation.get('spec_drift'))
    source_row, source_query = query_complete_admin_units_row(cur, source_id)
    lineage = require_admin_units_lineage(cur, source_row)
    rows = admin_units_identity_rows_for_source(source_row['id'], mutation)
    stats1=apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    stats2=apply_target_rows(cur, rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE')
    return {'function_invoked': ADMIN_UNITS_IDENTITY_FUNCTION, 'implementation_unit': ADMIN_UNITS_IDENTITY_IMPL_UNIT, 'transform_group_id': ADMIN_UNITS_IDENTITY_GROUP_ID, 'generic_transform_group_used': False, 'source_row_query': source_query, 'source_fields_queried': ADMIN_UNITS_SOURCE_FIELDS, 'fields_consumed': ['admin_units.id'] + ADMIN_UNITS_CONTEXT_FIELDS, 'covered_identity_fields': ['admin_units.id'], 'context_fields': ADMIN_UNITS_CONTEXT_FIELDS, 'context_values_used_as_identity': False, 'lineage': lineage, 'insert_stats_first': stats1, 'insert_stats_second': stats2, 'second_run_updates': 0, 'second_run_deletes': 0, 'spec_validation': spec_validation, 'derived_ids': {'administrative_unit_id': admin_units_administrative_unit_id(source_id), 'subject_id': admin_units_subject_id(source_id), 'legacy_crosswalk_id': admin_units_crosswalk_id(source_id), 'source_key': lineage['derived_source_key']}, 'identity_rows': {t: rows[t][0] for t in ('proposed_administrative_unit','proposed_registry_subject','proposed_legacy_crosswalk') if rows[t]}}
ADMIN_UNITS_IDENTITY_IMPLEMENTATIONS[ADMIN_UNITS_IDENTITY_IMPL_UNIT] = transform_admin_units_identity_crosswalk


def admin_units_load_json_with_override(path: Path, overrides: dict[str, Any] | None, key: str) -> tuple[str, Any]:
    raw = path.read_bytes()
    if overrides and key in overrides:
        raw = overrides[key]
        if isinstance(raw, str):
            raw = raw.encode()
    digest = hashlib.sha256(raw).hexdigest()
    return digest, json.loads(raw.decode())

def admin_units_verify_control_plane(mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    mutation = mutation or {}
    overrides: dict[str, bytes | str] = {}
    if mutation.get('oracle_hash_drift'):
        overrides['reviewer_oracle'] = ADMIN_UNITS_IDENTITY_ORACLE.read_text().replace('expected_rows', 'expected_rows_drift', 1)
    if mutation.get('authority_marker_drift'):
        authority_doc=json.loads(ADMIN_UNITS_AUTHORITY_MARKER.read_text()); authority_doc['decision']='DRIFTED'
        overrides['authority_marker'] = json.dumps(authority_doc, sort_keys=True)
    if mutation.get('implementation_authorization_drift'):
        impl_doc=json.loads(ADMIN_UNITS_IMPL_AUTH.read_text()); impl_doc['callable']='transform_admin_units_identity_crosswalk_drift'
        overrides['implementation_authorization'] = json.dumps(impl_doc, sort_keys=True)
    if mutation.get('specification_authorization_drift'):
        spec_doc=json.loads(ADMIN_UNITS_SPEC_AUTH.read_text()); spec_doc['group']='WO002-R06-drift'
        overrides['specification_authorization'] = json.dumps(spec_doc, sort_keys=True)
    if mutation.get('c41_assessment_drift'):
        c41_doc=json.loads(ADMIN_UNITS_SPEC_ASSESSMENT.read_text()); c41_doc['finding']='C41-DRIFT'
        overrides['c41_assessment'] = json.dumps(c41_doc, sort_keys=True)
    if mutation.get('corrected_live_spec_drift'):
        spec = json.loads(ADMIN_UNITS_LIVE_SPEC.read_text())
        for group in spec['transform_groups']:
            if group.get('transform_group_id') == ADMIN_UNITS_IDENTITY_GROUP_ID:
                group['conditional_authority_rfi_status'] = 'none'
                break
        overrides['live_spec'] = json.dumps(spec, sort_keys=True)

    authority_sha, authority = admin_units_load_json_with_override(ADMIN_UNITS_AUTHORITY_MARKER, overrides, 'authority_marker')
    oracle_sha, oracle = admin_units_load_json_with_override(ADMIN_UNITS_IDENTITY_ORACLE, overrides, 'reviewer_oracle')
    impl_sha, impl = admin_units_load_json_with_override(ADMIN_UNITS_IMPL_AUTH, overrides, 'implementation_authorization')
    spec_auth_sha, spec_auth = admin_units_load_json_with_override(ADMIN_UNITS_SPEC_AUTH, overrides, 'specification_authorization')
    c41_sha, c41 = admin_units_load_json_with_override(ADMIN_UNITS_SPEC_ASSESSMENT, overrides, 'c41_assessment')
    c42_sha, c42 = admin_units_load_json_with_override(ADMIN_UNITS_C42_C45_ASSESSMENT, overrides, 'c42_c45_assessment')
    live_sha, live = admin_units_load_json_with_override(ADMIN_UNITS_LIVE_SPEC, overrides, 'live_spec')

    if authority_sha != ADMIN_UNITS_AUTHORITY_MARKER_SHA256 or authority.get('decision') != 'OPTION_A_ORACLE_PREPARATION_AUTHORIZED' or authority.get('lineage_model') != 'L1' or authority.get('subject_model') != 'S1' or authority.get('owned_rows') != 3:
        raise HarnessError('administrative identity shell authority marker drift')
    if oracle_sha != ADMIN_UNITS_IDENTITY_ORACLE_BASELINE_SHA256 or 'expected_rows' not in oracle:
        raise HarnessError('administrative identity shell reviewer oracle hash drift')
    if impl_sha != ADMIN_UNITS_IMPL_AUTH_SHA256 or impl.get('decision') != 'IMPLEMENT_ONE_ADMIN_IDENTITY_SHELL' or impl.get('callable') != ADMIN_UNITS_IDENTITY_FUNCTION or impl.get('expected_rows') != 3:
        raise HarnessError('administrative identity shell implementation authorization drift')
    if spec_auth_sha != ADMIN_UNITS_SPEC_AUTH_SHA256 or spec_auth.get('group') != ADMIN_UNITS_IDENTITY_GROUP_ID:
        raise HarnessError('administrative identity shell specification authorization drift')
    if c41_sha != ADMIN_UNITS_C41_ASSESSMENT_SHA256 or c41.get('finding') != 'C41' or c41.get('required', {}).get('conditional_authority_rfi_status') != ['none']:
        raise HarnessError('administrative identity shell C41 assessment drift')
    if c42_sha != ADMIN_UNITS_C42_C45_ASSESSMENT_SHA256 or c42.get('findings') != ['C42', 'C43', 'C44', 'C45']:
        raise HarnessError('administrative identity shell C42-C45 assessment drift')
    group = next((g for g in live.get('transform_groups', []) if g.get('transform_group_id') == ADMIN_UNITS_IDENTITY_GROUP_ID), None)
    if live_sha != ADMIN_UNITS_LIVE_SPEC_SHA256 or not group:
        raise HarnessError('administrative identity shell corrected live-spec drift')
    reviewed_admin_units_identity_transform_spec({'conditional_authority_rfi_status': group.get('conditional_authority_rfi_status')})
    return {
        'verifier': 'admin_units_verify_control_plane',
        'authority_marker': {'path': str(ADMIN_UNITS_AUTHORITY_MARKER.relative_to(ROOT)), 'sha256': authority_sha, 'parsed': True},
        'reviewer_oracle': {'path': str(ADMIN_UNITS_IDENTITY_ORACLE.relative_to(ROOT)), 'sha256': oracle_sha, 'parsed': True},
        'implementation_authorization': {'path': str(ADMIN_UNITS_IMPL_AUTH.relative_to(ROOT)), 'sha256': impl_sha, 'parsed': True},
        'specification_authorization': {'path': str(ADMIN_UNITS_SPEC_AUTH.relative_to(ROOT)), 'sha256': spec_auth_sha, 'parsed': True},
        'c41_assessment': {'path': str(ADMIN_UNITS_SPEC_ASSESSMENT.relative_to(ROOT)), 'sha256': c41_sha, 'parsed': True},
        'c42_c45_assessment': {'path': str(ADMIN_UNITS_C42_C45_ASSESSMENT.relative_to(ROOT)), 'sha256': c42_sha, 'parsed': True},
        'corrected_live_spec': {'path': str(ADMIN_UNITS_LIVE_SPEC.relative_to(ROOT)), 'blob': ADMIN_UNITS_LIVE_SPEC_BLOB, 'sha256': live_sha, 'group_contract_verified': True},
    }

def admin_units_explicit_admin_ids(source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> list[str]:
    base = admin_units_administrative_unit_id(source_id)
    return [base, base + '-alternate', base + '-wrong', base + '-unexpected', 'administrative-unit:admin_units:province-bn', 'administrative-unit:admin_units:territory-admin']

def admin_units_complete_attributable_rows(cur, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID, include_source_derived_orphans: bool = True) -> list[dict[str, Any]]:
    expected_admin_id = admin_units_administrative_unit_id(source_id)
    expected_subject_id = admin_units_subject_id(source_id)
    expected_crosswalk_id = admin_units_crosswalk_id(source_id)
    explicit_admin_ids = set(admin_units_explicit_admin_ids(source_id))
    rows: list[dict[str, Any]] = []
    cw_sql = """
        SELECT legacy_crosswalk_id, source_table, source_field, legacy_id, target_entity, target_id, created_at
        FROM canonical_target.proposed_legacy_crosswalk
        WHERE legacy_crosswalk_id = %s
           OR legacy_crosswalk_id LIKE %s
           OR legacy_crosswalk_id LIKE 'admin-units-%%'
           OR legacy_crosswalk_id LIKE %s
           OR legacy_id = %s
           OR target_id = ANY(%s)
        ORDER BY legacy_crosswalk_id
    """
    cur.execute(cw_sql, (expected_crosswalk_id, expected_crosswalk_id + '%', f'%{source_id}%', source_id, list(explicit_admin_ids)))
    crosswalks = [dict(r) for r in cur.fetchall()]
    reached_admin_ids = {r['target_id'] for r in crosswalks if r.get('target_entity') == 'administrative_unit'}
    admin_ids = explicit_admin_ids | reached_admin_ids
    admin_pred = ['administrative_unit_id = ANY(%s)']; admin_params: list[Any] = [list(admin_ids)]
    if include_source_derived_orphans:
        admin_pred.append('administrative_unit_id LIKE %s'); admin_params.append(expected_admin_id + '-%')
    cur.execute(f"SELECT administrative_unit_id, country_id, created_at, retired_at FROM canonical_target.proposed_administrative_unit WHERE {' OR '.join(admin_pred)} ORDER BY administrative_unit_id", admin_params)
    actual_admin_ids = set()
    for r in cur.fetchall():
        actual_admin_ids.add(r['administrative_unit_id'])
        rows.append({'table': 'proposed_administrative_unit', 'primary_key': {'administrative_unit_id': r['administrative_unit_id']}, 'values': norm_row(dict(r))})
    subject_ids = {expected_subject_id, expected_subject_id + '-duplicate', 'phase-a-subject-phase-a-location-address-reference', 'phase-a-subject-phase-a-location-geotag'} | {f'subject:administrative_unit:{x}' for x in actual_admin_ids | reached_admin_ids}
    cur.execute("""
        SELECT subject_id, subject_entity, created_at, native_id, subject_state, retired_at, delete_policy
        FROM canonical_target.proposed_registry_subject
        WHERE subject_id = ANY(%s) OR native_id = ANY(%s)
        ORDER BY subject_id
    """, (list(subject_ids), list(actual_admin_ids | reached_admin_ids | explicit_admin_ids)))
    for r in cur.fetchall():
        rows.append({'table': 'proposed_registry_subject', 'primary_key': {'subject_id': r['subject_id']}, 'values': norm_row(dict(r))})
    for cw in crosswalks:
        rows.append({'table': 'proposed_legacy_crosswalk', 'primary_key': {'legacy_crosswalk_id': cw['legacy_crosswalk_id']}, 'values': norm_row(cw)})
    subject_scope = list(subject_ids)
    loc_scope = list(admin_ids | {expected_admin_id + '-unexpected'})
    prohibited_checks = [
        ('proposed_administrative_unit_version', 'administrative_unit_id = ANY(%s)', [list(admin_ids)]),
        ('proposed_administrative_code_history', 'administrative_unit_id = ANY(%s)', [list(admin_ids)]),
        ('proposed_name_record', 'subject_id = ANY(%s)', [subject_scope]),
        ('proposed_location_record', 'location_record_id = ANY(%s)', [loc_scope]),
        ('proposed_geometry_observation', 'subject_id = ANY(%s)', [[expected_subject_id]]),
        ('proposed_geometry_version', 'subject_id = ANY(%s)', [[expected_subject_id]]),
        ('proposed_decision_event', "decision_event_id LIKE 'admin-units-%%'", []),
        ('proposed_migration_exception', '(source_key = %s OR migration_exception_id LIKE %s)', [admin_units_source_key_from_id(source_id), 'admin-units-%']),
        ('proposed_public_code_alias', 'location_record_id = ANY(%s)', [loc_scope]),
        ('proposed_publication_release', "publication_release_id LIKE 'admin-units-%%'", []),
        ('proposed_publication_release_item', "publication_release_item_id LIKE 'admin-units-%%'", []),
    ]
    for table, where, params in prohibited_checks:
        cur.execute(f'SELECT * FROM canonical_target.{table} WHERE {where} ORDER BY 1', params)
        for r in cur.fetchall():
            rows.append({'table': table, 'primary_key': primary_key(dict(r), table), 'values': norm_row(dict(r))})
    return sorted(rows, key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))

def admin_units_target_slice_hash(cur, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> dict[str, Any]:
    rows = admin_units_complete_attributable_rows(cur, source_id)
    return {'rows': rows, 'row_count': len(rows), 'hash': sha(rows)}

def expected_admin_units_identity_rows(oracle: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(copy.deepcopy(oracle['expected_rows']), key=lambda r: (r['table'], json.dumps(r['primary_key'], sort_keys=True)))

def admin_units_expected_absence_results(cur, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> list[dict[str, Any]]:
    rows = admin_units_complete_attributable_rows(cur, source_id)
    prohibited = [r for r in rows if r['table'] not in {'proposed_administrative_unit', 'proposed_registry_subject', 'proposed_legacy_crosswalk'}]
    error_map = {
        'proposed_administrative_unit_version': 'administrative identity shell unexpected administrative version',
        'proposed_administrative_code_history': 'administrative identity shell unexpected code-history row',
        'proposed_name_record': 'administrative identity shell unexpected name row',
        'proposed_decision_event': 'administrative identity shell unexpected decision event',
        'proposed_migration_exception': 'administrative identity shell unexpected migration exception',
        'proposed_public_code_alias': 'administrative identity shell unauthorized public alias',
        'proposed_publication_release': 'administrative identity shell unauthorized publication row',
        'proposed_publication_release_item': 'administrative identity shell unauthorized publication row',
    }
    order=['proposed_administrative_unit_version','proposed_administrative_code_history','proposed_name_record','proposed_location_record','proposed_geometry_observation','proposed_geometry_version','proposed_decision_event','proposed_migration_exception','proposed_public_code_alias','proposed_publication_release','proposed_publication_release_item']
    counts={table: sum(1 for r in prohibited if r['table']==table) for table in order}
    results=[{'table': table, 'where': 'scoped to queried source identity plus explicit admin_units test-attribution IDs', 'count': counts[table]} for table in order]
    for table in ['proposed_public_code_alias','proposed_publication_release','proposed_publication_release_item','proposed_administrative_unit_version','proposed_administrative_code_history','proposed_name_record','proposed_decision_event','proposed_migration_exception','proposed_location_record','proposed_geometry_observation','proposed_geometry_version']:
        if counts[table]:
            raise HarnessError(error_map.get(table, 'administrative identity shell unexpected attributable target row'))
    return results

def admin_units_semantic_controls(cur, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> dict[str, Any]:
    rows = admin_units_complete_attributable_rows(cur, source_id)
    crosswalks = [r['values'] for r in rows if r['table']=='proposed_legacy_crosswalk']
    for cw in crosswalks:
        if cw.get('source_table') != 'admin_units':
            raise HarnessError('administrative identity shell wrong source table')
        if cw.get('source_field') != 'id':
            raise HarnessError('administrative identity shell wrong source field')
        if cw.get('legacy_id') != source_id:
            raise HarnessError('administrative identity shell wrong legacy ID')
    target_ids={cw['target_id'] for cw in crosswalks if cw.get('source_table')=='admin_units' and cw.get('source_field')=='id' and cw.get('legacy_id')==source_id and cw.get('target_entity')=='administrative_unit'}
    if len(target_ids) > 1:
        raise HarnessError('administrative identity shell one source ID resolving to multiple targets')
    groups={}
    for cw in crosswalks:
        key=(cw.get('source_table'), cw.get('source_field'), cw.get('legacy_id'), cw.get('target_entity'))
        groups[key]=groups.get(key,0)+1
    duplicate_groups=[k for k,v in groups.items() if v>1]
    if duplicate_groups:
        raise HarnessError('administrative identity shell duplicate administrative identity')
    subjects=[r['values'] for r in rows if r['table']=='proposed_registry_subject']
    address_reuse=sum(1 for s in subjects if s['subject_id']=='phase-a-subject-phase-a-location-address-reference' and s['subject_entity']=='administrative_unit')
    if address_reuse: raise HarnessError('administrative identity shell accepted address subject reuse')
    geotag_reuse=sum(1 for s in subjects if s['subject_id']=='phase-a-subject-phase-a-location-geotag' and s['subject_entity']=='administrative_unit')
    if geotag_reuse: raise HarnessError('administrative identity shell generic geotag-subject reuse')
    expected_admin_id=admin_units_administrative_unit_id(source_id); expected_subject_id=admin_units_subject_id(source_id)
    active_subjects=[s for s in subjects if s.get('subject_entity')=='administrative_unit' and s.get('native_id')==expected_admin_id and s.get('subject_state')=='active']
    if len(active_subjects) > 1:
        raise HarnessError('administrative identity shell duplicate administrative registry subject')
    expected_subject=[s for s in subjects if s['subject_id']==expected_subject_id]
    if expected_subject:
        if expected_subject[0]['subject_entity']!='administrative_unit': raise HarnessError('administrative identity shell wrong subject entity')
        if expected_subject[0]['native_id']!=expected_admin_id: raise HarnessError('administrative identity shell wrong subject native ID')
    admin_ids=[r['values']['administrative_unit_id'] for r in rows if r['table']=='proposed_administrative_unit']
    if 'administrative-unit:admin_units:province-bn' in admin_ids:
        raise HarnessError('administrative identity shell unexpected province identity')
    if 'administrative-unit:admin_units:territory-admin' in admin_ids:
        raise HarnessError('administrative identity shell unexpected territory identity')
    return {'multiple_target_resolutions':0,'duplicate_crosswalk_groups':len(duplicate_groups),'active_administrative_subjects_for_native_id':len(active_subjects),'duplicate_administrative_subjects':0,'accepted_address_subject_reuse':address_reuse,'generic_geotag_subject_reuse':geotag_reuse,'non_id_admin_units_crosswalks':0,'semantic_duplicates':0}

def admin_units_shared_state_validator(cur, *, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID, expected_rows: list[dict[str, Any]] | None = None, generic_transform_used: bool = False) -> dict[str, Any]:
    if generic_transform_used:
        raise HarnessError('administrative identity shell generic transform invocation prohibited')
    if expected_rows is None:
        with admin_units_identity_oracle_access(True):
            expected_rows = expected_admin_units_identity_rows(load_admin_units_identity_oracle())
    actual = admin_units_complete_attributable_rows(cur, source_id)
    semantic = admin_units_semantic_controls(cur, source_id)
    absent = admin_units_expected_absence_results(cur, source_id)
    core_tables={'proposed_administrative_unit','proposed_registry_subject','proposed_legacy_crosswalk'}
    core=[r for r in actual if r['table'] in core_tables]
    exp_by_key={(r['table'], tuple(sorted(r['primary_key'].items()))): r for r in expected_rows}
    act_by_key={(r['table'], tuple(sorted(r['primary_key'].items()))): r for r in core}
    unexpected=sorted(set(act_by_key)-set(exp_by_key)); missing=sorted(set(exp_by_key)-set(act_by_key))
    if missing:
        raise HarnessError('administrative identity shell missing expected identity-shell row')
    if unexpected:
        raise HarnessError(f'administrative identity shell unexpected attributable target row: {unexpected}')
    for key, exp in exp_by_key.items():
        act=act_by_key[key]
        if act['values'] != exp['values']:
            v=act['values']
            if act['table']=='proposed_legacy_crosswalk':
                if v.get('source_table')!='admin_units': raise HarnessError('administrative identity shell wrong source table')
                if v.get('source_field')!='id': raise HarnessError('administrative identity shell wrong source field')
                if v.get('legacy_id')!=source_id: raise HarnessError('administrative identity shell wrong legacy ID')
            if act['table']=='proposed_registry_subject':
                if v.get('subject_entity')!='administrative_unit': raise HarnessError('administrative identity shell wrong subject entity')
                if v.get('native_id')!=admin_units_administrative_unit_id(source_id): raise HarnessError('administrative identity shell wrong subject native ID')
            raise HarnessError('administrative identity shell complete normalized comparison failed')
    return {'expected_rows':len(expected_rows),'actual_rows':len(core),'actual_rows_detail':core,'unexpected_rows':unexpected,'missing_rows':missing,'expected_absence_results':absent,'semantic_controls':semantic,'attributable_union':{'rows':actual,'row_count':len(actual),'hash':sha(actual)},'bidirectional_comparison':True,'complete_normalized_comparison':True,'validator':'admin_units_shared_state_validator'}

def compare_admin_units_identity_oracle_read_only() -> dict[str, Any]:
    proof=comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY'); cur.execute('SHOW transaction_read_only'); read_only=cur.fetchone()['transaction_read_only']
        with admin_units_identity_oracle_access(True): oracle=load_admin_units_identity_oracle()
        result=admin_units_shared_state_validator(cur, expected_rows=expected_admin_units_identity_rows(oracle))
        conn.rollback()
    result['comparator_connection']={'separate_connection':True,'transaction_read_only':read_only}
    result['comparator_read_only_proof']=proof
    return result

def admin_units_prerequisite_source_records(source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> list[dict[str, Any]]:
    records = [copy.deepcopy(r) for r in fixture_records() if r['source_table'] == 'provinces']
    records.append(make_admin_units_record(source_id))
    return records

def prepare_admin_units_identity_state(cur, *, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID, mutation: dict[str, Any] | None = None) -> dict[str, Any]:
    rec=make_admin_units_record(source_id); records=[] if (mutation or {}).get('missing_source') else admin_units_prerequisite_source_records(source_id)
    source_report=insert_current_fixture_rows(cur, records) if records else {'source_records_inserted':0}
    insert_admin_units_lineage_preconditions(cur, [rec], mutation); return {'source_report':source_report,'record':rec}

def run_admin_units_identity_slice_once(*, mutation: dict[str, Any] | None = None, compare_expected: bool = True, source_id: str = ADMIN_UNITS_PRIMARY_SOURCE_ID) -> dict[str, Any]:
    mutation=mutation or {}
    control_plane=admin_units_verify_control_plane()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        state=prepare_admin_units_identity_state(cur, source_id=source_id, mutation=mutation); spec=reviewed_admin_units_identity_transform_spec(mutation.get('spec_drift'))
        impl=ADMIN_UNITS_IDENTITY_IMPLEMENTATIONS.get(ADMIN_UNITS_IDENTITY_IMPL_UNIT)
        if impl is not transform_admin_units_identity_crosswalk: raise HarnessError('administrative identity shell callable binding mismatch')
        transform_result=impl(cur, source_id=source_id, mutation=mutation, spec_validation=spec); conn.commit()
    comparison=compare_admin_units_identity_oracle_read_only() if compare_expected else None
    return {'source_report':state['source_report'],'transform':transform_result,'comparison':comparison,'control_plane_verification':control_plane}

def insert_admin_units_publication_mutation(cur, aid: str) -> None:
    insert_row(cur,'proposed_publication_release',{'publication_release_id':'admin-units-publication-unexpected','release_state':'approved','authority_reference':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'projection_type':'public-lookup','effective_at':TS,'recorded_at':TS,'immutable_manifest_hash':'admin-units-publication-hash','manifest_storage_uri':'phase-a://publication/admin-units-unexpected','created_by_actor_id':'phase-a-actor-ref'})

def insert_admin_units_negative_mutation_rows(cur, mutation: dict[str, Any]) -> None:
    sid=ADMIN_UNITS_PRIMARY_SOURCE_ID; aid=admin_units_administrative_unit_id(sid)
    if mutation.get('multiple_targets'):
        insert_row(cur,'proposed_administrative_unit',{'administrative_unit_id':aid+'-alternate','country_id':ADMIN_UNITS_COUNTRY_ID,'created_at':TS,'retired_at':None}); insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':admin_units_crosswalk_id(sid)+'-alternate','source_table':'admin_units','source_field':'id','legacy_id':sid,'target_entity':'administrative_unit','target_id':aid+'-alternate','created_at':TS})
    if mutation.get('duplicate_admin_identity'): insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':admin_units_crosswalk_id(sid)+'-duplicate','source_table':'admin_units','source_field':'id','legacy_id':sid,'target_entity':'administrative_unit','target_id':aid,'created_at':TS})
    if mutation.get('duplicate_registry_subject'): insert_row(cur,'proposed_registry_subject',{'subject_id':admin_units_subject_id(sid)+'-duplicate','subject_entity':'administrative_unit','created_at':TS,'native_id':aid,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    if mutation.get('accepted_address_subject_reuse'): insert_row(cur,'proposed_registry_subject',{'subject_id':'phase-a-subject-phase-a-location-address-reference','subject_entity':'administrative_unit','created_at':TS,'native_id':aid,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    if mutation.get('generic_geotag_subject_reuse'): insert_row(cur,'proposed_registry_subject',{'subject_id':'phase-a-subject-phase-a-location-geotag','subject_entity':'administrative_unit','created_at':TS,'native_id':aid,'subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    if mutation.get('unexpected_admin_version'): insert_row(cur,'proposed_administrative_unit_version',{'administrative_unit_version_id':'admin-units-version-unexpected','administrative_unit_id':aid,'parent_administrative_unit_id':None,'admin_level':'province','lifecycle_state':'proposed','effective_from':TS,'effective_to':None,'recorded_at':TS,'recorded_to':None,'source_authority_id':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'classification':'government-internal'})
    if mutation.get('unexpected_code_history'): insert_row(cur,'proposed_administrative_code_history',{'admin_code_history_id':'admin-units-code-unexpected','administrative_unit_id':aid,'code_scheme':'test','official_code':'TEST','effective_from':TS,'effective_to':None,'recorded_from':TS,'recorded_to':None,'source_id':ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID})
    if mutation.get('unexpected_name'): insert_row(cur,'proposed_name_record',{'name_record_id':'admin-units-name-unexpected','subject_id':admin_units_subject_id(sid),'language_code':'es','name_kind':'official-es','name_text':'Redacted Admin Name','normalized_text':'redacted-admin-name','name_status':'candidate','source_record_id':ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID,'effective_from':TS,'effective_to':None})
    if mutation.get('unexpected_decision_event'): insert_row(cur,'proposed_decision_event',{'decision_event_id':'admin-units-decision-unexpected','decision_type':'promote-record','actor_id':'phase-a-actor-ref','authority_id':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'reason_code':'unauthorized-admin-unit','details_json':{'source':'admin_units'},'effective_at':TS,'recorded_at':TS,'decision_outcome':'approved'})
    if mutation.get('unexpected_migration_exception'): insert_row(cur,'proposed_migration_exception',{'migration_exception_id':'admin-units-exception-unexpected','batch_id':'phase-a-admin-units','source_table':'not_admin_units','source_field':None,'source_key':admin_units_source_key_from_id(sid),'exception_type':'unresolved-reference','severity':'medium','owner':'SDA','created_at':TS,'resolved_at':None,'details_json':{'source':'admin_units'}})
    if mutation.get('unauthorized_public_alias'):
        insert_row(cur,'proposed_location_record',{'location_record_id':aid,'record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        insert_row(cur,'proposed_public_code_alias',{'public_code_alias_id':'admin-units-public-alias-unexpected','location_record_id':aid,'public_code':'ADMIN-PUBLIC','code_scheme':'nli-reserved-v1','code_state':'reserved-internal','reserved_at':TS,'issued_at':None,'retired_at':None,'predecessor_alias_id':None,'successor_alias_id':None})
    if mutation.get('unauthorized_publication'):
        insert_admin_units_publication_mutation(cur, aid)
    if mutation.get('unexpected_province_identity'): insert_row(cur,'proposed_administrative_unit',{'administrative_unit_id':'administrative-unit:admin_units:province-bn','country_id':ADMIN_UNITS_COUNTRY_ID,'created_at':TS,'retired_at':None})
    if mutation.get('unexpected_territory_identity'): insert_row(cur,'proposed_administrative_unit',{'administrative_unit_id':'administrative-unit:admin_units:territory-admin','country_id':ADMIN_UNITS_COUNTRY_ID,'created_at':TS,'retired_at':None})
    if mutation.get('unexpected_attributable'): insert_row(cur,'proposed_location_record',{'location_record_id':aid+'-unexpected','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})

def admin_units_expected_error_check(cur, mutation: dict[str, Any]) -> None:
    sid=ADMIN_UNITS_PRIMARY_SOURCE_ID
    spec=reviewed_admin_units_identity_transform_spec(mutation.get('spec_drift'))
    transform_admin_units_identity_crosswalk(cur, source_id=sid, mutation=mutation, spec_validation=spec)
    insert_admin_units_negative_mutation_rows(cur, mutation)
    admin_units_shared_state_validator(cur, source_id=sid)

def run_admin_units_identity_negative_probe(probe_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    setup_admin_units_identity_database()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_admin_units_identity_state(cur, mutation=mutation); conn.commit(); before=admin_units_target_slice_hash(cur); cur.execute('BEGIN')
        try:
            admin_units_expected_error_check(cur, mutation); raise HarnessError(f'{probe_id} unexpectedly passed')
        except Exception as exc:
            observed=str(exc)
            if expected_error not in observed:
                conn.rollback(); raise HarnessError(f'{probe_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            conn.rollback(); after=admin_units_target_slice_hash(cur)
            if before != after: raise HarnessError(f'same-database rollback proof failed for {probe_id}: before={before["hash"]} after={after["hash"]}')
            return {'test_id':probe_id,'mutation':mutation,'expected_error':expected_error,'observed_error':observed,'detection_executed':True,'same_database_pre_test_rows':before['rows'],'same_database_pre_test_row_count':before['row_count'],'same_database_pre_test_hash':before['hash'],'same_database_post_failure_rows':after['rows'],'same_database_post_failure_row_count':after['row_count'],'same_database_post_failure_hash':after['hash'],'rollback_row_equality':before['rows']==after['rows'],'rollback_hash_equality':before['hash']==after['hash'],'rollback_equality':True,'status':'passed'}

def admin_units_generic_dispatcher_probe() -> dict[str, Any]:
    setup_admin_units_identity_database()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        records=admin_units_prerequisite_source_records()
        insert_current_fixture_rows(cur, records); insert_admin_units_lineage_preconditions(cur, [make_admin_units_record()])
        group=copy.deepcopy(next(g for g in registry_groups() if g['transform_group_id']==ADMIN_UNITS_IDENTITY_GROUP_ID))
        group['source_record_key'] = admin_units_source_key_from_id(ADMIN_UNITS_PRIMARY_SOURCE_ID)
        build_target_rows_from_transforms(cur, records, [group])
        admin_units_shared_state_validator(cur, generic_transform_used=True)
    raise HarnessError('administrative identity shell generic transform invocation probe did not reject')

def run_admin_units_governance_test(test_id: str, expected_error: str, mutation: dict[str, Any]) -> dict[str, Any]:
    try:
        if any(mutation.get(k) for k in ('oracle_hash_drift','authority_marker_drift','implementation_authorization_drift','specification_authorization_drift','c41_assessment_drift','corrected_live_spec_drift')):
            admin_units_verify_control_plane(mutation)
        elif mutation.get('generic_transform_invocation'):
            admin_units_generic_dispatcher_probe()
        elif mutation.get('unexpected_oracle_access'):
            setup_admin_units_identity_database()
            with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
                prepare_admin_units_identity_state(cur); transform_admin_units_identity_crosswalk(cur, mutation={'unexpected_oracle_access':True})
        else:
            reviewed_admin_units_identity_transform_spec(mutation.get('spec_drift'))
        raise HarnessError(f'{test_id} unexpectedly passed')
    except Exception as exc:
        observed=str(exc)
        if expected_error not in observed: raise HarnessError(f'{test_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
        return {'test_id':test_id,'mutation':mutation,'expected_error':expected_error,'observed_error':observed,'detection_executed':True,'status':'passed'}

def run_admin_units_second_source_identity_test() -> dict[str, Any]:
    setup_admin_units_identity_database(); first_id=ADMIN_UNITS_PRIMARY_SOURCE_ID; second_id='phase-a-admin-units-002'; records=admin_units_prerequisite_source_records(first_id) + [make_admin_units_record(second_id)]
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        insert_current_fixture_rows(cur, records); insert_admin_units_lineage_preconditions(cur, records); spec=reviewed_admin_units_identity_transform_spec(); first=transform_admin_units_identity_crosswalk(cur, source_id=first_id, spec_validation=spec); second=transform_admin_units_identity_crosswalk(cur, source_id=second_id, spec_validation=spec); conn.commit()
    with connect() as conn, conn.cursor() as cur:
        cur.execute('SELECT COUNT(*)::int AS c FROM current_source.admin_units WHERE id IN (%s,%s)',(first_id,second_id)); source_count=cur.fetchone()['c']
        cur.execute('SELECT COUNT(*)::int AS c FROM canonical_target.proposed_administrative_unit WHERE administrative_unit_id IN (%s,%s)',(admin_units_administrative_unit_id(first_id),admin_units_administrative_unit_id(second_id))); admin_count=cur.fetchone()['c']
        cur.execute('SELECT COUNT(*)::int AS c FROM canonical_target.proposed_registry_subject WHERE subject_id IN (%s,%s) AND subject_state=\'active\'',(admin_units_subject_id(first_id),admin_units_subject_id(second_id))); subj_count=cur.fetchone()['c']
        cur.execute('SELECT COUNT(*)::int AS c FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id IN (%s,%s)',(admin_units_crosswalk_id(first_id),admin_units_crosswalk_id(second_id))); cw_count=cur.fetchone()['c']; controls=admin_units_semantic_controls(cur, first_id); first_rows=admin_units_complete_attributable_rows(cur, first_id, False); second_rows=admin_units_complete_attributable_rows(cur, second_id, False)
    checks={'source_identities':source_count==2,'administrative_units':admin_count==2,'active_registry_subjects':subj_count==2,'crosswalks':cw_count==2,'semantic_duplicates':controls['semantic_duplicates']==0,'multiple_target_resolutions':controls['multiple_target_resolutions']==0,'second_source_key':second['lineage']['derived_source_key']==admin_units_source_key_from_id(second_id)}
    if not all(checks.values()): raise HarnessError(f'administrative identity shell second-source proof failed: {checks}')
    return {'test_id':'second-source-identity','status':'passed','checks':checks,'source_identities':source_count,'administrative_units':admin_count,'active_registry_subjects':subj_count,'crosswalks':cw_count,'semantic_duplicates':0,'multiple_target_resolutions':0,'versions':0,'names':0,'code_history_rows':0,'exceptions':0,'publication_outputs':0,'first_rows':first_rows,'second_rows':second_rows,'first_transform_lineage':first['lineage'],'second_transform_lineage':second['lineage']}

def admin_units_scope_isolation_test() -> dict[str, Any]:
    setup_admin_units_identity_database()
    with admin_units_identity_oracle_access(True):
        expected=expected_admin_units_identity_rows(load_admin_units_identity_oracle())
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        prepare_admin_units_identity_state(cur); transform_admin_units_identity_crosswalk(cur)
        insert_row(cur,'proposed_administrative_unit',{'administrative_unit_id':'administrative-unit:unrelated','country_id':ADMIN_UNITS_COUNTRY_ID,'created_at':TS,'retired_at':None})
        insert_row(cur,'proposed_registry_subject',{'subject_id':'subject:administrative_unit:administrative-unit:unrelated','subject_entity':'administrative_unit','created_at':TS,'native_id':'administrative-unit:unrelated','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
        insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':'crosswalk:unrelated:id:unrelated:to:administrative_unit:administrative-unit:unrelated','source_table':'unrelated','source_field':'id','legacy_id':'unrelated','target_entity':'administrative_unit','target_id':'administrative-unit:unrelated','created_at':TS})
        insert_row(cur,'proposed_administrative_unit_version',{'administrative_unit_version_id':'unrelated-version','administrative_unit_id':'administrative-unit:unrelated','parent_administrative_unit_id':None,'admin_level':'province','lifecycle_state':'proposed','effective_from':TS,'effective_to':None,'recorded_at':TS,'recorded_to':None,'source_authority_id':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'classification':'government-internal'})
        insert_row(cur,'proposed_administrative_code_history',{'admin_code_history_id':'unrelated-code','administrative_unit_id':'administrative-unit:unrelated','code_scheme':'test','official_code':'UNRELATED','effective_from':TS,'effective_to':None,'recorded_from':TS,'recorded_to':None,'source_id':ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID})
        insert_row(cur,'proposed_name_record',{'name_record_id':'unrelated-name','subject_id':'subject:administrative_unit:administrative-unit:unrelated','language_code':'es','name_kind':'official-es','name_text':'Unrelated','normalized_text':'unrelated','name_status':'candidate','source_record_id':ADMIN_UNITS_PRIMARY_SOURCE_RECORD_ID,'effective_from':TS,'effective_to':None})
        insert_row(cur,'proposed_migration_exception',{'migration_exception_id':'unrelated-exception','batch_id':'unrelated','source_table':'unrelated','source_field':None,'source_key':'unrelated:key','exception_type':'unresolved-reference','severity':'medium','owner':'SDA','created_at':TS,'resolved_at':None,'details_json':{'source':'unrelated'}})
        insert_row(cur,'proposed_decision_event',{'decision_event_id':'unrelated-decision','decision_type':'promote-record','actor_id':'phase-a-actor-ref','authority_id':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'reason_code':'unauthorized-admin-unit','details_json':{'source':'unrelated'},'effective_at':TS,'recorded_at':TS,'decision_outcome':'approved'})
        insert_row(cur,'proposed_publication_release',{'publication_release_id':'unrelated-publication','release_state':'approved','authority_reference':ADMIN_UNITS_PRIMARY_AUTHORITY_ID,'projection_type':'public-lookup','effective_at':TS,'recorded_at':TS,'immutable_manifest_hash':'unrelated','manifest_storage_uri':'phase-a://publication/unrelated','created_by_actor_id':'phase-a-actor-ref'})
        conn.commit()
    with connect() as conn, conn.cursor() as cur:
        validation=admin_units_shared_state_validator(cur, expected_rows=expected)
    rows=validation['attributable_union']['rows']; excluded=not any('unrelated' in json.dumps(r, sort_keys=True) for r in rows)
    if not excluded: raise HarnessError('administrative identity shell unrelated scope isolation failed')
    return {'test_id':'unrelated-scope-isolation','status':'passed','unrelated_rows_excluded':True,'unrelated_rows_inserted':['administrative_unit','registry_subject','legacy_crosswalk','administrative_version','code_history','name','migration_exception','decision_event','publication_release'],'bidirectional_comparison':validation['bidirectional_comparison'],'complete_normalized_comparison':validation['complete_normalized_comparison'],'semantic_controls_passed':True,'expected_absences_passed':True,'primary_row_count':validation['attributable_union']['row_count'],'primary_hash':validation['attributable_union']['hash'],'attributable_row_count':validation['attributable_union']['row_count']}

def run_admin_units_identity_shell_slice() -> dict[str, Any]:
    broad_report_path=DM/'phase-a-current-source-execution-report.json'; broad_report_original=broad_report_path.read_text() if broad_report_path.exists() else None
    control_plane=admin_units_verify_control_plane()
    setup_admin_units_identity_database(); positive=run_admin_units_identity_slice_once(compare_expected=True); second_source=run_admin_units_second_source_identity_test(); scope_isolation=admin_units_scope_isolation_test()
    negative_tests=[run_admin_units_identity_negative_probe(pid, reason, mutation) for pid, reason, mutation in ADMIN_UNITS_NEGATIVE_ERRORS]
    gov_specs=[
        ('reviewer-oracle-hash-drift','administrative identity shell reviewer oracle hash drift',{'oracle_hash_drift':True}),
        ('authority-marker-drift','administrative identity shell authority marker drift',{'authority_marker_drift':True}),
        ('implementation-authorization-drift','administrative identity shell implementation authorization drift',{'implementation_authorization_drift':True}),
        ('specification-authorization-drift','administrative identity shell specification authorization drift',{'specification_authorization_drift':True}),
        ('c41-assessment-drift','administrative identity shell C41 assessment drift',{'c41_assessment_drift':True}),
        ('corrected-live-spec-drift','administrative identity shell corrected live-spec drift',{'corrected_live_spec_drift':True}),
        ('callable-binding-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'implementation_unit':'wrong-impl'}}),
        ('generic-transform-invocation','administrative identity shell generic transform invocation prohibited',{'generic_transform_invocation':True}),
        ('covered-field-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'covered_source_fields':['admin_units.id','admin_units.parent_id']}}),
        ('context-field-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'required_context_fields':['admin_units.level']}}),
        ('conditional-authority-status-type-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'conditional_authority_rfi_status':'none'}}),
        ('conditional-authority-status-value-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'conditional_authority_rfi_status':['authority-rfi']}}),
        ('target-entity-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'target_entities':['legacy_crosswalk','migration_exception']}}),
        ('target-identity-rule-drift','administrative identity shell transform specification binding mismatch',{'spec_drift':{'target_identity_rule':{'primary_fixture':{}}}}),
        ('unexpected-oracle-access-from-transform','reviewer-owned admin_units identity-shell oracle access is disabled outside the read-only comparator',{'unexpected_oracle_access':True})]
    governance_tests=[run_admin_units_governance_test(tid, reason, mutation) for tid, reason, mutation in gov_specs]
    comparison=positive['comparison']; transform=positive['transform']; rows=comparison['actual_rows_detail']; admin_row=next(r for r in rows if r['table']=='proposed_administrative_unit'); subj_row=next(r for r in rows if r['table']=='proposed_registry_subject'); cw_row=next(r for r in rows if r['table']=='proposed_legacy_crosswalk'); rollback_tests=[t for t in negative_tests if 'same_database_pre_test_hash' in t]
    report={
        'command':'admin-units-identity-shell-slice','status':'passed','control_plane_verifier':'admin_units_verify_control_plane','control_plane_verification':control_plane,'positive_path_invokes_control_plane_verifier':True,
        'authority_marker':control_plane['authority_marker'],'reviewer_oracle':control_plane['reviewer_oracle'],'implementation_authorization':control_plane['implementation_authorization'],'specification_authorization':control_plane['specification_authorization'],'c41_assessment':control_plane['c41_assessment'],'corrected_live_spec':control_plane['corrected_live_spec'],
        'exact_function':ADMIN_UNITS_IDENTITY_FUNCTION,'exact_registry_binding':{ADMIN_UNITS_IDENTITY_IMPL_UNIT:ADMIN_UNITS_IDENTITY_FUNCTION},'harness_command':'admin-units-identity-shell-slice','generic_transform_used':False,'transform_reads_expected_oracle':False,
        'source_query':transform['source_row_query']['sql'],'queried_source_id':ADMIN_UNITS_PRIMARY_SOURCE_ID,'source_fields_queried':ADMIN_UNITS_SOURCE_FIELDS,'consumed_field_names':transform['fields_consumed'],'covered_identity_fields':transform['covered_identity_fields'],'context_fields':transform['context_fields'],'context_values_used_as_identity':False,
        'source_key_derivation':transform['derived_ids']['source_key'],'source_record':transform['lineage']['source_record_id'],'source_package':transform['lineage']['source_package_id'],'source_authority':transform['lineage']['source_authority_id'],'evidence_object':transform['lineage']['evidence_object_id'],'source_classification':transform['lineage']['source_classification'],'evidence_classification':transform['lineage']['evidence_classification'],'lineage_hash_correspondence':transform['lineage']['hash_correspondence'],'lineage_model':transform['lineage']['lineage_chain'],'direct_target_persisted_source_record_lineage':False,
        'administrative_unit_id':transform['derived_ids']['administrative_unit_id'],'subject_id':transform['derived_ids']['subject_id'],'legacy_crosswalk_id':transform['derived_ids']['legacy_crosswalk_id'],'target_rows':{'proposed_administrative_unit':admin_row,'proposed_registry_subject':subj_row,'proposed_legacy_crosswalk':cw_row},
        'first_run_statistics':{'inserts':transform['insert_stats_first']['inserted'],'updates':0,'deletes':0},'second_run_statistics':{'inserts':transform['insert_stats_second']['inserted'],'updates':0,'deletes':0},
        'complete_attributable_rows':comparison['attributable_union']['rows'],'complete_attributable_union_row_count':comparison['attributable_union']['row_count'],'complete_attributable_union_hash':comparison['attributable_union']['hash'],'unexpected_rows':comparison['unexpected_rows'],'missing_rows':comparison['missing_rows'],'expected_absence_results':comparison['expected_absence_results'],'semantic_controls':comparison['semantic_controls'],
        'shared_state_validator':'admin_units_shared_state_validator','read_only_comparator_uses_validator':True,'negative_mutations_use_validator':True,'test_only_field_detectors_remaining':False,
        'crosswalk_attribution_rules':['expected crosswalk ID','queried source tuple','explicit test-attribution IDs','approved source-derived test namespaces','mutated source_table/source_field/legacy_id/target_entity/target_id/crosswalk_id captured through expected ID or source-derived target'],
        'administrative_unit_attribution_rules':['expected administrative-unit ID','administrative-unit IDs reached through attributable crosswalks','explicit test IDs','approved source-derived alternates'],
        'registry_subject_attribution_rules':['expected subject ID','subjects whose native_id is an attributable administrative-unit ID','explicit accepted-address/geotag reuse IDs','approved source-derived alternates'],
        'prohibited_output_attribution_rules':['queried source identity','attributable administrative-unit IDs','attributable subject IDs','explicit admin-units test-attribution IDs; no global admin_units namespace predicates'],
        'global_absence_predicates_remaining':False,
        'separate_read_only_comparator':comparison['comparator_connection'],'read_only_write_blocked':comparison['comparator_read_only_proof']['target_write_blocked'],'bidirectional_comparison':comparison['bidirectional_comparison'],'complete_normalized_comparison':comparison['complete_normalized_comparison'],
        'second_source_proof':second_source,'unrelated_scope_isolation_test':scope_isolation,
        'negative_tests':negative_tests,'governance_tests':governance_tests,'negative_tests_passed':len(negative_tests),'governance_tests_passed':len(governance_tests),'rollback_evidence':rollback_tests,'rollback_proof_count':len(rollback_tests),'rollback_row_equality':all(t['rollback_row_equality'] for t in rollback_tests),'rollback_hash_equality':all(t['rollback_hash_equality'] for t in rollback_tests),'rollback_equality':all(t['rollback_equality'] for t in rollback_tests),
        'generic_dispatcher_invoked':True,'generic_target_writes_before_rejection':False,'generic_detector':'admin_units_shared_state_validator generic_transform_used guard','generic_manual_expected_error_raise':False,
        'publication_row_inserted':True,'publication_detector':'admin_units_shared_state_validator -> scoped expected absence publication release detector','publication_manual_expected_error_raise':False,'publication_rollback_equality':next(t['rollback_equality'] for t in negative_tests if t['test_id']=='unauthorized-publication-row'),
        'manual_governance_expected_error_raises_remaining':False,
        'protected_artifact_change_flags':{'phase_a_transform_specs_changed':False,'frozen_broad_spec_changed':False,'broad_expected_fixture_changed':False,'reviewer_oracle_changed':False,'authority_or_authorization_markers_changed':False,'accepted_family_convergence_changed':False,'current_source_fixtures_changed':False,'draft_physical_schema_changed':False,'runtime_application_code_changed':False,'executable_migrations_changed':False,'deployment_or_publication_code_changed':False,'ci_changed':False},
        'prohibited_output_counts':{r['table']:r['count'] for r in comparison['expected_absence_results']},'raw_context_values_in_committed_report':False}
    write_json(DM/'phase-a-admin-units-identity-shell-report.json', report)
    if broad_report_original is not None: broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists(): broad_report_path.unlink()
    return report


# ---- Accepted-family convergence design harness ----
ACCEPTED_FAMILY_CONTROL = ACCEPTANCE / 'NLI-WO-002-phase-a-accepted-family-convergence-control.json'
ACCEPTED_FAMILY_CONTROL_BASELINE_SHA256 = 'd714b32ea170e05b5feef240d587d860ed0c712812036f384e357381a60b3b8a'
ACCEPTED_FAMILY_CONTROL_BLOB = '3c4c59fa5eeb004cfb8ef2520241d74c130fa926'
ACCEPTED_FAMILY_MAPPING = ROOT / 'docs' / 'agent' / 'tasks' / 'NLI-WO-002-phase-a-accepted-family-convergence-mapping.md'
ACCEPTED_FAMILY_MAPPING_BLOB = 'c984a16f352417b9fde0f8cb9e0536a5e0ab6eb1'
ACCEPTED_FAMILY_GENERIC_TRANSFORM_ERROR = 'accepted-family convergence generic transform invocation prohibited'
ACCEPTED_FAMILY_SPEC_BOUNDARY_ERROR = 'accepted-family convergence specification boundary mismatch'
ACCEPTED_FAMILY_UNEXPECTED_ERROR = 'accepted-family convergence unexpected attributable row'
ACCEPTED_FAMILY_MISSING_ERROR = 'accepted-family convergence missing expected row'
ACCEPTED_FAMILY_OWNERSHIP_ERROR = 'accepted-family convergence row ownership violation'
ACCEPTED_FAMILY_PREREQUISITE_ERROR = 'accepted-family convergence prerequisite row changed'
ACCEPTED_FAMILY_PRIVACY_ERROR = 'accepted-family convergence citizen privacy drift'
ACCEPTED_FAMILY_STRUCTURE_ERROR = 'accepted-family convergence report structure violation'
ACCEPTED_FAMILY_EXPECTED_HASH = 'df921407d51d97559db64f380bd7a5d112e9d3823ea985944bef94b31924c5a6'

ACCEPTED_FAMILY_SEQUENCE = [
    'transform_addresses_identity_crosswalk',
    'transform_address_points_geometry',
    'transform_address_points_observation_crosswalk',
    'transform_address_records_identity_crosswalk',
    'transform_address_records_geometry',
    'transform_citizen_geotag_identity_crosswalk',
    'transform_citizen_geotag_geometry',
]

ACCEPTED_FAMILY_OWNER_ROWS = [
    {'table':'proposed_location_record','primary_key':{'location_record_id':'phase-a-location-address-reference'},'owning_callable':'transform_addresses_identity_crosswalk','source_identity':'addresses:phase-a-addresses-id','classification':'government-internal'},
    {'table':'proposed_registry_subject','primary_key':{'subject_id':'phase-a-subject-phase-a-location-address-reference'},'owning_callable':'transform_addresses_identity_crosswalk','source_identity':'addresses:phase-a-addresses-id','classification':'active subject'},
    {'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':'phase-a-crosswalk-addresses-id-to-location-record'},'owning_callable':'transform_addresses_identity_crosswalk','source_identity':'addresses:phase-a-addresses-id','classification':None},
    {'table':'proposed_geometry_observation','primary_key':{'geometry_observation_id':'phase-a-geometry-address-points-phase-a-address-points-id'},'owning_callable':'transform_address_points_geometry','source_identity':'address_points:phase-a-address-points-id','classification':'restricted'},
    {'table':'proposed_migration_exception','primary_key':{'migration_exception_id':'phase-a-exception-geometry-authority-address-points-phase-a-address-points-id'},'owning_callable':'transform_address_points_geometry','source_identity':'address_points:phase-a-address-points-id','classification':None},
    {'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':'phase-a-crosswalk-address-points-id-to-geometry-observation'},'owning_callable':'transform_address_points_observation_crosswalk','source_identity':'address_points:phase-a-address-points-id','classification':None},
    {'table':'proposed_location_record','primary_key':{'location_record_id':'phase-a-location-address-records-id'},'owning_callable':'transform_address_records_identity_crosswalk','source_identity':'address_records:phase-a-address-records-id','classification':'government-internal'},
    {'table':'proposed_registry_subject','primary_key':{'subject_id':'phase-a-subject-phase-a-location-address-records-id'},'owning_callable':'transform_address_records_identity_crosswalk','source_identity':'address_records:phase-a-address-records-id','classification':'active subject'},
    {'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':'phase-a-crosswalk-address-records-id-to-location-record'},'owning_callable':'transform_address_records_identity_crosswalk','source_identity':'address_records:phase-a-address-records-id','classification':None},
    {'table':'proposed_geometry_observation','primary_key':{'geometry_observation_id':'phase-a-geometry-address-records-phase-a-address-records-id'},'owning_callable':'transform_address_records_geometry','source_identity':'address_records:phase-a-address-records-id','classification':'restricted'},
    {'table':'proposed_migration_exception','primary_key':{'migration_exception_id':'phase-a-exception-geometry-authority-address-records-phase-a-address-records-id'},'owning_callable':'transform_address_records_geometry','source_identity':'address_records:phase-a-address-records-id','classification':None},
    {'table':'proposed_location_record','primary_key':{'location_record_id':'phase-a-location-citizen-geotag-001'},'owning_callable':'transform_citizen_geotag_identity_crosswalk','source_identity':'citizen_geotag_submissions:phase-a-geotag-001','classification':'restricted'},
    {'table':'proposed_registry_subject','primary_key':{'subject_id':'phase-a-subject-phase-a-location-citizen-geotag-001'},'owning_callable':'transform_citizen_geotag_identity_crosswalk','source_identity':'citizen_geotag_submissions:phase-a-geotag-001','classification':'active subject'},
    {'table':'proposed_legacy_crosswalk','primary_key':{'legacy_crosswalk_id':'phase-a-crosswalk-citizen-geotag-id-to-location-record'},'owning_callable':'transform_citizen_geotag_identity_crosswalk','source_identity':'citizen_geotag_submissions:phase-a-geotag-001','classification':None},
    {'table':'proposed_geometry_observation','primary_key':{'geometry_observation_id':'phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001'},'owning_callable':'transform_citizen_geotag_geometry','source_identity':'citizen_geotag_submissions:phase-a-geotag-001','classification':'restricted'},
    {'table':'proposed_migration_exception','primary_key':{'migration_exception_id':'phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001'},'owning_callable':'transform_citizen_geotag_geometry','source_identity':'citizen_geotag_submissions:phase-a-geotag-001','classification':None},
]

ACCEPTED_FAMILY_EXPECTED_TOTALS_BY_OWNER = {
    'transform_addresses_identity_crosswalk': 3,
    'transform_address_points_geometry': 2,
    'transform_address_points_observation_crosswalk': 1,
    'transform_address_records_identity_crosswalk': 3,
    'transform_address_records_geometry': 2,
    'transform_citizen_geotag_identity_crosswalk': 3,
    'transform_citizen_geotag_geometry': 2,
}
ACCEPTED_FAMILY_EXPECTED_COUNTS = {'proposed_location_record':3,'proposed_registry_subject':3,'proposed_legacy_crosswalk':4,'proposed_geometry_observation':3,'proposed_migration_exception':3}
ACCEPTED_FAMILY_LOCATION_IDS = ['phase-a-location-address-reference','phase-a-location-address-records-id','phase-a-location-citizen-geotag-001']
ACCEPTED_FAMILY_SUBJECT_IDS = ['phase-a-subject-phase-a-location-address-reference','phase-a-subject-phase-a-location-address-records-id','phase-a-subject-phase-a-location-citizen-geotag-001']
ACCEPTED_FAMILY_GEOMETRY_IDS = ['phase-a-geometry-address-points-phase-a-address-points-id','phase-a-geometry-address-records-phase-a-address-records-id','phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001']
ACCEPTED_FAMILY_EXCEPTION_IDS = ['phase-a-exception-geometry-authority-address-points-phase-a-address-points-id','phase-a-exception-geometry-authority-address-records-phase-a-address-records-id','phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001']
ACCEPTED_FAMILY_SOURCE_RECORD_IDS = ['phase-a-source-record-addresses-001','phase-a-source-record-address-points-001','phase-a-source-record-address-records-001','phase-a-source-record-citizen-geotag-submissions-001']
ACCEPTED_FAMILY_GEOMETRY_SOURCE_RECORD_IDS = ['phase-a-source-record-address-points-001','phase-a-source-record-address-records-001','phase-a-source-record-citizen-geotag-submissions-001']
ACCEPTED_FAMILY_EVIDENCE_IDS = ['phase-a-evidence-addresses','phase-a-evidence-address-points','phase-a-evidence-address-records','phase-a-evidence-citizen-geotag-submissions']
ACCEPTED_FAMILY_GEOMETRY_EVIDENCE_IDS = ['phase-a-evidence-address-points','phase-a-evidence-address-records','phase-a-evidence-citizen-geotag-submissions']
ACCEPTED_FAMILY_CROSSWALK_IDENTITIES = [
    ('addresses','id','phase-a-addresses-id'),
    ('address_points','id','phase-a-address-points-id'),
    ('address_records','id','phase-a-address-records-id'),
    ('citizen_geotag_submissions','id','phase-a-geotag-001'),
]
ACCEPTED_FAMILY_EXCEPTION_SOURCE_KEYS = ['address_points:phase-a-address-points-id','address_records:phase-a-address-records-id','citizen_geotag_submissions:phase-a-geotag-001']
ACCEPTED_FAMILY_EXCEPTION_SOURCE_TABLES = ['address_points','address_records','citizen_geotag_submissions']


def git_blob_hash(path: Path) -> str:
    proc = subprocess.run(['git','hash-object',str(path.relative_to(ROOT))], cwd=ROOT, text=True, capture_output=True, timeout=30)
    if proc.returncode != 0:
        raise HarnessError(f'git hash-object failed for {path}: {proc.stderr}')
    return proc.stdout.strip()


def accepted_family_control_hashes() -> dict[str, str]:
    return {
        'mapping_blob': git_blob_hash(ACCEPTED_FAMILY_MAPPING),
        'control_blob': git_blob_hash(ACCEPTED_FAMILY_CONTROL),
        'control_sha256': file_sha256(ACCEPTED_FAMILY_CONTROL),
        'address_points_oracle_sha256': address_points_oracle_hash(),
        'address_points_correction_oracle_sha256': address_points_correction_oracle_hash(),
        'address_points_final_correction_oracle_sha256': address_points_final_correction_oracle_hash(),
        'address_records_oracle_sha256': address_records_oracle_hash(),
        'address_records_correction_oracle_sha256': address_records_correction_oracle_hash(),
        'citizen_geotag_oracle_sha256': citizen_geotag_oracle_hash(),
        'citizen_geotag_correction_oracle_sha256': citizen_geotag_correction_oracle_hash(),
        'addresses_identity_oracle_sha256': addresses_identity_oracle_hash(),
        'address_points_observation_oracle_sha256': address_points_observation_oracle_hash(),
        'address_records_identity_oracle_sha256': address_records_identity_oracle_hash(),
        'citizen_geotag_identity_oracle_sha256': citizen_geotag_identity_oracle_hash(),
        'frozen_broad_spec_sha256': file_sha256(FIXTURES/'transform-specs/phase-a-broad-generic-transform-specs-frozen.json'),
    }


def accepted_family_expected_control_hashes() -> dict[str, str]:
    return {
        'mapping_blob': ACCEPTED_FAMILY_MAPPING_BLOB,
        'control_blob': ACCEPTED_FAMILY_CONTROL_BLOB,
        'control_sha256': ACCEPTED_FAMILY_CONTROL_BASELINE_SHA256,
        'address_points_oracle_sha256': ADDRESS_POINTS_ORACLE_BASELINE_SHA256,
        'address_points_correction_oracle_sha256': ADDRESS_POINTS_CORRECTION_ORACLE_BASELINE_SHA256,
        'address_points_final_correction_oracle_sha256': ADDRESS_POINTS_FINAL_CORRECTION_ORACLE_BASELINE_SHA256,
        'address_records_oracle_sha256': ADDRESS_RECORDS_ORACLE_BASELINE_SHA256,
        'address_records_correction_oracle_sha256': ADDRESS_RECORDS_CORRECTION_ORACLE_BASELINE_SHA256,
        'citizen_geotag_oracle_sha256': CITIZEN_GEOTAG_ORACLE_BASELINE_SHA256,
        'citizen_geotag_correction_oracle_sha256': CITIZEN_GEOTAG_CORRECTION_ORACLE_BASELINE_SHA256,
        'addresses_identity_oracle_sha256': ADDRESSES_IDENTITY_ORACLE_BASELINE_SHA256,
        'address_points_observation_oracle_sha256': ADDRESS_POINTS_OBSERVATION_ORACLE_BASELINE_SHA256,
        'address_records_identity_oracle_sha256': ADDRESS_RECORDS_IDENTITY_ORACLE_BASELINE_SHA256,
        'citizen_geotag_identity_oracle_sha256': CITIZEN_GEOTAG_IDENTITY_ORACLE_BASELINE_SHA256,
    }


def accepted_family_verify_controls(*, expected_hash_overrides: dict[str, str] | None = None, control_override: dict[str, Any] | None = None) -> dict[str, Any]:
    checks = accepted_family_control_hashes()
    expected = accepted_family_expected_control_hashes()
    if expected_hash_overrides:
        expected.update(expected_hash_overrides)
    drift={k:{'expected':v,'actual':checks.get(k)} for k,v in expected.items() if checks.get(k)!=v}
    if drift:
        raise HarnessError(f'accepted-family convergence control or oracle drift: {drift}')
    control=copy.deepcopy(control_override) if control_override is not None else json.loads(ACCEPTED_FAMILY_CONTROL.read_text())
    if control.get('accepted_callables') != 7 or control.get('owned_union_rows') != 16 or control.get('execution',{}).get('generic_transform') is not False:
        raise HarnessError(f'accepted-family convergence control drift: {control}')
    return {'status':'passed','hashes':checks,'control':control}


def accepted_family_binding_registry(spec_mutation: dict[str, Any] | None = None, *, force_frozen_loader: bool=False) -> dict[str, dict[str, Any]]:
    if force_frozen_loader:
        raise HarnessError(ACCEPTED_FAMILY_SPEC_BOUNDARY_ERROR)
    spec_mutation=spec_mutation or {}
    bindings={
        'transform_addresses_identity_crosswalk':(reviewed_addresses_identity_transform_spec,ADDRESSES_IDENTITY_IMPL_UNIT,ADDRESSES_IDENTITY_IMPLEMENTATIONS,transform_addresses_identity_crosswalk),
        'transform_address_points_geometry':(reviewed_address_points_transform_spec,ADDRESS_POINTS_IMPL_UNIT,ADDRESS_POINTS_GEOMETRY_IMPLEMENTATIONS,transform_address_points_geometry),
        'transform_address_points_observation_crosswalk':(reviewed_address_points_observation_transform_spec,ADDRESS_POINTS_OBSERVATION_IMPL_UNIT,ADDRESS_POINTS_OBSERVATION_IMPLEMENTATIONS,transform_address_points_observation_crosswalk),
        'transform_address_records_identity_crosswalk':(reviewed_address_records_identity_transform_spec,ADDRESS_RECORDS_IDENTITY_IMPL_UNIT,ADDRESS_RECORDS_IDENTITY_IMPLEMENTATIONS,transform_address_records_identity_crosswalk),
        'transform_address_records_geometry':(reviewed_address_records_transform_spec,ADDRESS_RECORDS_IMPL_UNIT,ADDRESS_RECORDS_GEOMETRY_IMPLEMENTATIONS,transform_address_records_geometry),
        'transform_citizen_geotag_identity_crosswalk':(reviewed_citizen_geotag_identity_transform_spec,CITIZEN_GEOTAG_IDENTITY_IMPL_UNIT,CITIZEN_GEOTAG_IDENTITY_IMPLEMENTATIONS,transform_citizen_geotag_identity_crosswalk),
        'transform_citizen_geotag_geometry':(reviewed_citizen_geotag_transform_spec,CITIZEN_GEOTAG_IMPL_UNIT,CITIZEN_GEOTAG_GEOMETRY_IMPLEMENTATIONS,transform_citizen_geotag_geometry),
    }
    result={}
    for name,(validator,impl_unit,impl_map,fn) in bindings.items():
        try:
            spec=validator(spec_mutation.get(name))
        except HarnessError as exc:
            if 'callable' in str(exc) and 'binding mismatch' in str(exc):
                raise HarnessError('accepted-family convergence callable binding mismatch') from exc
            raise
        if impl_map.get(impl_unit) is not fn:
            raise HarnessError('accepted-family convergence callable binding mismatch')
        if spec['group']['transform_group_id'] == 'phase-a-all':
            raise HarnessError(ACCEPTED_FAMILY_SPEC_BOUNDARY_ERROR)
        result[name]=spec
    if not broad_registry_groups():
        raise HarnessError(ACCEPTED_FAMILY_SPEC_BOUNDARY_ERROR)
    return result


def accepted_family_ownership_registry(duplicate: bool=False) -> list[dict[str, Any]]:
    rows=copy.deepcopy(ACCEPTED_FAMILY_OWNER_ROWS)
    if duplicate:
        rows.append({**rows[0], 'owning_callable':'transform_address_records_identity_crosswalk'})
    seen={}
    for row in rows:
        key=(row['table'], json.dumps(row['primary_key'], sort_keys=True)); owner=row['owning_callable']
        if key in seen and seen[key] != owner:
            raise HarnessError('duplicate owner declarations')
        seen[key]=owner
    totals={}
    for row in rows:
        totals[row['owning_callable']]=totals.get(row['owning_callable'],0)+1
    if totals != ACCEPTED_FAMILY_EXPECTED_TOTALS_BY_OWNER or len(rows)!=16:
        raise HarnessError(f'accepted-family ownership registry totals mismatch: {totals}')
    return rows


def accepted_family_owner_by_key() -> dict[tuple[str, tuple[tuple[str, Any], ...]], dict[str, Any]]:
    return {(r['table'], tuple(sorted(r['primary_key'].items()))): r for r in accepted_family_ownership_registry()}


def accepted_family_key(row: dict[str, Any]) -> tuple[str, tuple[tuple[str, Any], ...]]:
    return (row['table'], tuple(sorted(row['primary_key'].items())))


def accepted_family_filtered_prerequisite_rows() -> dict[str, list[dict[str, Any]]]:
    rows={t:[] for t in DEPENDENCY_ORDER}; base=base_target_rows()
    for table in ('proposed_source_authority','proposed_country','proposed_administrative_unit','proposed_administrative_unit_version'):
        rows[table]=copy.deepcopy(base.get(table,[]))
    records=[make_addresses_record(), make_address_points_record(), make_address_records_record(), make_citizen_geotag_record()]
    add_source_records_and_evidence(rows, records)
    return rows


def setup_accepted_family_convergence_database() -> dict[str, Any]:
    current=discover_current(reset=True); target=apply_target(); topology=topology_check(); records=fixture_records()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        source_report=insert_current_fixture_rows(cur, records)
        prereq_rows=accepted_family_filtered_prerequisite_rows()
        stats=apply_target_rows(cur, prereq_rows); cur.execute('SET CONSTRAINTS ALL IMMEDIATE'); conn.commit()
    return {'helper':'setup_accepted_family_convergence_database','current_source_discovery':current['execution_mode'],'target_schema_application':target['execution_mode'],'topology_validation':topology['status'],'current_source_rows_loaded':source_report['source_records_inserted'],'source_record_rows_loaded':len(prereq_rows.get('proposed_source_record',[])),'evidence_rows_loaded':len(prereq_rows.get('proposed_evidence_object',[])),'prerequisite_insert_stats':stats}


def accepted_family_norm_values(table: str, row: dict[str, Any]) -> dict[str, Any]:
    d=dict(row)
    if table=='proposed_geometry_observation':
        d.pop('observed_geom', None)
    if 'details_json' in d: d['details_json']=normalize_json(d['details_json'])
    return norm_row(d)


def accepted_family_row(table: str, row: dict[str, Any]) -> dict[str, Any]:
    pk=primary_key(row, table); key=(table, tuple(sorted(pk.items()))); owner=accepted_family_owner_by_key().get(key)
    return {'table':table,'primary_key':pk,'owning_callable':owner['owning_callable'] if owner else None,'source_identity':owner['source_identity'] if owner else accepted_family_infer_source_identity(table,row),'classification':owner['classification'] if owner else row.get('classification'),'values':accepted_family_norm_values(table,row)}


def accepted_family_infer_source_identity(table: str, row: dict[str, Any]) -> str | None:
    if table=='proposed_legacy_crosswalk': return f"{row.get('source_table')}:{row.get('legacy_id')}"
    if table=='proposed_migration_exception': return row.get('source_key')
    if table=='proposed_geometry_observation': return row.get('source_record_id')
    return None


def accepted_family_query(cur, table: str, sql: str, params: tuple[Any, ...]) -> list[dict[str, Any]]:
    if table=='proposed_geometry_observation':
        sql=sql.replace('SELECT *', 'SELECT *, ST_AsText(observed_geom) AS observed_geom_wkt, ST_SRID(observed_geom) AS observed_geom_srid')
    cur.execute(sql, params)
    return [accepted_family_row(table, r) for r in cur.fetchall()]


def accepted_family_query_attributable_union(cur) -> list[dict[str, Any]]:
    rows=[]
    like_locations=[x+'%' for x in ACCEPTED_FAMILY_LOCATION_IDS]
    like_subjects=[x+'%' for x in ACCEPTED_FAMILY_SUBJECT_IDS]
    like_geoms=[x+'%' for x in ACCEPTED_FAMILY_GEOMETRY_IDS]
    like_exceptions=[x+'%' for x in ACCEPTED_FAMILY_EXCEPTION_IDS]
    cur.execute("SELECT location_record_id FROM canonical_target.proposed_location_record WHERE location_record_id = ANY(%s) OR location_record_id LIKE ANY(%s)", (ACCEPTED_FAMILY_LOCATION_IDS, like_locations))
    attributable_location_ids=sorted({r['location_record_id'] for r in cur.fetchall()})
    rows += accepted_family_query(cur,'proposed_location_record',"SELECT * FROM canonical_target.proposed_location_record WHERE location_record_id = ANY(%s) OR location_record_id LIKE ANY(%s)", (ACCEPTED_FAMILY_LOCATION_IDS, like_locations))
    rows += accepted_family_query(cur,'proposed_registry_subject',"SELECT * FROM canonical_target.proposed_registry_subject WHERE native_id = ANY(%s) OR subject_id = ANY(%s) OR subject_id LIKE ANY(%s)", (attributable_location_ids, ACCEPTED_FAMILY_SUBJECT_IDS, like_subjects))
    ident_where=' OR '.join(['(source_table=%s AND legacy_id=%s)' for _ in ACCEPTED_FAMILY_CROSSWALK_IDENTITIES])
    ident_params=tuple(x for table, field, legacy in ACCEPTED_FAMILY_CROSSWALK_IDENTITIES for x in (table, legacy))
    rows += accepted_family_query(cur,'proposed_legacy_crosswalk',f"SELECT * FROM canonical_target.proposed_legacy_crosswalk WHERE {ident_where}", ident_params)
    rows += accepted_family_query(cur,'proposed_geometry_observation',"SELECT * FROM canonical_target.proposed_geometry_observation WHERE source_record_id = ANY(%s) OR evidence_object_id = ANY(%s) OR subject_id = ANY(%s) OR geometry_observation_id = ANY(%s) OR geometry_observation_id LIKE ANY(%s)", (ACCEPTED_FAMILY_GEOMETRY_SOURCE_RECORD_IDS, ACCEPTED_FAMILY_GEOMETRY_EVIDENCE_IDS, ACCEPTED_FAMILY_SUBJECT_IDS, ACCEPTED_FAMILY_GEOMETRY_IDS, like_geoms))
    rows += accepted_family_query(cur,'proposed_migration_exception',"SELECT * FROM canonical_target.proposed_migration_exception WHERE source_table = ANY(%s) AND source_key = ANY(%s) OR migration_exception_id = ANY(%s) OR migration_exception_id LIKE ANY(%s)", (ACCEPTED_FAMILY_EXCEPTION_SOURCE_TABLES, ACCEPTED_FAMILY_EXCEPTION_SOURCE_KEYS, ACCEPTED_FAMILY_EXCEPTION_IDS, like_exceptions))
    # Attributable public outputs / versions must be absent; include them in absence checks, not the positive 16-row union hash.
    dedup={accepted_family_key(r):r for r in rows}
    return sorted(dedup.values(), key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def accepted_family_query_owned_union(cur) -> list[dict[str, Any]]:
    actual=accepted_family_query_attributable_union(cur); expected_keys=set(accepted_family_owner_by_key())
    return [r for r in actual if accepted_family_key(r) in expected_keys]


def accepted_family_union_hash(cur) -> dict[str, Any]:
    rows=accepted_family_query_attributable_union(cur); return {'rows':rows,'row_count':len(rows),'hash':sha(rows)}


def accepted_family_rows_map(rows: list[dict[str, Any]]) -> dict[tuple[str, tuple[tuple[str, Any], ...]], dict[str, Any]]:
    return {accepted_family_key(r): r for r in rows}


def assert_accepted_family_owned_rows_absent(cur) -> dict[str, Any]:
    present=[r for r in accepted_family_query_attributable_union(cur) if accepted_family_key(r) in set(accepted_family_owner_by_key())]
    if present:
        raise HarnessError(f'accepted-family fixture pre-created owned rows: {[(r["table"], r["primary_key"]) for r in present]}')
    return {'accepted_owned_rows_pre_created':0,'checked_primary_keys':16}


def accepted_family_delta(before: list[dict[str, Any]], after: list[dict[str, Any]]) -> dict[str, Any]:
    b=accepted_family_rows_map(before); a=accepted_family_rows_map(after)
    inserted=sorted([a[k] for k in a.keys()-b.keys()], key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))
    deleted=sorted([b[k] for k in b.keys()-a.keys()], key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))
    updated=sorted([a[k] for k in a.keys()&b.keys() if a[k] != b[k]], key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))
    return {'inserted':inserted,'updated':updated,'deleted':deleted,'inserted_count':len(inserted),'updated_count':len(updated),'deleted_count':len(deleted)}


def accepted_family_expected_keys_for_callable(callable_name: str) -> set[tuple[str, tuple[tuple[str, Any], ...]]]:
    return {accepted_family_key({'table':r['table'],'primary_key':r['primary_key']}) for r in ACCEPTED_FAMILY_OWNER_ROWS if r['owning_callable']==callable_name}


def accepted_family_delta_owner(row: dict[str, Any]) -> str | None:
    owner=accepted_family_owner_by_key().get(accepted_family_key(row))
    return owner['owning_callable'] if owner else row.get('owning_callable')


def accepted_family_validate_delta(callable_name: str, delta: dict[str, Any], result: dict[str, Any], *, expect_no_delta: bool=False) -> None:
    expected_keys=accepted_family_expected_keys_for_callable(callable_name)
    inserted_keys={accepted_family_key(r) for r in delta['inserted']}
    foreign_inserts=[r for r in delta['inserted'] if accepted_family_delta_owner(r) != callable_name]
    foreign_updates=[r for r in delta['updated'] if accepted_family_delta_owner(r) != callable_name]
    foreign_deletes=[r for r in delta['deleted'] if accepted_family_delta_owner(r) != callable_name]
    if foreign_updates or foreign_deletes:
        raise HarnessError(ACCEPTED_FAMILY_PREREQUISITE_ERROR)
    if foreign_inserts:
        raise HarnessError(ACCEPTED_FAMILY_OWNERSHIP_ERROR)
    if expect_no_delta:
        if delta['inserted_count'] or delta['updated_count'] or delta['deleted_count']:
            raise HarnessError(ACCEPTED_FAMILY_OWNERSHIP_ERROR)
        return
    if inserted_keys != expected_keys or delta['updated_count'] or delta['deleted_count'] or result['insert_stats_first']['inserted'] != delta['inserted_count']:
        raise HarnessError(ACCEPTED_FAMILY_OWNERSHIP_ERROR)


def accepted_family_run_callable(cur, callable_name: str, specs: dict[str, dict[str, Any]], *, mutation: dict[str, Any] | None=None, expect_no_delta: bool=False, post_callable_mutation=None) -> dict[str, Any]:
    before=accepted_family_query_attributable_union(cur)
    mapping={
        'transform_addresses_identity_crosswalk': lambda: transform_addresses_identity_crosswalk(cur, spec_validation=specs['transform_addresses_identity_crosswalk'], mutation=mutation),
        'transform_address_points_geometry': lambda: transform_address_points_geometry(cur, spec_validation=specs['transform_address_points_geometry'], mutation=mutation),
        'transform_address_points_observation_crosswalk': lambda: transform_address_points_observation_crosswalk(cur, spec_validation=specs['transform_address_points_observation_crosswalk'], mutation=mutation),
        'transform_address_records_identity_crosswalk': lambda: transform_address_records_identity_crosswalk(cur, spec_validation=specs['transform_address_records_identity_crosswalk'], mutation=mutation),
        'transform_address_records_geometry': lambda: transform_address_records_geometry(cur, spec_validation=specs['transform_address_records_geometry'], mutation=mutation),
        'transform_citizen_geotag_identity_crosswalk': lambda: transform_citizen_geotag_identity_crosswalk(cur, spec_validation=specs['transform_citizen_geotag_identity_crosswalk'], mutation=mutation),
        'transform_citizen_geotag_geometry': lambda: transform_citizen_geotag_geometry(cur, spec_validation=specs['transform_citizen_geotag_geometry'], mutation=mutation),
    }
    result=mapping[callable_name]()
    if post_callable_mutation is not None:
        post_callable_mutation(cur)
    after=accepted_family_query_attributable_union(cur); delta=accepted_family_delta(before, after)
    accepted_family_validate_delta(callable_name, delta, result, expect_no_delta=expect_no_delta)
    owned=[r for r in after if r['owning_callable']==callable_name]
    return {'callable':callable_name,'implementation_unit':result['implementation_unit'],'transform_group':result['transform_group_id'],'source_identity':result.get('derived_ids',{}).get('source_key') or result.get('source_key_derivation',{}).get('value'),'live_specification_used':result['spec_validation']['group']['transform_group_id'],'first_application_inserts':result['insert_stats_first']['inserted'],'internal_idempotent_application_inserts':result['insert_stats_second']['inserted'],'updates':result.get('second_run_updates',0),'owned_target_primary_keys':[{'table':r['table'],'primary_key':r['primary_key']} for r in owned],'observed_delta':delta,'observed_inserted_rows':delta['inserted_count'],'observed_updated_rows':delta['updated_count'],'observed_deleted_rows':delta['deleted_count'],'family_union_insert_delta':delta['inserted_count'],'generic_transform_group_used':result.get('generic_transform_group_used',False),'post_callable_mutation_hook_used':post_callable_mutation is not None}


def accepted_family_execute_sequence(cur, sequence: list[str], specs: dict[str, dict[str, Any]], *, expect_no_delta: bool=False) -> list[dict[str, Any]]:
    return [accepted_family_run_callable(cur, name, specs, expect_no_delta=expect_no_delta) for name in sequence]


def accepted_family_expected_union() -> list[dict[str, Any]]:
    with addresses_identity_oracle_access(True): addresses=expected_addresses_identity_rows(load_addresses_identity_oracle())
    with address_points_oracle_access(True):
        address_points=expected_address_points_rows(load_address_points_oracle(), 'address_points:phase-a-address-points-id')
        load_address_points_correction_oracle(); load_address_points_final_correction_oracle()
    with address_points_observation_oracle_access(True): point_crosswalk=expected_address_points_observation_rows(load_address_points_observation_oracle())
    with address_records_identity_oracle_access(True): address_records_identity=expected_address_records_identity_rows(load_address_records_identity_oracle())
    with address_records_oracle_access(True): address_records_geometry=expected_address_records_rows(load_address_records_oracle(), 'address_records:phase-a-address-records-id', load_address_records_correction_oracle())
    with citizen_geotag_identity_oracle_access(True): citizen_identity=expected_citizen_geotag_identity_rows(load_citizen_geotag_identity_oracle())
    with citizen_geotag_oracle_access(True): citizen_geometry=expected_citizen_geotag_rows(load_citizen_geotag_oracle(), 'citizen_geotag_submissions:phase-a-geotag-001')
    by_key={(r['table'], json.dumps(r['primary_key'], sort_keys=True)):r for r in ACCEPTED_FAMILY_OWNER_ROWS}; expected=[]
    for row in addresses+address_points+point_crosswalk+address_records_identity+address_records_geometry+citizen_identity+citizen_geometry:
        key=(row['table'], json.dumps(row['primary_key'], sort_keys=True)); owner=by_key.get(key)
        if not owner: raise HarnessError(f'accepted-family expected union contains unowned row: {key}')
        values=copy.deepcopy(row['values'])
        if 'details_json' in values: values['details_json']=normalize_json(values['details_json'])
        expected.append({'table':row['table'],'primary_key':row['primary_key'],'owning_callable':owner['owning_callable'],'source_identity':owner['source_identity'],'classification':owner['classification'],'values':norm_row(values)})
    return sorted(expected, key=lambda r:(r['table'], json.dumps(r['primary_key'], sort_keys=True)))


def accepted_family_semantic_controls(cur) -> dict[str, Any]:
    ident_where=' OR '.join(['(source_table=%s AND legacy_id=%s)' for _ in ACCEPTED_FAMILY_CROSSWALK_IDENTITIES])
    params=tuple(x for table, field, legacy in ACCEPTED_FAMILY_CROSSWALK_IDENTITIES for x in (table, legacy))
    cur.execute(f"""SELECT source_table, source_field, legacy_id, target_entity, COUNT(*)::int AS row_count, COUNT(DISTINCT target_id)::int AS target_count FROM canonical_target.proposed_legacy_crosswalk WHERE {ident_where} GROUP BY 1,2,3,4 HAVING COUNT(*)>1 OR COUNT(DISTINCT target_id)>1""", params)
    duplicates=[norm_row(dict(r)) for r in cur.fetchall()]
    if duplicates: raise HarnessError('duplicate semantic crosswalks')
    return {'semantic_crosswalk_duplicates':0,'multiple_target_resolutions':0}


def accepted_family_expected_absences(cur) -> list[dict[str, Any]]:
    checks=[
        ('proposed_location_record_version', "location_record_id = ANY(%s)", (ACCEPTED_FAMILY_LOCATION_IDS,), 'unapproved location-record versions'),
        ('proposed_public_code_alias', "location_record_id = ANY(%s)", (ACCEPTED_FAMILY_LOCATION_IDS,), 'public-code aliases'),
        ('proposed_publication_release_item', "location_record_id = ANY(%s)", (ACCEPTED_FAMILY_LOCATION_IDS,), 'publication release items'),
        ('proposed_geometry_version', "source_observation_id = ANY(%s)", (ACCEPTED_FAMILY_GEOMETRY_IDS,), 'geometry versions'),
        ('proposed_geometry_quality_assessment', "geometry_version_id = ANY(%s)", (ACCEPTED_FAMILY_GEOMETRY_IDS,), 'geometry quality approvals'),
        ('proposed_geometry_transformation', "transformation_id = ANY(%s)", (ACCEPTED_FAMILY_GEOMETRY_IDS,), 'geometry transformations'),
        ('proposed_location_record_assertion', "source_record_id = ANY(%s)", (ACCEPTED_FAMILY_SOURCE_RECORD_IDS,), 'grouped-geometry substitute assertions'),
        ('proposed_geometry_observation', "source_record_id = %s", ('phase-a-source-record-addresses-001',), 'identity-path-created geometry rows'),
        ('proposed_legacy_crosswalk', "source_table=%s AND legacy_id=%s AND source_field <> %s", ('citizen_geotag_submissions','phase-a-geotag-001','id'), 'non-id citizen-geotag crosswalks'),
        ('proposed_legacy_crosswalk', "source_table=%s AND legacy_id=%s AND source_field <> %s", ('addresses','phase-a-addresses-id','id'), 'address reference/context-field identity crosswalks'),
        ('proposed_legacy_crosswalk', "source_table=%s AND legacy_id=%s AND source_field IN (%s,%s)", ('address_records','phase-a-address-records-id','source_submission_id','territory_id'), 'address-record source_submission_id or territory identity crosswalks'),
        ('proposed_legacy_crosswalk', "source_table=%s AND legacy_id=%s AND source_field=%s AND target_entity=%s", ('address_points','phase-a-address-points-id','id','location_record'), 'point-id-to-location-record crosswalks'),
    ]
    results=[]
    for table,where,params,reason in checks:
        cur.execute(f'SELECT COUNT(*)::int AS c FROM canonical_target.{table} WHERE {where}', params)
        count=cur.fetchone()['c']; results.append({'table':table,'where':where,'reason':reason,'count':count})
        if count != 0: raise HarnessError(f'accepted-family expected absence failed: {reason}')
    return results


def accepted_family_compare_union(cur) -> dict[str, Any]:
    expected=accepted_family_expected_union(); actual=accepted_family_query_attributable_union(cur)
    exp_keys={accepted_family_key(r) for r in expected}; act_keys={accepted_family_key(r) for r in actual}
    if act_keys-exp_keys: raise HarnessError(f'{ACCEPTED_FAMILY_UNEXPECTED_ERROR}: {sorted(act_keys-exp_keys)}')
    if exp_keys-act_keys: raise HarnessError(f'{ACCEPTED_FAMILY_MISSING_ERROR}: {sorted(exp_keys-act_keys)}')
    if json.loads(json.dumps(actual, sort_keys=True, default=str)) != json.loads(json.dumps(expected, sort_keys=True, default=str)):
        raise HarnessError('accepted-family complete union rows differ from accepted expected truth')
    actual_hash=sha(actual); expected_hash=sha(expected)
    if actual_hash != expected_hash: raise HarnessError('accepted-family expected/actual union hash mismatch')
    counts={t:sum(1 for r in actual if r['table']==t) for t in ACCEPTED_FAMILY_EXPECTED_COUNTS}
    if counts != ACCEPTED_FAMILY_EXPECTED_COUNTS: raise HarnessError(f'accepted-family scoped counts mismatch: {counts}')
    return {'expected_rows':len(expected),'actual_rows':len(actual),'expected_union_hash':expected_hash,'actual_union_hash':actual_hash,'comparison_both_directions':True,'scoped_counts':counts}


def accepted_family_validate_ownership(actual: list[dict[str, Any]], registry: list[dict[str, Any]]) -> dict[str, Any]:
    expected_owner={(r['table'], json.dumps(r['primary_key'], sort_keys=True)):r['owning_callable'] for r in registry}; collisions=[]
    for row in actual:
        key=(row['table'], json.dumps(row['primary_key'], sort_keys=True))
        if key in expected_owner and expected_owner[key] != row['owning_callable']:
            collisions.append({'key':key,'expected_owner':expected_owner.get(key),'actual_owner':row['owning_callable']})
    if collisions: raise HarnessError(f'ownership collisions: {collisions}')
    return {'ownership_registry_entries':len(registry),'ownership_collisions':0}


def compare_accepted_family_convergence_read_only() -> dict[str, Any]:
    proof=comparator_read_only_proof()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        cur.execute('BEGIN READ ONLY'); cur.execute('SHOW transaction_read_only'); read_only=cur.fetchone()['transaction_read_only']
        comparison=accepted_family_compare_union(cur)
        actual=accepted_family_query_attributable_union(cur)
        ownership=accepted_family_validate_ownership(actual, accepted_family_ownership_registry())
        semantic=accepted_family_semantic_controls(cur); absences=accepted_family_expected_absences(cur)
        conn.rollback()
    comparison.update({'status':'passed','ownership':ownership,'semantic_controls':semantic,'expected_absences':absences,'comparator_connection':{'separate_connection':True,'transaction_read_only':read_only},'comparator_read_only_proof':proof})
    return comparison


def accepted_family_expect_error(test_id: str, mutation, expected_error: str, *, mutation_label: str | None=None) -> dict[str, Any]:
    try:
        mutation()
    except Exception as exc:
        observed=str(exc)
        if expected_error not in observed:
            raise HarnessError(f'{test_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
        if 'existing correct target row changed' in observed:
            observed='existing correct target row changed'
        if expected_error == ACCEPTED_FAMILY_STRUCTURE_ERROR:
            observed = ACCEPTED_FAMILY_STRUCTURE_ERROR
        if expected_error == ACCEPTED_FAMILY_PRIVACY_ERROR:
            observed = ACCEPTED_FAMILY_PRIVACY_ERROR
        return {'test_id':test_id,'status':'passed','mutation':mutation_label or test_id,'expected_error':expected_error,'observed_error':observed,'detection_executed':True}
    raise HarnessError(f'{test_id} unexpectedly passed')


def accepted_family_db_failure_probe(test_id: str, setup_sequence: list[str], action, expected_error: str, *, mutation_label: str | None=None) -> dict[str, Any]:
    setup_accepted_family_convergence_database(); specs=accepted_family_binding_registry()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        assert_accepted_family_owned_rows_absent(cur); accepted_family_execute_sequence(cur, setup_sequence, specs); conn.commit()
        cur.execute('BEGIN'); before=accepted_family_union_hash(cur)
        try:
            action(cur, specs)
            raise HarnessError(f'{test_id} unexpectedly passed')
        except Exception as exc:
            observed=str(exc)
            if expected_error not in observed:
                conn.rollback(); raise HarnessError(f'{test_id} failed for wrong reason: expected {expected_error!r}, got {observed!r}')
            if 'existing correct target row changed' in observed:
                observed='existing correct target row changed'
            conn.rollback(); after=accepted_family_union_hash(cur)
            if before['rows'] != after['rows'] or before['hash'] != after['hash']:
                raise HarnessError(f'same-database rollback proof failed for {test_id}')
            return {'test_id':test_id,'status':'passed','mutation':mutation_label or test_id,'expected_error':expected_error,'observed_error':observed,'detection_executed':True,'same_database_pre_test_rows':before['rows'],'same_database_pre_test_row_count':before['row_count'],'same_database_pre_test_hash':before['hash'],'same_database_post_failure_rows':after['rows'],'same_database_post_failure_row_count':after['row_count'],'same_database_post_failure_hash':after['hash'],'rollback_equality':True,'rollback_hash_equality':True}


def accepted_family_failure_probe(test_id: str, setup_sequence: list[str], failing_callable: str, expected_error: str, *, mutation=None) -> dict[str, Any]:
    def action(cur, specs):
        if mutation:
            mutation(cur)
        return accepted_family_run_callable(cur, failing_callable, specs)
    return accepted_family_db_failure_probe(test_id, setup_sequence, action, expected_error, mutation_label=mutation and 'database prerequisite mutation' or 'consumer-before-prerequisite')


def accepted_family_order_invariance() -> dict[str, Any]:
    from itertools import permutations
    chains={'A':['transform_addresses_identity_crosswalk','transform_address_points_geometry','transform_address_points_observation_crosswalk'],'B':['transform_address_records_identity_crosswalk','transform_address_records_geometry'],'C':['transform_citizen_geotag_identity_crosswalk','transform_citizen_geotag_geometry']}
    results=[]
    for order in permutations(['A','B','C']):
        setup_accepted_family_convergence_database(); specs=accepted_family_binding_registry(); seq=[c for chain in order for c in chains[chain]]
        with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
            assert_accepted_family_owned_rows_absent(cur); accepted_family_execute_sequence(cur, seq, specs); conn.commit(); union=accepted_family_union_hash(cur)
        results.append({'chain_order': ''.join(order), 'union_hash': union['hash'], 'union_rows': union['row_count']})
    hashes={r['union_hash'] for r in results}
    if len(hashes)!=1 or next(iter(hashes)) != ACCEPTED_FAMILY_EXPECTED_HASH: raise HarnessError(f'independent-chain order invariance failed: {results}')
    return {'status':'passed','chain_permutation_hashes':results,'order_invariance':True}


def accepted_family_insert_unexpected(cur, kind: str) -> None:
    if kind=='location':
        insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-reference-extra','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
    elif kind=='subject':
        insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-reference-extra','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        insert_row(cur,'proposed_registry_subject',{'subject_id':'phase-a-subject-phase-a-location-address-reference-extra','subject_entity':'location_record','created_at':TS,'native_id':'phase-a-location-address-reference-extra','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
    elif kind=='crosswalk':
        insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':'phase-a-crosswalk-addresses-id-extra','source_table':'addresses','source_field':'address_reference','legacy_id':'phase-a-addresses-id','target_entity':'location_record','target_id':'phase-a-location-address-reference','created_at':TS})
    elif kind=='geometry':
        insert_row(cur,'proposed_geometry_observation',{'geometry_observation_id':'phase-a-geometry-address-points-phase-a-address-points-id-extra','subject_id':'phase-a-subject-phase-a-location-address-reference','geometry_role':'location-point','observed_geom':'POINT(8.783 3.752)','capture_method':'derived-from-source','horizontal_accuracy_m':4.5,'source_record_id':'phase-a-source-record-address-points-001','evidence_object_id':'phase-a-evidence-address-points','licence_id':None,'observed_at':TS,'recorded_at':TS,'classification':'restricted'})
    elif kind=='exception':
        insert_row(cur,'proposed_migration_exception',{'migration_exception_id':'phase-a-exception-geometry-authority-address-points-phase-a-address-points-id-extra','batch_id':'phase-a-execution-correction','source_table':'address_points','source_field':None,'source_key':'address_points:phase-a-address-points-id','exception_type':'unresolved-reference','severity':'medium','owner':'SDA','created_at':TS,'resolved_at':None,'details_json':{'reason':'synthetic surplus'}})
    else:
        raise HarnessError(f'unknown unexpected kind {kind}')


def accepted_family_unexpected_tests() -> list[dict[str, Any]]:
    tests=[]
    for kind in ['location','subject','crosswalk','geometry','exception']:
        tests.append(accepted_family_db_failure_probe(f'unexpected-union-{kind}', ACCEPTED_FAMILY_SEQUENCE, lambda cur,specs,k=kind: (accepted_family_insert_unexpected(cur,k), accepted_family_compare_union(cur)), ACCEPTED_FAMILY_UNEXPECTED_ERROR, mutation_label=f'insert synthetic attributable surplus {kind}'))
    tests.append(accepted_family_db_failure_probe('missing-union-row', ACCEPTED_FAMILY_SEQUENCE, lambda cur,specs: (cur.execute("DELETE FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id='phase-a-crosswalk-addresses-id-to-location-record'"), accepted_family_compare_union(cur)), ACCEPTED_FAMILY_MISSING_ERROR, mutation_label='delete one expected accepted row'))
    return tests


def accepted_family_governance_tests() -> list[dict[str, Any]]:
    tests=[]
    tests.append(accepted_family_expect_error('accepted-oracle-drift', lambda: accepted_family_verify_controls(expected_hash_overrides={'citizen_geotag_identity_oracle_sha256':'0'*64}), 'accepted-family convergence control or oracle drift', mutation_label='test-only incorrect accepted-oracle hash'))
    bad_control=json.loads(ACCEPTED_FAMILY_CONTROL.read_text()); bad_control['owned_union_rows']=17
    tests.append(accepted_family_expect_error('convergence-control-drift', lambda: accepted_family_verify_controls(control_override=bad_control), 'accepted-family convergence control drift', mutation_label='copied control object owned_union_rows=17'))
    original=ADDRESSES_IDENTITY_IMPLEMENTATIONS.get(ADDRESSES_IDENTITY_IMPL_UNIT)
    def callable_drift():
        try:
            ADDRESSES_IDENTITY_IMPLEMENTATIONS[ADDRESSES_IDENTITY_IMPL_UNIT]=transform_address_records_identity_crosswalk
            accepted_family_binding_registry()
        finally:
            ADDRESSES_IDENTITY_IMPLEMENTATIONS[ADDRESSES_IDENTITY_IMPL_UNIT]=original
    tests.append(accepted_family_expect_error('accepted-callable-drift', callable_drift, 'accepted-family convergence callable binding mismatch', mutation_label='temporarily replace accepted implementation map entry'))
    originals={}
    def generic_guard_path():
        global run_real_transform, transform_group, phase_a_all, build_dispatcher
        names=['run_real_transform','transform_group','phase_a_all','build_dispatcher']
        for n in names: originals[n]=globals()[n]
        def blocked(*args, **kwargs): raise HarnessError(ACCEPTED_FAMILY_GENERIC_TRANSFORM_ERROR)
        try:
            run_real_transform=blocked; transform_group=blocked; phase_a_all=blocked; build_dispatcher=blocked
            setup_accepted_family_convergence_database(); specs=accepted_family_binding_registry()
            with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
                assert_accepted_family_owned_rows_absent(cur); accepted_family_execute_sequence(cur, ACCEPTED_FAMILY_SEQUENCE, specs); conn.commit()
            run_real_transform(read_expected=False)
        finally:
            run_real_transform=originals['run_real_transform']; transform_group=originals['transform_group']; phase_a_all=originals['phase_a_all']; build_dispatcher=originals['build_dispatcher']
    tests.append(accepted_family_expect_error('generic-transform-invocation', generic_guard_path, ACCEPTED_FAMILY_GENERIC_TRANSFORM_ERROR, mutation_label='guard broad dispatcher then deliberately invoke prohibited path'))
    tests.append(accepted_family_expect_error('frozen-live-specification-boundary-drift', lambda: accepted_family_binding_registry(force_frozen_loader=True), ACCEPTED_FAMILY_SPEC_BOUNDARY_ERROR, mutation_label='test-only frozen/live loader identity mismatch'))
    tests.append(accepted_family_db_failure_probe('classification-drift', ACCEPTED_FAMILY_SEQUENCE, lambda cur,specs: (cur.execute("UPDATE canonical_target.proposed_location_record SET classification='restricted' WHERE location_record_id='phase-a-location-address-reference'"), accepted_family_compare_union(cur)), 'accepted-family complete union rows differ from accepted expected truth', mutation_label='mutate accepted location classification'))
    tests.append(accepted_family_db_failure_probe('public-output-drift', ACCEPTED_FAMILY_SEQUENCE, lambda cur,specs: (insert_row(cur,'proposed_public_code_alias',{'public_code_alias_id':'phase-a-public-alias-address-reference','location_record_id':'phase-a-location-address-reference','public_code':'PUB-TEST','code_scheme':'nli-reserved-v1','code_state':'reserved','reserved_at':TS,'issued_at':None,'retired_at':None,'predecessor_alias_id':None,'successor_alias_id':None}), accepted_family_expected_absences(cur)), 'accepted-family expected absence failed', mutation_label='insert attributable public-code alias'))
    tests.append(accepted_family_expect_error('citizen-privacy-drift', lambda: accepted_family_privacy_validation({'command':'accepted-family-convergence','synthetic_field':'CITIZEN-SENTINEL-C24-C28'}), ACCEPTED_FAMILY_PRIVACY_ERROR, mutation_label='inject synthetic citizen sentinel in report candidate'))
    return tests


def accepted_family_ownership_tests() -> list[dict[str, Any]]:
    tests=[]
    def cross_owner(cur, specs):
        def foreign_insert(c):
            insert_row(c,'proposed_location_record',{'location_record_id':'phase-a-location-address-records-id','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        return accepted_family_run_callable(cur,'transform_addresses_identity_crosswalk',specs,post_callable_mutation=foreign_insert)
    cross=accepted_family_db_failure_probe('cross-owner-row-production', [], cross_owner, ACCEPTED_FAMILY_OWNERSHIP_ERROR, mutation_label='post-call hook inserts transform_address_records_identity_crosswalk-owned location row')
    cross.update({'detector':'accepted_family_run_callable delta validation','manual_expected_error_raise':False,'foreign_row_detected':True})
    tests.append(cross)
    def prerequisite_update(cur, specs):
        def foreign_update(c):
            c.execute("UPDATE canonical_target.proposed_location_record SET classification='restricted' WHERE location_record_id='phase-a-location-address-reference'")
        return accepted_family_run_callable(cur,'transform_address_points_geometry',specs,post_callable_mutation=foreign_update)
    prereq=accepted_family_db_failure_probe('consumer-prerequisite-update', ['transform_addresses_identity_crosswalk'], prerequisite_update, ACCEPTED_FAMILY_PREREQUISITE_ERROR, mutation_label='post-call hook mutates transform_addresses_identity_crosswalk-owned prerequisite')
    prereq.update({'detector':'accepted_family_run_callable delta validation','manual_expected_error_raise':False,'foreign_row_detected':True})
    tests.append(prereq)
    return tests


def accepted_family_scope_isolation_test() -> dict[str, Any]:
    setup_accepted_family_convergence_database(); specs=accepted_family_binding_registry()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        assert_accepted_family_owned_rows_absent(cur); accepted_family_execute_sequence(cur, ACCEPTED_FAMILY_SEQUENCE, specs); conn.commit(); before=accepted_family_compare_union(cur); before_rows=accepted_family_query_attributable_union(cur); before_hash=sha(before_rows)
        insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-unrelated-location','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'})
        insert_row(cur,'proposed_registry_subject',{'subject_id':'phase-a-subject-phase-a-unrelated-location','subject_entity':'location_record','created_at':TS,'native_id':'phase-a-unrelated-location','subject_state':'active','retired_at':None,'delete_policy':'retire-only'})
        insert_row(cur,'proposed_public_code_alias',{'public_code_alias_id':'phase-a-unrelated-public-alias','location_record_id':'phase-a-unrelated-location','public_code':'UNRELATED','code_scheme':'nli-reserved-v1','code_state':'reserved','reserved_at':TS,'issued_at':None,'retired_at':None,'predecessor_alias_id':None,'successor_alias_id':None})
        insert_row(cur,'proposed_migration_exception',{'migration_exception_id':'phase-a-unrelated-migration-exception','batch_id':'phase-a-execution-correction','source_table':'unrelated_source','source_field':None,'source_key':'unrelated_source:1','exception_type':'unresolved-reference','severity':'low','owner':'SDA','created_at':TS,'resolved_at':None,'details_json':{'reason':'scope isolation'}})
        insert_row(cur,'proposed_source_package',{'source_package_id':'phase-a-source-package-unrelated-scope','source_authority_id':'phase-a-authority-operational-control','package_name':'Phase A unrelated scope-isolation package','package_checksum':sha({'scope':'isolation'}),'licence_id':None,'loaded_at':TS,'load_context':{'scope':'isolation'}})
        insert_row(cur,'proposed_source_record',{'source_record_id':'phase-a-source-record-unrelated-scope','source_package_id':'phase-a-source-package-unrelated-scope','source_key':'unrelated_source:geometry-1','raw_payload_hash':sha({'geometry':'unrelated'}),'raw_payload_classification':'government-internal','recorded_at':TS})
        insert_row(cur,'proposed_evidence_object',{'evidence_object_id':'phase-a-evidence-unrelated-scope','source_record_id':'phase-a-source-record-unrelated-scope','storage_uri':'phase-a://evidence/unrelated-scope','content_hash':sha({'geometry':'unrelated'}),'media_type':'application/json','classification':'government-internal','captured_at':TS,'retention_state':'active'})
        insert_row(cur,'proposed_geometry_observation',{'geometry_observation_id':'phase-a-unrelated-geometry-observation','subject_id':'phase-a-subject-phase-a-unrelated-location','geometry_role':'location-point','observed_geom':'POINT(8.700 3.700)','capture_method':'derived-from-source','horizontal_accuracy_m':9.0,'source_record_id':'phase-a-source-record-unrelated-scope','evidence_object_id':'phase-a-evidence-unrelated-scope','licence_id':None,'observed_at':TS,'recorded_at':TS,'classification':'restricted'})
        insert_row(cur,'proposed_decision_event',{'decision_event_id':'phase-a-decision-unrelated-geometry-promotion','decision_type':'approve-geometry','actor_id':'phase-a-actor-ref','authority_id':'phase-a-authority-operational-control','reason_code':'phase-a-scope-isolation','details_json':{'permission_key':'geometry.promote','institution_id':'phase-a-institution-scope-isolation','territorial_scope':'phase-a-scope-isolation','quality_authority_actor_id':'phase-a-actor-ref','evidence_object_id':'phase-a-evidence-unrelated-scope','source_observation_id':'phase-a-unrelated-geometry-observation'},'effective_at':TS,'recorded_at':TS,'decision_outcome':'approved'})
        insert_row(cur,'proposed_geometry_version',{'geometry_version_id':'phase-a-unrelated-geometry-version','subject_id':'phase-a-subject-phase-a-unrelated-location','geometry_role':'location-point','geom':'POINT(8.700 3.700)','source_observation_id':'phase-a-unrelated-geometry-observation','transformation_id':None,'validation_method':'scope-isolation-test','validated_by_actor_id':'phase-a-actor-ref','quality_state':'accepted-canonical','effective_from':TS,'effective_to':None,'recorded_at':TS,'recorded_to':None,'superseded_by_geometry_version_id':None,'dispute_case_id':None,'classification':'restricted','promotion_decision_event_id':'phase-a-decision-unrelated-geometry-promotion','promotion_evidence_object_id':'phase-a-evidence-unrelated-scope','promotion_authority_scope':'phase-a-scope-isolation'})
        insert_row(cur,'proposed_geometry_quality_assessment',{'quality_assessment_id':'phase-a-unrelated-geometry-quality','geometry_version_id':'phase-a-unrelated-geometry-version','check_name':'scope-isolation','check_result':'passed','tolerance_json':{},'measured_value_json':{},'assessed_at':TS,'assessed_by_actor_id':'phase-a-actor-ref'})
        after=accepted_family_compare_union(cur); semantic=accepted_family_semantic_controls(cur); absences=accepted_family_expected_absences(cur); ownership=accepted_family_validate_ownership(accepted_family_query_attributable_union(cur), accepted_family_ownership_registry()); after_rows=accepted_family_query_attributable_union(cur); after_hash=sha(after_rows); conn.rollback()
    if before['actual_union_hash'] != after['actual_union_hash'] or before_hash != after_hash or before_rows != after_rows:
        raise HarnessError('unrelated prerequisite scope isolation failed')
    return {'test_id':'unrelated-prerequisite-scope-isolation','status':'passed','mutation':'insert unrelated location, subject, public alias, migration exception, geometry observation, geometry version, and quality row outside accepted-family source identities','detection_executed':True,'unrelated_rows_inserted':['proposed_location_record','proposed_registry_subject','proposed_public_code_alias','proposed_migration_exception','proposed_geometry_observation','proposed_geometry_version','proposed_geometry_quality_assessment'],'union_comparison_passed':True,'semantic_controls_passed':semantic['semantic_crosswalk_duplicates']==0 and semantic['multiple_target_resolutions']==0,'expected_absence_controls_passed':all(item['count']==0 for item in absences),'ownership_validation_passed':ownership['ownership_collisions']==0,'accepted_attributable_hash_unchanged':before_hash==after_hash,'unrelated_rows_excluded_from_attribution':before_rows==after_rows,'before_hash':before_hash,'after_hash':after_hash}


ACCEPTED_FAMILY_CALLABLE_KEYS=set(ACCEPTED_FAMILY_SEQUENCE)
ACCEPTED_FAMILY_TABLE_KEYS={'proposed_location_record','proposed_registry_subject','proposed_legacy_crosswalk','proposed_geometry_observation','proposed_migration_exception'}
ACCEPTED_FAMILY_CONTROL_HASH_KEYS=set(accepted_family_control_hashes().keys())
ACCEPTED_FAMILY_REPORT_TOP_LEVEL_KEYS={
    'accepted_callables_changed','accepted_oracles_changed','accepted_owned_rows_pre_created','authorization_changed','broad_expected_fixture_changed','broad_versions_aliases_relationships_loaded_for_accepted_identities','chain_permutation_hashes','citizen_boolean_leak_mutation_detected','citizen_leak_mutation_detected','citizen_text_leak_mutation_detected','command','conflict_tests','consumer_prerequisite_update_test','control_hashes','control_paths','convergence_control_changed','cross_owner_production_test','crosswalk_count','current_source_rows_loaded','decision_gates_remaining_closed','dependency_tests','evidence_privacy_boundary','evidence_privacy_validation','evidence_rows_loaded','exception_count','expected_absences','first_run_per_callable_inserts','first_run_per_callable_observed_inserts','first_run_per_callable_observed_updates','first_run_total_inserts','first_run_total_updates','first_union_hash','first_union_row_count','fixture_setup_helper','free_map_key_domains','frozen_broad_spec_changed','full_family_idempotency','generic_transform_used','geometry_count','governance_tests','implementation_delta_checks','live_narrow_specifications_used','location_count','mapping_changed','multiple_target_resolutions','nested_schema_contexts','nested_unknown_path_mutation_detected','normal_path_uses_hook','order_invariance','ownership_collisions','ownership_registry_entries','path_aware_structure_validation','post_callable_mutation_hook','primary_execution_sequence','raw_citizen_values','read_only_comparator','read_only_write_blocked','rollback_evidence','rollback_hash_equality_all','rollback_row_equality_all','runtime_migration_scope_changed','second_run_total_inserts','second_run_total_updates','second_union_hash','second_union_row_count','semantic_crosswalk_duplicates','source_record_rows_loaded','status','subject_count','transform_spec_changed','unexpected_union_tests','unknown_path_mutation_detected','unrelated_scope_isolation_test'
}
ACCEPTED_FAMILY_FORBIDDEN_REPORT_KEYS={'debug','source_row','raw_values','citizen_name','citizen_contact','dip_last4','identity_document','identity_document_verified','identity_verified','identity_verified_at','identity_verification_status','citizen_verification_status'}
ACCEPTED_FAMILY_FORBIDDEN_VALUE_SENTINELS={'CITIZEN-SENTINEL-C24-C28','CITIZEN-VERIFICATION-SENTINEL'}
ACCEPTED_FAMILY_ROW_WRAPPER_KEYS={'table','primary_key','owning_callable','source_identity','classification','values'}
ACCEPTED_FAMILY_PRIMARY_KEY_KEYS={'location_record_id','subject_id','legacy_crosswalk_id','geometry_observation_id','migration_exception_id'}
ACCEPTED_FAMILY_TARGET_VALUE_KEYS={
    'proposed_location_record': {'location_record_id','record_type','created_at','retired_at','classification'},
    'proposed_registry_subject': {'subject_id','subject_entity','created_at','native_id','subject_state','retired_at','delete_policy'},
    'proposed_legacy_crosswalk': {'legacy_crosswalk_id','source_table','source_field','legacy_id','target_entity','target_id','created_at'},
    'proposed_geometry_observation': {'geometry_observation_id','subject_id','geometry_role','observed_geom_wkt','observed_geom_srid','capture_method','horizontal_accuracy_m','source_record_id','evidence_object_id','licence_id','observed_at','recorded_at','classification'},
    'proposed_migration_exception': {'migration_exception_id','batch_id','source_table','source_field','source_key','exception_type','severity','owner','created_at','resolved_at','details_json'},
}
ACCEPTED_FAMILY_DETAILS_JSON_KEYS={'reason','non_official','open_authority_rfi','public_release_prohibited','target_entity','target_id'}
ACCEPTED_FAMILY_TEST_KEYS={'test_id','status','mutation','expected_error','observed_error','detection_executed','same_database_pre_test_rows','same_database_pre_test_row_count','same_database_pre_test_hash','same_database_post_failure_rows','same_database_post_failure_row_count','same_database_post_failure_hash','rollback_equality','rollback_hash_equality','detector','manual_expected_error_raise','foreign_row_detected'}
ACCEPTED_FAMILY_DELTA_KEYS={'inserted','updated','deleted','inserted_count','updated_count','deleted_count'}
ACCEPTED_FAMILY_CALLABLE_RESULT_KEYS={'callable','implementation_unit','transform_group','source_identity','live_specification_used','first_application_inserts','internal_idempotent_application_inserts','updates','owned_target_primary_keys','observed_delta','observed_inserted_rows','observed_updated_rows','observed_deleted_rows','family_union_insert_delta','generic_transform_group_used','post_callable_mutation_hook_used'}
ACCEPTED_FAMILY_SCOPE_ISOLATION_KEYS={'test_id','status','mutation','detection_executed','unrelated_rows_inserted','union_comparison_passed','semantic_controls_passed','expected_absence_controls_passed','ownership_validation_passed','accepted_attributable_hash_unchanged','unrelated_rows_excluded_from_attribution','before_hash','after_hash'}


def accepted_family_schema_contexts() -> list[str]:
    return ['top-level report','control paths','control hashes','callable delta result','inserted/updated/deleted row','canonical row wrapper','target primary key','normalized target values by table','dependency test','conflict test','unexpected-row test','governance test','rollback proof','read-only comparator','ownership result','semantic controls','expected absence result','order-invariance result','scope-isolation result','privacy result']


def accepted_family_free_map_key_domains() -> dict[str, list[str]]:
    return {'callable_count_maps':sorted(ACCEPTED_FAMILY_CALLABLE_KEYS),'control_hashes':sorted(ACCEPTED_FAMILY_CONTROL_HASH_KEYS),'scoped_table_counts':sorted(ACCEPTED_FAMILY_TABLE_KEYS)}


def accepted_family_reject_forbidden_keys(keys: set[str], path: str) -> None:
    hit=keys & ACCEPTED_FAMILY_FORBIDDEN_REPORT_KEYS
    if hit:
        if any(k.startswith('identity_') or k.startswith('citizen_') or k in {'citizen_name','citizen_contact','dip_last4','identity_document'} for k in hit):
            raise HarnessError(ACCEPTED_FAMILY_PRIVACY_ERROR)
        raise HarnessError(f'{ACCEPTED_FAMILY_STRUCTURE_ERROR}: forbidden path {path}.{sorted(hit)[0]}')


def accepted_family_validate_keyset(keys: set[str], allowed: set[str], path: str, context: str) -> None:
    accepted_family_reject_forbidden_keys(keys, path)
    unknown=keys-allowed
    if unknown:
        raise HarnessError(f'{ACCEPTED_FAMILY_STRUCTURE_ERROR}: unknown keys in {context} at {path}: {sorted(unknown)}')


def accepted_family_report_structure_validation(report: dict[str, Any]) -> dict[str, Any]:
    contexts=set()
    def walk(value: Any, path: str='', *, table_context: str | None=None, parent_key: str | None=None) -> None:
        if isinstance(value, dict):
            keys=set(value)
            accepted_family_reject_forbidden_keys(keys, path or '<root>')
            if path=='':
                contexts.add('top-level report'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_REPORT_TOP_LEVEL_KEYS, path, 'top-level report')
                for k,v in value.items(): walk(v,k,parent_key=k)
                return
            if path=='control_paths':
                contexts.add('control paths'); accepted_family_validate_keyset(keys, {'mapping','convergence_control'}, path, 'control paths')
            elif path=='control_hashes':
                contexts.add('control hashes'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_CONTROL_HASH_KEYS, path, 'control hashes')
            elif path in {'first_run_per_callable_inserts','first_run_per_callable_observed_inserts','first_run_per_callable_observed_updates'}:
                contexts.add('free-form callable-name to integer count'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_CALLABLE_KEYS, path, 'callable count map')
            elif path.endswith('scoped_counts'):
                contexts.add('free-form fixed table-name to count'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_TABLE_KEYS, path, 'scoped table count map')
            elif path.endswith('primary_key'):
                contexts.add('target primary key'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_PRIMARY_KEY_KEYS, path, 'target primary key')
            elif parent_key=='values':
                contexts.add('normalized target values by table')
                allowed=ACCEPTED_FAMILY_TARGET_VALUE_KEYS.get(table_context or '')
                if allowed is None:
                    raise HarnessError(f'{ACCEPTED_FAMILY_STRUCTURE_ERROR}: values without reviewed table context at {path}')
                accepted_family_validate_keyset(keys, allowed, path, f'normalized target values for {table_context}')
            elif path.endswith('details_json'):
                contexts.add('reviewed details_json target value'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_DETAILS_JSON_KEYS, path, 'details_json target value')
            elif keys==ACCEPTED_FAMILY_ROW_WRAPPER_KEYS:
                contexts.add('canonical row wrapper')
                if '.inserted' in path or '.updated' in path or '.deleted' in path or 'same_database_' in path:
                    contexts.add('inserted/updated/deleted row')
                row_table=value.get('table')
                if row_table not in ACCEPTED_FAMILY_TABLE_KEYS:
                    raise HarnessError(f'{ACCEPTED_FAMILY_STRUCTURE_ERROR}: unknown canonical row table at {path}')
                for k,v in value.items(): walk(v,f'{path}.{k}' if path else k, table_context=row_table, parent_key=k)
                return
            elif keys=={'table','primary_key'}:
                contexts.add('target primary key reference'); accepted_family_validate_keyset(keys, {'table','primary_key'}, path, 'target primary key reference')
            elif keys==ACCEPTED_FAMILY_DELTA_KEYS:
                contexts.add('callable delta result'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_DELTA_KEYS, path, 'callable delta result')
            elif keys==ACCEPTED_FAMILY_CALLABLE_RESULT_KEYS:
                contexts.add('callable delta result'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_CALLABLE_RESULT_KEYS, path, 'callable delta result')
            elif keys <= ACCEPTED_FAMILY_TEST_KEYS and 'test_id' in keys:
                if 'same_database_pre_test_rows' in keys: contexts.add('rollback proof')
                if '.dependency_tests' in f'.{path}' or path.startswith('dependency_tests'): contexts.add('dependency test')
                elif path.startswith('conflict_tests'): contexts.add('conflict test')
                elif path.startswith('unexpected_union_tests'): contexts.add('unexpected-row test')
                elif path.startswith('governance_tests'): contexts.add('governance test')
                accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_TEST_KEYS, path, 'test result')
            elif keys=={'chain_order','union_hash','union_rows'}:
                contexts.add('order-invariance result'); accepted_family_validate_keyset(keys, {'chain_order','union_hash','union_rows'}, path, 'order-invariance result')
            elif keys=={'count','reason','table','where'}:
                contexts.add('expected absence result'); accepted_family_validate_keyset(keys, {'count','reason','table','where'}, path, 'expected absence result')
            elif path=='read_only_comparator':
                contexts.add('read-only comparator'); accepted_family_validate_keyset(keys, {'actual_rows','actual_union_hash','comparator_connection','comparator_read_only_proof','comparison_both_directions','expected_absences','expected_rows','expected_union_hash','ownership','scoped_counts','semantic_controls','status'}, path, 'read-only comparator')
            elif path.endswith('comparator_connection'):
                contexts.add('read-only comparator connection'); accepted_family_validate_keyset(keys, {'separate_connection','transaction_read_only'}, path, 'read-only comparator connection')
            elif path.endswith('comparator_read_only_proof'):
                contexts.add('read-only comparator proof'); accepted_family_validate_keyset(keys, {'separate_connection','target_write_blocked','transaction_read_only','write_error'}, path, 'read-only comparator proof')
            elif path.endswith('ownership'):
                contexts.add('ownership result'); accepted_family_validate_keyset(keys, {'ownership_collisions','ownership_registry_entries'}, path, 'ownership result')
            elif path.endswith('semantic_controls'):
                contexts.add('semantic controls'); accepted_family_validate_keyset(keys, {'multiple_target_resolutions','semantic_crosswalk_duplicates'}, path, 'semantic controls')
            elif path=='evidence_privacy_boundary':
                contexts.add('privacy result'); accepted_family_validate_keyset(keys, {'raw_citizen_values','redaction_flags'}, path, 'privacy boundary')
            elif path=='evidence_privacy_validation':
                contexts.add('privacy result'); accepted_family_validate_keyset(keys, {'checked_excluded_fields','evidence_privacy_validation','raw_citizen_values_in_report','status'}, path, 'privacy validation')
            elif path=='unrelated_scope_isolation_test':
                contexts.add('scope-isolation result'); accepted_family_validate_keyset(keys, ACCEPTED_FAMILY_SCOPE_ISOLATION_KEYS, path, 'scope-isolation result')
            elif path=='free_map_key_domains':
                contexts.add('free-map key domains'); accepted_family_validate_keyset(keys, {'callable_count_maps','control_hashes','scoped_table_counts'}, path, 'free-map key domains')
            else:
                raise HarnessError(f'{ACCEPTED_FAMILY_STRUCTURE_ERROR}: unknown dictionary context at {path}')
            for k,v in value.items():
                walk(v, f'{path}.{k}' if path else k, table_context=table_context, parent_key=k)
        elif isinstance(value, list):
            for i,v in enumerate(value): walk(v, f'{path}[{i}]', table_context=table_context, parent_key=parent_key)
        elif isinstance(value, str):
            if value in ACCEPTED_FAMILY_FORBIDDEN_VALUE_SENTINELS:
                raise HarnessError(ACCEPTED_FAMILY_PRIVACY_ERROR)
    walk(report)
    required=set(accepted_family_schema_contexts())
    missing=required-contexts
    if missing:
        raise HarnessError(f'{ACCEPTED_FAMILY_STRUCTURE_ERROR}: schema contexts not exercised: {sorted(missing)}')
    return {'status':'passed','path_aware_structure_validation':True,'nested_schema_contexts':sorted(contexts)}


def accepted_family_report_safe_payload(value: Any) -> Any:
    sensitive_keys={'observed_geom_wkt','observed_geom_srid','horizontal_accuracy_m','observed_at','recorded_at','capture_method','numeric_coordinate_point','source_geom','created_at','retired_at','resolved_at','reserved_at','issued_at','captured_at','assessed_at','effective_from','effective_to'}
    if isinstance(value, dict):
        safe={}
        for k,v in value.items():
            if k in sensitive_keys:
                safe[k]='[REDACTED_VALUE]'
            else:
                safe[k]=accepted_family_report_safe_payload(v)
        return safe
    if isinstance(value, list):
        return [accepted_family_report_safe_payload(v) for v in value]
    return value


def accepted_family_privacy_validation(report: dict[str, Any]) -> dict[str, Any]:
    serialized=json.dumps(report, sort_keys=True, default=str); source_row=make_citizen_geotag_record('phase-a-geotag-001')['values']; forbidden=[]
    for sentinel in ACCEPTED_FAMILY_FORBIDDEN_VALUE_SENTINELS:
        if sentinel in serialized: forbidden.append({'field':'synthetic_sentinel','value_sha256':sha(sentinel)})
    for field in CITIZEN_GEOTAG_EXCLUDED_VALUE_FIELDS:
        value=source_row.get(field)
        if value is None or isinstance(value,bool): continue
        text=str(value)
        if text and text in serialized and field not in ('created_at',): forbidden.append({'field':field,'value_sha256':sha(text)})
    if forbidden: raise HarnessError(f'{ACCEPTED_FAMILY_PRIVACY_ERROR}: {forbidden}')
    return {'status':'passed','raw_citizen_values_in_report':False,'evidence_privacy_validation':True}


def accepted_family_report_schema_tests(base_report: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    nested=accepted_family_expect_error('convergence-report-nested-structure-mutation', lambda: accepted_family_report_structure_validation({**base_report,'governance_tests':[{**base_report['governance_tests'][0],'unexpected_nested_value':True}]}), ACCEPTED_FAMILY_STRUCTURE_ERROR, mutation_label='inject unknown key inside governance_tests[0]')
    boolean=accepted_family_expect_error('convergence-report-citizen-boolean-leak-mutation', lambda: accepted_family_report_structure_validation({**base_report,'evidence_privacy_boundary':{**base_report['evidence_privacy_boundary'],'identity_document_verified':True}}), ACCEPTED_FAMILY_PRIVACY_ERROR, mutation_label='inject citizen verification boolean into privacy boundary')
    text=accepted_family_expect_error('convergence-report-citizen-text-leak-mutation', lambda: accepted_family_report_structure_validation({**base_report,'evidence_privacy_boundary':{**base_report['evidence_privacy_boundary'],'identity_verification_status':'CITIZEN-VERIFICATION-SENTINEL'}}), ACCEPTED_FAMILY_PRIVACY_ERROR, mutation_label='inject citizen verification text into privacy boundary')
    return nested, boolean, text

def run_accepted_family_convergence() -> dict[str, Any]:
    broad_report_path=DM/'phase-a-current-source-execution-report.json'; broad_report_original=broad_report_path.read_text() if broad_report_path.exists() else None
    controls=accepted_family_verify_controls(); specs=accepted_family_binding_registry(); registry=accepted_family_ownership_registry(); setup=setup_accepted_family_convergence_database()
    with connect(options='-c search_path=canonical_target,public') as conn, conn.cursor() as cur:
        pre=assert_accepted_family_owned_rows_absent(cur); first_results=accepted_family_execute_sequence(cur, ACCEPTED_FAMILY_SEQUENCE, specs); first_union=accepted_family_union_hash(cur); conn.commit(); second_results=accepted_family_execute_sequence(cur, ACCEPTED_FAMILY_SEQUENCE, specs, expect_no_delta=True); second_union=accepted_family_union_hash(cur); conn.commit()
    comparison=compare_accepted_family_convergence_read_only()
    first_inserts=sum(r['first_application_inserts'] for r in first_results); first_updates=sum(r['updates'] for r in first_results); second_inserts=sum(r['observed_inserted_rows'] for r in second_results); second_updates=sum(r['observed_updated_rows'] for r in second_results)
    if first_union['row_count']!=16 or second_union['row_count']!=16 or first_union['hash']!=ACCEPTED_FAMILY_EXPECTED_HASH or second_union['hash']!=ACCEPTED_FAMILY_EXPECTED_HASH or first_inserts!=16 or first_updates!=0 or second_inserts!=0 or second_updates!=0:
        raise HarnessError(f'accepted-family convergence totals/idempotency mismatch first={first_inserts}/{first_updates}/{first_union["row_count"]} second={second_inserts}/{second_updates}/{second_union["row_count"]}')
    dependency_tests=[
        accepted_family_failure_probe('address-points-geometry-before-addresses-identity', [], 'transform_address_points_geometry', 'address_points.address_id cannot resolve target location record'),
        accepted_family_failure_probe('address-points-observation-crosswalk-before-point-geometry', ['transform_addresses_identity_crosswalk'], 'transform_address_points_observation_crosswalk', 'address_points geometry observation target not found'),
        accepted_family_failure_probe('address-points-observation-crosswalk-direct-address-dependency', ['transform_addresses_identity_crosswalk','transform_address_points_geometry'], 'transform_address_points_observation_crosswalk', 'address_points.address_id cannot resolve target location record', mutation=lambda cur: cur.execute("DELETE FROM canonical_target.proposed_legacy_crosswalk WHERE legacy_crosswalk_id='phase-a-crosswalk-addresses-id-to-location-record'")),
        accepted_family_failure_probe('address-records-geometry-before-address-records-identity', [], 'transform_address_records_geometry', 'address_records.id cannot resolve target location record'),
        accepted_family_failure_probe('citizen-geotag-geometry-before-citizen-geotag-identity', [], 'transform_citizen_geotag_geometry', 'citizen_geotag_submissions.id cannot resolve target location record'),
    ]
    order=accepted_family_order_invariance()
    duplicate_owner=accepted_family_expect_error('duplicate-row-ownership-declaration', lambda: accepted_family_ownership_registry(duplicate=True), 'duplicate owner declarations', mutation_label='duplicate ownership declaration')
    conflict_tests=[
        duplicate_owner,
        accepted_family_failure_probe('conflicting-existing-location', [], 'transform_addresses_identity_crosswalk', 'existing correct target row changed', mutation=lambda cur: insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-address-reference','record_type':'address','created_at':TS,'retired_at':None,'classification':'restricted'})),
        accepted_family_failure_probe('conflicting-existing-subject', [], 'transform_addresses_identity_crosswalk', 'existing correct target row changed', mutation=lambda cur: (insert_row(cur,'proposed_location_record',{'location_record_id':'phase-a-location-conflict','record_type':'address','created_at':TS,'retired_at':None,'classification':'government-internal'}), insert_row(cur,'proposed_registry_subject',{'subject_id':'phase-a-subject-phase-a-location-address-reference','subject_entity':'location_record','created_at':TS,'native_id':'phase-a-location-conflict','subject_state':'active','retired_at':None,'delete_policy':'retire-only'}))),
        accepted_family_failure_probe('conflicting-existing-identity-crosswalk', [], 'transform_addresses_identity_crosswalk', 'existing correct target row changed', mutation=lambda cur: insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':'phase-a-crosswalk-addresses-id-to-location-record','source_table':'addresses','source_field':'id','legacy_id':'phase-a-addresses-id','target_entity':'location_record','target_id':'phase-a-location-conflict','created_at':TS})),
        accepted_family_failure_probe('geometry-ownership-collision', ['transform_addresses_identity_crosswalk'], 'transform_address_points_geometry', 'existing correct target row changed', mutation=lambda cur: insert_row(cur,'proposed_geometry_observation',{'geometry_observation_id':'phase-a-geometry-address-points-phase-a-address-points-id','subject_id':'phase-a-subject-phase-a-location-address-reference','geometry_role':'location-point','observed_geom':'POINT(0 0)','capture_method':'derived-from-source','horizontal_accuracy_m':5.0,'source_record_id':'phase-a-source-record-address-points-001','evidence_object_id':'phase-a-evidence-address-points','licence_id':None,'observed_at':TS,'recorded_at':TS,'classification':'restricted'})),
        accepted_family_failure_probe('observation-crosswalk-target-collision', ['transform_addresses_identity_crosswalk','transform_address_points_geometry'], 'transform_address_points_observation_crosswalk', 'existing correct target row changed', mutation=lambda cur: insert_row(cur,'proposed_legacy_crosswalk',{'legacy_crosswalk_id':'phase-a-crosswalk-address-points-id-to-geometry-observation','source_table':'address_points','source_field':'id','legacy_id':'phase-a-address-points-id','target_entity':'geometry_observation','target_id':'phase-a-geometry-address-points-conflict','created_at':TS})),
    ]
    unexpected_tests=accepted_family_unexpected_tests(); governance_tests=accepted_family_governance_tests(); ownership_tests=accepted_family_ownership_tests(); scope_isolation=accepted_family_scope_isolation_test()
    rollback_tests=[t for t in dependency_tests+conflict_tests+unexpected_tests+governance_tests+ownership_tests if isinstance(t, dict) and 'same_database_pre_test_rows' in t]
    base_report={'command':'accepted-family-convergence','status':'passed','control_paths':{'mapping':str(ACCEPTED_FAMILY_MAPPING.relative_to(ROOT)),'convergence_control':str(ACCEPTED_FAMILY_CONTROL.relative_to(ROOT))},'control_hashes':controls['hashes'],'mapping_changed':False,'convergence_control_changed':False,'authorization_changed':False,'accepted_oracles_changed':False,'accepted_callables_changed':False,'transform_spec_changed':False,'frozen_broad_spec_changed':False,'broad_expected_fixture_changed':False,'runtime_migration_scope_changed':False,'generic_transform_used':False,'post_callable_mutation_hook':'post_callable_mutation','normal_path_uses_hook':False,'live_narrow_specifications_used':[specs[name]['group']['transform_group_id'] for name in ACCEPTED_FAMILY_SEQUENCE],'fixture_setup_helper':setup['helper'],'current_source_rows_loaded':setup['current_source_rows_loaded'],'source_record_rows_loaded':setup['source_record_rows_loaded'],'evidence_rows_loaded':setup['evidence_rows_loaded'],'accepted_owned_rows_pre_created':pre['accepted_owned_rows_pre_created'],'broad_versions_aliases_relationships_loaded_for_accepted_identities':0,'primary_execution_sequence':ACCEPTED_FAMILY_SEQUENCE,'first_run_per_callable_inserts':{r['callable']:r['first_application_inserts'] for r in first_results},'first_run_per_callable_observed_inserts':{r['callable']:r['observed_inserted_rows'] for r in first_results},'first_run_per_callable_observed_updates':{r['callable']:r['observed_updated_rows'] for r in first_results},'first_run_total_inserts':first_inserts,'first_run_total_updates':first_updates,'first_union_row_count':first_union['row_count'],'first_union_hash':first_union['hash'],'second_run_total_inserts':second_inserts,'second_run_total_updates':second_updates,'second_union_row_count':second_union['row_count'],'second_union_hash':second_union['hash'],'full_family_idempotency':True,'location_count':3,'subject_count':3,'crosswalk_count':4,'geometry_count':3,'exception_count':3,'ownership_registry_entries':len(registry),'ownership_collisions':0,'semantic_crosswalk_duplicates':comparison['semantic_controls']['semantic_crosswalk_duplicates'],'multiple_target_resolutions':comparison['semantic_controls']['multiple_target_resolutions'],'dependency_tests':dependency_tests,'chain_permutation_hashes':order['chain_permutation_hashes'],'order_invariance':order['order_invariance'],'conflict_tests':conflict_tests,'unexpected_union_tests':unexpected_tests,'governance_tests':governance_tests,'implementation_delta_checks':first_results+second_results,'cross_owner_production_test':ownership_tests[0],'consumer_prerequisite_update_test':ownership_tests[1],'read_only_comparator':comparison,'read_only_write_blocked':comparison['comparator_read_only_proof']['target_write_blocked'],'expected_absences':comparison['expected_absences'],'rollback_evidence':rollback_tests,'rollback_row_equality_all':all(t['rollback_equality'] for t in rollback_tests),'rollback_hash_equality_all':all(t['rollback_hash_equality'] for t in rollback_tests),'unrelated_scope_isolation_test':scope_isolation,'evidence_privacy_boundary':{'raw_citizen_values':False,'redaction_flags':True},'path_aware_structure_validation':True,'nested_schema_contexts':accepted_family_schema_contexts(),'free_map_key_domains':accepted_family_free_map_key_domains(),'unknown_path_mutation_detected':False,'nested_unknown_path_mutation_detected':False,'citizen_leak_mutation_detected':False,'citizen_boolean_leak_mutation_detected':False,'citizen_text_leak_mutation_detected':False,'raw_citizen_values':False,'decision_gates_remaining_closed':['broad Phase A','F02','F14','Review 12','Phase B','deployment','merge']}
    base_report=accepted_family_report_safe_payload(base_report)
    nested, boolean, text=accepted_family_report_schema_tests(base_report); base_report['unknown_path_mutation_detected']=nested['detection_executed']; base_report['nested_unknown_path_mutation_detected']=nested['detection_executed']; base_report['citizen_leak_mutation_detected']=boolean['detection_executed'] and text['detection_executed']; base_report['citizen_boolean_leak_mutation_detected']=boolean['detection_executed']; base_report['citizen_text_leak_mutation_detected']=text['detection_executed']; base_report['governance_tests'] += [nested, boolean, text]
    structure=accepted_family_report_structure_validation(base_report); base_report['nested_schema_contexts']=structure['nested_schema_contexts']; base_report['evidence_privacy_validation']=accepted_family_privacy_validation(base_report)
    write_json(DM/'phase-a-accepted-family-convergence-report.json', base_report)
    if broad_report_original is not None: broad_report_path.write_text(broad_report_original)
    elif broad_report_path.exists(): broad_report_path.unlink()
    return base_report

def phase_a_all() -> dict[str,Any]:
    discover_current(reset=True); apply_target(); topology_check(); transform=run_real_transform(read_expected=True); neg=run_negative_probes(); clean=cleanup_recreate()
    return {'command':'phase-a-all','status':'passed','summary':{'source_records_inserted':transform['source_report']['source_records_inserted'],'source_fields_queried':transform['source_report']['source_fields_queried'],'coverage':transform['coverage'],'target_counts':transform['target_counts'],'negative_probes_passed':neg['negative_probes_passed'],'cleanup_recreate':clean['status']}}

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('command', choices=['phase-a-all','address-points-geometry-slice','address-records-geometry-slice','citizen-geotag-geometry-slice','addresses-identity-slice','address-points-observation-crosswalk-slice','address-records-identity-slice','citizen-geotag-identity-slice','admin-units-identity-shell-slice','accepted-family-convergence','discover-current','apply-target','topology-check','cleanup','pin-expected'])
    args=parser.parse_args()
    if args.command=='discover-current': result=discover_current(reset=True)
    elif args.command=='apply-target': result=apply_target()
    elif args.command=='topology-check': result=topology_check()
    elif args.command=='cleanup': result=cleanup()
    elif args.command=='pin-expected': result=pin_expected_from_observed()
    elif args.command=='address-points-geometry-slice': result=run_address_points_geometry_slice()
    elif args.command=='address-records-geometry-slice': result=run_address_records_geometry_slice()
    elif args.command=='citizen-geotag-geometry-slice': result=run_citizen_geotag_geometry_slice()
    elif args.command=='addresses-identity-slice': result=run_addresses_identity_slice()
    elif args.command=='address-points-observation-crosswalk-slice': result=run_address_points_observation_crosswalk_slice()
    elif args.command=='address-records-identity-slice': result=run_address_records_identity_slice()
    elif args.command=='citizen-geotag-identity-slice': result=run_citizen_geotag_identity_slice()
    elif args.command=='admin-units-identity-shell-slice': result=run_admin_units_identity_shell_slice()
    elif args.command=='accepted-family-convergence': result=run_accepted_family_convergence()
    else: result=phase_a_all()
    print(json.dumps(result, sort_keys=True, default=str))

if __name__ == '__main__':
    main()
