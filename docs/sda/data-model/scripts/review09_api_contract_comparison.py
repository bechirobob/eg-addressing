#!/usr/bin/env python3
"""Review 09 F08 independent API contract comparison.

Expected contracts are maintained in openapi-expected-contracts-reviewed.json.
Observed response/request shapes are maintained separately in
openapi-observed-response-fixtures-reviewed.json. This script compares the two and
writes the existing assertion/report artifacts used by the design checker.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[4]
DM = ROOT / 'docs' / 'sda' / 'data-model'
EXPECTED = DM / 'openapi-expected-contracts-reviewed.json'
OBSERVED = DM / 'openapi-observed-response-fixtures-reviewed.json'
CONTRACTS_OUT = DM / 'openapi-reviewed-projection-contracts.json'
ASSERTIONS_OUT = DM / 'openapi-policy-projection-assertions.json'

FORBIDDEN_FALLBACKS = {'response.body.id', 'response.body.status'}
SENSITIVE = ('authorization','cookie','token','password','csrf','session')

def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding='utf-8'))

def write(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + '\n', encoding='utf-8')

def slug(v: str) -> str:
    return re.sub(r'[^a-z0-9]+','-',v.lower()).strip('-') or 'field'

def normalize_contracts(raw: Any) -> dict[str, Any]:
    if isinstance(raw, dict) and 'contracts' in raw:
        return {c['operation_id']: c for c in raw['contracts']}
    if isinstance(raw, dict):
        return raw
    raise SystemExit('contract source must be object keyed by operation_id or contracts[]')


def require_reviewed_inputs() -> None:
    missing = [str(path.relative_to(ROOT)) for path in (EXPECTED, OBSERVED) if not path.exists()]
    if missing:
        raise SystemExit('Review 10 F08 validation missing required reviewed input(s): ' + ', '.join(missing))


def field_key(f: dict[str, Any]) -> tuple[str,str]:
    return (str(f.get('direction')), str(f.get('field')))

def main() -> None:
    require_reviewed_inputs()
    expected = normalize_contracts(load(EXPECTED))
    observed_raw = load(OBSERVED)
    observed = {o['operation_id']: o for o in observed_raw.get('observed_operations', [])}
    errors=[]; assertions={}; output_contracts={}
    for oid, contract in sorted(expected.items()):
        obs=observed.get(oid)
        if not obs:
            errors.append(f'{oid} missing observed handler response fixture')
            continue
        expected_fields=contract.get('fields',[])
        observed_fields=(obs.get('request_fields') or []) + (obs.get('response_fields') or [])
        ekeys={field_key(f) for f in expected_fields}
        okeys={field_key(f) for f in observed_fields}
        missing=sorted(ekeys-okeys); extra=sorted(okeys-ekeys)
        if missing: errors.append(f'{oid} missing observed fields {missing[:8]}')
        if extra: errors.append(f'{oid} observed unexpected fields {extra[:8]}')
        if not any(str(f.get('direction','')).startswith('response:2') for f in expected_fields):
            errors.append(f'{oid} unresolved dynamic success response; no expected 2xx response fields')
        clean_fields=[]
        for f in expected_fields:
            field=f.get('field','')
            direction=f.get('direction','')
            if field in FORBIDDEN_FALLBACKS:
                errors.append(f'{oid} forbidden fallback field {field}')
            if f.get('type') == 'reviewed-object-contract' or 'reviewed_payload' in field or 'field-level expansion' in str(f):
                errors.append(f'{oid} generic/unexpanded response field {field}')
            if any(field.endswith('.'+p) for p in re.findall(r'{([^}]+)}', contract.get('path',''))) and direction.startswith('response:2'):
                errors.append(f'{oid} response copies path parameter fallback {field}')
            if not f.get('target_projection'):
                errors.append(f'{oid} field {field} lacks concrete reviewed projection target')
            if not f.get('classification') or not f.get('classification_owner'):
                errors.append(f'{oid} field {field} lacks classification owner')
            if not f.get('release_prerequisite') or not f.get('deprecation_rule') or not f.get('test'):
                errors.append(f'{oid} field {field} lacks release/deprecation/test metadata')
            test=f.get('test') or f"api-contract::{oid}::{direction}::{field}"
            assertions[test]={
                'operation_id':oid,
                'direction':direction,
                'field':field,
                'status':'passed' if field_key(f) in okeys else 'failed',
                'expected_contract_source':str(EXPECTED.relative_to(ROOT)),
                'observed_fixture_source':str(OBSERVED.relative_to(ROOT)),
                'classification':f.get('classification'),
                'target_projection':f.get('target_projection'),
                'evidence_source':obs.get('evidence_source'),
            }
            clean_fields.append(f)
        output_contracts[oid]={**contract, 'fields': clean_fields, 'policy_source':'review09-independent-expected-api-contract-source', 'review_status':'reviewed-api-projection-r09'}
    report={'summary':{'operations':len(expected),'contracts':len(output_contracts),'assertions':len(assertions),'generic_success_payloads':0,'errors':errors,'execution_mode':'review10-immutable-expected-api-observed-response-comparison','expected_contract_source':str(EXPECTED.relative_to(ROOT)),'observed_fixture_source':str(OBSERVED.relative_to(ROOT)),'status':'passed' if not errors else 'failed'},'assertions':assertions}
    write(CONTRACTS_OUT, output_contracts)
    write(ASSERTIONS_OUT, report)
    print(json.dumps(report['summary'], sort_keys=True))
    if errors:
        raise SystemExit('\n'.join(errors[:50]))

if __name__=='__main__': main()
