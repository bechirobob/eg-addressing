#!/usr/bin/env python3
from __future__ import annotations
import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
from typing import Any, Callable

ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs'/'sda'/'data-model'
REPORT=DM/'semantic-mutation-test-report.json'
REPORT_MD=DM/'semantic-mutation-test-report.md'

def load(p:Path)->Any: return json.loads(p.read_text(encoding='utf-8'))
def write(p:Path,d:Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(d,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def md_table(headers,rows): return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('|','\\|') for c in r)+' |' for r in rows)+'\n'

def copy_workspace(tmp:Path)->Path:
    work=tmp/'repo'
    (work/'docs'/'sda').mkdir(parents=True)
    shutil.copytree(DM, work/'docs'/'sda'/'data-model')
    reviews=ROOT/'docs'/'sda'/'reviews'
    if reviews.exists(): shutil.copytree(reviews, work/'docs'/'sda'/'reviews')
    return work

def mutate_json(path:Path, fn:Callable[[Any],None]):
    data=load(path); fn(data); write(path,data)

def m_wrong_transform(work):
    p=work/'docs/sda/data-model/review09-transform-implementation-reviewed.json'
    mutate_json(p, lambda d: d['fixtures'][0]['transforms'][0].update({'operation':'formal-exception'}))
def m_expected_mismatch(work):
    p=work/'docs/sda/data-model/review09-expected-target-fixtures-reviewed.json'
    mutate_json(p, lambda d: d['fixtures'][0]['target_rows'][0].update({'expected_target_value':'__wrong_expected__'}))
def m_missing_archive_fk(work):
    p=work/'docs/sda/data-model/review09-transform-implementation-reviewed.json'
    def fn(d):
        for g in d['fixtures']:
            for t in g['transforms']:
                if t.get('requires_archive') or t.get('requires_final_fk'):
                    t['requires_archive']=False; t['requires_final_fk']=False; return
    mutate_json(p, fn)
def m_wrong_classification(work):
    p=work/'docs/sda/data-model/openapi-expected-contracts-reviewed.json'
    mutate_json(p, lambda d: d['contracts'][0]['fields'][0].update({'classification_owner':''}))
def m_cardinality_source_defect(work):
    p=work/'docs/sda/data-model/review08-f04-f07-integrity-report.json'
    mutate_json(p, lambda d: d['summary'].update({'status':'failed','errors':['cardinality source defect']}))
def m_temporal_defect(work):
    p=work/'docs/sda/data-model/review08-f04-f07-integrity-report.json'
    mutate_json(p, lambda d: d['F05']['negative_tests']['overlap'].update({'status':'passed-invalidly'}))
def m_geometry_authority(work):
    p=work/'docs/sda/data-model/review08-f04-f07-integrity-report.json'
    mutate_json(p, lambda d: d['F06']['trigger_text_checks'].update({'geometry promotion actor lacks required permission':False}))
def m_lifecycle_defect(work):
    p=work/'docs/sda/data-model/review08-f04-f07-integrity-report.json'
    mutate_json(p, lambda d: d['summary'].update({'f07_lifecycle_edges':0}))
def m_api_drift(work):
    p=work/'docs/sda/data-model/openapi-observed-response-fixtures-reviewed.json'
    def fn(d):
        d['observed_operations']=d['observed_operations'][1:]
    mutate_json(p, fn)
def m_scenario_history(work):
    p=next((work/'docs/sda/data-model/review09/scenarios').glob('*/expected.json'))
    mutate_json(p, lambda d: d['expected']['entity_counts'].update({'__wrong__':999}))
def m_negative_harness(work):
    p=work/'docs/sda/data-model/target-schema-catalog.json'
    mutate_json(p, lambda d: d['report']['negative_harness_regression'].update({'status':'failed'}))

CASES=[
 ('wrong-transformation-logic',m_wrong_transform,'target-value'),
 ('expected-versus-observed-transform-mismatch',m_expected_mismatch,'target-value'),
 ('missing-archive-or-real-fk',m_missing_archive_fk,'archive-created'),
 ('wrong-classification',m_wrong_classification,'classification owner'),
 ('cardinality-source-defect',m_cardinality_source_defect,'integrity report'),
 ('temporal-cycle-owner-overlap-backdated-defect',m_temporal_defect,'F05'),
 ('weakened-typed-geometry-authority',m_geometry_authority,'F06'),
 ('lifecycle-graph-contextual-authorization-defect',m_lifecycle_defect,'F07'),
 ('observed-versus-expected-api-drift',m_api_drift,'missing observed handler response fixture'),
 ('incorrect-scenario-projection-history',m_scenario_history,'entity_counts'),
 ('negative-harness-false-pass-regression',m_negative_harness,'negative harness'),
]

def run_chain(work:Path)->tuple[int,str]:
    env=os.environ.copy(); env.setdefault('DATABASE_URL', os.environ.get('DATABASE_URL',''))
    py = str(ROOT / '.venv-api-test' / 'bin' / 'python') if (ROOT / '.venv-api-test' / 'bin' / 'python').exists() else sys.executable
    cmds=[
        [py,'docs/sda/data-model/scripts/review09_f02_independent_transform.py'],
        [py,'docs/sda/data-model/scripts/review09_api_contract_comparison.py'],
        [py,'docs/sda/data-model/scripts/review09_scenario_comparison.py'],
        [py,'docs/sda/data-model/scripts/design_consistency_check.py'],
    ]
    out=[]
    for cmd in cmds:
        cp=subprocess.run(cmd,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
        out.append('$ '+' '.join(cmd)+'\n'+cp.stdout[-4000:])
        if cp.returncode!=0: return cp.returncode,'\n'.join(out)
    return 0,'\n'.join(out)

def main():
    results=[]
    for name,mutator,reason in CASES:
        with tempfile.TemporaryDirectory(prefix='r09-mut-') as td:
            work=copy_workspace(Path(td)); mutator(work)
            code,out=run_chain(work)
            matched=code!=0 and reason.lower() in out.lower()
            results.append({'mutation':name,'expected_reason':reason,'exit_code':code,'status':'passed' if matched else 'failed','observed_excerpt':out[-1500:]})
    failed=[r for r in results if r['status']!='passed']
    report={'summary':{'execution_mode':'review09-temp-repo-disposable-db-full-pipeline-mutations','mutations':len(results),'caught':len(results)-len(failed),'failed':len(failed),'status':'passed' if not failed else 'failed'},'results':results}
    write(REPORT,report)
    REPORT_MD.write_text('# Semantic Mutation Test Report\n\n'+md_table(['Mutation','Status','Expected reason'],[[r['mutation'],r['status'],r['expected_reason']] for r in results]),encoding='utf-8')
    print(json.dumps(report['summary'],sort_keys=True))
    if failed: raise SystemExit(json.dumps(failed[:3],indent=2))
if __name__=='__main__': main()
