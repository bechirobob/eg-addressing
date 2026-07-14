#!/usr/bin/env python3
from __future__ import annotations
import json, os
from pathlib import Path
from typing import Any
import psycopg
from psycopg.rows import dict_row

ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs'/'sda'/'data-model'
SCENARIO_DIR=DM/'review09'/'scenarios'
REPORT=DM/'review09-scenario-comparison-report.json'
REPORT_MD=DM/'review09-scenario-comparison-report.md'
REQUIRED=['urban-street-address','rural-landmark-location','multi-unit-building','no-formal-road-location','corrected-superseded-address','disputed-geometry','administrative-boundary-change']
SECTIONS=['canonical','effective_as_of','recorded_as_of','public_release','operator_projection','expected_absences']

def load(p:Path)->Any: return json.loads(p.read_text(encoding='utf-8'))
def write(p:Path,d:Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def md_table(headers,rows): return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('|','\\|') for c in r)+' |' for r in rows)+'\n'
def db_url():
    url=os.environ.get('DATABASE_URL')
    if not url: raise SystemExit('DATABASE_URL is required for Review 10 scenario execution')
    return url

def require_reviewed_inputs():
    missing=[]
    for name in REQUIRED:
        for rel in ('source.json','expected.json'):
            path=SCENARIO_DIR/name/rel
            if not path.exists(): missing.append(str(path.relative_to(ROOT)))
    if missing: raise SystemExit('Review 10 F10 validation missing required reviewed input(s): '+', '.join(missing))

def compare_values(path, expected, observed, errors):
    if isinstance(expected, dict):
        if not isinstance(observed, dict): errors.append(f'{path} expected object got {type(observed).__name__}'); return
        for k,v in expected.items():
            if k not in observed: errors.append(f'{path}.{k} missing observed value')
            else: compare_values(f'{path}.{k}', v, observed[k], errors)
    elif isinstance(expected, list):
        if expected != observed: errors.append(f'{path} list mismatch expected={expected} observed={observed}')
    else:
        if expected != observed: errors.append(f'{path} mismatch expected={expected!r} observed={observed!r}')

def setup(cur):
    cur.execute('''DROP TABLE IF EXISTS r10_scenario_entity CASCADE;
    CREATE TEMP TABLE r10_scenario_entity(
      scenario text, entity_id text PRIMARY KEY, entity_type text, label text,
      canonical_state text, effective_from date, effective_to date,
      recorded_from timestamptz, recorded_to timestamptz,
      public_release_date date, operator_visible boolean, public_visible boolean,
      attributes jsonb NOT NULL DEFAULT '{}'::jsonb
    );''')

def insert_source(cur, scenario, source):
    for e in source['entities']:
        cur.execute('INSERT INTO r10_scenario_entity VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)',(
            scenario,e['entity_id'],e['entity_type'],e['label'],e['canonical_state'],e['effective_from'],e.get('effective_to'),e['recorded_from'],e.get('recorded_to'),e.get('public_release_date'),e.get('operator_visible',True),e.get('public_visible',False),json.dumps(e.get('attributes',{}))))

def run_queries(cur, scenario, dates):
    out={}
    cur.execute('SELECT entity_id,entity_type,label,canonical_state FROM r10_scenario_entity WHERE scenario=%s ORDER BY entity_id',(scenario,))
    out['canonical']=[dict(r) for r in cur.fetchall()]
    cur.execute('SELECT entity_id,label FROM r10_scenario_entity WHERE scenario=%s AND effective_from <= %s AND COALESCE(effective_to,\'infinity\') > %s ORDER BY entity_id',(scenario,dates['effective'],dates['effective']))
    out['effective_as_of']=[dict(r) for r in cur.fetchall()]
    cur.execute('SELECT entity_id,label FROM r10_scenario_entity WHERE scenario=%s AND recorded_from <= %s AND COALESCE(recorded_to,\'infinity\') > %s ORDER BY entity_id',(scenario,dates['recorded'],dates['recorded']))
    out['recorded_as_of']=[dict(r) for r in cur.fetchall()]
    cur.execute('SELECT entity_id,label FROM r10_scenario_entity WHERE scenario=%s AND public_visible AND public_release_date <= %s ORDER BY entity_id',(scenario,dates['public_release']))
    out['public_release']=[dict(r) for r in cur.fetchall()]
    cur.execute('SELECT entity_id,entity_type,label,canonical_state,attributes FROM r10_scenario_entity WHERE scenario=%s AND operator_visible ORDER BY entity_id',(scenario,))
    out['operator_projection']=[{**{k:v for k,v in dict(r).items() if k!='attributes'}, 'attributes':r['attributes']} for r in cur.fetchall()]
    out['expected_absences']={}
    return out

def main():
    require_reviewed_inputs()
    results={}; all_errors=[]
    with psycopg.connect(db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            for name in REQUIRED:
                setup(cur)
                source=load(SCENARIO_DIR/name/'source.json')
                expected=load(SCENARIO_DIR/name/'expected.json')
                errors=[]
                if source.get('review_status')!='approved-review10-scenario-source': errors.append('source not approved Review10')
                if expected.get('review_status')!='approved-review10-scenario-expected-result': errors.append('expected not approved Review10')
                insert_source(cur,name,source)
                observed=run_queries(cur,name,expected['query_dates'])
                for sec in SECTIONS:
                    if sec not in expected['expected']: errors.append(f'expected missing {sec}')
                    else: compare_values(sec, expected['expected'][sec], observed.get(sec), errors)
                # Explicit absence queries.
                for absence in expected.get('expected_absence_queries',[]):
                    cur.execute(absence['sql'], tuple(absence.get('params',[])))
                    rows=cur.fetchall()
                    if rows: errors.append(f"absence query {absence['name']} returned {len(rows)} rows")
                assertions={f'F10-review10-{name}-{sec}':{'finding':'F10','status':'passed' if not [e for e in errors if e.startswith(sec)] else 'failed','evidence_source':'review10-fresh-postgresql-scenario-query'} for sec in SECTIONS}
                results[name]={'status':'passed' if not errors else 'failed','errors':errors,'source_file':str((SCENARIO_DIR/name/'source.json').relative_to(ROOT)),'expected_file':str((SCENARIO_DIR/name/'expected.json').relative_to(ROOT)),'query_dates':expected['query_dates'],'assertions':assertions,'observed':observed}
                all_errors.extend([f'{name}: {e}' for e in errors])
                conn.rollback()
    out={'summary':{'execution_mode':'review10-fresh-postgresql-scenario-source-expected-comparison','scenarios':len(results),'assertions':sum(len(v['assertions']) for v in results.values()),'failed':[k for k,v in results.items() if v['status']!='passed'],'errors':all_errors[:80],'status':'passed' if not all_errors else 'failed'},'scenarios':results}
    write(REPORT,out)
    REPORT_MD.write_text('# Review 10 Scenario Comparison Report\n\n'+md_table(['Metric','Value'],[[k,v] for k,v in out['summary'].items()]),encoding='utf-8')
    print(json.dumps(out['summary'],sort_keys=True))
    if all_errors: raise SystemExit('Review10 scenario comparison failed')
if __name__=='__main__': main()
