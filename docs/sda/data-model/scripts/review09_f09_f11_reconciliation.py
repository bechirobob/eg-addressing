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
    f04f07=load('review09-f04-f07-executed-test-suite.json')
    scenario=load('review09-scenario-comparison-report.json')
    api=load('openapi-policy-projection-assertions.json')
    mutations=load('semantic-mutation-test-report.json')
    passed={a['assertion_id']:a for a in tx['assertions'] if a.get('status')=='passed'}
    unit_results=[]; errors=[]
    for u in units:
        ids=set(u.get('transform_assertion_ids') or [])
        missing=sorted(ids-set(passed))
        execution_backed=all(passed[i]['evidence'].get('execution_mode')=='review09-independent-source-expected-transform-execution' for i in ids if i in passed)
        final_fk_ok=True
        for i in ids:
            a=passed.get(i)
            if a and a.get('assertion_class')=='reference-final-fk' and not a['evidence'].get('final_canonical_fk'):
                final_fk_ok=False
        status=not missing and execution_backed and final_fk_ok and tx['summary'].get('idempotency_status')=='passed'
        if not status: errors.append(u.get('unit_id'))
        unit_results.append({'unit_id':u.get('unit_id'),'transform_group_id':u.get('transform_group_id'),'assertions':len(ids),'missing':missing,'execution_backed':execution_backed,'final_fk_ok':final_fk_ok,'status':'passed' if status else 'failed'})
    adr_rows=[
        ['ADR-005','identity/public aliases/crosswalk authority','F02/F09','F02-source-row-identity-*; F02-reference-final-fk-*; F02-review09-real-idempotency; F09-review09-convergence-*','review09-source-fixtures-reviewed.json; review09-expected-target-fixtures-reviewed.json; review09-transform-implementation-reviewed.json; transformation-fixture-report.json; review09-f09-f11-reconciliation-report.json','proposed; executable Review 09 evidence passing','NLI-WO-002B unauthorized; owner approval and runtime migration authority still required'],
        ['ADR-006','administrative geography and operational areas','F05/F09/F10','F05-review09-executed-report-passed; F05-admin-boundary-*; F10-review09-independent-scenario-comparison-passed; F10-scenario-*; F09-review09-convergence-*; F09-reviewed-convergence-unit-*','review09-f05-temporal-execution-report.json; review09-scenario-comparison-report.json; review09-f09-f11-reconciliation-report.json','proposed; executable Review 09 evidence passing','official territorial rollout/publication authority remains future SDA decision'],
        ['ADR-007','subject registry and addressable object cardinality','F04/F10','F04-review09-executed-report-passed; F04-cardinality-positive-*; F10-review09-scenario-*; F10-scenario-*','review09-f04-record-role-execution-report.json; review09-scenario-comparison-report.json','proposed; executable Review 09 evidence passing','runtime migration/application changes remain out of scope'],
        ['ADR-008','temporal versioning and supersession','F05/F07/F10/F12','F05-review09-executed-report-passed; F05-admin-boundary-*; F07-review09-lifecycle-graph-report-passed; F07-lifecycle-positive-*; F10-review09-independent-scenario-comparison-passed; F10-scenario-*; F12-mutation-*','review09-f05-temporal-execution-report.json; review09-f07-lifecycle-graph-report.json; review09-scenario-comparison-report.json; semantic-mutation-test-report.json','proposed; executable Review 09 evidence passing','dual-read parity and removal authority require future WO-002B'],
        ['ADR-009','geometry evidence and provenance','F06/F12','F06-review09-executed-report-passed; F06-geometry-authority-*; F12-mutation-weakened-typed-geometry-authority','review09-f06-typed-geometry-authority-report.json; semantic-mutation-test-report.json','proposed; executable Review 09 evidence passing','institutional actors/scopes remain design evidence only until SDA approval'],
    ]
    matrix='# ADR-005 through ADR-009 Review 09 Evidence Matrix\n\nThis matrix keeps ADRs proposed and maps each defining statement to specific independently executable Review 09 assertions/artifacts. It does not authorize NLI-WO-002B, rollout, publication, or runtime migration.\n\n'+md_table(['ADR','Claim/constraint','Finding dependency','Named executable assertions','Evidence artifact','Status','Unresolved condition / RFI'],adr_rows)
    (DM/'adr-005-009-evidence-matrix.md').write_text(matrix,encoding='utf-8')
    report={'summary':{'execution_mode':'review09-f09-f11-revalidation-after-independent-suites','convergence_units':len(units),'units_passed':len([u for u in unit_results if u['status']=='passed']),'adr_rows':len(adr_rows),'f02_execution_mode':tx['summary'].get('execution_mode'),'f02_idempotency':tx['summary'].get('idempotency_status'),'f04_f07_status':f04f07['summary'].get('status'),'f10_status':scenario['summary'].get('status'),'f08_status':api['summary'].get('status'),'f12_status':mutations['summary'].get('status'),'errors':errors,'status':'passed' if not errors and f04f07['summary'].get('status')=='passed' and scenario['summary'].get('status')=='passed' and api['summary'].get('status')=='passed' and mutations['summary'].get('status')=='passed' else 'failed'},'convergence_units':unit_results,'adr_rows':adr_rows}
    write('review09-f09-f11-reconciliation-report.json',report)
    (DM/'review09-f09-f11-reconciliation-report.md').write_text('# Review 09 F09/F11 Reconciliation Report\n\n'+md_table(['Metric','Value'],[[k,v] for k,v in report['summary'].items()]),encoding='utf-8')
    print(json.dumps(report['summary'],sort_keys=True))
    if report['summary']['status']!='passed': raise SystemExit(report['summary'])
if __name__=='__main__': main()
