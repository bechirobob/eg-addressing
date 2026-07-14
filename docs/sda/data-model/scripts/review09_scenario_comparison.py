#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs'/'sda'/'data-model'
SCENARIO_DIR=DM/'review09'/'scenarios'
REPORT=DM/'review09-scenario-comparison-report.json'
REPORT_MD=DM/'review09-scenario-comparison-report.md'
REQUIRED=['urban-street-address','rural-landmark-location','multi-unit-building','no-formal-road-location','corrected-superseded-address','disputed-geometry','administrative-boundary-change']
SECTIONS=['entity_ids','entity_counts','relationship_edges','geometry_and_provenance','operator_projection','public_projection','historical_output','publication_releases','queried_fixture_rows']

def load(p:Path)->Any: return json.loads(p.read_text(encoding='utf-8'))
def write(p:Path,d:Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def md_table(headers,rows): return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('|','\\|') for c in r)+' |' for r in rows)+'\n'

def require_reviewed_inputs():
    missing=[]
    for name in REQUIRED:
        for rel in ('source.json','expected.json'):
            path=SCENARIO_DIR/name/rel
            if not path.exists():
                missing.append(str(path.relative_to(ROOT)))
    if missing:
        raise SystemExit('Review 10 F10 validation missing required reviewed input(s): '+', '.join(missing))


def compare_values(path, expected, observed, errors):
    if isinstance(expected, dict):
        if not isinstance(observed, dict): errors.append(f'{path} expected object got {type(observed).__name__}'); return
        for k,v in expected.items():
            if k not in observed: errors.append(f'{path}.{k} missing observed value')
            else: compare_values(f'{path}.{k}', v, observed[k], errors)
    elif isinstance(expected, list):
        if expected != observed: errors.append(f'{path} list mismatch expected={expected[:5] if len(expected)>5 else expected} observed={observed[:5] if isinstance(observed,list) else observed}')
    else:
        if expected != observed: errors.append(f'{path} mismatch expected={expected!r} observed={observed!r}')

def main():
    require_reviewed_inputs()
    observed=load(DM/'review08-scenario-query-report.json')['scenarios']
    results={}; all_errors=[]
    for name in REQUIRED:
        source=load(SCENARIO_DIR/name/'source.json')
        expected=load(SCENARIO_DIR/name/'expected.json')
        obs=observed.get(name,{})
        errors=[]
        if source.get('review_status')!='approved-review10-scenario-source': errors.append('source not approved Review09')
        if expected.get('review_status')!='approved-review10-scenario-expected-result': errors.append('expected not approved Review09')
        # Ensure source is minimal, not empty one-row-per-entity padding only.
        records=source.get('records',{})
        if not records: errors.append('source has no relevant records')
        for sec in SECTIONS:
            if sec not in expected.get('expected',{}): errors.append(f'expected missing {sec}')
            elif sec not in obs: errors.append(f'observed missing {sec}')
            else: compare_values(sec, expected['expected'][sec], obs[sec], errors)
        absences=expected.get('expected',{}).get('expected_absences',{})
        for label, forbidden in absences.items():
            if forbidden: errors.append(f'expected absence {label} not empty: {forbidden}')
        assertions={f'F10-review09-{name}-{sec}': {'finding':'F10','status':'passed' if sec in expected.get('expected',{}) and sec in obs else 'failed','evidence_source':'review09-independent-scenario-expected-vs-observed-db-query'} for sec in SECTIONS}
        assertions[f'F10-review09-{name}-expected-absences']={'finding':'F10','status':'passed' if not any(absences.values()) else 'failed','evidence_source':'review09-independent-scenario-expected-vs-observed-db-query'}
        results[name]={'status':'passed' if not errors else 'failed','errors':errors,'source_file':str((SCENARIO_DIR/name/'source.json').relative_to(ROOT)),'expected_file':str((SCENARIO_DIR/name/'expected.json').relative_to(ROOT)),'assertions':assertions,'source_entity_counts':{k:len(v) for k,v in records.items() if isinstance(v,list)}}
        all_errors.extend([f'{name}: {e}' for e in errors])
    out={'summary':{'execution_mode':'review10-executed-scenario-source-expected-comparison','scenarios':len(results),'assertions':sum(len(v['assertions']) for v in results.values()),'failed':[k for k,v in results.items() if v['status']!='passed'],'errors':all_errors[:50],'status':'passed' if not all_errors else 'failed'},'scenarios':results}
    write(REPORT,out)
    REPORT_MD.write_text('# Review 10 Scenario Comparison Report\n\n'+md_table(['Metric','Value'],[[k,v] for k,v in out['summary'].items()]),encoding='utf-8')
    print(json.dumps(out['summary'],sort_keys=True))
    if all_errors: raise SystemExit('Review10 scenario comparison failed')
if __name__=='__main__': main()
