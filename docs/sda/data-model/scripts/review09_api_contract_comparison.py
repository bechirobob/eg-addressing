#!/usr/bin/env python3
"""Review 10 F08 immutable expected API contract vs current FastAPI/OpenAPI observation.

Expected contracts are reviewed input. Validation never creates or repairs them.
Observed contracts are rebuilt from the current FastAPI app OpenAPI schema on each run.
"""
from __future__ import annotations
import json, re, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs'/'sda'/'data-model'
EXPECTED=DM/'openapi-expected-contracts-reviewed.json'
OBSERVED=DM/'openapi-observed-response-fixtures-reviewed.json'
CONTRACTS_OUT=DM/'openapi-reviewed-projection-contracts.json'
ASSERTIONS_OUT=DM/'openapi-policy-projection-assertions.json'
FORBIDDEN_FALLBACKS={'response.body.id','response.body.status'}
SENSITIVE=('authorization','cookie','token','password','csrf','session')

def load(path:Path)->Any: return json.loads(path.read_text(encoding='utf-8'))
def write(path:Path,data:Any)->None: path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def normalize_contracts(raw:Any)->dict[str,Any]:
    if isinstance(raw,dict) and 'contracts' in raw: return {c['operation_id']:c for c in raw['contracts']}
    if isinstance(raw,dict): return raw
    raise SystemExit('contract source must be object keyed by operation_id or contracts[]')
def require_reviewed_inputs()->None:
    missing=[str(EXPECTED.relative_to(ROOT))] if not EXPECTED.exists() else []
    if missing: raise SystemExit('Review 10 F08 validation missing required reviewed input(s): '+', '.join(missing))

def schema_type(schema:dict[str,Any])->str:
    if '$ref' in schema: return 'object'
    if 'type' in schema: return str(schema['type'])
    if 'anyOf' in schema or 'oneOf' in schema: return 'union'
    return 'object'

def resolve(schema:dict[str,Any], components:dict[str,Any])->dict[str,Any]:
    if '$ref' in schema:
        name=schema['$ref'].split('/')[-1]
        return components.get(name,{})
    return schema

def flatten_schema(prefix:str, schema:dict[str,Any], components:dict[str,Any], required_parent:set[str]|None=None, limit:int=80)->list[dict[str,Any]]:
    schema=resolve(schema or {}, components)
    required=set(schema.get('required') or [])
    props=schema.get('properties') or {}
    if not props:
        return [{'field':prefix,'type':schema_type(schema),'required':'true' if required_parent is None else 'false'}]
    out=[]
    for name,sub in sorted(props.items()):
        field=f'{prefix}.{name}' if prefix else name
        sub_res=resolve(sub or {}, components)
        if (sub_res.get('properties') or {}) and len(out)<limit:
            nested=flatten_schema(field, sub_res, components, required, limit)
            out.extend(nested[:max(0,limit-len(out))])
        else:
            out.append({'field':field,'type':schema_type(sub_res),'required':'true' if name in required else 'false'})
        if len(out)>=limit: break
    return out

def observe_openapi()->dict[str,Any]:
    sys.path.insert(0,str(ROOT/'services/api'))
    from app.main import app  # type: ignore
    schema=app.openapi(); components=schema.get('components',{}).get('schemas',{})
    observed=[]
    for path,methods in sorted(schema['paths'].items()):
        for method,op in sorted(methods.items()):
            if method not in {'get','post','put','patch','delete'}: continue
            oid=op['operationId']; req_fields=[]; resp_fields=[]
            for p in op.get('parameters') or []:
                direction='request:parameter' if p.get('in')!='header' else 'request:header'
                req_fields.append({'direction':direction,'field':p['name'],'type':schema_type(p.get('schema') or {}),'required':'true' if p.get('required') else 'false','evidence_source':'review10-fastapi-openapi-operation-schema'})
            rb=op.get('requestBody') or {}
            content=rb.get('content') or {}
            for media,body in sorted(content.items()):
                if 'json' in media:
                    for f in flatten_schema('request.body', body.get('schema') or {}, components):
                        f.update({'direction':'request:body','evidence_source':'review10-fastapi-openapi-operation-schema'}); req_fields.append(f)
            for status,resp in sorted((op.get('responses') or {}).items()):
                content=(resp or {}).get('content') or {}
                if status == '204':
                    resp_fields.append({'direction':'response:204','field':'response.no_body','type':'none','required':'true','evidence_source':'review10-fastapi-openapi-operation-schema'})
                    continue
                for media,body in sorted(content.items()):
                    if 'json' in media:
                        schema_obj=body.get('schema') or {}
                        fields=flatten_schema('response.body', schema_obj, components)
                        for f in fields:
                            f.update({'direction':f'response:{status}','evidence_source':'review10-fastapi-openapi-operation-schema'}); resp_fields.append(f)
                if status.startswith(('4','5')) and not any(f['direction']==f'response:{status}' for f in resp_fields):
                    resp_fields.append({'direction':f'response:{status}','field':'response.body.detail','type':'string','required':'false','evidence_source':'review10-fastapi-openapi-operation-schema'})
            observed.append({'operation_id':oid,'method':method.upper(),'path':path,'handler':op.get('operationId'),'evidence_source':'review10-current-fastapi-openapi-observation','request_fields':sorted(req_fields,key=lambda x:(x['direction'],x['field'])),'response_fields':sorted(resp_fields,key=lambda x:(x['direction'],x['field']))})
    return {'version':'review10','observed_operations':observed}

def field_key(f:dict[str,Any])->tuple[str,str]: return (str(f.get('direction')),str(f.get('field')))
def compatible_type(expected:str, observed:str)->bool:
    if not expected or expected=='unknown': return True
    if expected==observed: return True
    return expected in {'controlled-fixture-field','reviewed-object-contract'} and observed in {'object','array'}

def main()->None:
    require_reviewed_inputs()
    expected=normalize_contracts(load(EXPECTED))
    observed_raw=observe_openapi()
    write(OBSERVED, observed_raw)
    observed={o['operation_id']:o for o in observed_raw['observed_operations']}
    errors=[]; assertions={}; output_contracts={}
    for oid,contract in sorted(expected.items()):
        obs=observed.get(oid)
        if not obs:
            errors.append(f'{oid} missing observed FastAPI operation')
            continue
        expected_fields=contract.get('fields',[])
        observed_fields=(obs.get('request_fields') or [])+(obs.get('response_fields') or [])
        ekeys={field_key(f) for f in expected_fields}; okeys={field_key(f) for f in observed_fields}
        missing=sorted(ekeys-okeys); extra=sorted(okeys-ekeys)
        if missing: errors.append(f'{oid} missing observed fields {missing[:8]}')
        # Extra observed fields are recorded but not an automatic failure for compatibility; assertions below cover expected fields.
        if not any(str(f.get('direction','')).startswith('response:2') for f in expected_fields): errors.append(f'{oid} unresolved expected success response shape')
        if not any(str(f.get('direction','')).startswith('response:2') for f in observed_fields): errors.append(f'{oid} unresolved observed success response shape')
        observed_by_key={field_key(f):f for f in observed_fields}
        clean_fields=[]
        for f in expected_fields:
            field=f.get('field',''); direction=f.get('direction',''); key=field_key(f); obs_f=observed_by_key.get(key)
            if field in FORBIDDEN_FALLBACKS or 'reviewed_payload' in field or 'field-level expansion' in str(f): errors.append(f'{oid} forbidden/generic field {field}')
            if not f.get('target_projection') or 'pending' in str(f.get('classification_owner','')).lower() or 'pending' in str(f.get('review_owner','')).lower(): errors.append(f'{oid} field {field} lacks accountable owner/target')
            if 'exact reviewed projection target for' in str(f.get('target_projection')) or 'canonical/read-model/release projection' in str(f.get('target_projection')): errors.append(f'{oid} field {field} has generic target projection')
            if not f.get('release_prerequisite') or not f.get('deprecation_rule') or not f.get('test'): errors.append(f'{oid} field {field} lacks release/deprecation/test metadata')
            type_ok=bool(obs_f) and compatible_type(str(f.get('type','')), str(obs_f.get('type','')))
            status='passed' if obs_f and type_ok else 'failed'
            assertions[f.get('test') or f'api-contract::{oid}::{direction}::{field}']={'operation_id':oid,'direction':direction,'field':field,'status':status,'expected_contract_source':str(EXPECTED.relative_to(ROOT)),'observed_fixture_source':str(OBSERVED.relative_to(ROOT)),'observed_type':obs_f.get('type') if obs_f else None,'expected_type':f.get('type'),'evidence_source':'review10-current-fastapi-openapi-observation'}
            if status!='passed': errors.append(f'{oid} field {field} missing or type mismatch in observed FastAPI schema')
            clean_fields.append(f)
        output_contracts[oid]={**contract,'fields':clean_fields,'review_status':'reviewed-api-projection-r10','policy_source':'review10-immutable-expected-contract-vs-fastapi-observation','observed_extra_fields':extra[:80]}
    write(CONTRACTS_OUT, output_contracts)
    summary={'execution_mode':'review10-immutable-expected-api-vs-fastapi-openapi-observation','expected_contract_source':str(EXPECTED.relative_to(ROOT)),'observed_fixture_source':str(OBSERVED.relative_to(ROOT)),'contracts':len(expected),'operations':len(observed),'assertions':len(assertions),'generic_success_payloads':0,'errors':errors[:80],'status':'passed' if not errors else 'failed'}
    write(ASSERTIONS_OUT, {'summary':summary,'assertions':assertions})
    print(json.dumps(summary,sort_keys=True))
    if errors: raise SystemExit('Review 10 API contract comparison failed')
if __name__=='__main__': main()
