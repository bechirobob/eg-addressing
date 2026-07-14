# SDA Review — NLI-WO-002 — Review 07

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `af7f296f5672bbb2b060b912607b965ac90d8fae`  
**Primary Review 06 remediation commit:** `1cf7d555a08de750c580b87de14bc2020dc7a052`  
**Skill-protocol checkpoint commit:** `af7f296f5672bbb2b060b912607b965ac90d8fae`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact remote PR head, the merged repository-native agent skill pack, the Review 06 task-context pack and finding-resolution matrix, the complete Review 06 remediation set, current PostGIS catalog artefacts, reviewed transformation registry, typed target model, disposable physical proposal, record/object cardinality rules, temporal and geometry triggers, lifecycle transition registry, OpenAPI operation/policy/projection artefacts, seven positive scenario namespaces, seven reported negative cases, convergence units, ADRs 005–009, controlled PR evidence, PR #7 changed paths, and the separately isolated migration-ledger maintenance PR #8.

Independent PR-state verification at the reviewed implementation head:

- PR #7 is **open**, **draft**, **mergeable**, and **unmerged**.
- PR #7 head is `af7f296f5672bbb2b060b912607b965ac90d8fae`.
- NLI-WO-002B remains unauthorized.
- PR #7 no longer changes `infra/scripts/migrate.py`, application source, executable migrations, application directories, Docker runtime configuration, production/pilot data, or environment files.
- The migration-ledger race fix is isolated in draft PR #8 at `5650cd219156d23f10836ab7041b34693e9250b0`.

Independent workflow verification at `af7f296f5672bbb2b060b912607b965ac90d8fae`:

- Agent skills CI run `29345219086`: **success**
  - `validate-agent-skill-pack` job `87127013050`: success
- API CI run `29345218658`: **success**
  - `migration-lifecycle` job `87127010745`: success
  - `api-image-runtime` job `87127010827`: success
  - `sda-design-model` job `87127010839`: success
  - `api-tests` job `87127010871`: success
- Frontend CI run `29345218529`: **success**
  - `frontend` job `87127010434`: success

The new skill-protocol checkpoint is valid. It correctly records authority, scope, prohibited paths, selected skills, acceptance criteria, the separate maintenance dependency, and the distinction between agent readiness and SDA acceptance. It does not itself establish that the model findings are resolved.

This review confirms substantial technical improvement since Review 06: the record/object matrix now uses canonical record types; location-version and public-alias chains have reciprocal and cycle checks; object-link intervals are checked against owning versions; geometry promotion records decision/evidence/scope and validates observation/subject/role/type; method-plus-path route identity and all `_require_role` arguments are captured; the runtime race fix is separated; and PR #7 satisfies its design-only boundary.

The model is still not safe to authorize for executable convergence. The largest remaining problems are that transformation and no-loss statements are not executed as transformations, current semantic classifications remain heuristic, the lifecycle policy table is not shown populated or positively exercised, API projections remain generic for dynamic responses, the negative-test harness converts successful invalid actions into reported rejections, scenario fixtures remain broad generated shells, and the semantic PASS report does not detect those defects.

This review does not authorize NLI-WO-002B, executable schema convergence, production deployment, official publication, public-code issuance, or real-data migration.

## 2. Agent skill-protocol assessment

| Control | Assessment |
|---|---|
| Authority and scope header | PASS — work order, review, branch, change class, standards, and readiness boundary are identified. |
| Skill routing | PASS — S01/S02/S03/S05/S06/S08/S09/S11/S12/S13/S14/S16 are correctly selected for the current work. |
| Separate maintenance isolation | PASS for PR #7 — the runtime migration-ledger change is moved to PR #8. |
| Finding-specific planning | CONDITION — the matrix is more specific, but most findings still point to the same remediation commit and to reports that do not execute all claimed assertions. |
| Exact-head submission | PASS — remote head, PR state, workflows, and jobs are verified. |
| S16 self-audit | NOT RECORDED as a completed task artefact at the reviewed head; required before the next review request. |
| Reviewer-record protection | PASS — reviewer-owned Review 06 sections remain intact; agent changes are confined to the resolution log. |

## 3. Review 06 finding disposition

| Finding | Review 07 disposition | Assessment |
|---|---|---|
| F02 | OPEN — BLOCKER | Controlled-value examples improved and unknown fields fail closed, but reference mappings, no-loss assertions, archive transformations, classifications, and validations remain non-executed, generic, or semantically incomplete. |
| F04 | PARTIALLY RESOLVED — OPEN | `standard-address` is removed; actual record types, subject types, maximum counts, required roles, and interval containment are represented. Complete positive/negative proof for every record type and retirement/merge/name behavior is absent. |
| F05 | PARTIALLY RESOLVED — OPEN | Location-version and public-alias reciprocal/cycle checks and object-link containment are added. Complete supersession/relationship chains and temporal classification of every mutable authoritative entity remain incomplete. |
| F06 | PARTIALLY RESOLVED — OPEN | Geometry promotion now requires a decision ID, evidence ID, authority-scope value, matching observation, accepted quality, and same-subject/role successor. It does not prove permission-bearing actor/institution/scope authority or a decision-to-evidence/observation relationship. |
| F07 | OPEN — BLOCKER | Transition metadata is richer, but the disposable policy table is created without demonstrated population or positive execution; the only executed lifecycle case is a rejection that would also occur against an empty table. Graph completeness remains weakly checked. |
| F08 | OPEN — BLOCKER | Method/path/handler identities and complete role arguments improved. The expected registry describes itself as generated from observed AST, response contracts remain generic for dynamic 2xx objects, and classifications/target projections are still keyword/default driven. |
| F09 | OPEN — REQUIRED | Migration units contain complete field lists, but are generated groups with repeated controls and inherit no-loss statements that are not executed transformations. |
| F10 | OPEN — BLOCKER | Scenario namespaces and some histories improved. The negative harness catches its own “did not fail” assertion and reports rejection, so none of the seven negative results is trustworthy. Positive scenarios remain generated one-row-per-entity shells with limited scenario-specific assertions. |
| F11 | OPEN — ARCHITECTURE DECISION REQUIRED | ADRs are source-controlled and better structured, but several acceptance claims exceed the assertions actually performed and cannot be accepted while their defining findings remain open. |
| F12 | OPEN — BLOCKER | Exact-head semantic CI is deterministic and database-backed, but its checks still allow reproducible mapping, lifecycle, API, scenario, and negative-test defects while reporting zero errors. |
| F13 | RESOLVED FOR PR #7 WITH EXTERNAL CONDITION | The runtime fix is removed from PR #7 and isolated in PR #8. PR #8 remains a separate draft maintenance dependency requiring current-main synchronization, focused review, and acceptance under NLI-WO-001 controls. |

## 4. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 — Complete current-state inventory | FAIL | live pg_catalog inventory | Physical schema coverage is strong; semantic classification, purpose, field-specific readers/writers, authority, retention, and projections are still inferred or incomplete. F02/F08/F12. |
| AC-02 — One canonical registry authority | CONDITION | target model, subject registry, crosswalk model | `location_record` remains the intended sole anchor; reference-transform and relationship proof is not complete. F02/F04. |
| AC-03 — Administrative geography explicit | CONDITION | identity/version/code-history model | Code authority and hierarchy structure improved; complete temporal and institutional authority remains conditional. F05 and open RFIs. |
| AC-04 — Operational areas separate | CONDITION | operational-area model and lifecycle | Conceptual separation remains sound; migration and geometry authority are not implementation-ready. F06/F09. |
| AC-05 — Addressable-object coverage | FAIL | object/cardinality model and scenarios | Canonical types and matrix exist, but not every record type has executed positive/negative cardinality proof or complete merge/retirement behavior. F04/F10. |
| AC-06 — Identifier separation | FAIL | ADR-005, crosswalks, transformation registry | Internal/public/legacy separation is clear; final reference-FK and crosswalk algorithms are not executable or fully reconciled. F02/F11. |
| AC-07 — Lifecycle separation | FAIL | lifecycle registries and policy helper | Fields bind to entity-specific graphs, but complete positive execution and graph semantics are unproved. F07/F12. |
| AC-08 — Temporal reconstruction | FAIL | version/alias triggers, exclusions, release snapshots | Important chain and interval controls exist; comprehensive entity temporal strategy and every supersession relationship remain incomplete. F05. |
| AC-09 — Geometry provenance and quality | FAIL | observation/version model and trigger | Technical promotion checks improved; institutional permission/actor/evidence linkage and complete negative proof remain incomplete. F06/F10/F12. |
| AC-10 — Multilingual and naming integrity | CONDITION | `name_record`, subject FK, current-name rule | Reusable naming and current-name uniqueness exist; complete multilingual/history/retirement behavior is not scenario-tested. F04/F10. |
| AC-11 — Source and authority lineage | FAIL | source/archive/evidence and mapping rows | Structures exist, but several source facts and reference joins are not executed and reconciled into authoritative target facts. F02. |
| AC-12 — Data classification | FAIL | current inventory and API contracts | Target classifications exist; current/API classifications still rely materially on keyword rules and generic defaults. F02/F08. |
| AC-13 — Controlled vocabularies | CONDITION | vocabularies and lifecycle binding | Entity-specific bindings improved; executable lifecycle behavior and complete graph tests remain open. F07. |
| AC-14 — Integrity constraints | FAIL | disposable SQL/catalog and reported negatives | Many constraints/triggers execute, but complete cardinality, temporal, lifecycle, promotion and negative assertions are not proven. F04–F07/F10/F12. |
| AC-15 — API projection compatibility | FAIL | OpenAPI/AST inventory and projection contracts | Operation identity improved; dynamic success fields and exact target projections/classifications remain generic or unresolved. F08. |
| AC-16 — Current-to-target no-loss mapping | FAIL | reviewed 237-row registry | Row coverage is exact, but value/relationship transforms and no-loss assertions are not actually executed against source and target data. F02/F12. |
| AC-17 — Expand–migrate–contract plan | FAIL | convergence groups | Generated units inherit unaccepted transformations and generic recovery/cutover language. F02/F09. |
| AC-18 — Representative records | FAIL | seven scenarios and seven reported negatives | Scenario-specific additions exist, but complete scenario outcomes are absent and the negative harness is false-positive prone. F10/F12. |
| AC-19 — Scale and index rationale | CONDITION | planning ranges and index list | Useful assumptions exist but remain unapproved estimates without capacity calculations and accountable owner approval. F09. |
| AC-20 — Draft physical schema coherent | FAIL | disposable target SQL/catalog | Schema executes, but open semantic constraints and unreliable negative evidence prevent coherence acceptance. F04–F07/F10/F12. |
| AC-21 — ADR decision pack | FAIL | ADRs 005–009/RFIs | Better source control and structure; acceptance claims remain ahead of evidence. F11. |
| AC-22 — No runtime behavior change | PASS | current PR #7 changed paths | Runtime fix is absent from PR #7 and isolated in PR #8. F13 condition applies separately. |

## 5. Open findings

### NLI-WO-002-F02 — Mapping coverage is exact, but transformations and no-loss evidence are not executable authority

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-06, AC-11, AC-12, AC-16, AC-17

**Observation:** The registry now contains stable source-row keys, observed correction values, valid correction-type outputs, review IDs, archive references, and explicit reference metadata. Unknown current fields fail CI. These are meaningful improvements.

Material defects remain:

- reference rows such as `address_corrections.address_id` name the final output as `proposed_legacy_crosswalk.legacy_id`; the prose says a later migration unit resolves a canonical target, but the registry does not execute or verify the final `location_record_id` foreign-key result;
- `executable_no_loss_assertion` values are stored SQL-like strings using `raise_exception(...)`, but the pipeline never executes them against transformed source and target fixtures;
- the registry loader only verifies that validation text begins with `SELECT` and that required keys/targets exist;
- several `validation_sql` statements only return counts or contain comments saying a later process must compare them;
- governed archive rows describe a URI/reference but do not execute creation of one archive object/value record per source field and reconcile it;
- current field classifications and lifecycle meanings continue to be generated from field-name keywords rather than a fully reviewed field semantic inventory.

**Risk/consequence:** WO-002B could satisfy registry row coverage while leaving references unresolved, producing duplicate grouped outputs, misclassifying sensitive facts, and claiming no loss without transformed-value reconciliation.

**Required resolution:** Create executable source-to-target transformation fixtures in disposable PostgreSQL/PostGIS. For every transform group, insert representative current rows, run the exact transformation, and assert target values, row identity, reference crosswalk joins, archive/evidence references, exceptions, and no-loss reconciliation. Replace nonstandard/pseudo assertion text with executable validation functions or test code. For reference fields, name and prove the final canonical FK output. Replace keyword-derived semantic classification/readers/writers with a reviewed field-semantic registry or explicitly owned exceptions.

**Disposition:** OPEN

### NLI-WO-002-F04 — Canonical cardinality model is improved but not comprehensively proven

**Class:** REQUIRED / ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-05, AC-10, AC-14, AC-20

**Observation:** The former `standard-address` defect is corrected. The physical matrix now uses canonical record types; triggers read the owning record type, enforce allowed subject types and maximum counts, and defer required-role checking. Subject registration also verifies native target existence.

The evidence does not yet demonstrate the complete matrix:

- positive scenarios cover `address`, `landmark`, `unit`, and `service-location`, but not canonical `building`, `entrance`, or `non-building-object` records;
- negative testing checks one duplicate-primary-object case, not missing roles, invalid role/entity combinations, excessive counts, or each record type;
- retirement and merge behavior is stored as matrix metadata but is not executed or tested;
- multilingual current-name/history behavior is not tested across all relevant subject types;
- the multi-unit example creates a second unit but not a separate canonical unit record, alias, release item, and expected projection for each independently addressable unit.

**Risk/consequence:** The model can appear complete while unsupported record compositions or lifecycle behavior remain to be invented during implementation.

**Required resolution:** Execute positive and negative datasets for every canonical record type. Test required and optional roles, minima/maxima, allowed subject types, missing-role failure, excessive-count failure, invalid role/entity pairing, subject retirement/merge effects, and multilingual official-name history. Complete the multi-unit scenario with independently addressable canonical unit records and projections or revise ADR-007 to state a different, fully tested rule.

**Disposition:** OPEN

### NLI-WO-002-F05 — Core chains improved, but complete temporal authority remains undefined

**Class:** BLOCKER  
**Affected criteria:** AC-03, AC-07, AC-08, AC-14, AC-20

**Observation:** Location-record versions and public-code aliases now have no-self, same-owner, reciprocal, and recursive cycle checks. Object-link effective periods are checked against the owning version. Geometry supersession includes self/cycle and same-subject/role checks. Effective/recorded exclusion constraints and current-row indexes are present.

Open gaps remain:

- `location_record_relationship` includes correction/supersession semantics but no equivalent reciprocal, same-owner or acyclic rule is demonstrated;
- not every mutable authoritative entity is classified and implemented as immutable, effective-only, recorded-time versioned, or bitemporal;
- administrative, road, building, unit, locality, name, publication and operational-area history are not all demonstrated through historical reconstruction tests;
- no executed suite proves two-node and longer cycles, reciprocal mismatch, cross-owner links, backdated corrections, and every contained/uncontained dependent interval.

**Risk/consequence:** A subset of history may be reconstructable while other authoritative chains can diverge or cycle.

**Required resolution:** Publish a complete temporal-strategy register for every mutable authoritative entity. Add equivalent chain rules to every relationship that represents correction/supersession. Execute positive historical reconstruction and negative two-node/multi-node cycle, reciprocal mismatch, cross-owner, overlap, backdated correction and interval-containment tests.

**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry promotion records authority metadata but does not verify institutional authorization

**Class:** BLOCKER  
**Affected criteria:** AC-04, AC-09, AC-11, AC-14, AC-20

**Observation:** Geometry observations and approved versions are separate. The trigger validates registered subject type, role, geometry type, SRID, dimensionality, validity, matching source observation, accepted quality, non-null decision/evidence/scope values, approved/accepted decision outcome, and same-subject/same-role successor.

The trigger does not establish that:

- the decision is specifically an `approve-geometry` decision;
- the actor held the role/permission named by the geometry-role matrix;
- the approving institution and territorial scope match the subject and geometry role;
- the evidence object is linked to the source observation and decision rather than merely existing;
- the quality assessment and decision were produced by authorized actors;
- promotion was denied for missing or mismatched actor/permission/scope combinations.

The matrix stores a `promotion_permission`, but the trigger does not use it.

**Risk/consequence:** A technically valid geometry with arbitrary approved decision/evidence identifiers can be promoted as canonical without the required government authority chain.

**Required resolution:** Model and validate actor, institution, permission, territorial/data scope, decision type, source observation, evidence, and quality-assessment relationships. Require the geometry-role matrix permission and subject scope during promotion. Execute negative tests for wrong decision type, unauthorized actor, wrong institution/scope, unrelated evidence, unrelated assessment, cross-subject/role supersession, and cycles.

**Disposition:** OPEN

### NLI-WO-002-F07 — Lifecycle policy is documented but not positively executed as an authoritative graph

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-13, AC-14

**Observation:** Lifecycle transitions are hand-authored and carry permission, scope, authority, evidence, audit, public-effect, time, reversal and denial metadata. Fields bind to entity-specific lifecycle vocabularies.

The disposable SQL creates `lifecycle_transition_policy` and a validator that accepts a row only when the table contains the edge. The reviewed pipeline does not demonstrate insertion of the authored transition rows into that table before scenario execution. The only executed lifecycle test calls a forbidden transition; an empty table would reject it and produce the same reported result.

The semantic checker validates metadata presence and a short forbidden-edge list, but does not prove complete graph reachability, intended terminality, re-entry policy, orphan-state absence, duplicate edges, or positive transitions for every lifecycle family.

**Risk/consequence:** The design can claim executable lifecycle policy while no valid transition is accepted in the physical proposal.

**Required resolution:** Populate the disposable transition-policy table from the independently reviewed lifecycle source. Execute positive and negative transitions for every bound lifecycle family. Validate graph reachability, initial and terminal states, allowed re-entry, orphan states, duplicate/conflicting edges, field-to-graph binding, permission/scope/evidence/audit requirements, and public effects.

**Disposition:** OPEN

### NLI-WO-002-F08 — Operation identity improved, but expected policy and field projections are not independent or field-complete

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-10–AC-12, AC-15

**Observation:** Method, path, operation ID, handler, source span, all role arguments, optional authentication and session-required logout are now captured. The earlier GET/POST and first-role defects for address routes are corrected.

Open defects remain:

- expected-policy rows state that they were generated from the exact handler AST; they are therefore not a genuinely independent reviewed expectation source;
- the pipeline copies the reviewed registry into the expected registry and compares identity, rather than maintaining a separately authored policy decision source with owner approval;
- dynamic successful responses are represented by a generic field such as `response` of type `object` rather than the actual returned field structure;
- target projections frequently use generic text such as `source_payload_archive or typed target projection listed in adapter test` rather than an exact target projection;
- request `authorization` is assigned an archive/target projection even though credentials must never be migrated as business data;
- current and API field classification still originates from keyword-based helper functions before being copied into reviewed artefacts;
- contract test identifiers are strings in documentation; this review found no executed field-level adapter tests for each listed dynamic field.

**Risk/consequence:** The pack can record incorrect authority or sensitive-field exposure and still pass by comparing generated/derived artefacts with one another.

**Required resolution:** Maintain a human-reviewed expected policy registry independent of AST generation and sign it through a controlled owner/status field. Verify every row against observed implementation. Define executable response-shape fixtures or explicit Pydantic models for dynamic successful responses. Map every request, success and error field to an exact target/projection, classification owner, release prerequisite, compatibility rule, adapter/deprecation path and real test. Explicitly prohibit credential/header migration.

**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence units remain generated summaries rather than implementation-authority units

**Class:** REQUIRED  
**Affected criteria:** AC-17, AC-19

**Observation:** Units now group complete source fields and cite target rows and source keys. `render_convergence()` still emits repeated generic crosswalk, read/write, idempotency, conflict, recovery, monitoring and cutover language. It carries up to six stored no-loss assertion strings per group, although those assertions are not executed transforms. The machine-readable units contain only unit ID, group, source fields and target fields.

**Risk/consequence:** NLI-WO-002B cannot derive safe migration ordering, application compatibility, exception capacity, rollback/forward recovery and cutover from these summaries.

**Required resolution:** After F02 closes, hand-review named migration units with executable transformation commands/tests, dependencies, distinct identity/reference crosswalk behavior, target FK outputs, application-version matrix, write ownership, exception schema/SLA, idempotency, conflict precedence, validation SQL and tolerance, backup/forward-recovery boundary, monitoring window, measurable cutover/abort gates and retirement proof. Keep scale figures explicitly unapproved until accountable owners approve their source and confidence.

**Disposition:** OPEN

### NLI-WO-002-F10 — Negative evidence is invalid and positive scenarios remain insufficiently specific

**Class:** BLOCKER  
**Affected criteria:** AC-05, AC-08–AC-11, AC-14, AC-18, AC-20

**Observation:** Seven independently named positive scenarios are executed and several scenario-specific rows/history were added. All seven named negative cases are reported as `rejected-by-real-execution`.

The negative harness is logically invalid. `expect_sql_failure()` raises `AssertionError` when all invalid statements succeed, then catches that same exception through a broad `except Exception` and records the test as rejected. It also does not compare the actual database/policy error to the expected error text stored in the fixture. Therefore a prohibited operation that succeeds is still reported as a passing negative test.

Positive scenario limitations remain:

- every scenario begins as a generated one-row-per-entity shell containing many unrelated placeholder records;
- the multi-unit case adds a second unit but not a separate canonical unit record, alias, release item and expected projection for both units;
- correction history adds two versions and releases but does not execute historical public/operator projection assertions at both dates;
- disputed geometry jumps to a resolved state without exercising open/hold/review/resolution/public-effect behavior;
- administrative-boundary change adds old/new administrative versions but not complete old/new approved boundary geometry versions and resulting authority/public behavior;
- the report validates insertion counts, not scenario-specific expected outcomes.

**Risk/consequence:** The design reports strong scenario and negative coverage even when semantic safeguards do not execute or fail.

**Required resolution:** Rewrite the negative harness so success of an invalid action fails outside the exception handler; catch only expected database/policy exceptions and assert the expected error class/message and unchanged state. Author seven independent scenario datasets/builders containing only relevant entities. Execute scenario-specific assertions for cardinality, history, geometry, evidence, authority, releases and exact public/operator projections.

**Disposition:** OPEN

### NLI-WO-002-F11 — ADRs are better controlled but cannot be accepted ahead of their defining evidence

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21

**Observation:** ADRs 005–009 are maintained as source documents, identify model objects, list alternatives and remain proposed. That is the correct control direction.

Several ADR acceptance checks claim that CI rejects invalid mappings, alias-chain gaps, missing promotion authority, and other safeguards that this review finds incomplete or incorrectly tested. ADR evidence points broadly to `Generated checks: 41, Errors: 0`, rather than to named assertions with known limitations.

**Risk/consequence:** Moving the ADRs to accepted status would authorize guarantees that the current executable design evidence does not establish.

**Required resolution:** Keep ADRs proposed. Reconcile every decision constraint and acceptance statement to a named passing assertion after F02/F04–F10/F12 close. Record unresolved institutional RFIs and unimplemented safeguards explicitly. Remove aggregate PASS counts as the primary decision evidence.

**Disposition:** OPEN

### NLI-WO-002-F12 — Exact-head semantic CI remains false-positive prone

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21

**Observation:** The pipeline builds a live current catalog, generates OpenAPI, executes the target schema, inserts fixtures, records constraints/indexes/triggers and runs deterministic CI. Those foundations are valuable.

The final assurance remains insufficient:

- the design checker validates transformation SQL by string prefix but does not execute transformations/no-loss statements;
- current/API classifications remain keyword-generated;
- route and projection artefacts contain generic values that satisfy required-key checks;
- physical parity checks compare field presence, type and nullability but not every expected default, FK target, vocabulary FK, check, unique/exclusion constraint, index, trigger and trigger behavior;
- lifecycle policy positive execution is absent;
- scenario success is primarily insertion/count based;
- the negative harness reports success even when the invalid action succeeds;
- `Generated checks: 41` is a fixed report line rather than a machine-derived inventory of named assertions.

**Risk/consequence:** A semantically incomplete national model receives a green design signal and appears ready for implementation authorization.

**Required resolution:** Add named executable assertions for every remaining finding: transformation examples and no-loss values/relationships, reviewed classifications, independent route expectations, exact dynamic response fields, lifecycle positive/negative graphs, complete metadata-to-catalog parity, scenario-specific outputs, and corrected negative tests. Generate the check count from executed named assertions and report limitations; fail CI whenever an asserted safeguard is not exercised.

**Disposition:** OPEN

### NLI-WO-002-F13 — Runtime maintenance is correctly isolated from PR #7

**Class:** RESOLVED FOR THIS WORK ORDER / EXTERNAL CONDITION  
**Affected criterion:** AC-22

**Observation:** PR #7 no longer contains `infra/scripts/migrate.py` or other prohibited runtime paths. The advisory-lock/ledger fix exists in separate draft PR #8 with one changed file and green API CI.

**Required condition:** Keep the fix out of PR #7. Rebase or merge the latest `main` into PR #8, rerun exact-head lifecycle/API tests, and obtain focused NLI-WO-001 maintenance review before merging it. PR #8 acceptance is separate from NLI-WO-002 design acceptance.

**Disposition:** RESOLVED FOR PR #7; EXTERNAL MAINTENANCE OPEN

## 6. Positive controls to preserve

- Repository-native skill routing and exact-head evidence protocol.
- Valid Review 06 task-context and finding-resolution checkpoint.
- PR #7 design-only changed-path boundary.
- Separate maintenance PR #8 for the migration-ledger race.
- Live PostGIS current catalog and actual OpenAPI generation.
- Unknown current fields fail the reviewed transformation registry.
- `location_record` remains the intended sole canonical anchor.
- Administrative code history remains separate from identity.
- Entity-specific lifecycle vocabulary binding remains fixed.
- Canonical record-type cardinality matrix replaces `standard-address`.
- Native subject existence and allowed subject-type checks.
- Location-version/public-alias reciprocal and cycle checks.
- Object-link interval containment.
- Geometry observation/version separation and enhanced technical promotion checks.
- Immutable release payload/hash/manifest and exact version/alias references.
- ADRs are source-controlled rather than generated output.
- Exact-head agent/API/frontend CI remains green.
- PR #7 remains draft and NLI-WO-002B remains unauthorized.

## 7. Evidence quality

The exact-head workflows are accepted as proof that the current agent pack, application, migration lifecycle, image runtime, frontend and design pipeline execute successfully at the reviewed commit. They are not accepted as proof that all Review 06 findings are closed because the exact source shows non-executed transformation assertions, generic API projections, incomplete lifecycle authority and a false-positive negative-test harness.

The task-context and finding matrix are useful planning records. A completed S16 self-audit artefact is absent at the reviewed head and must be added before Review 08 is requested. The Review 06 resolution log also uses repeated commit/evidence language; future updates must be finding-specific and must not represent agent readiness as SDA resolution.

## 8. Decision

`REWORK REQUIRED`

Review 07 recognizes substantial progress in scope discipline and several model constraints. The remaining defects are concentrated in the most consequential proof layers: source-to-target transformation, institutional geometry promotion, lifecycle execution, API projection, temporal completeness, representative scenarios and the semantic test harness itself.

Accepting the current pack would authorize NLI-WO-002B on the basis of no-loss statements that are not executed, route/projection contracts that remain generic, lifecycle policy without demonstrated valid transitions, and negative tests that can pass when the invalid operation succeeds.

Keep PR #7 draft and unmerged. NLI-WO-002B remains unauthorized.

## 9. Required follow-up sequence

1. Correct the negative-test harness first; add a regression proving an invalid action that succeeds causes the test suite to fail.
2. Execute reviewed transformation groups and no-loss/value/reference/archive assertions in disposable source and target schemas.
3. Complete record-type/cardinality and independent scenario proof for every canonical record type.
4. Complete temporal strategy and tests for every authoritative chain/entity.
5. Bind geometry promotion to actor, permission, institution, scope, decision type, observation, evidence and quality authority.
6. Populate and positively/negatively execute every reviewed lifecycle graph.
7. Replace generated/derived expected route policy with an independently controlled decision source and complete dynamic field projections.
8. Rebuild convergence units only from accepted executable transformations.
9. Reconcile ADR claims only after their named evidence passes.
10. Expand semantic CI to detect every Review 07 defect and produce a machine-derived named assertion report.
11. Add and complete the S16 self-audit artefact, update finding-specific resolution rows and exact-head evidence, run green CI, and request SDA Review 08.
12. Handle PR #8 through its separate NLI-WO-001 maintenance review; do not merge or duplicate it through PR #7.

## 10. Review 07 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F02 | Pending | — | OPEN | 2026-07-14 |
| F04 | Pending | — | OPEN | 2026-07-14 |
| F05 | Pending | — | OPEN | 2026-07-14 |
| F06 | Pending | — | OPEN | 2026-07-14 |
| F07 | Pending | — | OPEN | 2026-07-14 |
| F08 | Pending | — | OPEN | 2026-07-14 |
| F09 | Pending | — | OPEN | 2026-07-14 |
| F10 | Pending | — | OPEN | 2026-07-14 |
| F11 | Pending | — | OPEN | 2026-07-14 |
| F12 | Pending | — | OPEN | 2026-07-14 |
| F13 | Separate maintenance PR #8 | `5650cd219156d23f10836ab7041b34693e9250b0`; API CI `29332358470` | RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN | 2026-07-14 |
