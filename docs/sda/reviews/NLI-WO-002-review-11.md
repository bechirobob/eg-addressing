# SDA Review — NLI-WO-002 — Review 11

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `d2354ffb92f773d9d0310b4f9c8c817026d96525`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact remote PR head, PR body and Review 11 request, Review 10 task context/resolution matrix/S16 self-audit, exact-head GitHub Actions, changed-path inventory, F02 source/expected/implementation artefacts and transformation runner, F04–F07 PostgreSQL suite, F08 expected contracts and current OpenAPI observer/comparator, seven scenario sources/expected results and PostgreSQL comparison runner, F09/F11 reconciliation, F12 temporary-workspace mutation runner, controlled PR evidence, Review 10 resolution log, and separate maintenance PR #8.

Independent PR-state verification:

- PR #7 is **open**, **draft**, **mergeable**, and **unmerged**.
- Reviewed implementation/design head: `d2354ffb92f773d9d0310b4f9c8c817026d96525`.
- PR #7 remains within its design/evidence boundary. No application runtime implementation, executable migration, migration-runner change, frontend application, Docker runtime configuration, production/pilot data, or environment-secret path is introduced by the Review 10 remediation.
- NLI-WO-002B remains unauthorized.
- Maintenance PR #8 remains open, draft, unmerged, and separate.

Independent exact-head workflow verification:

- Agent skills CI run `29379279053`: **success**
  - `validate-agent-skill-pack` job `87239208161`: success
- API CI run `29379279075`: **success**
  - `sda-design-model` job `87239208387`: success
  - `api-tests` job `87239208348`: success
  - `migration-lifecycle` job `87239208373`: success
  - `api-image-runtime` job `87239208324`: success
- Frontend CI run `29379279063`: **success**
  - `frontend` job `87239208621`: success

Review 10 remediation removes validation-time bootstrap/repair from the main F02, F08 and F10 validators, corrects F02 second-run idempotency, adds PostgreSQL transactions to the F04–F07 suite, rebuilds observed OpenAPI from the current application, inserts scenario files into fresh temporary tables, and invokes a broader command chain in mutation workspaces. These are real improvements.

The design remains unaccepted because the evidence architecture still tests parallel shadow representations rather than the canonical target design and current runtime behavior. F02 treats each field as a separate source row and target identity, writes all values through generic text staging tables, and never constructs a complete target entity row in the proposed schema. F04–F07 use new `r10_*` tables and custom Python rules rather than the constraints, functions and typed entities of `draft-physical-schema.sql`. F05 still labels all required negative temporal cases as rejected without executing them. F08 observes OpenAPI only; dynamic successful responses remain a single `response.body` object and no FastAPI handler response is executed. F10 loads a generic scenario table rather than the proposed target tables; the multi-unit scenario contains one unit, and the disputed-geometry scenario contains no geometry/evidence/decision timeline. F12 reuses one database, omits `infra/` from mutation workspaces, seeds a passing mutation report, and several mutations sabotage test code rather than authoritative model or policy sources.

The repeated creation of review-specific parallel schemas and reports is now itself a blocker. A single authoritative design validation harness must execute the proposed model directly.

This review does not authorize NLI-WO-002B, executable convergence, production deployment, official publication, public-code issuance, certificates/signage, partner release, or real-data migration.

## 2. Review 10 finding disposition

| Finding | Review 11 disposition | Assessment |
|---|---|---|
| F02 | **OPEN — BLOCKER** | Validation no longer authors missing fixtures and idempotency is corrected. The source fixture remains one field per synthetic source row; a transform group therefore creates multiple target identities instead of one coherent target entity row. Output is stored in generic text tables and final FKs point to a generic identity table rather than actual proposed target entities. |
| F04 | **PARTIALLY RESOLVED — OPEN** | PostgreSQL transactions now execute many cases. They exercise a parallel `r10_*` schema and custom Python policy, not the proposed target constraints. Optional-role absence, every role maximum, and actual merged-subject repointing remain incomplete. |
| F05 | **OPEN — BLOCKER** | Three named-date queries execute for one synthetic history. Strategies are inferred from free-text metadata and only a subset is reported. Required cycle, reciprocal, cross-owner, overlap, backdated and interval cases are returned as labels rather than executed operations. |
| F06 | **PARTIALLY RESOLVED — OPEN** | A typed temporary trust model and several negative cases execute. Those entities/relationships are not part of the target model or physical proposal; actor/quality-actor, institution, observation, successor and multi-node cases remain incomplete. |
| F07 | **PARTIALLY RESOLVED — OPEN** | Graph reachability is computed and context negatives execute. Initial/terminal states are inferred instead of reviewed, re-entry/forbidden/conflict rules are not validated, and context uses a generic `transition:<vocab>` permission on only the first edge rather than each transition’s reviewed metadata. |
| F08 | **OPEN — BLOCKER** | Expected contracts are no longer repaired during validation and current OpenAPI is regenerated. The observer does not execute endpoints/handlers; dynamic responses remain broad `response.body: object`, exact nested success fields are absent, route auth/roles/scopes are not compared by the comparator, and extra observed fields are non-failing. |
| F09 | **OPEN — REQUIRED** | Units still inherit F02 assertion labels and generic identity/FK evidence rather than complete transformed target entity rows. |
| F10 | **OPEN — BLOCKER** | Fresh PostgreSQL tables are used, but they are a generic `r10_scenario_entity` shadow model rather than the proposed target schema. Scenario data is materially incomplete and cannot prove object relationships, evidence, geometry authority, lifecycle or release behavior. |
| F11 | **OPEN — ARCHITECTURE DECISION REQUIRED** | ADRs correctly remain proposed, but their evidence matrix inherits unresolved F02/F04–F10/F12 claims. |
| F12 | **OPEN — BLOCKER** | The command chain is broader. Mutation workspaces copy `docs/` and `services/` but not `infra/`, reuse the same database rather than creating a fresh database/schema per case, pre-seed the mutation report as passing, and several cases modify test scripts to raise expected text instead of mutating authoritative domain rules. |
| F13 | **RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN** | The runtime race fix remains isolated in PR #8 and absent from PR #7. |
| F14 | **NEW — BLOCKER: ASSURANCE ARCHITECTURE** | Review-specific shadow tables, generic entity stores and parallel policy implementations can pass while the proposed target schema remains wrong or incomplete. Evidence is not consistently generated by the design it claims to validate. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence/condition |
|---|---|---|
| AC-01 — Complete current-state inventory | CONDITION | Physical inventory is strong; several semantic owners/classifications and exact API projections remain unresolved or overly broad. |
| AC-02 — One canonical registry authority | CONDITION | `location_record` remains the intended anchor; transformation and relationship execution do not yet produce coherent target entity rows. |
| AC-03 — Administrative geography explicit | CONDITION | Structural concepts are coherent; authority and complete temporal/boundary execution remain conditional. |
| AC-04 — Operational areas separate | CONDITION | Conceptual separation exists; target-schema and authority execution remain incomplete. |
| AC-05 — Addressable-object coverage | FAIL | The model has a role matrix, but complete target-schema cardinality and representative multi-unit/rural/informal behavior are not proved. |
| AC-06 — Identifier separation | FAIL | Identifier classes are documented; final source-row-to-real-target-ID/FK execution is not proved. |
| AC-07 — Lifecycle separation | FAIL | Graphs/edges exist; reviewed graph semantics and transition-specific contextual enforcement are incomplete. |
| AC-08 — Temporal reconstruction | FAIL | A limited synthetic example executes; complete named-time reconstruction and chain negatives do not. |
| AC-09 — Geometry provenance and quality | FAIL | Technical concepts are strong; typed institutional authority is absent from the actual target model/schema and scenario evidence is incomplete. |
| AC-10 — Multilingual and naming integrity | CONDITION | A name model and one bilingual example exist; complete target-schema historical/merge/retirement behavior remains unproved. |
| AC-11 — Source and authority lineage | FAIL | Field-level staging does not demonstrate coherent source-record-to-target-entity lineage. |
| AC-12 — Data classification | CONDITION | Reviewed classification artifacts exist; API success fields remain broad and target ownership is not field-complete for dynamic outputs. |
| AC-13 — Controlled vocabularies | CONDITION | Vocabulary/edge sources exist; complete graph/context enforcement remains open. |
| AC-14 — Integrity constraints | FAIL | Many draft constraints execute, but new assurance suites often test custom shadow policies rather than the draft schema itself. |
| AC-15 — API projection compatibility | FAIL | OpenAPI schema compatibility is checked, but actual dynamic handler results and exact nested target projections are not. |
| AC-16 — Current-to-target no-loss mapping | FAIL | Field coverage exists, but grouped source rows are fragmented into per-field identities and actual target rows/FKs are not created. |
| AC-17 — Expand–migrate–contract plan | FAIL | Units depend on unresolved F02/F04–F10 assurance. |
| AC-18 — Representative records | FAIL | Seven names/files exist, but several scenarios are simplified generic entities rather than complete target-domain records and histories. |
| AC-19 — Scale and index rationale | CONDITION | Assumptions remain owner-pending and are not national production evidence. |
| AC-20 — Draft physical schema coherent | FAIL | The schema executes, but the main assurance suites do not consistently validate that exact schema and its functions. |
| AC-21 — ADR decision pack | FAIL | ADRs correctly remain proposed; defining guarantees and institutional conditions remain open. |
| AC-22 — No runtime behavior change | PASS | PR #7 remains design/evidence only; PR #8 remains separate. |

## 4. Open findings

### NLI-WO-002-F02 — Field-level fixtures do not transform coherent source records into real target entities

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-02, AC-06, AC-11, AC-16, AC-17, AC-20

**Observation:** Validation-time authoring has been removed and expected fixtures are read only by comparison. However, each field has its own synthetic `source_row_key`. Fields from one operational record—such as correction type, public code and status—are therefore treated as separate source rows. `execute_transform_once()` creates one target identity and target output per field, not one coherent `correction_case` or other target entity populated by the group. Structured latitude/longitude/accuracy inputs are likewise represented as separate field rows.

The runner writes all outputs to generic temporary tables with text `target_entity`, `target_field` and `actual_target_value` columns. `final_canonical_fk` references the generic `review09_transform_target_identity` table rather than the primary key of the proposed target entity. The target value is always stored as text even when an `actual_value_type` label says integer, numeric, boolean, JSON, timestamp or date. `no-loss-count` is set true per observed row rather than derived from a group-level source-record-to-target-row reconciliation.

**Risk/consequence:** The suite can pass while producing three correction-case identities from one correction row, multiple geometry observations from one grouped coordinate record, invalid target types, or FKs that never reference the actual target schema.

**Required resolution:** Replace field-row fixtures with complete source-record fixtures keyed by actual source primary/natural keys. Each transform group must consume one or more complete source records and construct the intended target entity rows and grouped child rows. Execute into `draft-physical-schema.sql` tables in an isolated schema, or exact typed mirrors generated mechanically from the target field registry with real PostgreSQL types and target-entity FKs. Validate one-to-one, one-to-many and grouped transforms at the entity/relationship level. Final FKs must reference actual inserted target rows. Derive group-level counts, hashes and relationships from queries. Preserve strict expected-error matching and zero-second-run-insert idempotency.

**Disposition:** OPEN

### NLI-WO-002-F04 — Record/cardinality tests run against a parallel policy implementation

**Class:** REQUIRED  
**Affected criteria:** AC-02–AC-05, AC-10, AC-14, AC-20

**Observation:** Fifty-seven PostgreSQL-backed cases are reported. The suite creates its own `r10_role_rule`, subject, record, version, link and name tables and implements cardinality in Python helpers rather than exercising the proposed physical schema’s tables/triggers. The valid case inserts every optional role rather than proving optional absence. Maximum-count testing uses only the first role for each record type. A merged subject is accepted when it has a successor, but the link is not actually repointed to that successor.

**Required resolution:** Run the matrix against the actual draft target tables, vocabulary rows and trigger/functions. For every role, test required/optional absence, minimum and maximum, each allowed/disallowed subject type, retired/deleted/merged behavior and actual successor repointing. Query exact persisted links and bilingual name history from the target schema. Delete the parallel role policy once parity is demonstrated.

**Disposition:** OPEN

### NLI-WO-002-F05 — Required temporal negative cases remain result labels, not executions

**Class:** BLOCKER  
**Affected criteria:** AC-03, AC-07, AC-08, AC-14, AC-20

**Observation:** The suite executes registry-as-recorded, effective-as-of and public-release queries against one synthetic `location_record_version` history. Entity strategies are inferred from free-text field metadata and only the first forty sorted entities receive report cases. The required two-node cycle, multi-node cycle, reciprocal mismatch, cross-owner, overlap, backdated correction and dependent-interval cases are implemented as lambdas returning `rejected-by-temporal-policy`; they do not perform an invalid insert/update or invoke a target policy.

**Required resolution:** Maintain an explicit reviewed temporal-strategy registry covering every authoritative mutable entity. Load representative histories into the actual draft target tables. Execute invalid chain/interval operations and require the target constraints/functions to reject for expected reasons with unchanged state. Execute independent named-date expected histories for administrative geography, records, names/codes, geometry, relationships, corrections/disputes and releases.

**Disposition:** OPEN

### NLI-WO-002-F06 — Typed geometry authority is a test-only schema, not part of the canonical model

**Class:** REQUIRED / ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-04, AC-09, AC-11, AC-14, AC-20, AC-21

**Observation:** The suite creates temporary actor, service, institution, membership, permission, territorial scope, data scope and authority-assertion tables and executes several useful cases. Those entities and relationships were not added to the target model or draft physical schema in this remediation. Geometry promotion in the canonical proposal therefore still depends materially on decision text/JSON rather than this typed trust model.

The matrix does not independently test a wrong institution separate from scope, a mismatched quality-assessment actor, an unrelated observation independent from evidence, cross-role/cross-subject successor integrity or a multi-node supersession cycle.

**Required resolution:** Decide through the appropriate ADR/RFI whether canonical identity/authorization entities are owned by this model or referenced from the future Identity and Trust domain. Add enforceable typed references/authority assertions to the target model and draft schema without duplicating identity authority. Bind geometry decision, observation, evidence and quality assessment to that assertion. Execute the complete target-schema positive/negative matrix.

**Disposition:** OPEN

### NLI-WO-002-F07 — Lifecycle graph semantics and contextual policy are inferred and generic

**Class:** REQUIRED  
**Affected criteria:** AC-07, AC-13, AC-14, AC-20

**Observation:** Reachability is now computed, but initial states are inferred as states with no incoming edges and terminal states as states with no outgoing edges. The suite does not compare these with reviewed initial/terminal declarations, validate permitted re-entry or forbidden transitions, or detect conflicting semantic edges beyond the temporary table primary key.

For each vocabulary, only the first transition is context-tested. The required permission is generated as `transition:<vocab>` rather than using the edge’s reviewed `permission_key`, institution/scope, evidence, audit event and public-effect metadata. The target transition validator remains less expressive than the temporary test policy.

**Required resolution:** Add reviewed graph metadata for initial states, terminal states, allowed re-entry and forbidden transitions. Compute graph properties against those declarations. Execute every edge or a coverage-complete policy partition using the actual reviewed transition metadata. Implement and test one target-schema contextual transition function/policy that enforces actor/permission, institution/scope, evidence, audit and public-effect prerequisites.

**Disposition:** OPEN

### NLI-WO-002-F08 — OpenAPI observation does not establish field-complete dynamic response contracts

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-10–AC-12, AC-15

**Observation:** The expected contract is now required and is no longer rewritten during validation. The observer regenerates the current FastAPI OpenAPI schema. It does not execute endpoints or deterministic handler/service fixtures. Where the OpenAPI response is an untyped object, `flatten_schema()` records only `response.body` with type `object`. Expected contracts therefore accept broad object envelopes such as the address-corrections response rather than enumerating the returned item and paging/status fields.

The comparator checks expected field keys and compatible types but does not compare method, path, handler identity, authentication mode, roles or scopes. Extra observed fields are explicitly non-failing. An API can therefore expose a new sensitive field while the contract remains green.

**Required resolution:** Execute current routes through a controlled FastAPI test client or deterministic handler/service fixtures and recursively capture actual success/error shapes. Keep expected contracts human-reviewed and field-complete, including collection item fields. Compare method/path/operation/handler/auth/roles/scopes, exact field set, type and requiredness. Unexpected fields must fail or be explicitly reviewed/classified. Map every field to an exact target/read-model/release field or explicit non-migrated decision.

**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence units remain dependent on field-level shadow-transform evidence

**Class:** REQUIRED  
**Affected criteria:** AC-17, AC-19

**Observation:** The reconciliation verifies assertion IDs, execution-mode labels, non-empty generic final-FK evidence and report summaries. It does not verify coherent source-record-to-target-entity output, actual target-table FKs, grouped transforms or entity-level idempotency. F02 remains open.

**Required resolution:** Revalidate every unit only after F02 uses coherent source rows and actual target entities. Reference exact transform commands, observed target keys/relationships, exceptions/archive results, group-level no-loss queries, idempotent rerun and recovery/cutover evidence.

**Disposition:** OPEN

### NLI-WO-002-F10 — Scenario execution uses a generic entity table and materially incomplete scenarios

**Class:** BLOCKER  
**Affected criteria:** AC-05, AC-08–AC-11, AC-14, AC-18, AC-20

**Observation:** Validation no longer bootstraps missing files and each scenario is inserted into a fresh temporary table. That table is a generic `r10_scenario_entity` with labels, date fields, booleans and JSON attributes; it is not the proposed target schema. It cannot enforce or prove canonical object links, geometry/evidence lineage, lifecycle transitions, typed authority, public alias/release item integrity or target constraints.

The multi-unit scenario contains one building and one unit while a string attribute says `units: 2`; it does not prove a building with multiple independently addressable units. The disputed-geometry source contains one address row and a `dispute_case` text attribute, with no geometry observation/version, evidence, decision, quality assessment, hold or resolution timeline. The boundary-change source contains two generic administrative-unit rows but no boundary geometry versions or authority decisions.

**Required resolution:** Load each hand-authored scenario into a fresh execution of `draft-physical-schema.sql` and use the actual target entities/relationships. Complete the multi-unit case with at least two independently addressable units, versions, aliases and release behavior. Complete correction, dispute and boundary histories with exact evidence, geometry, decision, lifecycle and release rows. Query named-time canonical, effective, recorded, operator and public projections and compare exact values/absences with independently reviewed expected results.

**Disposition:** OPEN

### NLI-WO-002-F11 — ADR evidence remains conditional on unresolved model execution

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21

**Observation:** ADRs remain proposed, which is correct. The evidence matrix describes the Review 10 suites as independently executable even though F02/F04–F10/F12 remain open and F06 still requires a trust-domain architecture decision.

**Required resolution:** Keep ADRs proposed. After underlying findings close, bind each ADR statement to target-schema or current-runtime evidence, preserve institutional RFIs, and obtain explicit SDA disposition for the architecture decisions.

**Disposition:** OPEN

### NLI-WO-002-F12 — Mutation suite is not isolated and several mutations sabotage tests rather than domain sources

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21

**Observation:** The mutation chain now invokes the main pipeline, F02, F08, F10, F04–F07, F09/F11 and consistency checker. However:

- each workspace copies `docs/` and `services/` but not `infra/` or other complete repository inputs required by the design pipeline;
- all mutation cases use the same `DATABASE_URL` rather than creating a fresh database/schema and cleaning it per mutation;
- the workspace pre-seeds `semantic-mutation-test-report.json` as passing;
- the cardinality mutation edits the test script to raise `maximum count exceeded` immediately;
- the geometry mutation changes the test’s guard to demand a missing rule;
- the lifecycle mutation changes the test script to raise unconditionally;
- these cases prove that an intentionally broken test program exits, not that a defect in the authoritative target model/policy is detected.

**Required resolution:** Copy or check out the complete repository per mutation. Provision a fresh disposable database or isolated schema per case, apply current migrations and target design from empty, and clean it afterward. Mutate authoritative target model, transition registry, role/cardinality source, geometry authority model, expected API contract or runtime response, transform implementation, and scenario source/query logic—not the test code that should detect the defect. Do not pre-seed passing assurance results. Run the exact same CI command path and require the named gate/reason.

**Disposition:** OPEN

### NLI-WO-002-F13 — Runtime maintenance remains correctly isolated

**Class:** RESOLVED FOR THIS WORK ORDER / EXTERNAL CONDITION  
**Affected criterion:** AC-22

**Observation:** PR #7 contains no migration-runner runtime fix. PR #8 remains separate.

**Condition:** PR #8 requires current-main synchronization, exact-head CI and its own NLI-WO-001 maintenance review before merge.

**Disposition:** RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN

### NLI-WO-002-F14 — Parallel shadow assurance architecture can diverge from the proposed model

**Class:** BLOCKER / ARCHITECTURAL REDESIGN REQUIRED  
**Affected criteria:** AC-02–AC-18, AC-20, AC-21

**Observation:** Review-specific scripts now create separate generic transformation, cardinality, temporal, authority, lifecycle and scenario schemas. These schemas and Python policies are not mechanically derived from or executed against the authoritative target model/draft physical schema. A safeguard can pass in the shadow model while being absent or different in the actual proposal. Repeated review cycles have added more reports and wrappers without eliminating this divergence.

**Risk/consequence:** Assertion volume and green CI can grow while the later WO-002B implementer still must invent target-table transforms, contextual lifecycle enforcement, typed trust references, exact API projections and representative target records.

**Required resolution:** Redesign the assurance architecture around one executable source of target truth:

1. Apply accepted current migrations in an isolated current/source schema.
2. Apply `draft-physical-schema.sql` in an isolated target schema.
3. Load hand-authored complete source records and independently reviewed expected target records.
4. Execute group-specific design transforms into the actual target tables.
5. Run F04–F07 and scenario cases through the target constraints/functions, not parallel policies.
6. Observe current API behavior through real test-client/handler execution and compare with immutable expected contracts.
7. Generate convergence and ADR evidence only from these authoritative executions.
8. Run mutations against authoritative sources in fresh, complete repository/database environments.

Retire the redundant `r10_*` shadow policy/schema paths once equivalent authoritative tests exist. Do not create another review-numbered parallel evidence framework.

**Disposition:** OPEN

## 5. Positive controls to preserve

- Exact-head GitHub submission and green CI.
- PR #7 draft/design-only boundary and separate PR #8.
- Live current pg_catalog and actual OpenAPI generation.
- Unknown-current-field fail-closed registries.
- Canonical `location_record` intent and identifier/public-alias separation.
- Administrative code history separate from identity.
- Draft target role matrix, native-subject checks, version/alias chains, object-link containment and release integrity.
- Corrected negative SQL helper with expected message matching.
- F02 zero-second-run-insert and duplicate checks.
- Required reviewed F02/F08/F10 inputs; no validation-time bootstrap/repair.
- Populated lifecycle transition source and positive edge execution.
- ADRs remain proposed rather than overclaimed accepted.
- S16 authorization boundary and NLI-WO-002B lock.

## 6. Evidence quality

The exact-head workflows prove that the submitted scripts and current assertions execute successfully. They do not establish assertions performed against different schemas, generic objects or synthetic policy helpers as facts about the canonical target design.

Reported counts—`1,607 transformation assertions`, `555 API assertions`, `57/50/11/133 F04–F07 cases`, `42 scenario assertions`, `4,371 checks` and `11/11 mutations caught`—must not be used as acceptance evidence without identifying the authoritative behavior each assertion executes. The current controlled evidence also retains older count/wording in the generator, reinforcing the need to replace report aggregation with evidence generated from the single authoritative harness.

## 7. Decision

`REWORK REQUIRED`

Review 11 recognizes genuine improvements in validation discipline. The remaining blocker is architectural: validation is fragmented across parallel shadow schemas and custom policies. Adding more report rows or review-specific wrappers will not close the work order. The next remediation must consolidate evidence around the actual draft target schema and current runtime API behavior.

Keep PR #7 draft and unmerged. NLI-WO-002B remains unauthorized.

## 8. Required follow-up sequence

1. Create one Review 11 assurance-harness architecture and migration plan; do not create another independent shadow schema.
2. Execute F02 complete-record transforms into actual target tables with real grouped identities/FKs/types.
3. Move F04–F07 tests to actual target constraints/functions and complete every required case.
4. Execute F08 through FastAPI test-client/handler observations with exact field-complete expected contracts.
5. Execute all seven F10 scenarios in the actual target schema with complete domain records and named-time outputs.
6. Rebuild F12 with complete repository copies and fresh database/schema per mutation, mutating authoritative sources only.
7. Revalidate F09/F11 after F02/F04–F10/F12 close.
8. Update Review 11 resolution rows, S16, controlled evidence and PR body at the new exact head; obtain green exact-head CI and request SDA Review 12.
9. Handle PR #8 separately under NLI-WO-001 maintenance controls.

## 9. Review 11 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F02 | Pending | — | OPEN | 2026-07-15 |
| F04 | Pending | — | OPEN | 2026-07-15 |
| F05 | Pending | — | OPEN | 2026-07-15 |
| F06 | Pending | — | OPEN | 2026-07-15 |
| F07 | Pending | — | OPEN | 2026-07-15 |
| F08 | Pending | — | OPEN | 2026-07-15 |
| F09 | Pending | — | OPEN | 2026-07-15 |
| F10 | Pending | — | OPEN | 2026-07-15 |
| F11 | Pending | — | OPEN | 2026-07-15 |
| F12 | Pending | — | OPEN | 2026-07-15 |
| F13 | Separate maintenance PR #8 | PR #8 remains separate | RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN | 2026-07-15 |
| F14 | Pending assurance-harness redesign | — | OPEN | 2026-07-15 |
