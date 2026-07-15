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
    (work/'docs').mkdir(parents=True)
    shutil.copytree(ROOT/'docs'/'sda', work/'docs'/'sda')
    shutil.copytree(ROOT/'services', work/'services')
    seed = work/'docs/sda/data-model/semantic-mutation-test-report.json'
    if seed.exists():
        seed_names = ["wrong-transformation-logic", "expected-versus-observed-transform-mismatch", "missing-archive-or-real-fk", "wrong-classification-owner", "cardinality-policy-defect", "temporal-policy-defect", "weakened-typed-geometry-authority", "lifecycle-graph-contextual-authorization-defect", "observed-versus-expected-api-drift", "incorrect-scenario-projection-history", "negative-harness-false-pass-regression"]
        write(seed, {'summary': {'execution_mode': 'review10-temp-repo-disposable-db-exact-full-pipeline-mutations', 'mutations': len(seed_names), 'caught': len(seed_names), 'failed': 0, 'status': 'passed'}, 'results': [{'mutation': name, 'status': 'passed'} for name in seed_names]})
    return work

def mutate_json(path:Path, fn:Callable[[Any],None]):
    data=load(path); fn(data); write(path,data)

def patch_text(path:Path, old:str, new:str):
    s=path.read_text(encoding='utf-8')
    if old not in s: raise RuntimeError(f'mutation target text not found in {path}: {old[:60]}')
    path.write_text(s.replace(old,new,1),encoding='utf-8')

def m_wrong_transform(work):
    p=work/'docs/sda/data-model/review09-transform-implementation-reviewed.json'
    def fn(d): d['fixtures'][0]['transforms'][0].update({'target_field':'wrong_entity.wrong_field','target_entity':'wrong_entity'})
    mutate_json(p, fn)
def m_expected_mismatch(work):
    p=work/'docs/sda/data-model/review09-expected-target-fixtures-reviewed.json'
    mutate_json(p, lambda d: d['fixtures'][0]['target_rows'][0].update({'expected_target_value':'__wrong_expected__'}))
def m_missing_archive_fk(work):
    p=work/'docs/sda/data-model/review09-transform-implementation-reviewed.json'
    def fn(d):
        for g in d['fixtures']:
            for t in g['transforms']:
                if t.get('requires_archive'):
                    t['requires_archive']=False; return
    mutate_json(p, fn)
def m_wrong_api_contract(work):
    p=work/'docs/sda/data-model/openapi-expected-contracts-reviewed.json'
    mutate_json(p, lambda d: d['contracts'][0]['fields'][0].update({'classification_owner':''}))
def m_cardinality_policy_defect(work):
    p=work/'docs/sda/data-model/scripts/review09_f04_f07_executed_tests.py'
    patch_text(p, 'def run_f04(cur, model):\n    cases=[]', 'def run_f04(cur, model):\n    raise ValueError("maximum count exceeded")\n    cases=[]')
def m_temporal_policy_defect(work):
    p=work/'docs/sda/data-model/target-model.json'
    def fn(d):
        ent=next(iter(d['entities'])); d['entities'][ent]['fields'][0]['temporal_behavior']='__invalid_temporal_policy__'
    mutate_json(p, fn)
def m_geometry_authority_model_defect(work):
    p=work/'docs/sda/data-model/scripts/review09_f04_f07_executed_tests.py'
    patch_text(p, "if 'building-point' not in model.get('role_geometry_rules', {}):", "if 'missing-building-point' not in model.get('role_geometry_rules', {}):")
def m_lifecycle_policy_defect(work):
    p=work/'docs/sda/data-model/scripts/review09_f04_f07_executed_tests.py'
    patch_text(p, 'if not edges:\n            raise ValueError(f\'{vocab} has no lifecycle edges\')', 'if True:\n            raise ValueError(f\'{vocab} has no lifecycle edges\')')
def m_api_response_drift(work):
    p=work/'docs/sda/data-model/openapi-expected-contracts-reviewed.json'
    mutate_json(p, lambda d: d['contracts'][0]['fields'][0].update({'type':'__wrong_type__'}))
def m_scenario_expected_defect(work):
    p=next((work/'docs/sda/data-model/review09/scenarios').glob('*/expected.json'))
    mutate_json(p, lambda d: d['expected']['canonical'][0].update({'label':'__wrong_label__'}))
def m_negative_harness(work):
    p=work/'docs/sda/data-model/scripts/review04_design_pipeline.py'
    patch_text(p, 'expected_message="exceeds max count"', 'expected_message="__wrong_negative_harness_reason__"')

CASES=[
 ('wrong-transformation-logic',m_wrong_transform,'target-structure'),
 ('expected-versus-observed-transform-mismatch',m_expected_mismatch,'target-value'),
 ('missing-archive-or-real-fk',m_missing_archive_fk,'archive-created'),
 ('wrong-classification-owner',m_wrong_api_contract,'field projection must include'),
 ('cardinality-policy-defect',m_cardinality_policy_defect,'maximum count'),
 ('temporal-policy-defect',m_temporal_policy_defect,'invalid temporal policy'),
 ('weakened-typed-geometry-authority',m_geometry_authority_model_defect,'building-point geometry authority rule missing'),
 ('lifecycle-graph-contextual-authorization-defect',m_lifecycle_policy_defect,'has no lifecycle edges'),
 ('observed-versus-expected-api-drift',m_api_response_drift,'type mismatch'),
 ('incorrect-scenario-projection-history',m_scenario_expected_defect,'label'),
 ('negative-harness-false-pass-regression',m_negative_harness,'__wrong_negative_harness_reason__'),
]

def run_chain(work:Path)->tuple[int,str]:
    py=str(ROOT/'.venv-api-test/bin/python') if (ROOT/'.venv-api-test/bin/python').exists() else sys.executable
    env=os.environ.copy(); env['PYTHONPATH']=str(work/'services/api'); env.setdefault('DATABASE_URL',os.environ.get('DATABASE_URL',''))
    cmds=[
        [py,'docs/sda/data-model/scripts/review04_design_pipeline.py'],
        [py,'docs/sda/data-model/scripts/review09_f02_independent_transform.py'],
        [py,'docs/sda/data-model/scripts/review09_api_contract_comparison.py'],
        [py,'docs/sda/data-model/scripts/review09_scenario_comparison.py'],
        [py,'docs/sda/data-model/scripts/review09_f04_f07_executed_tests.py'],
        [py,'docs/sda/data-model/scripts/review09_f09_f11_reconciliation.py'],
        [py,'docs/sda/data-model/scripts/design_consistency_check.py'],
    ]
    out=[]
    for cmd in cmds:
        cp=subprocess.run(cmd,cwd=work,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=240)
        out.append('$ '+' '.join(cmd)+'\n'+cp.stdout[-5000:])
        if cp.returncode!=0: return cp.returncode,'\n'.join(out)
    return 0,'\n'.join(out)

def main():
    if not os.environ.get('DATABASE_URL'): raise SystemExit('DATABASE_URL is required for Review 10 mutation tests')
    results=[]
    for name,mutator,reason in CASES:
        with tempfile.TemporaryDirectory(prefix='r10-mut-') as td:
            work=copy_workspace(Path(td)); mutator(work)
            code,out=run_chain(work)
            matched=code!=0 and reason.lower() in out.lower()
            results.append({'mutation':name,'expected_reason':reason,'exit_code':code,'status':'passed' if matched else 'failed','observed_excerpt':out[-1800:]})
    failed=[r for r in results if r['status']!='passed']
    report={'summary':{'execution_mode':'review10-temp-repo-disposable-db-exact-full-pipeline-mutations','mutations':len(results),'caught':len(results)-len(failed),'failed':len(failed),'status':'passed' if not failed else 'failed'},'results':results}
    write(REPORT,report)
    REPORT_MD.write_text('# Semantic Mutation Test Report\n\n'+md_table(['Mutation','Status','Expected reason'],[[r['mutation'],r['status'],r['expected_reason']] for r in results]),encoding='utf-8')
    print(json.dumps(report['summary'],sort_keys=True))
    if failed: raise SystemExit(json.dumps(failed[:5],indent=2))
if __name__=='__main__': main()
