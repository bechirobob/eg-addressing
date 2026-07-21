#!/usr/bin/env python3
from __future__ import annotations
import json
from pathlib import Path
from typing import Any
ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs'/'sda'/'data-model'

def load(name:str)->Any: return json.loads((DM/name).read_text(encoding='utf-8'))
def write(name:str,data:Any): (DM/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def md_table(headers, rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('|','\\|') for c in r)+' |' for r in rows)+'\n'

def main():
    units=load('schema-convergence-units-reviewed.json')['migration_units']
    tx=load('transformation-fixture-report.json')
    integrity=load('review08-f04-f07-integrity-report.json')
    scenario=load('review08-scenario-query-report.json')
    api=load('openapi-policy-projection-assertions.json')
    mutations=load('semantic-mutation-test-report.json')
    passed={a['assertion_id']:a for a in tx['assertions'] if a.get('status')=='passed'}
    unit_results=[]; errors=[]
    for u in units:
        ids=set(u.get('transform_assertion_ids') or [])
        missing=sorted(ids-set(passed))
        execution_backed=all(passed[i]['evidence'].get('execution_mode')=='review08-disposable-source-to-target-db-execution' for i in ids if i in passed)
        final_fk_ok=True
        for i in ids:
            a=passed.get(i)
            if a and a.get('assertion_class')=='reference-final-fk' and not a['evidence'].get('final_canonical_fk'):
                final_fk_ok=False
        status=not missing and execution_backed and final_fk_ok
        if not status: errors.append(u.get('unit_id'))
        unit_results.append({'unit_id':u.get('unit_id'),'transform_group_id':u.get('transform_group_id'),'assertions':len(ids),'missing':missing,'execution_backed':execution_backed,'final_fk_ok':final_fk_ok,'status':'passed' if status else 'failed'})
    adr_rows=[
        ['ADR-005','identity/public aliases/crosswalk authority','F02/F09','F02-source-row-identity-*; F02-reference-final-fk-*; F09-review08-convergence-*','transformation-fixture-report.json; review08-f09-f11-reconciliation-report.json','proposed; executable evidence passing','NLI-WO-002B unauthorized; owner approval still required'],
        ['ADR-006','administrative geography and operational areas','F05/F09','F05-admin-boundary-old-new-versions; F05-temporal-review08-register; F10-administrative-boundary-change-*; F09-reviewed-convergence-unit-*','review08-f04-f07-integrity-report.json; review08-scenario-query-report.json','proposed; executable evidence passing','official territorial rollout/publication authority remains future SDA decision'],
        ['ADR-007','subject registry and addressable object cardinality','F04/F10','F04-cardinality-positive-record-type-*; F04-cardinality-review08-matrix; F10-scenario-*; F10-review08-query-sections-*','review08-f04-f07-integrity-report.json; review08-scenario-query-report.json','proposed; executable evidence passing','runtime migration/application changes remain out of scope'],
        ['ADR-008','temporal versioning and supersession','F05/F07/F10/F12','F05-temporal-review08-register; F07-lifecycle-positive-*; F07-lifecycle-review08-graph; F12-*','review08-f04-f07-integrity-report.json; semantic-mutation-test-report.json','proposed; executable evidence passing','dual-read parity and removal authority require future WO-002B'],
        ['ADR-009','geometry evidence and provenance','F06/F12','F06-geometry-authority-review08; weakened-geometry-authority mutation','review08-f04-f07-integrity-report.json; semantic-mutation-test-report.json','proposed; executable evidence passing','institutional actors/scopes remain design evidence only'],
    ]
    matrix='# ADR-005 through ADR-009 Review 08 Evidence Matrix\n\nThis matrix preserves ADRs as proposed and ties each defining guarantee to named executable Review 08 assertions. It does not authorize NLI-WO-002B or production/runtime migration.\n\n'+md_table(['ADR','Claim/constraint','Finding dependency','Named executable assertions','Evidence artifact','Status','Unresolved condition / RFI'],adr_rows)
    (DM/'adr-005-009-evidence-matrix.md').write_text(matrix,encoding='utf-8')
    report={'summary':{'execution_mode':'review08-f09-f11-revalidation','convergence_units':len(units),'units_passed':len([u for u in unit_results if u['status']=='passed']),'adr_rows':len(adr_rows),'f02_execution_mode':tx['summary'].get('execution_mode'),'f04_f07_status':integrity['summary'].get('status'),'f10_status':scenario['summary'].get('failed')==[],'f08_assertions':api['summary'].get('assertions'),'f12_status':mutations['summary'].get('status'),'errors':errors,'status':'passed' if not errors else 'failed'},'convergence_units':unit_results,'adr_rows':adr_rows}
    write('review08-f09-f11-reconciliation-report.json',report)
    (DM/'review08-f09-f11-reconciliation-report.md').write_text('# Review 08 F09/F11 Reconciliation Report\n\n'+md_table(['Metric','Value'],[[k,v] for k,v in report['summary'].items()]),encoding='utf-8')
    print(json.dumps(report['summary'],sort_keys=True))
    if errors: raise SystemExit(errors)
if __name__=='__main__': main()
