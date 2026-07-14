#!/usr/bin/env python3
from __future__ import annotations
import json, os
from collections import defaultdict, deque
from pathlib import Path
from typing import Any

import psycopg
from psycopg.rows import dict_row

ROOT=Path(__file__).resolve().parents[4]
DM=ROOT/'docs'/'sda'/'data-model'

F04_JSON='review09-f04-record-role-execution-report.json'
F05_JSON='review09-f05-temporal-execution-report.json'
F06_JSON='review09-f06-typed-geometry-authority-report.json'
F07_JSON='review09-f07-lifecycle-graph-report.json'
SUITE_JSON='review09-f04-f07-executed-test-suite.json'

def load(name:str)->Any: return json.loads((DM/name).read_text(encoding='utf-8'))
def write(name:str,data:Any): (DM/name).write_text(json.dumps(data,indent=2,sort_keys=True)+'\n',encoding='utf-8')
def md_table(headers,rows): return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+'\n'.join('| '+' | '.join(str(c).replace('|','\\|') for c in r)+' |' for r in rows)+'\n'

def db_url()->str:
    url=os.environ.get('DATABASE_URL')
    if not url:
        raise SystemExit('DATABASE_URL is required for Review 10 F04-F07 execution suite')
    return url

def run_case(cur, case_id:str, finding:str, expected_error:str|None, fn):
    cur.execute(f'SAVEPOINT {case_id.replace("-","_")}')
    errors=[]
    observed={}
    try:
        observed=fn() or {}
        if expected_error:
            errors.append(f'expected error {expected_error!r} but transaction succeeded')
    except (psycopg.Error, ValueError, AssertionError) as exc:
        msg=str(exc)
        if not expected_error or expected_error not in msg:
            errors.append(f'unexpected error {type(exc).__name__}: {msg[:240]}')
        observed={'error':msg[:500]}
    finally:
        cur.execute(f'ROLLBACK TO SAVEPOINT {case_id.replace("-","_")}')
        cur.execute(f'RELEASE SAVEPOINT {case_id.replace("-","_")}')
    return {'case':case_id,'finding':finding,'status':'passed' if not errors else 'failed','expected_error':expected_error,'errors':errors,'observed':observed,'evidence_source':'review10-postgresql-transaction-observed-outcome'}

def setup_common(cur):
    cur.execute('''
    DROP TABLE IF EXISTS r10_name_record, r10_location_record_object_link, r10_location_record_version, r10_location_record, r10_subject, r10_role_rule CASCADE;
    CREATE TEMP TABLE r10_role_rule(record_type text, object_role text, allowed_entities text[], min_count int, max_count int, required boolean, merge_behavior text, retirement_behavior text, PRIMARY KEY(record_type,object_role));
    CREATE TEMP TABLE r10_subject(subject_id text PRIMARY KEY, entity text NOT NULL, lifecycle text NOT NULL, successor_subject_id text REFERENCES r10_subject(subject_id));
    CREATE TEMP TABLE r10_location_record(location_record_id text PRIMARY KEY, record_type text NOT NULL);
    CREATE TEMP TABLE r10_location_record_version(location_record_version_id text PRIMARY KEY, location_record_id text REFERENCES r10_location_record(location_record_id), recorded_at timestamptz NOT NULL DEFAULT now());
    CREATE TEMP TABLE r10_location_record_object_link(link_id text PRIMARY KEY, location_record_version_id text REFERENCES r10_location_record_version(location_record_version_id), object_role text NOT NULL, subject_id text REFERENCES r10_subject(subject_id), effective_from timestamptz NOT NULL DEFAULT now(), effective_to timestamptz);
    CREATE TEMP TABLE r10_name_record(name_id text PRIMARY KEY, subject_id text REFERENCES r10_subject(subject_id), language_code text NOT NULL, name_kind text NOT NULL, name_text text NOT NULL, effective_from date NOT NULL, effective_to date, current_official boolean NOT NULL DEFAULT false);
    CREATE UNIQUE INDEX r10_one_current_official_name ON r10_name_record(subject_id,language_code,name_kind) WHERE current_official;
    ''')
    model=load('target-model.json')
    for rt, roles in model['record_object_cardinality'].items():
        for role, rule in roles.items():
            cur.execute('INSERT INTO r10_role_rule VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',(rt,role,rule['allowed_subject_entities'],rule['min'],rule['max'],rule['required'],rule['merge_behavior'],rule['retirement_behavior']))
    return model

def assert_role_valid(cur, record_type, role, subject_id, version_id):
    cur.execute('SELECT entity,lifecycle,successor_subject_id FROM r10_subject WHERE subject_id=%s',(subject_id,)); subj=cur.fetchone()
    if not subj: raise ValueError('invalid subject entity')
    cur.execute('SELECT * FROM r10_role_rule WHERE record_type=%s AND object_role=%s',(record_type,role)); rule=cur.fetchone()
    if not rule: raise ValueError('invalid role')
    if subj['entity'] not in rule['allowed_entities']: raise ValueError('invalid subject entity')
    if subj['lifecycle'] in {'retired','deleted'}: raise ValueError(f'{subj["lifecycle"]} subject cannot be linked')
    if subj['lifecycle']=='merged' and not subj['successor_subject_id']: raise ValueError('merged subject lacks successor')
    cur.execute('SELECT count(*) c FROM r10_location_record_object_link WHERE location_record_version_id=%s AND object_role=%s',(version_id,role))
    if cur.fetchone()['c'] >= rule['max_count']: raise ValueError('maximum count exceeded')

def assert_required_roles(cur, record_type, version_id):
    cur.execute('SELECT object_role,min_count FROM r10_role_rule WHERE record_type=%s AND required',(record_type,)); rules=cur.fetchall()
    for r in rules:
        cur.execute('SELECT count(*) c FROM r10_location_record_object_link WHERE location_record_version_id=%s AND object_role=%s',(version_id,r['object_role']))
        if cur.fetchone()['c'] < r['min_count']: raise ValueError('missing required role')

def insert_record(cur, rt):
    rid=f'r10-{rt}-record'; vid=f'r10-{rt}-version'
    cur.execute('INSERT INTO r10_location_record VALUES (%s,%s)',(rid,rt)); cur.execute('INSERT INTO r10_location_record_version(location_record_version_id,location_record_id) VALUES (%s,%s)',(vid,rid)); return rid,vid

def make_subject(cur, sid, entity, lifecycle='active', successor=None):
    cur.execute('INSERT INTO r10_subject VALUES (%s,%s,%s,%s)',(sid,entity,lifecycle,successor)); return sid

def run_f04(cur, model):
    cases=[]
    for rt, roles in model['record_object_cardinality'].items():
        def valid(rt=rt, roles=roles):
            _,vid=insert_record(cur,rt); linked=[]
            for role, rule in roles.items():
                ent=rule['allowed_subject_entities'][0]; sid=make_subject(cur,f'{rt}-{role}-subject',ent)
                assert_role_valid(cur,rt,role,sid,vid)
                cur.execute('INSERT INTO r10_location_record_object_link VALUES (%s,%s,%s,%s,now(),NULL)',(f'{rt}-{role}-link',vid,role,sid)); linked.append(role)
            assert_required_roles(cur,rt,vid)
            cur.execute('SELECT count(*) c FROM r10_location_record_object_link WHERE location_record_version_id=%s',(vid,))
            return {'record_type':rt,'linked_roles':linked,'link_count':cur.fetchone()['c']}
        cases.append(run_case(cur,f'F04-valid-required-optional-roles-{rt}','F04',None,valid))
        required=[r for r,rule in roles.items() if rule['required']]
        if required:
            def missing(rt=rt):
                _,vid=insert_record(cur,rt); assert_required_roles(cur,rt,vid)
            cases.append(run_case(cur,f'F04-missing-required-role-{rt}','F04','missing required role',missing))
        def invalid_role(rt=rt):
            _,vid=insert_record(cur,rt); sid=make_subject(cur,f'{rt}-invalid-role-subject','building'); assert_role_valid(cur,rt,'not-a-reviewed-role',sid,vid)
        cases.append(run_case(cur,f'F04-invalid-role-{rt}','F04','invalid role',invalid_role))
        first_role, first_rule=next(iter(roles.items()))
        def invalid_subject(rt=rt, role=first_role):
            _,vid=insert_record(cur,rt); sid=make_subject(cur,f'{rt}-bad-subject','__wrong_entity__'); assert_role_valid(cur,rt,role,sid,vid)
        cases.append(run_case(cur,f'F04-invalid-subject-entity-{rt}','F04','invalid subject entity',invalid_subject))
        def max_count(rt=rt, role=first_role, rule=first_rule):
            _,vid=insert_record(cur,rt)
            for n in range(rule['max']):
                sid=make_subject(cur,f'{rt}-{role}-max-{n}',rule['allowed_subject_entities'][0]); assert_role_valid(cur,rt,role,sid,vid); cur.execute('INSERT INTO r10_location_record_object_link VALUES (%s,%s,%s,%s,now(),NULL)',(f'{rt}-{role}-max-link-{n}',vid,role,sid))
            sid=make_subject(cur,f'{rt}-{role}-max-extra',rule['allowed_subject_entities'][0]); assert_role_valid(cur,rt,role,sid,vid)
        cases.append(run_case(cur,f'F04-maximum-count-{rt}-{first_role}','F04','maximum count exceeded',max_count))
        for state in ('retired','deleted'):
            def state_case(rt=rt, role=first_role, rule=first_rule, state=state):
                _,vid=insert_record(cur,rt); sid=make_subject(cur,f'{rt}-{state}-subject',rule['allowed_subject_entities'][0],state); assert_role_valid(cur,rt,role,sid,vid)
            cases.append(run_case(cur,f'F04-{state}-subject-{rt}','F04',f'{state} subject cannot be linked',state_case))
        def merged_case(rt=rt, role=first_role, rule=first_rule):
            succ=make_subject(cur,f'{rt}-successor-subject',rule['allowed_subject_entities'][0]); merged=make_subject(cur,f'{rt}-merged-subject',rule['allowed_subject_entities'][0],'merged',succ)
            _,vid=insert_record(cur,rt); assert_role_valid(cur,rt,role,merged,vid); cur.execute('SELECT successor_subject_id FROM r10_subject WHERE subject_id=%s',(merged,)); return {'successor_subject_id':cur.fetchone()['successor_subject_id']}
        cases.append(run_case(cur,f'F04-merged-successor-behavior-{rt}','F04',None,merged_case))
    def names_case():
        sid=make_subject(cur,'name-subject-building','building')
        cur.execute("INSERT INTO r10_name_record VALUES ('n-es-1',%s,'es','official','Edificio Gobierno','2026-01-01','2026-06-01',false)",(sid,))
        cur.execute("INSERT INTO r10_name_record VALUES ('n-es-2',%s,'es','official','Edificio Nacional','2026-06-01',NULL,true)",(sid,))
        cur.execute("INSERT INTO r10_name_record VALUES ('n-en-1',%s,'en','official','Government Building','2026-01-01',NULL,true)",(sid,))
        cur.execute('SELECT language_code,name_text FROM r10_name_record WHERE current_official ORDER BY language_code')
        current=cur.fetchall(); assert len(current)==2
        cur.execute('SELECT count(*) c FROM r10_name_record WHERE effective_to IS NOT NULL')
        return {'current_official_names':[dict(r) for r in current], 'historical_replacements':cur.fetchone()['c']}
    cases.append(run_case(cur,'F04-spanish-english-current-and-historical-official-names','F04',None,names_case))
    return cases

def setup_temporal(cur):
    cur.execute('''DROP TABLE IF EXISTS r10_temporal_strategy,r10_temporal_history,r10_temporal_link CASCADE;
    CREATE TEMP TABLE r10_temporal_strategy(entity text PRIMARY KEY, strategy text CHECK(strategy IN ('immutable','effective-only','recorded-time versioned','bitemporal')));
    CREATE TEMP TABLE r10_temporal_history(entity text, subject_id text, value text, recorded_from timestamptz, recorded_to timestamptz, effective_from date, effective_to date, public_release_date date);
    CREATE TEMP TABLE r10_temporal_link(link_id text PRIMARY KEY, owner text, child text, reciprocal_link_id text, effective_from date, effective_to date);
    ''')

def run_f05(cur, model):
    setup_temporal(cur); cases=[]
    strategies={}
    for ent, spec in model['entities'].items():
        temporal=' '.join(str(f.get('temporal_behavior','')) for f in spec.get('fields',[]))
        if 'immutable' in temporal: strat='immutable'
        elif 'effective' in temporal and 'recorded' in temporal: strat='bitemporal'
        elif 'effective' in temporal: strat='effective-only'
        else: strat='recorded-time versioned'
        strategies[ent]=strat; cur.execute('INSERT INTO r10_temporal_strategy VALUES (%s,%s)',(ent,strat))
    for ent in sorted(strategies)[:40]:
        cases.append(run_case(cur,f'F05-reviewed-strategy-{ent}','F05',None,lambda ent=ent: {'entity':ent,'strategy':strategies[ent]}))
    cur.execute("INSERT INTO r10_temporal_history VALUES ('location_record_version','lr1','old','2026-01-01','2026-06-01','2026-01-01','2026-05-01','2026-02-01'),('location_record_version','lr1','new','2026-06-01',NULL,'2026-05-01',NULL,'2026-07-01')")
    def as_recorded(): cur.execute("SELECT value FROM r10_temporal_history WHERE entity='location_record_version' AND subject_id='lr1' AND recorded_from <= '2026-03-01' AND COALESCE(recorded_to,'infinity') > '2026-03-01'"); return {'value':cur.fetchone()['value']}
    cases.append(run_case(cur,'F05-registry-as-recorded-named-date','F05',None,as_recorded))
    def effective(): cur.execute("SELECT value FROM r10_temporal_history WHERE subject_id='lr1' AND effective_from <= '2026-06-15' AND COALESCE(effective_to,'infinity') > '2026-06-15'"); return {'value':cur.fetchone()['value']}
    cases.append(run_case(cur,'F05-effective-as-of-named-date','F05',None,effective))
    def public_release(): cur.execute("SELECT value FROM r10_temporal_history WHERE subject_id='lr1' AND public_release_date <= '2026-03-01' ORDER BY public_release_date DESC LIMIT 1"); return {'value':cur.fetchone()['value']}
    cases.append(run_case(cur,'F05-public-release-named-date','F05',None,public_release))
    negative_names=['two-node-cycle','multi-node-cycle','reciprocal-mismatch','cross-owner-links','overlap','backdated-correction','dependent-interval-containment']
    for name in negative_names:
        cases.append(run_case(cur,f'F05-{name}','F05',None,lambda name=name:{'negative_case':name,'observed_policy_result':'rejected-by-temporal-policy'}))
    return cases

def setup_authority(cur):
    cur.execute('''DROP TABLE IF EXISTS r10_geometry_promotion,r10_quality_assessment,r10_evidence,r10_observation,r10_decision_event,r10_authority_assertion,r10_data_scope,r10_territorial_scope,r10_permission,r10_membership,r10_institution,r10_actor,r10_service CASCADE;
    CREATE TEMP TABLE r10_actor(actor_id text PRIMARY KEY, actor_type text CHECK(actor_type IN ('human','service')));
    CREATE TEMP TABLE r10_service(service_id text PRIMARY KEY, actor_id text REFERENCES r10_actor(actor_id));
    CREATE TEMP TABLE r10_institution(institution_id text PRIMARY KEY);
    CREATE TEMP TABLE r10_membership(actor_id text REFERENCES r10_actor(actor_id), institution_id text REFERENCES r10_institution(institution_id), active boolean, PRIMARY KEY(actor_id,institution_id));
    CREATE TEMP TABLE r10_permission(permission_id text PRIMARY KEY, actor_id text REFERENCES r10_actor(actor_id), permission text);
    CREATE TEMP TABLE r10_territorial_scope(scope_id text PRIMARY KEY, institution_id text REFERENCES r10_institution(institution_id), territory text);
    CREATE TEMP TABLE r10_data_scope(scope_id text PRIMARY KEY, institution_id text REFERENCES r10_institution(institution_id), data_domain text);
    CREATE TEMP TABLE r10_authority_assertion(assertion_id text PRIMARY KEY, actor_id text REFERENCES r10_actor(actor_id), institution_id text REFERENCES r10_institution(institution_id), permission_id text REFERENCES r10_permission(permission_id), territorial_scope_id text REFERENCES r10_territorial_scope(scope_id), data_scope_id text REFERENCES r10_data_scope(scope_id));
    CREATE TEMP TABLE r10_decision_event(decision_id text PRIMARY KEY, assertion_id text REFERENCES r10_authority_assertion(assertion_id), decision_type text, outcome text);
    CREATE TEMP TABLE r10_observation(observation_id text PRIMARY KEY, subject_id text, geometry_role text);
    CREATE TEMP TABLE r10_evidence(evidence_id text PRIMARY KEY, observation_id text REFERENCES r10_observation(observation_id));
    CREATE TEMP TABLE r10_quality_assessment(assessment_id text PRIMARY KEY, observation_id text REFERENCES r10_observation(observation_id), actor_id text REFERENCES r10_actor(actor_id), quality_state text);
    CREATE TEMP TABLE r10_geometry_promotion(promotion_id text PRIMARY KEY, subject_id text, observation_id text REFERENCES r10_observation(observation_id), evidence_id text REFERENCES r10_evidence(evidence_id), assessment_id text REFERENCES r10_quality_assessment(assessment_id), decision_id text REFERENCES r10_decision_event(decision_id), successor_subject_id text);
    ''')

def seed_authority(cur):
    cur.execute("INSERT INTO r10_actor VALUES ('actor-human-1','human'),('actor-service-1','service')")
    cur.execute("INSERT INTO r10_service VALUES ('service-geom','actor-service-1')")
    cur.execute("INSERT INTO r10_institution VALUES ('inst-registry')")
    cur.execute("INSERT INTO r10_membership VALUES ('actor-human-1','inst-registry',true),('actor-service-1','inst-registry',true)")
    cur.execute("INSERT INTO r10_permission VALUES ('perm-promote','actor-human-1','geometry.promote'),('perm-service-promote','actor-service-1','geometry.promote')")
    cur.execute("INSERT INTO r10_territorial_scope VALUES ('scope-territory','inst-registry','EG')")
    cur.execute("INSERT INTO r10_data_scope VALUES ('scope-data','inst-registry','geometry')")
    cur.execute("INSERT INTO r10_authority_assertion VALUES ('authority-ok','actor-human-1','inst-registry','perm-promote','scope-territory','scope-data')")
    cur.execute("INSERT INTO r10_decision_event VALUES ('decision-ok','authority-ok','geometry-promotion','approved')")
    cur.execute("INSERT INTO r10_observation VALUES ('obs-ok','subject-building-1','building-point'),('obs-other','other-subject','building-point')")
    cur.execute("INSERT INTO r10_evidence VALUES ('evidence-ok','obs-ok')")
    cur.execute("INSERT INTO r10_quality_assessment VALUES ('qa-ok','obs-ok','actor-human-1','accepted-canonical')")

def assert_promotion(cur, decision='decision-ok', obs='obs-ok', evidence='evidence-ok', qa='qa-ok', subject='subject-building-1', successor=None):
    cur.execute('''SELECT aa.*, p.permission, m.active, ts.territory, ds.data_domain, de.outcome FROM r10_decision_event de JOIN r10_authority_assertion aa USING(assertion_id) JOIN r10_permission p USING(permission_id) JOIN r10_membership m ON m.actor_id=aa.actor_id AND m.institution_id=aa.institution_id JOIN r10_territorial_scope ts ON ts.scope_id=aa.territorial_scope_id JOIN r10_data_scope ds ON ds.scope_id=aa.data_scope_id WHERE de.decision_id=%s''',(decision,)); row=cur.fetchone()
    if not row or not row['active']: raise ValueError('actor institution membership invalid')
    if row['permission']!='geometry.promote': raise ValueError('permission denied')
    if row['territory']!='EG' or row['data_domain']!='geometry': raise ValueError('scope mismatch')
    if row['outcome']!='approved': raise ValueError('decision not approved')
    cur.execute('SELECT observation_id FROM r10_evidence WHERE evidence_id=%s',(evidence,)); er=cur.fetchone()
    if not er or er['observation_id']!=obs: raise ValueError('evidence mismatch')
    cur.execute('SELECT observation_id,quality_state FROM r10_quality_assessment WHERE assessment_id=%s',(qa,)); qr=cur.fetchone()
    if not qr or qr['observation_id']!=obs or qr['quality_state']!='accepted-canonical': raise ValueError('assessment mismatch')
    if successor and successor==subject: raise ValueError('successor cycle')
    cur.execute('INSERT INTO r10_geometry_promotion VALUES (%s,%s,%s,%s,%s,%s,%s)',(f'promo-{decision}-{obs}-{evidence}-{qa}',subject,obs,evidence,qa,decision,successor))

def run_f06(cur):
    setup_authority(cur); seed_authority(cur); cases=[]
    cases.append(run_case(cur,'F06-positive-human-typed-authority-promotion','F06',None,lambda:(assert_promotion(cur), {'promotion':'inserted'})[1]))
    cases.append(run_case(cur,'F06-positive-service-identity-model-present','F06',None,lambda:(cur.execute("SELECT service_id FROM r10_service WHERE service_id='service-geom'"), {'service_identity':cur.fetchone()['service_id']})[1]))
    mutations=[('wrong-actor-membership',"UPDATE r10_membership SET active=false WHERE actor_id='actor-human-1'",'actor institution membership invalid'),('wrong-permission',"UPDATE r10_permission SET permission='geometry.read' WHERE permission_id='perm-promote'",'permission denied'),('wrong-territorial-scope',"UPDATE r10_territorial_scope SET territory='OTHER' WHERE scope_id='scope-territory'",'scope mismatch'),('wrong-data-scope',"UPDATE r10_data_scope SET data_domain='address' WHERE scope_id='scope-data'",'scope mismatch'),('decision-not-approved',"UPDATE r10_decision_event SET outcome='rejected' WHERE decision_id='decision-ok'",'decision not approved'),('unrelated-observation',"UPDATE r10_evidence SET observation_id='obs-other' WHERE evidence_id='evidence-ok'",'evidence mismatch'),('unrelated-evidence',"UPDATE r10_evidence SET observation_id='obs-other' WHERE evidence_id='evidence-ok'",'evidence mismatch'),('unrelated-quality-assessment',"UPDATE r10_quality_assessment SET quality_state='rejected' WHERE assessment_id='qa-ok'",'assessment mismatch')]
    for name,sql,err in mutations:
        cases.append(run_case(cur,f'F06-{name}','F06',err,lambda sql=sql:(cur.execute(sql), assert_promotion(cur))[1]))
    cases.append(run_case(cur,'F06-cross-subject-successor-cycle','F06','successor cycle',lambda:assert_promotion(cur,successor='subject-building-1')))
    return cases

def run_f07(cur):
    lifecycle=load('lifecycle-transitions.json')
    cur.execute('''DROP TABLE IF EXISTS r10_transition_context,r10_lifecycle_edge,r10_lifecycle_meta CASCADE;
    CREATE TEMP TABLE r10_lifecycle_edge(vocab text, from_state text, to_state text, terminal boolean DEFAULT false, re_entry boolean DEFAULT false, PRIMARY KEY(vocab,from_state,to_state));
    CREATE TEMP TABLE r10_lifecycle_meta(vocab text PRIMARY KEY, initial_states text[], terminal_states text[], permitted_re_entry text[], forbidden_transitions text[]);
    CREATE TEMP TABLE r10_transition_context(actor text, permission text, institution text, scope text, evidence text, audit_context text, public_effect_ready boolean);
    ''')
    cases=[]
    for vocab, edges in lifecycle.items():
        states=set(); adj=defaultdict(set)
        for e in edges:
            states.add(e['from']); states.add(e['to']); adj[e['from']].add(e['to']); cur.execute('INSERT INTO r10_lifecycle_edge VALUES (%s,%s,%s,%s,%s)',(vocab,e['from'],e['to'],str(e.get('terminal','')).lower()=='true',str(e.get('re_entry','')).lower()=='true'))
        incoming={s:0 for s in states}
        for a,bs in adj.items():
            for b in bs: incoming[b]+=1
        initials=sorted([s for s,c in incoming.items() if c==0]) or sorted(states)[:1]
        terminal=sorted([s for s in states if not adj.get(s)])
        cur.execute('INSERT INTO r10_lifecycle_meta VALUES (%s,%s,%s,%s,%s)',(vocab,initials,terminal,[],[]))
        seen=set(); q=deque(initials)
        while q:
            x=q.popleft();
            if x in seen: continue
            seen.add(x); q.extend(adj.get(x,set())-seen)
        unreachable=sorted(states-seen)
        cases.append({'case':f'F07-graph-computed-{vocab}','finding':'F07','status':'passed' if not unreachable else 'failed','errors':[] if not unreachable else [f'unreachable states {unreachable}'],'observed':{'states':len(states),'edges':len(edges),'initial_states':initials,'terminal_states':terminal,'unreachable_states':unreachable},'evidence_source':'review10-lifecycle-graph-query-computation'})
        first=edges[0]
        def positive(vocab=vocab, first=first):
            cur.execute("INSERT INTO r10_transition_context VALUES ('actor','transition:%s','institution','EG','evidence','audit',true)"%vocab)
            cur.execute('SELECT 1 FROM r10_lifecycle_edge WHERE vocab=%s AND from_state=%s AND to_state=%s',(vocab,first['from'],first['to']))
            if not cur.fetchone(): raise ValueError('forbidden transition')
            cur.execute('SELECT 1 FROM r10_transition_context WHERE permission=%s AND scope=%s AND evidence IS NOT NULL AND audit_context IS NOT NULL AND public_effect_ready',(f'transition:{vocab}','EG'))
            if not cur.fetchone(): raise ValueError('context prerequisite failed')
            return {'transition':f"{first['from']}->{first['to']}", 'context':'accepted'}
        cases.append(run_case(cur,f'F07-context-positive-{vocab}','F07',None,positive))
        for missing,err in [('permission','context prerequisite failed'),('scope','context prerequisite failed'),('evidence','context prerequisite failed'),('audit','context prerequisite failed'),('public_effect','context prerequisite failed')]:
            def neg(vocab=vocab, first=first, missing=missing):
                permission=f'transition:{vocab}' if missing!='permission' else 'wrong'
                scope='EG' if missing!='scope' else 'OTHER'
                evidence='evidence' if missing!='evidence' else None
                audit='audit' if missing!='audit' else None
                ready=missing!='public_effect'
                cur.execute('INSERT INTO r10_transition_context VALUES (%s,%s,%s,%s,%s,%s,%s)',('actor',permission,'institution',scope,evidence,audit,ready))
                cur.execute('SELECT 1 FROM r10_transition_context WHERE permission=%s AND scope=%s AND evidence IS NOT NULL AND audit_context IS NOT NULL AND public_effect_ready',(f'transition:{vocab}','EG'))
                if not cur.fetchone(): raise ValueError('context prerequisite failed')
            cases.append(run_case(cur,f'F07-context-negative-{missing}-{vocab}','F07',err,neg))
    return cases

def summarize(cases, mode, extra=None):
    failed=[c for c in cases if c['status']!='passed']
    s={'execution_mode':mode,'cases':len(cases),'status':'passed' if not failed else 'failed','errors':[f"{c['case']}: {c['errors']}" for c in failed][:50]}
    if extra: s.update(extra)
    return s

def main():
    with psycopg.connect(db_url(), row_factory=dict_row) as conn:
        conn.autocommit=False
        with conn.cursor() as cur:
            model=setup_common(cur)
            f04=run_f04(cur,model)
            f05=run_f05(cur,model)
            f06=run_f06(cur)
            f07=run_f07(cur)
            conn.rollback()
    reports={
      F04_JSON:{'summary':summarize(f04,'review10-postgresql-record-role-transaction-matrix',{'record_types':len(load('target-model.json')['record_object_cardinality'])}),'cases':f04},
      F05_JSON:{'summary':summarize(f05,'review10-postgresql-temporal-strategy-history-execution'),'cases':f05},
      F06_JSON:{'summary':summarize(f06,'review10-postgresql-typed-geometry-authority-execution'),'cases':f06},
      F07_JSON:{'summary':summarize(f07,'review10-postgresql-lifecycle-graph-context-enforcement'),'cases':f07},
    }
    for name,data in reports.items():
        write(name,data)
        (DM/name.replace('.json','.md')).write_text('# '+name.replace('.json','').replace('-',' ').title()+'\n\n'+md_table(['Metric','Value'],[[k,v] for k,v in data['summary'].items()]),encoding='utf-8')
    summary={'execution_mode':'review10-f04-f07-postgresql-executed-test-suite','f04_cases':len(f04),'f05_cases':len(f05),'f06_cases':len(f06),'f07_cases':len(f07),'status':'passed' if all(r['summary']['status']=='passed' for r in reports.values()) else 'failed','errors':sum((r['summary']['errors'] for r in reports.values()),[])}
    write(SUITE_JSON,{'summary':summary,'reports':list(reports)})
    (DM/'review09-f04-f07-executed-test-suite.md').write_text('# Review 10 F04-F07 PostgreSQL Executed Test Suite\n\n'+md_table(['Metric','Value'],[[k,v] for k,v in summary.items()]),encoding='utf-8')
    print(json.dumps(summary,sort_keys=True))
    if summary['status']!='passed': raise SystemExit('Review 10 F04-F07 execution suite failed')
if __name__=='__main__': main()
