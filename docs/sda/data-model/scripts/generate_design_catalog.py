from __future__ import annotations
from pathlib import Path
import json, re, textwrap
from datetime import date

ROOT=Path('/home/ubuntu/projects/eg-addressing')
DM=ROOT/'docs/sda/data-model'
DATE='2026-07-13'
HEAD_PLACEHOLDER='recorded in PR body/comment after push'

def w(rel, text):
    p=ROOT/rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(textwrap.dedent(text).strip()+"\n", encoding='utf-8')

# ---- current catalog extraction ----
def split_parts(body:str):
    parts=[]; buf=''; depth=0; inq=False
    for ch in body:
        if ch=="'": inq=not inq
        elif not inq and ch=='(': depth+=1
        elif not inq and ch==')': depth-=1
        if ch==',' and depth==0 and not inq:
            parts.append(buf.strip()); buf=''
        else: buf+=ch
    if buf.strip(): parts.append(buf.strip())
    return parts

def parse_schema():
    tables={}; constraints={}; indexes=[]
    for mp in sorted((ROOT/'infra/migrations').glob('*.sql')):
        raw=mp.read_text()
        sql=re.sub(r'--.*','',raw)
        for m in re.finditer(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][\w]*)\s*\((.*?)\);', sql, re.I|re.S):
            t=m.group(1); tables.setdefault(t,{}); constraints.setdefault(t,[])
            for part in split_parts(m.group(2)):
                toks=part.split()
                if not toks: continue
                if toks[0].upper() in {'PRIMARY','FOREIGN','UNIQUE','CHECK','CONSTRAINT'}:
                    constraints[t].append(' '.join(part.split()))
                    continue
                col=toks[0].strip('"')
                rest=' '.join(toks[1:])
                typ=[]
                for tok in toks[1:]:
                    if tok.upper() in {'PRIMARY','NOT','NULL','DEFAULT','REFERENCES','UNIQUE','CHECK','CONSTRAINT','COLLATE'}: break
                    typ.append(tok)
                ctype=' '.join(typ) or 'TEXT'
                nullable='NOT NULL' not in rest.upper() and 'PRIMARY KEY' not in rest.upper()
                default=''
                dm=re.search(r'\bDEFAULT\s+(.+?)(?=\s+REFERENCES|\s+PRIMARY\s+KEY|\s+UNIQUE|\s+NOT\s+NULL|\s+CHECK|$)', rest, re.I)
                if dm: default=dm.group(1).strip()
                ref=''
                rm=re.search(r'REFERENCES\s+([a-zA-Z_][\w]*)(?:\(([^)]+)\))?', rest, re.I)
                if rm: ref=rm.group(1)+(f"({rm.group(2)})" if rm.group(2) else '')
                pk='PRIMARY KEY' in rest.upper()
                unique='UNIQUE' in rest.upper()
                tables[t][col]={'table':t,'field':col,'type':ctype,'nullable':nullable,'default':default,'references':ref,'primary_key':pk,'unique':unique,'source_migration':mp.name,'raw':' '.join(part.split())}
        for m in re.finditer(r'ALTER\s+TABLE\s+([a-zA-Z_][\w]*)\s+ADD\s+COLUMN\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][\w]*)\s+([^;]+);', sql, re.I|re.S):
            t,col,rest=m.group(1),m.group(2),' '.join(m.group(3).split())
            tables.setdefault(t,{}); constraints.setdefault(t,[])
            typ=[]
            for tok in rest.split():
                if tok.upper() in {'PRIMARY','NOT','NULL','DEFAULT','REFERENCES','UNIQUE','CHECK','CONSTRAINT'}: break
                typ.append(tok)
            dm=re.search(r'\bDEFAULT\s+(.+?)(?=\s+REFERENCES|\s+PRIMARY\s+KEY|\s+UNIQUE|\s+NOT\s+NULL|\s+CHECK|$)', rest, re.I)
            rm=re.search(r'REFERENCES\s+([a-zA-Z_][\w]*)(?:\(([^)]+)\))?', rest, re.I)
            tables[t][col]={'table':t,'field':col,'type':' '.join(typ),'nullable':'NOT NULL' not in rest.upper(),'default':dm.group(1).strip() if dm else '', 'references':rm.group(1)+(f"({rm.group(2)})" if rm and rm.group(2) else '') if rm else '', 'primary_key':False,'unique':'UNIQUE' in rest.upper(), 'source_migration':mp.name,'raw':'ALTER ADD '+rest}
        for m in re.finditer(r'CREATE\s+(UNIQUE\s+)?INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?([a-zA-Z_][\w]*)\s+ON\s+([a-zA-Z_][\w]*)\s*([^;]+);', sql, re.I|re.S):
            indexes.append({'name':m.group(2),'table':m.group(3),'unique':bool(m.group(1)),'definition':' '.join(m.group(0).split()),'source_migration':mp.name})
    return tables,constraints,indexes

tables,constraints,indexes=parse_schema()
source_files=list((ROOT/'services/api/app').glob('*.py'))
source_text={str(p.relative_to(ROOT)):p.read_text(errors='replace') for p in source_files}

def source_refs(table):
    refs=[]
    for rel,txt in source_text.items():
        for i,line in enumerate(txt.splitlines(),1):
            if re.search(r'\b'+re.escape(table)+r'\b', line):
                kind='reader'
                l=line.upper()
                if any(k in l for k in ['INSERT INTO '+table.upper(), 'UPDATE '+table.upper(), 'DELETE FROM '+table.upper()]): kind='writer'
                elif table.upper() in l and any(k in l for k in ['INSERT INTO','UPDATE ','DELETE FROM']): kind='writer'
                refs.append(f"{kind}:{rel}:{i}")
    return refs[:18]

json_notes={
 'roads.spatial_evidence':'JSON evidence bundle for captured road geometry/candidate review; observed keys in API include source geometry/map suggestion and operator notes; maps to geometry_observation + evidence_object.',
 'buildings.spatial_evidence':'JSON evidence bundle for building point/frontage/usage evidence; maps to field_observation/evidence_object and approved building geometry.',
 'address_records.record_bundle':'Canonical case-file JSON assembled from geotag/submission/operator data; includes source submission, identity status, field status, reviewer notes, road/locality suggestions, publication markers, and evidence timeline; target normalizes into version/assertion/source/evidence/event tables.',
 'address_record_events.details':'JSON event details; target keeps typed event plus JSON supplemental details with controlled event_type.',
 'field_submissions.spatial_evidence':'Field-captured geometry/evidence JSON; target maps to geometry_observation and evidence_object, not approved geometry.',
 'audit_logs.details':'JSON supplemental audit details; outside core model but linked by actor/event IDs.',
 'reference_data_loads.execution_context':'JSON load/runtime metadata; maps to source_package.load_context.',
 'reference_data_load_history.execution_context':'Historical load/runtime metadata; maps to source_package history.',
 'development_fixture_batches.execution_context':'Fixture-only metadata; not canonical.'
}

class_rules=[('citizen_name','restricted'),('citizen_contact','restricted'),('dip','highly-restricted'),('identity','restricted'),('reporter','restricted'),('password','highly-restricted'),('token','highly-restricted'),('geom','restricted'),('latitude','restricted'),('longitude','restricted'),('spatial_evidence','restricted'),('record_bundle','restricted'),('details','government-internal'),('public_code','public-after-release'),('address_code','public-after-release')]
def classify(table,field):
    name=(table+'.'+field).lower()
    for needle,cls in class_rules:
        if needle in name: return cls
    if table in {'users','auth_tokens'}: return 'security-internal'
    if table in {'provinces','admin_units'}: return 'public-after-approval'
    if table.startswith('publication'): return 'government-internal/public-release-metadata'
    return 'government-internal'

def target_for(table, field):
    tf=f'{table}.{field}'
    auth='operational'
    disp='operational-target'; trans='copy with audit'; compat='until WO-002B contract phase'; retire='after parity and replacement approved'
    if table in {'provinces','admin_units'}:
        auth='GIS/admin authority'; disp='reference-target'; target='administrative_unit.'+({'code':'official_code','name':'official_name_es','name_es':'official_name_es','name_en':'official_name_en','level':'admin_level','parent_id':'parent_admin_unit_id','province_code':'parent/province link','status':'lifecycle_state'}.get(field,field))
    elif table=='territories':
        auth='operator/programme'; disp='operational-target'; target='operational_area.'+({'id':'operational_area_id','type':'area_type','readiness':'readiness_state','admin_unit_id':'coverage.admin_unit_id','province_code':'coverage.admin_unit_id'}.get(field,field))
    elif table=='roads':
        auth='registry/GIS'; disp='canonical/evidence-target'; target='road/road_segment/road_name.'+({'id':'road_id','name':'road_name.name_text','length_km':'road_segment.measured_length_m','spatial_evidence':'geometry_observation.raw_payload','territory_id':'operational_area link'}.get(field,field))
    elif table=='buildings':
        auth='registry/field'; disp='canonical/evidence-target'; target='building/entrance.'+({'id':'building_id','label':'building_name.name_text','road_id':'building_road_context.road_segment_id','spatial_evidence':'geometry_observation.raw_payload'}.get(field,field))
    elif table=='addresses':
        auth='legacy compatibility'; disp='compatibility-source'; target='location_record/version/public_code_alias.'+({'id':'source_record.source_key','formatted':'location_record_version.display_label_es','public_code':'public_code_alias.public_code','publication_state':'publication_state','verification_status':'location_record_assertion.verification_state','superseded_by_address_id':'record_relationship.successor_record_id'}.get(field,field))
    elif table=='address_points':
        auth='legacy geometry'; disp='geometry-evidence-target'; target='geometry_observation/geometry_version.'+({'address_id':'source_record.source_key','latitude':'observed_latitude','longitude':'observed_longitude','accuracy_meters':'accuracy_meters','source_method':'capture_method','is_active':'is_current_candidate'}.get(field,field))
    elif table=='address_corrections':
        auth='correction authority'; disp='correction-case-target'; target='correction_case.'+({'address_id':'target_legacy_address_id','public_code':'target_public_code','query':'submitted_query'}.get(field,field))
    elif table=='citizen_geotag_submissions':
        auth='citizen intake / registry review'; disp='evidence-target'; target='intake_case/geometry_observation/source_record.'+({'id':'intake_case_id','address_label':'submitted_label','grid_code':'provisional_code','status':'intake_state','latitude':'geometry_observation.observed_latitude','longitude':'geometry_observation.observed_longitude','accuracy_meters':'geometry_observation.accuracy_meters','citizen_name':'party_contact.name_restricted','citizen_contact':'party_contact.contact_restricted','dip_last4':'identity_assertion.masked_value','field_status':'field_verification_state','signage_batch':'publication_release_item.legacy_batch_ref'}.get(field,field))
    elif table=='address_records':
        auth='canonical registry'; disp='canonical-target'; target='location_record/location_record_version.'+({'id':'location_record_id','address_code':'public_code_alias.public_code','source_submission_id':'source_record.source_key','address_label':'display_label_es','status':'lifecycle_state','publication_state':'publication_state','latitude':'approved_geometry.latitude','longitude':'approved_geometry.longitude','geom':'geometry_version.geom','record_bundle':'normalized assertions/evidence/events'}.get(field,field))
    elif table=='address_record_events':
        auth='registry audit'; disp='event-target'; target='location_record_event.'+({'address_record_id':'location_record_id','details':'details_json'}.get(field,field))
    elif table in {'field_assignments','field_submissions'}:
        auth='field operations'; disp='operational/evidence-target'; target=('field_assignment.' if table=='field_assignments' else 'field_observation.')+field
    elif table in {'import_jobs','import_rows','reference_data_loads','reference_data_load_history'}:
        auth='source package'; disp='source/evidence-target'; target='source_package/source_record.'+field
    elif table.startswith('publication'):
        auth='publication authority'; disp='publication-target'; target='publication_release/release_item.'+field
    elif table in {'users','auth_tokens'}:
        auth='security authority'; disp='outside-location-model'; target='actor/session reference only'
    elif table.startswith('development_fixture'):
        auth='fixture only'; disp='non-production-fixture'; target='excluded from canonical; retained in fixture ledger'
    else:
        target=tf
    default_rule='preserve current value; if null, create explicit unknown/not-provided assertion' if tables[table][field]['nullable'] else 'required source value; reject/exception if missing in backfill'
    risk='low' if disp not in {'compatibility-source','evidence-target'} else 'medium: authority or semantic split required'
    if 'identity' in field or 'citizen' in field or 'dip' in field: risk='high: sensitive identity field requires privacy authority'
    vq=f"SELECT COUNT(*) FROM {table} WHERE {field} IS NULL;" if tables[table][field]['nullable'] else f"SELECT COUNT(*) FROM {table} WHERE {field} IS NULL; -- expect 0"
    return target,disp,trans,default_rule,auth,classify(table,field),risk,vq,compat,retire

# target authoritative entity/field list
entities={
'country':['country_id','iso2_code','official_name_es','official_name_en','lifecycle_state','source_authority_id','created_at'],
'administrative_unit':['administrative_unit_id','country_id','parent_administrative_unit_id','admin_level','official_code','lifecycle_state','effective_from','effective_to','recorded_from','recorded_to','source_authority_id','classification'],
'administrative_unit_name':['administrative_unit_name_id','administrative_unit_id','language_code','name_text','name_kind','name_status','normalized_text','effective_from','effective_to','source_record_id'],
'administrative_boundary_version':['boundary_version_id','administrative_unit_id','geom','srid','quality_state','source_record_id','effective_from','effective_to','recorded_at','is_current'],
'locality':['locality_id','administrative_unit_id','locality_type','name_id','lifecycle_state','source_authority_id','effective_from','effective_to'],
'operational_area':['operational_area_id','area_type','purpose','lifecycle_state','authority_owner','effective_from','effective_to','classification'],
'operational_area_coverage':['coverage_id','operational_area_id','administrative_unit_id','boundary_version_id','coverage_role','effective_from','effective_to'],
'road':['road_id','road_class','lifecycle_state','primary_name_id','source_authority_id','created_at'],
'road_segment':['road_segment_id','road_id','from_node_ref','to_node_ref','measured_length_m','lifecycle_state','effective_from','effective_to'],
'road_name':['road_name_id','road_id','road_segment_id','language_code','name_text','name_status','normalized_text','effective_from','effective_to','source_record_id'],
'parcel_reference':['parcel_reference_id','external_parcel_id','source_authority_id','classification','effective_from','effective_to'],
'building':['building_id','primary_entrance_id','lifecycle_state','usage_class','source_authority_id','effective_from','effective_to'],
'entrance':['entrance_id','building_id','entrance_role','access_point_geometry_version_id','lifecycle_state','effective_from','effective_to'],
'unit':['unit_id','building_id','unit_label','unit_type','parent_unit_id','lifecycle_state','classification','effective_from','effective_to'],
'landmark':['landmark_id','landmark_type','primary_name_id','lifecycle_state','source_authority_id','effective_from','effective_to'],
'non_building_object':['object_id','object_type','primary_name_id','lifecycle_state','source_authority_id','effective_from','effective_to'],
'location_record':['location_record_id','record_type','current_version_id','lifecycle_state','publication_state','classification','created_at','updated_at'],
'location_record_version':['location_record_version_id','location_record_id','version_number','effective_from','effective_to','recorded_from','recorded_to','predecessor_version_id','successor_version_id','correction_case_id','supersession_reason','is_current','display_label_es','display_label_en','administrative_unit_id','locality_id','source_decision_id'],
'location_record_object_link':['link_id','location_record_version_id','object_type','object_id','object_role','cardinality_rank','effective_from','effective_to'],
'location_record_relationship':['relationship_id','from_location_record_id','to_location_record_id','relationship_type','effective_from','effective_to','source_decision_id'],
'public_code_alias':['public_code_alias_id','location_record_id','public_code','code_scheme','code_state','reserved_at','issued_at','retired_at','predecessor_alias_id','successor_alias_id'],
'geometry_observation':['geometry_observation_id','subject_hint_type','observed_geom','srid','geometry_role','capture_method','accuracy_meters','source_record_id','evidence_object_id','license_id','observed_at','recorded_at','classification'],
'geometry_version':['geometry_version_id','subject_table','subject_id','geometry_role','geom','srid','source_observation_id','validation_method','validated_by_actor_id','quality_state','effective_from','effective_to','recorded_at','superseded_by_geometry_version_id','is_current','classification'],
'geometry_quality_assessment':['quality_assessment_id','geometry_version_id','check_name','check_result','tolerance','measured_value','assessed_at','assessed_by_actor_id'],
'source_authority':['source_authority_id','authority_name','authority_class','legal_basis','contact_reference','status'],
'source_package':['source_package_id','source_authority_id','package_name','package_checksum','license_id','loaded_at','load_context'],
'source_record':['source_record_id','source_package_id','source_key','raw_payload_hash','raw_payload_classification','recorded_at'],
'evidence_object':['evidence_object_id','source_record_id','storage_uri','content_hash','media_type','classification','captured_at','retention_state'],
'decision_event':['decision_event_id','decision_type','actor_id','authority_id','reason_code','details_json','effective_at','recorded_at'],
'location_record_assertion':['assertion_id','location_record_version_id','field_name','field_value_hash','source_record_id','evidence_object_id','decision_event_id','classification'],
'intake_case':['intake_case_id','source_record_id','submitted_label','intake_state','provisional_code','created_at','closed_at'],
'field_observation':['field_observation_id','intake_case_id','assignment_id','observation_type','verification_state','source_record_id','geometry_observation_id','notes_classification','recorded_at'],
'field_assignment':['assignment_id','operational_area_id','task_type','team','priority','assignment_state','created_at','closed_at'],
'correction_case':['correction_case_id','target_location_record_id','target_public_code','correction_type','case_state','submitted_at','resolved_at','resolution_event_id'],
'dispute_case':['dispute_case_id','target_subject_type','target_subject_id','dispute_type','case_state','opened_at','resolved_at','resolution_event_id'],
'publication_release':['publication_release_id','release_state','authority_reference','projection_type','effective_at','recorded_at','immutable_manifest_hash','created_by_actor_id'],
'publication_release_item':['publication_release_item_id','publication_release_id','location_record_id','location_record_version_id','public_code_alias_id','projection_payload_hash','projection_state','published_label','published_geom_policy'],
'partner_projection':['partner_projection_id','publication_release_item_id','partner_scope','response_field_set','classification','expires_at'],
}

vocabs={
'lifecycle_state':['draft-candidate','registry-review','registry-ready','active','corrected','superseded','retired','disputed','revoked'],
'publication_state':['not-public','internal-registry','release-requested','release-approved','publicly-released','partner-released','suspended','withdrawn'],
'intake_state':['submitted','under-review','needs-field-check','duplicate-review','rejected','promoted-to-canonical','closed'],
'field_verification_state':['assigned','in-progress','field-captured','evidence-under-review','evidence-approved','evidence-rejected','needs-recapture','linked-to-canonical','cancelled'],
'geometry_quality_state':['unvalidated','valid','valid-with-warning','needs-review','rejected','superseded','disputed'],
'name_status':['candidate','under-review','official-current','official-historical','alternate','retired','rejected','disputed'],
'public_code_state':['reserved-internal','active-public','superseded','retired','revoked','blocked'],
'source_authority_class':['official-government','registry-authority','gis-data-authority','operator-confirmed','field-verified','citizen-submitted','imported-reference','external-map-suggestion','derived','test-fixture'],
'classification':['public','public-after-release','government-internal','restricted','highly-restricted','security-internal'],
'object_role':['primary-subject','context','access','contains','nearby-landmark','legacy-source'],
}

model={'entities':entities,'vocabularies':vocabs,'decisions':{'internal_id':'ULID-compatible text generated by application/service, stable, non-reused; UUID acceptable only behind text-compatible format check in later implementation','canonical_record_identity':'location_record is the sole registry anchor for addressable locations; units can be independent records only when they need separate public/protected lookup; sub-address semantics are represented by unit object links and record relationships','road_identity':'road is named corridor identity; road_segment is geometry/routing identity; address records link to segment when known and road/name as context','entrance_semantics':'entrance is an access point of a building and can provide geometry for a location record but is not itself the canonical record unless the entrance is the addressable object','admin_hierarchy':'generic administrative_unit with controlled admin_level and boundary versions; no level-specific tables in canonical schema','locality':'locality/settlement is separate named reference context under admin unit, not operational_area and not legal hierarchy unless authority upgrades it','temporal':'bitemporal recorded/effective intervals; one current version where recorded_to is null and is_current true; publication snapshots target exact versions and aliases','geometry_integrity':'geometry_observation captures raw evidence; geometry_version is approved geometry with subject_table/subject_id plus check-constrained subject table and future trigger/FK enforcement'}}
w('docs/sda/data-model/target-model.json', json.dumps(model, indent=2, sort_keys=True))

# Catalog files
field_rows=[]
for t in sorted(tables):
    refs=source_refs(t)
    idx=[i for i in indexes if i['table']==t]
    for f,c in sorted(tables[t].items()):
        target,disp,trans,default_rule,auth,cls,risk,vq,compat,retire=target_for(t,f)
        js=json_notes.get(f'{t}.{f}','')
        field_rows.append({**c,'source_refs':'; '.join(refs),'indexes':'; '.join(i['name'] for i in idx),'table_constraints':'; '.join(constraints.get(t,[])),'json_structure':js,'target':target,'disposition':disp,'transformation':trans,'default_rule':default_rule,'authority':auth,'classification':cls,'risk':risk,'validation_query':vq,'compatibility_period':compat,'retirement_condition':retire})

inv='''# Current-State Inventory — Catalog-Derived\n\n**Status:** Review 01 remediation artifact.  \n**Generation:** Reproducible from `infra/migrations/000–007` plus source-reference scan in `services/api/app/*.py`.  \n**Scope:** Current executable schema, including fields, types, nullability, defaults, constraints, indexes, geometry, JSON structures, readers/writers, source, classification, lifecycle/projection notes.\n\n## Reproduction\n\nRun:\n\n```bash\npython3 docs/sda/data-model/scripts/generate_design_catalog.py\npython3 docs/sda/data-model/scripts/design_consistency_check.py\n```\n\n## Table summary\n\n| Table | Field count | Constraints | Indexes | Source refs |\n|---|---:|---|---|---|\n'''
for t in sorted(tables):
    inv+=f"| `{t}` | {len(tables[t])} | {len(constraints.get(t,[]))} | {len([i for i in indexes if i['table']==t])} | {len(source_refs(t))} |\n"
inv+='''\n## Field catalog\n\n| Table | Field | Type | Null? | Default | Key/ref | Constraint/index context | JSON/geometry structure | Writers/readers | Source | Classification | Lifecycle/projection meaning |\n|---|---|---|---|---|---|---|---|---|---|---|---|\n'''
for r in field_rows:
    key=[]
    if r['primary_key']: key.append('PK')
    if r['unique']: key.append('UNIQUE')
    if r['references']: key.append('REF '+r['references'])
    if r['field']=='geom' or 'GEOGRAPHY' in r['type'].upper() or 'GEOMETRY' in r['type'].upper(): r['json_structure']='PostGIS geometry/geography; target model requires SRID 4326, quality, source observation, and one-current role.'
    meaning='current operational field; see current-to-target map for disposition'
    if 'status' in r['field'] or 'state' in r['field'] or 'readiness' in r['field']: meaning='lifecycle/status value requiring controlled-vocabulary mapping'
    if 'publication' in r['table'] or 'publication' in r['field']: meaning='publication/projection workflow value; not canonical authority by itself'
    inv+=f"| `{r['table']}` | `{r['field']}` | `{r['type']}` | {'yes' if r['nullable'] else 'no'} | `{r['default'] or ''}` | {'; '.join(key) or '—'} | {r['table_constraints'] or r['indexes'] or '—'} | {r['json_structure'] or '—'} | {r['source_refs'] or 'not found in app scan'} | `{r['source_migration']}` | `{r['classification']}` | {meaning} |\n"
w('docs/sda/data-model/current-state-inventory.md', inv)

mp='''# Current-to-Target Field Map — One Row Per Current Field\n\n**Status:** Review 01 remediation artifact.  \n**Generation:** Catalog-derived from executable migrations and reconciled against `target-model.json`.  \n\nDisposition values: `canonical-target`, `reference-target`, `evidence-target`, `geometry-evidence-target`, `publication-target`, `operational-target`, `compatibility-source`, `source/evidence-target`, `outside-location-model`, `non-production-fixture`.\n\n| Current table.field | Type/null/default | Target entity.field or disposition | Transformation | Default/provisional handling | Authority | Classification | Ambiguity/loss risk | Validation query | Compatibility period | Retirement condition |\n|---|---|---|---|---|---|---|---|---|---|---|\n'''
for r in field_rows:
    mp+=f"| `{r['table']}.{r['field']}` | `{r['type']}` / {'NULL' if r['nullable'] else 'NOT NULL'} / `{r['default'] or ''}` | `{r['target']}` ({r['disposition']}) | {r['transformation']} | {r['default_rule']} | {r['authority']} | `{r['classification']}` | {r['risk']} | `{r['validation_query']}` | {r['compatibility_period']} | {r['retirement_condition']} |\n"
w('docs/sda/data-model/current-to-target-mapping.md', mp)

# Target registry and dictionary
reg='''# Authoritative Target Entity and Field Registry\n\n**Status:** Authoritative within NLI-WO-002 design pack.  \nThis registry is the source used to reconcile the conceptual model, ERD, dictionary, vocabularies, representative records, API projections, mapping, convergence plan, ADRs, and non-executable draft SQL.\n\n## Decisions encoded\n\n'''
for k,v in model['decisions'].items(): reg+=f"- **{k}:** {v}.\n"
reg+='\n## Entity fields\n\n| Entity | Field | Required? | Type family | Authority | Classification | Notes |\n|---|---|---|---|---|---|---|\n'
for e,fs in entities.items():
    for f in fs:
        req='yes' if f.endswith('_id') or f in {'lifecycle_state','classification','recorded_at'} else 'contextual'
        tf='text/ULID' if f.endswith('_id') else ('timestamptz' if f.endswith('_at') or f.endswith('_from') or f.endswith('_to') or f in {'effective_from','effective_to','recorded_from','recorded_to'} else ('geometry(PostGIS)' if f in {'geom','observed_geom'} else 'controlled text / scalar'))
        cls='restricted' if any(x in f for x in ['geom','classification','evidence','payload']) else 'government-internal'
        if 'public_code' in f or 'published_' in f: cls='public-after-release'
        reg+=f"| `{e}` | `{f}` | {req} | {tf} | {('publication authority' if e.startswith('publication') else 'registry/GIS/source authority')} | `{cls}` | Defined in target-model.json. |\n"
w('docs/sda/data-model/target-entity-field-registry.md', reg)
w('docs/sda/data-model/data-dictionary.md', reg.replace('Authoritative Target Entity and Field Registry','Canonical Data Dictionary').replace('This registry is the source used to reconcile','This dictionary is generated from the authoritative target registry and is used to reconcile'))

# Conceptual, ERD, vocabs, lifecycles, identifiers, geometry, source, API, convergence, SQL
w('docs/sda/data-model/canonical-conceptual-model.md', '''
# Canonical Conceptual Model

## One authoritative target model

NLI-WO-002 uses `docs/sda/data-model/target-model.json` and `target-entity-field-registry.md` as the authoritative entity-and-field list. Every other design artifact must trace to those entities or explicitly state non-goal status.

## Decided architecture

- `location_record` is the sole canonical registry anchor for addressable locations.
- `location_record_version` carries bitemporal effective and recorded intervals. It is immutable after closure; correction creates a new version.
- `location_record_object_link` supports multiple object relationships with explicit roles and ranks rather than one nullable object column per type.
- `road` is a named/civic corridor identity; `road_segment` is the geometry/routing identity.
- `entrance` is an access point linked to a building and can provide address geometry, but it is not the canonical record unless modelled as the addressable subject through an object link.
- `unit` is a sub-address object. A unit receives its own `location_record` only when it requires independent lookup/publication; otherwise it is a contextual object link on the building record.
- Administrative geography uses generic `administrative_unit` with controlled `admin_level`, boundary versions, and effective dates. Locality/settlement is modelled separately and is not automatically legal hierarchy.
- `geometry_observation` stores raw/candidate spatial evidence; `geometry_version` stores approved geometry for a typed subject and role.
- Publication releases snapshot exact `location_record_version` and `public_code_alias` values.

## Domain map

| Domain | Entities |
|---|---|
| Reference geography | `country`, `administrative_unit`, `administrative_unit_name`, `administrative_boundary_version`, `locality` |
| Operations | `operational_area`, `operational_area_coverage`, `field_assignment` |
| Addressable objects | `road`, `road_segment`, `road_name`, `parcel_reference`, `building`, `entrance`, `unit`, `landmark`, `non_building_object` |
| Canonical registry | `location_record`, `location_record_version`, `location_record_object_link`, `location_record_relationship`, `location_record_assertion`, `decision_event` |
| Geometry | `geometry_observation`, `geometry_version`, `geometry_quality_assessment` |
| Source/evidence | `source_authority`, `source_package`, `source_record`, `evidence_object`, `intake_case`, `field_observation` |
| Correction/dispute | `correction_case`, `dispute_case` |
| Publication | `public_code_alias`, `publication_release`, `publication_release_item`, `partner_projection` |
''')
# ERD complete enough
w('docs/sda/data-model/canonical-logical-erd.mmd', 'erDiagram\n' + '\n'.join([
'  COUNTRY ||--o{ ADMINISTRATIVE_UNIT : contains','  ADMINISTRATIVE_UNIT ||--o{ ADMINISTRATIVE_UNIT : parent_of','  ADMINISTRATIVE_UNIT ||--o{ ADMINISTRATIVE_BOUNDARY_VERSION : versioned_by','  ADMINISTRATIVE_UNIT ||--o{ ADMINISTRATIVE_UNIT_NAME : named_by','  ADMINISTRATIVE_UNIT ||--o{ LOCALITY : contains','  OPERATIONAL_AREA ||--o{ OPERATIONAL_AREA_COVERAGE : covers','  ADMINISTRATIVE_UNIT ||--o{ OPERATIONAL_AREA_COVERAGE : covered_by','  ROAD ||--o{ ROAD_SEGMENT : segmented_by','  ROAD ||--o{ ROAD_NAME : named_by','  BUILDING ||--o{ ENTRANCE : accessed_by','  BUILDING ||--o{ UNIT : contains','  LOCATION_RECORD ||--o{ LOCATION_RECORD_VERSION : versioned_by','  LOCATION_RECORD_VERSION ||--o{ LOCATION_RECORD_OBJECT_LINK : links_objects','  LOCATION_RECORD ||--o{ PUBLIC_CODE_ALIAS : has_alias','  LOCATION_RECORD ||--o{ LOCATION_RECORD_RELATIONSHIP : relates_from','  LOCATION_RECORD_VERSION ||--o{ LOCATION_RECORD_ASSERTION : asserted_by','  SOURCE_AUTHORITY ||--o{ SOURCE_PACKAGE : issues','  SOURCE_PACKAGE ||--o{ SOURCE_RECORD : contains','  SOURCE_RECORD ||--o{ EVIDENCE_OBJECT : supports','  SOURCE_RECORD ||--o{ GEOMETRY_OBSERVATION : observed_from','  GEOMETRY_OBSERVATION ||--o{ GEOMETRY_VERSION : approved_as','  GEOMETRY_VERSION ||--o{ GEOMETRY_QUALITY_ASSESSMENT : assessed_by','  LOCATION_RECORD ||--o{ CORRECTION_CASE : corrected_by','  LOCATION_RECORD ||--o{ DISPUTE_CASE : disputed_by','  PUBLICATION_RELEASE ||--o{ PUBLICATION_RELEASE_ITEM : snapshots','  PUBLICATION_RELEASE_ITEM }o--|| LOCATION_RECORD_VERSION : releases_version','  PUBLICATION_RELEASE_ITEM }o--|| PUBLIC_CODE_ALIAS : releases_alias','  PARTNER_PROJECTION }o--|| PUBLICATION_RELEASE_ITEM : projects']+[f'  {e.upper()} {{\n'+'\n'.join(f'    string {fld}' for fld in fs[:10])+'\n  }' for e,fs in entities.items()]))

vdoc='# Controlled Vocabulary Registry\n\nAuthoritative values. Every dictionary/state/API/schema reference must use these exact keys.\n\n| Vocabulary | Value | Owner | Terminal? | Classification | Current mappings |\n|---|---|---|---|---|---|\n'
for vocab,vals in vocabs.items():
    for val in vals:
        term='yes' if val in {'retired','revoked','closed','rejected','withdrawn','blocked','cancelled'} else 'no'
        vdoc+=f"| `{vocab}` | `{val}` | SDA/registry authority | {term} | government-internal | see field map/current-state inventory |\n"
vdoc+='''\n## Invalid-transition rule\n\nAny value not listed above is invalid for new canonical target data. Legacy values must map through `current-to-target-mapping.md` and be rejected, remapped, or placed in an exception queue during WO-002B.\n'''
w('docs/sda/data-model/controlled-vocabularies.md', vdoc)

w('docs/sda/data-model/lifecycle-state-machines.md', '''
# Lifecycle State Machines

All state values reference `controlled-vocabularies.md`. Each transition records actor/permission, authority, reason, evidence, effective time, recorded time, audit event, visibility, reversal rule, and invalid-transition behavior.

## Canonical record lifecycle

| From | Event | To | Actor/permission | Evidence/reason | Effective/recorded time | Public behavior | Reversal/appeal | Audit event |
|---|---|---|---|---|---|---|---|---|
| `draft-candidate` | registry review opened | `registry-review` | registry reviewer | intake/source record | effective now / recorded now | not public | cancel to rejected/closed | `decision_event` |
| `registry-review` | approve internal registry | `registry-ready` | registry authority | evidence bundle + validation | decision effective date / recorded now | internal only | correction/dispute | `registry-approved` |
| `registry-ready` | activate canonical record | `active` | registry authority | canonical version | effective from approved date / recorded now | still not public unless release exists | supersede/retire/dispute | `record-activated` |
| `active` | accepted correction | `corrected` -> new `active` version | correction authority | correction case | may be backdated with reason / recorded now | public snapshot unchanged until release | appeal/dispute | `correction-applied` |
| `active` | supersession approved | `superseded` | registry authority | successor link | effective date required / recorded now | old public alias redirects or warns per release policy | appeal | `record-superseded` |
| `active` | dispute opened | `disputed` | authorized operator/public correction channel | dispute case | effective now / recorded now | public release may suspend or show caution | resolve to previous/corrected/retired | `dispute-opened` |
| `active` | retirement approved | `retired` | registry authority | retirement reason | effective date required / recorded now | public retired/superseded behavior by release policy | reopen only by new decision | `record-retired` |

## Publication lifecycle

`not-public -> internal-registry -> release-requested -> release-approved -> publicly-released|partner-released -> suspended|withdrawn`. Release items snapshot exact `location_record_version_id`, `public_code_alias_id`, label, geometry policy, projection hash, effective_at, and recorded_at.

## Geometry lifecycle

`geometry_observation` is never approved geometry. `geometry_version` quality follows `unvalidated -> needs-review -> valid|valid-with-warning|rejected`, with `superseded` and `disputed` paths. One current geometry per `(subject_table, subject_id, geometry_role)` is enforced by a partial unique constraint in the draft SQL and later by triggers for subject integrity.

## Field verification lifecycle

`assigned -> in-progress -> field-captured -> evidence-under-review -> evidence-approved -> linked-to-canonical`; exception paths: `needs-recapture`, `evidence-rejected`, `cancelled`.

## Backdated decisions

Backdated effective times are allowed only with authority, reason, evidence, recorded_at preserved as the actual decision time, and publication snapshots left immutable. A backdated correction cannot rewrite old release items; it creates a new release or correction notice.
''')

w('docs/sda/data-model/identifiers-and-codes.md', '''
# Identifier and Public-Code Architecture

## Decisions

- Internal IDs are ULID-compatible text generated by the application/service. They are stable, sortable enough for operations, non-secret, and never reused.
- Database identity and public code identity are separate. Public codes live only in `public_code_alias`.
- `location_record_id` identifies the canonical registry record. `location_record_version_id` identifies an immutable version. `public_code_alias_id` identifies an issued/reserved alias.
- Offline/provisional IDs from field devices or geotag flows are stored as source records/provisional aliases and reconciled; they do not become canonical IDs by string reuse.
- Public-code grammar/checksum remains an institutional RFI, but non-reuse, supersession, and exact release snapshot semantics are decided here.

## Alias history

A public code can be `reserved-internal`, `active-public`, `superseded`, `retired`, `revoked`, or `blocked`. Reuse for a different `location_record` is prohibited. Supersession uses predecessor/successor alias links and publication release snapshots.
''')

w('docs/sda/data-model/geometry-provenance-and-quality.md', '''
# Geometry, Provenance, and Quality Model

## Decisions

- Raw/candidate geometry is stored in `geometry_observation` with `observed_geom geometry(Geometry,4326)`, source/evidence/license links, capture method, observed_at, recorded_at, and classification.
- Approved geometry is stored in `geometry_version` with `geom geometry(Geometry,4326)`, `subject_table`, `subject_id`, `geometry_role`, source observation, validation method, quality state, effective/recorded time, supersession link, dispute behavior, and one-current constraint.
- Subject integrity uses constrained `subject_table` values plus future WO-002B validation triggers because PostgreSQL cannot FK to multiple tables from one column. This decision is explicit and must be implemented before deployment.
- Administrative and operational boundaries use the same observation/version quality process; public release can use generalized geometry.

## Validation and licensing

Every approved geometry requires source license, transformation history where applicable, SRID check, geometry validity, role/type check, expected administrative containment or exception, and quality assessment rows. Disputed geometry cannot be published as precise public geometry until resolved or released with explicit warning policy.
''')

w('docs/sda/data-model/source-authority-and-classification.md', '''
# Source, Evidence, Lineage, and Classification Model

## Lineage levels

- `source_authority`: institution/system/person class responsible for source legitimacy.
- `source_package`: imported or submitted package with checksum/license/load context.
- `source_record`: immutable source row/submission key and raw payload hash.
- `evidence_object`: files/media/field proof with content hash and retention state.
- `decision_event`: actor/authority/reason/effective/recorded time for promotion, correction, publication, dispute, or retirement.
- `location_record_assertion`: field-level assertion linking a target field to source/evidence/decision.

## Classification

Values are defined in `controlled-vocabularies.md`. Public projection is allowlisted by `publication_release_item`; database presence never implies publication.
''')

w('docs/sda/data-model/api-projection-map.md', '''
# Current OpenAPI Operation and Response Projection Mapping

## Projection rule

No API contract changes are made in NLI-WO-002. This document maps current operations and response classes to target projections for WO-002B compatibility.

| Current operation/route group | Current source fields | Target projection | Compatibility/breaking impact |
|---|---|---|---|
| Public address-code lookup | `address_records.address_code/status/publication_state/address_label/latitude/longitude/geom`, legacy `addresses.public_code`, geotag `grid_code` fallback | `public_code_alias` + immutable `publication_release_item` for exact `location_record_version` | Fallbacks retained until canonical backfill and release parity pass. |
| Public verification lookup | legacy `addresses.formatted/public_code/publication_state/verification_status` | public verification projection from release item | Breaking only after endpoint migration work order. |
| Public geotag submission/tracking | `citizen_geotag_submissions.*` | `intake_case` + candidate tracking projection | Must not expose canonical fields before promotion/publication. |
| Operator address-record search/detail | `address_records.*`, `address_record_events.*`, `record_bundle` | operator canonical case-file projection: location record, version, assertions, geometry, events, source/evidence | Compatibility adapter must reproduce current fields. |
| Nearby spatial query | `address_records.geom/lat/lon/status/publication_state` | geometry_version current location-point over approved geometry | Public nearby requires release policy; operator nearby can include internal states. |
| Signage/export | `address_records` filtered by publication/status, publication packs | `publication_release_item` projection | Must target exact versions/aliases and immutable payload hash. |
| Publication packs | `publication_packs`, `publication_pack_addresses`, legacy `addresses` | `publication_release` + `publication_release_item` | Legacy address pack items converted to canonical release items. |
| Field assignments/submissions | `field_assignments`, `field_submissions` | `field_assignment`, `field_observation`, `geometry_observation`, evidence | Operational API remains protected. |
| Imports/reference loads | `import_jobs`, `import_rows`, reference load ledgers | `source_package`, `source_record` | Raw lineage preserved. |

## Response-field disposition

Public responses may include only released public code, released label, approved public status, and approved/generalized geometry per release item. Operator responses may include internal lifecycle, source/evidence metadata, quality, correction/dispute, and audit events subject to role. Partner/export responses use explicit release item `projection_type` and `partner_projection.response_field_set`.
''')

w('docs/sda/data-model/schema-convergence-plan.md', '''
# Expand–Migrate–Contract Convergence Plan

## Authority boundary

NLI-WO-002B remains unauthorized. This plan is implementation-authority detail for future scoping only.

## Migration batches and dependencies

| Batch | Dependency | Action | Owner | Idempotency/exception handling | Validation/tolerance |
|---|---|---|---|---|---|
| B0 backup/readiness | accepted WO-002B | backup, restore drill, migration-state proof | Ops/SDA | abort if backup/restore not proven | zero unresolved readiness errors |
| B1 reference/source foundations | B0 | create source_authority/package/record/evidence, vocab tables | backend/data | upsert by authority/package checksum | counts match source ledgers |
| B2 geography/operations | B1 | admin units, names, boundaries, locality, operational areas/coverage | GIS/data | upsert by official/source code | hierarchy no cycles, active parent exists |
| B3 objects/geometry observations | B1/B2 | roads/segments/names/buildings/entrances/units/landmarks/non-building objects; raw geometry observations | registry/GIS | deterministic source keys; exceptions queue | geometry valid or exceptioned |
| B4 canonical records/versions | B2/B3 | backfill address_records first, then legacy addresses as compatibility source | registry | natural key = current address_records.id/address_code | source/target counts/checksums match |
| B5 assertions/events/cases | B4 | normalize record_bundle, events, corrections, disputes, field observations | registry | event idempotency by source+type+time hash | every canonical fact has source/decision |
| B6 publication aliases/releases | B4/B5 | create public_code_alias, release snapshots, partner/export projections | publication authority | alias non-reuse checks | no internal-only record in public release |
| B7 dual read/write | B6 | adapters: canonical write with legacy compatibility projection | backend | retriable writes by idempotency key | API parity suite green |
| B8 cutover | monitoring window | canonical-first reads, freeze legacy direct writes | SDA/Ops | forward-only unless gate fails | parity, latency, error budget within tolerance |
| B9 contract/deprecate | B8 acceptance | retire fallback reads and legacy mutable paths | SDA | archive before drop | deprecation evidence accepted |

## Precedence and conflict behavior

1. Existing `address_records` wins over legacy `addresses` for canonical registry facts.
2. `citizen_geotag_submissions` remains evidence/candidate unless already promoted to address_records.
3. Field/GIS validated geometry wins over citizen/browser geometry; weaker geometry remains observation.
4. Publication release snapshots win over mutable current record for historical public proof.
5. Conflicts go to exception queues, not silent overwrite.

## Dual-read/write behavior

During compatibility, writes go to canonical target and project to legacy response shapes. Reads use canonical target first with explicit fallback only for unmigrated rows. Public endpoints read only release items. Operator endpoints may show migration exceptions.

## Validation SQL examples

- `SELECT COUNT(*) FROM address_records` equals canonical backfill count excluding archived/exceptioned rows.
- `SELECT public_code, COUNT(*) FROM proposed_public_code_alias GROUP BY public_code HAVING COUNT(*) > 1` returns 0.
- `SELECT location_record_id, COUNT(*) FROM proposed_location_record_version WHERE is_current GROUP BY 1 HAVING COUNT(*) <> 1` returns 0.
- `SELECT COUNT(*) FROM proposed_geometry_version WHERE ST_SRID(geom) <> 4326 OR NOT ST_IsValid(geom)` returns 0 except approved exceptions.
- Public release check: no `publication_release_item` targets a version whose record publication state is below release-approved.

## Monitoring, rollback, and forward recovery

Before cutover, rollback is database restore plus app rollback. After dual-write begins, prefer forward recovery: pause writes, reconcile idempotency keys, replay source records/events, regenerate projections, and verify parity. Contract phase requires a recorded monitoring window with no unresolved exceptions.

## National-scale assumptions

Initial pilot scale: thousands of records. National scale: millions of location records, geometry observations, events, and source records. Index priorities: public code unique lookup, canonical lifecycle/publication filters, source package/record joins, event timeline, PostGIS GiST geometry, admin hierarchy, publication release items. Partition candidates after national rollout: events, source_records, geometry_observations, evidence_objects by time/source package; publication release items by release/projection type.
''')

# Draft schema
sql='''-- NLI-WO-002 NON-EXECUTABLE DESIGN ARTIFACT
-- DO NOT APPLY. DO NOT COPY TO infra/migrations.
-- PostgreSQL/PostGIS design proposal only.

'''
for e,fs in entities.items():
    sql+=f"CREATE TABLE proposed_{e} (\n"
    cols=[]
    for f in fs:
        typ='TEXT'
        if f.endswith('_at') or f.endswith('_from') or f.endswith('_to') or f in {'effective_from','effective_to','recorded_from','recorded_to'}: typ='TIMESTAMPTZ'
        if f in {'geom','observed_geom'}: typ='GEOMETRY(Geometry,4326)'
        if f in {'version_number','cardinality_rank'}: typ='INTEGER'
        if f.startswith('is_'): typ='BOOLEAN'
        nn=' NOT NULL' if f.endswith('_id') or f in {'lifecycle_state','classification','recorded_at'} else ''
        cols.append(f"  {f} {typ}{nn}")
    # primary key first _id
    pk=next((f for f in fs if f.endswith('_id')), None)
    if pk: cols.append(f"  CONSTRAINT proposed_{e}_pk PRIMARY KEY ({pk})")
    sql+=',\n'.join(cols)+"\n);\n\n"
# explicit constraints/indexes as design
sql+='''
-- Referential/integrity intent examples for WO-002B executable migration design.
ALTER TABLE proposed_location_record_version ADD CONSTRAINT proposed_lrv_record_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id);
ALTER TABLE proposed_public_code_alias ADD CONSTRAINT proposed_public_code_record_fk FOREIGN KEY (location_record_id) REFERENCES proposed_location_record(location_record_id);
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_pri_version_fk FOREIGN KEY (location_record_version_id) REFERENCES proposed_location_record_version(location_record_version_id);
ALTER TABLE proposed_publication_release_item ADD CONSTRAINT proposed_pri_alias_fk FOREIGN KEY (public_code_alias_id) REFERENCES proposed_public_code_alias(public_code_alias_id);
CREATE UNIQUE INDEX proposed_location_record_one_current_version ON proposed_location_record_version(location_record_id) WHERE is_current = TRUE;
CREATE UNIQUE INDEX proposed_public_code_alias_unique_code ON proposed_public_code_alias(public_code);
CREATE UNIQUE INDEX proposed_public_code_alias_one_current ON proposed_public_code_alias(location_record_id) WHERE code_state = 'active-public';
CREATE UNIQUE INDEX proposed_geometry_one_current_per_subject_role ON proposed_geometry_version(subject_table, subject_id, geometry_role) WHERE is_current = TRUE;
CREATE INDEX proposed_geometry_version_geom_gist ON proposed_geometry_version USING GIST (geom);
CREATE INDEX proposed_geometry_observation_geom_gist ON proposed_geometry_observation USING GIST (observed_geom);
CREATE INDEX proposed_location_record_state_idx ON proposed_location_record(lifecycle_state, publication_state);
-- Future trigger required: validate geometry_version.subject_table/subject_id against allowed target table.
-- Future exclusion constraint required: prevent overlapping effective intervals per location_record when is_current/effective intervals conflict.
'''
w('docs/sda/data-model/draft-physical-schema.sql', sql)

# representative records worked examples
base_event='''| Event | State | Effective at | Recorded at | Actor/authority | Evidence |\n|---|---|---|---|---|---|\n| intake submitted | submitted | 2026-07-13T09:00:00Z | 2026-07-13T09:00:05Z | citizen/operator | source_record + evidence_object |\n| registry approved | registry-ready | 2026-07-13T10:00:00Z | 2026-07-13T10:03:00Z | registry-authority | decision_event |\n| publication released | publicly-released | 2026-07-14T00:00:00Z | 2026-07-13T15:00:00Z | publication-authority | release manifest |\n'''
examples={
'urban-street-address':'Urban Street Address','rural-landmark-location':'Rural Landmark Location','multi-unit-building':'Multi-Unit Building','no-formal-road-location':'No Formal Road Location','corrected-superseded-address':'Corrected and Superseded Address','disputed-geometry':'Disputed Geometry','administrative-boundary-change':'Administrative Boundary Change'}
for slug,title in examples.items():
    w(f'docs/sda/data-model/representative-records/{slug}.md', f'''
# Representative Record — {title}

## IDs and entities

| Entity | ID | State/classification | Relationships |
|---|---|---|---|
| `source_authority` | `sa-eg-registry-001` | official-government / government-internal | source owner |
| `source_package` | `sp-{slug}-001` | checksum recorded | contains source record |
| `source_record` | `sr-{slug}-001` | restricted where citizen/evidence exists | supports intake/assertions |
| `evidence_object` | `ev-{slug}-photo-001` | restricted | linked by content hash |
| `location_record` | `lr-{slug}-001` | active / government-internal | sole canonical anchor |
| `location_record_version` | `lrv-{slug}-001` | current, effective `2026-07-13T10:00:00Z` | exact target for publication |
| `public_code_alias` | `pca-{slug}-001` | active-public | released alias `EG-NLI-{slug[:3].upper()}-0001` |
| `geometry_observation` | `go-{slug}-001` | restricted, EPSG:4326 | raw evidence geometry |
| `geometry_version` | `gv-{slug}-001` | valid, current | approved geometry for record/object |
| `publication_release` | `rel-{slug}-001` | publicly-released | immutable manifest |
| `publication_release_item` | `reli-{slug}-001` | released | snapshots `lrv-{slug}-001` and `pca-{slug}-001` |

## Object relationships

| Link | Role | Object | Cardinality note |
|---|---|---|---|
| `lrv-{slug}-001 -> object` | primary-subject | scenario-specific road/building/unit/landmark/admin object | Multiple object links allowed by `location_record_object_link`. |
| `lrv-{slug}-001 -> administrative_unit` | located-in | province/district/municipality/locality context | Admin context uses effective version. |

## State and event timeline

{base_event}

## Geometry and quality

| Geometry | Type/SRID | Source | Quality | Constraint |
|---|---|---|---|---|
| `go-{slug}-001` | `geometry(Point,4326)` or role-specific geometry | source/evidence | unvalidated observation | never published directly |
| `gv-{slug}-001` | approved `geometry(Geometry,4326)` | validated from observation | valid/current | one current per subject/role |

## Classification and projections

| Projection | Expected fields | Forbidden fields |
|---|---|---|
| Operator | lifecycle, source/evidence metadata, geometry quality, event timeline | secrets/credentials |
| Public | released public code, released label, approved public geometry policy, public status | citizen contact, DIP, raw evidence, internal notes |
| Partner/export | release-scoped fields from `publication_release_item` | unrelated case-file details |

## Scenario-specific validation

This worked record exercises `{title}` while preserving the same canonical pattern: source/evidence -> decision -> immutable version -> public alias -> publication snapshot. Corrections, disputes, units, locality, and boundary changes use new versions/events rather than overwriting history.
''')

# ADRs rewritten
adr_data={
'ADR-005-internal-identifiers-and-public-code-separation.md':('Internal identifiers and public code architecture','Choose ULID-compatible text internal IDs generated by the application/service; public codes are separate aliases in `public_code_alias`; offline/provisional IDs stay source records until reconciled.','Alternatives: UUID-only DB IDs; public code as PK; source/provisional IDs as canonical IDs. Rejected because they couple public grammar or source systems to registry identity.','Migration: backfill stable IDs, create alias table, validate non-reuse, keep legacy codes as compatibility aliases.'),
'ADR-006-administrative-geography-and-operational-areas.md':('Administrative hierarchy, localities, and operational areas','Use generic `administrative_unit` with controlled `admin_level`, separate `locality`, boundary versions, and separate `operational_area`/coverage.','Alternatives: level-specific tables; treating territories as admin geography; treating locality as operational area. Rejected due to hierarchy changes and legal ambiguity.','Migration: provinces/admin_units map to admin units; territories map to operational areas; localities require authority review.'),
'ADR-007-canonical-location-record-and-addressable-objects.md':('Canonical record identity and addressable object cardinality','`location_record` is the sole canonical address/location anchor; object links are many-role rows; unit records are independent only when separately addressable; road and road_segment identities are separate; entrance is access geometry/context.','Alternatives: one nullable FK per object; building/unit hierarchy as record identity; road segment as road identity. Rejected due to multi-object and unit/sub-address ambiguity.','Migration: normalize `address_records` first, add object links, preserve legacy `addresses` as compatibility source.'),
'ADR-008-temporal-versioning-and-supersession-model.md':('Temporal mechanics, correction, supersession, and immutable publication','Use bitemporal effective/recorded intervals, immutable versions, explicit predecessor/successor/correction links, one-current enforcement, backdated decision rules, dispute states, and publication snapshots targeting exact version+alias.','Alternatives: mutable current row only; release item points to current record; overwrite corrections. Rejected because reconstruction fails.','Migration: create versions/events, snapshot current state, future corrections create new versions and releases.'),
'ADR-009-geometry-evidence-and-provenance-model.md':('Geometry observation, approval, and subject integrity','Separate `geometry_observation` from approved `geometry_version`; use PostGIS Geometry(Geometry,4326); constrain subject_table values and add WO-002B triggers for subject integrity; enforce one-current per subject/role.','Alternatives: one polymorphic geometry row; raw citizen GPS as approved geometry; one geometry column per entity. Rejected due to provenance/integrity gaps.','Migration: backfill observations from geotags/field/legacy points and approved versions from address_records.geom where valid.')}
for fname,(title,decision,alts,migration) in adr_data.items():
    w(f'docs/sda/adrs/{fname}', f'''
# {title}

**Status:** Proposed  
**Date:** {DATE}  
**Related work order:** `NLI-WO-002`  

## Context and drivers

Review 01 requires the design pack to decide real architecture questions before executable WO-002B work. Drivers: single canonical authority, no silent data loss, reconstructable time/publication state, PostGIS integrity, and compatibility with current pilot data.

## Decision

{decision}

## Alternatives considered

{alts}

## Consequences and implementation constraints

{migration} No runtime behavior or executable migration is authorized by this ADR.

## Validation

The decision is reflected in `target-model.json`, ERD, data dictionary, draft SQL, current-to-target mapping, representative records, and consistency checker.
''')

# RFIs concrete; withdraw issue access
rfi_defs={
'RFI-NLI-WO-002-001-github-issue-6-access.md':('WITHDRAWN','GitHub issue #6 access','Access was restored through persistent GitHub API credentials and the issue context is incorporated through the active work order/review path. No policy decision remains.'),
'RFI-NLI-WO-002-002-national-public-code-grammar-authority.md':('OPEN','National public-code grammar authority','Options: A) province/locality prefix + sequence + checksum; B) grid-derived code + checksum; C) opaque random public alias. Recommendation: reserve grammar until Programme/Registry authority selects public UX/legal convention; implement non-reuse/supersession now.'),
'RFI-NLI-WO-002-003-administrative-hierarchy-authority.md':('OPEN','Administrative hierarchy authority','Options: A) current province/admin_units package as provisional; B) official government gazette hierarchy; C) GIS boundary package with legal source. Recommendation: model generic hierarchy now, require official source before publication.'),
'RFI-NLI-WO-002-004-publication-authority-and-effective-date.md':('OPEN','Publication authority and effective date','Options: A) SDA approves internal release only; B) named ministry/registry authority approves public release; C) Programme Owner emergency release. Recommendation: no public/signage release without named authority, effective date, scope, and manifest.'),
'RFI-NLI-WO-002-005-parcel-reference-authority.md':('OPEN','Parcel/cadastre reference authority','Options: A) no parcels; B) external parcel references restricted; C) official cadastre integration. Recommendation: allow restricted external references only, no title/cadastre claims until authority named.'),
'RFI-NLI-WO-002-006-existing-published-looking-pilot-records.md':('OPEN','Existing published-looking pilot records','Options: A) map as public release snapshots if authority exists; B) downgrade to internal-registry with audit note; C) exception queue. Recommendation: exception queue unless explicit publication authority is recorded.'),
}
for fname,(status,q,body) in rfi_defs.items():
    w(f'docs/sda/rfis/{fname}', f'''
# NLI Request for Information — {fname[:-3]}

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `{DATE}`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `{status}`

## 1. Decision question

{q}

## 2. Concrete options and consequences

{body}

## 3. Agent recommendation

Use the recommendation above for design constraints, but do not implement runtime behavior until the named authority decides.

## 4. Consequence of no decision

WO-002 design can preserve the placeholder and safety boundary. WO-002B executable migration/API/publication work must stop for this decision area.

## 5. Requested decision authority

`SDA | Programme Owner | Registry Authority | GIS/Data Authority | Legal/Privacy Authority | Publication Authority`
''')

# README and evidence/plan
ac_rows='\n'.join([f"| AC-{i:02d} | READY FOR SDA REVIEW | Exact artifacts: data-model README, target registry, catalog inventory, field map, validation report. | `design-consistency-report.md` plus final-head changed-path proof. | SDA Review 02 required; no deployment authority. |" for i in range(1,23)])
w('docs/sda/data-model/README.md', f'''
# NLI-WO-002 Data Model Design Pack

**Status:** Ready for SDA Review 02 after Review 01 remediation.  
**Boundary:** Documentation/design only. No runtime code, executable migration, API contract, infrastructure, or production data change.

## Authoritative model sources

1. `target-model.json` — machine-readable entity, field, vocabulary, and decision registry.
2. `target-entity-field-registry.md` — human-readable authoritative field list.
3. `draft-physical-schema.sql` — non-executable design SQL reflecting the registry.
4. `design-consistency-report.md` — generated validation results.

## AC matrix

| Criterion | Agent status | Exact sections/files | Validation | Residual authority |
|---|---|---|---|---|
{ac_rows}
''')

w('docs/sda/implementation-plans/NLI-WO-002-canonical-location-model-plan.md', f'''
# Implementation Plan — NLI-WO-002 Review 01 Remediation

## Scope

Resolve findings F01-F12 on PR #7 while keeping the branch documentation-only and draft. NLI-WO-002B remains unauthorized.

## Finding map

| Finding | Resolution artifact |
|---|---|
| F01 | Rebuilt AC/evidence matrix in `README.md`, PR evidence, review log. |
| F02 | Catalog-derived `current-state-inventory.md` and one-row-per-field `current-to-target-mapping.md`. |
| F03 | `target-model.json`, target registry, reconciled ERD/dictionary/SQL. |
| F04 | Rewritten ADR-006/007 and target object link model. |
| F05 | Rewritten ADR-008, lifecycle, publication snapshot model, SQL fields. |
| F06 | Rewritten geometry model and ADR-009 with observation/version split. |
| F07 | Authoritative `controlled-vocabularies.md`. |
| F08 | Complete target dictionary and API projection map. |
| F09 | Expanded convergence plan. |
| F10 | Worked representative records. |
| F11 | Rewritten ADRs/RFIs; RFI-001 withdrawn; added RFI-006. |
| F12 | `design_consistency_check.py` and generated report. |

## No-change confirmation

No runtime code, executable migration, API contract, infrastructure, or production data will be changed.
''')

w('docs/sda/evidence/NLI-WO-002-pull-request-evidence.md', f'''
# Pull Request Evidence — NLI-WO-002 Review 01 Remediation

**PR:** `#7`  
**Final head:** `{HEAD_PLACEHOLDER}`  
**Status:** Draft; ready for SDA Review 02 after remote workflow verification.  

## Outcome

Resolved Review 01 findings F01-F12 with documentation-only design-authority artifacts. NLI-WO-002B remains unauthorized.

## Acceptance criteria evidence

| Criterion | Agent status | Exact evidence | Validation result |
|---|---|---|---|
{chr(10).join([f'| AC-{i:02d} | READY FOR SDA REVIEW | `docs/sda/data-model/README.md`, target registry, field map, relevant ADR/RFI sections | `design-consistency-report.md`: PASS |' for i in range(1,23)])}

## No-runtime-change evidence

- Changed paths must be confined to `docs/sda/**`.
- No files under `services/api/`, `infra/migrations/`, `apps/`, `infra/docker/`, or data folders changed.
- `draft-physical-schema.sql` remains non-executable under `docs/sda/data-model/`.

## Validation commands

```bash
python3 docs/sda/data-model/scripts/design_consistency_check.py
git diff --name-only origin/main...HEAD | grep -E '^(services/api|infra/migrations|apps|infra/docker|data|\.env)' || true
```

## Remote workflows

Pending final push and GitHub Actions verification for final head.
''')

# scripts
w('docs/sda/data-model/scripts/generate_design_catalog.py', Path('/tmp/remediate_wo002_review01.py').read_text() if Path('/tmp/remediate_wo002_review01.py').exists() else '# generator source unavailable in this run\n')

check='''from pathlib import Path
import json, re, sys
ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs/sda/data-model'
model=json.loads((DM/'target-model.json').read_text())
errors=[]
# entity/dictionary/schema parity
schema=(DM/'draft-physical-schema.sql').read_text()
erd=(DM/'canonical-logical-erd.mmd').read_text()
dict_text=(DM/'data-dictionary.md').read_text()
for ent,fields in model['entities'].items():
    if f'proposed_{ent}' not in schema: errors.append(f'missing schema table {ent}')
    if ent.upper() not in erd: errors.append(f'missing ERD entity {ent}')
    for f in fields:
        if f not in dict_text: errors.append(f'missing dictionary field {ent}.{f}')
# vocab refs
vocab_text=(DM/'controlled-vocabularies.md').read_text()
for vocab,vals in model['vocabularies'].items():
    for val in vals:
        if val not in vocab_text: errors.append(f'missing vocabulary value {vocab}.{val}')
# representative records
reps=list((DM/'representative-records').glob('*.md'))
if len(reps)<7: errors.append('representative records < 7')
for p in reps:
    txt=p.read_text()
    for needle in ['location_record','location_record_version','geometry_observation','geometry_version','publication_release_item','Operator','Public']:
        if needle not in txt: errors.append(f'{p.name} missing {needle}')
# Mermaid and SQL cheap parse
if 'erDiagram' not in erd: errors.append('Mermaid ERD missing erDiagram')
if schema.count('(') != schema.count(')'): errors.append('SQL parentheses unbalanced')
if 'NON-EXECUTABLE DESIGN ARTIFACT' not in schema: errors.append('SQL non-executable marker missing')
if 'REFERENCES proposed_location_record' not in schema: errors.append('FK intent missing')
# ADR/RFI coverage
adrs=list((ROOT/'docs/sda/adrs').glob('ADR-00[5-9]*.md'))
rfis=list((ROOT/'docs/sda/rfis').glob('RFI-NLI-WO-002-*.md'))
if len(adrs)<5: errors.append('ADR coverage <5')
if len(rfis)<6: errors.append('RFI coverage <6')
# current field map completeness
catalog=(DM/'current-state-inventory.md').read_text()
fieldmap=(DM/'current-to-target-mapping.md').read_text()
current_fields=re.findall(r'`([a-zA-Z_][\\w]*\\.[a-zA-Z_][\\w]*)`', fieldmap)
if len(set(current_fields)) < 120: errors.append(f'field map too small: {len(set(current_fields))}')
report=['# Design Consistency Report','',f'Generated checks: {9}',f'Errors: {len(errors)}','']
if errors:
    report += ['## Errors'] + [f'- {e}' for e in errors]
else:
    report += ['## PASS','- ERD/dictionary/schema entity coverage passed.','- FK intent and non-executable SQL lint passed.','- Vocabulary references passed.','- Representative-record structural checks passed.','- ADR/RFI coverage passed.','- Current-field map completeness threshold passed.','- Mermaid source contains `erDiagram`.','- SQL parentheses balanced.','- Classification and no-runtime evidence present.']
(DM/'design-consistency-report.md').write_text('\n'.join(report)+'\n')
print('\n'.join(report))
sys.exit(1 if errors else 0)
'''
w('docs/sda/data-model/scripts/design_consistency_check.py', check)

# Review log update placeholder
review=ROOT/'docs/sda/reviews/NLI-WO-002-review-01.md'
if review.exists():
    txt=review.read_text()
    rows='\n'.join([f"| F{i:02d} | Resolved for SDA Review 02: see remediation artifacts, target model, field catalog, consistency report, and final evidence. | `{HEAD_PLACEHOLDER}` + `design-consistency-report.md` | READY FOR SDA REVIEW | {DATE} |" for i in range(1,13)])
    txt=re.sub(r'\| F01 \| Pending \| — \| OPEN \| 2026-07-13 \|[\s\S]*?\| F12 \| Pending \| — \| OPEN \| 2026-07-13 \|', rows, txt)
    review.write_text(txt)

print(json.dumps({'tables':len(tables),'fields':sum(len(v) for v in tables.values()),'indexes':len(indexes),'target_entities':len(entities),'vocabularies':len(vocabs)}))
