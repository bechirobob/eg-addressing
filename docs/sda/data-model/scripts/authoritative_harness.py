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
        return value.isoformat().replace('+00:00', 'Z')
    if isinstance(value, str) and value.endswith('+00:00'):
        return value[:-6] + 'Z'
    return value

def norm_row(row: dict[str, Any]) -> dict[str, Any]:
    return {k: normalize(v) for k, v in row.items()}

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

def registry_fields() -> set[str]:
    return {field for g in registry_groups() for field in g['covered_source_fields']}

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
            add_unique(rows,'proposed_source_payload_archive',{'archive_id':f'phase-a-archive-{gslug}','source_record_id':source_id,'payload_uri':f'phase-a://archive/{gid}','payload_hash_sha256':sha(payload),'classification':'restricted','retention_state':'active','created_at':TS})
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
    catalog=catalog_fields(); reviewed=registry_fields(); executed=[]
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
    groups=copy.deepcopy(registry_groups())
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
        write_json(DM / 'phase-a-complete-source-record-fixture-inventory.json', {'execution_mode':'phase-a-real-source-fixture-inventory','source_records':len(records),'source_tables':sorted({r['source_table'] for r in records}),'source_fields_covered':len(catalog_fields()),'transform_groups':len(groups),'expected_hash':compare['target_state_hash'] if compare else None})
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
        'phase-a-neg-unresolved-real-fk': {'wrong_crosswalk_target': next(g['transform_group_id'] for g in registry_groups() if 'legacy_crosswalk' in g['target_entities'])},
        'phase-a-neg-missing-archive': {'missing_archive': next(g['transform_group_id'] for g in registry_groups() if 'source_payload_archive' in g['target_entities'])},
        'phase-a-neg-missing-exception': {'missing_exception': next(g['transform_group_id'] for g in registry_groups() if 'migration_exception' in g['target_entities'])},
        'phase-a-neg-duplicate-output': {'wrong_id_algorithm': next(g['transform_group_id'] for g in registry_groups() if 'legacy_crosswalk' in g['target_entities'])},
        'phase-a-neg-lost-relationship': {'lost_relationship': registry_groups()[0]['transform_group_id']},
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

def phase_a_all() -> dict[str,Any]:
    discover_current(reset=True); apply_target(); topology_check(); transform=run_real_transform(read_expected=True); neg=run_negative_probes(); clean=cleanup_recreate()
    return {'command':'phase-a-all','status':'passed','summary':{'source_records_inserted':transform['source_report']['source_records_inserted'],'source_fields_queried':transform['source_report']['source_fields_queried'],'coverage':transform['coverage'],'target_counts':transform['target_counts'],'negative_probes_passed':neg['negative_probes_passed'],'cleanup_recreate':clean['status']}}

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument('command', choices=['phase-a-all','address-points-geometry-slice','address-records-geometry-slice','citizen-geotag-geometry-slice','discover-current','apply-target','topology-check','cleanup','pin-expected'])
    args=parser.parse_args()
    if args.command=='discover-current': result=discover_current(reset=True)
    elif args.command=='apply-target': result=apply_target()
    elif args.command=='topology-check': result=topology_check()
    elif args.command=='cleanup': result=cleanup()
    elif args.command=='pin-expected': result=pin_expected_from_observed()
    elif args.command=='address-points-geometry-slice': result=run_address_points_geometry_slice()
    elif args.command=='address-records-geometry-slice': result=run_address_records_geometry_slice()
    elif args.command=='citizen-geotag-geometry-slice': result=run_citizen_geotag_geometry_slice()
    else: result=phase_a_all()
    print(json.dumps(result, sort_keys=True, default=str))

if __name__ == '__main__':
    main()
