# SDA Review — NLI-WO-002 — Review 08

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `c94ececed0d7ac15281624b4825082bc547185cf`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact remote PR head, Review 07 resolution log, S16 self-audit, current PostGIS catalog and reviewed field semantics, transformation registry/fixtures/report, convergence units, target model and executable disposable schema, cardinality/temporal/geometry/lifecycle functions, OpenAPI operation/policy/projection artefacts, seven positive scenario namespaces, negative SQL/policy fixtures, ADR evidence matrix, semantic mutation tests, controlled PR evidence, changed-path inventory, and exact-head workflows.

Independent PR-state verification:

- PR #7 is **open**, **draft**, **mergeable**, and **unmerged**.
- Reviewed head: `c94ececed0d7ac15281624b4825082bc547185cf`.
- PR #7 remains design/evidence only. The only non-document implementation-support path is `.github/workflows/api-ci.yml` for design validation.
- No `services/api/**`, `apps/**`, `infra/scripts/migrate.py`, executable migrations, Docker runtime configuration, production/pilot data, or environment-secret path is changed.
- NLI-WO-002B remains unauthorized.
- Maintenance PR #8 remains separate.

Independent exact-head workflow verification:

- Agent skills CI run `29365628417`: **success**
  - `validate-agent-skill-pack` job `87196346301`: success
- API CI run `29365628425`: **success**
  - `sda-design-model` job `87196346300`: success
  - `api-tests` job `87196346448`: success
  - `migration-lifecycle` job `87196346289`: success
  - `api-image-runtime` job `87196346277`: success
- Frontend CI run `29365628457`: **success**

The remediation makes meaningful progress. The negative-fixture helper no longer catches its own false-pass assertion; lifecycle policy rows are populated and 96 allowed edges execute; record/object rules use canonical record types; geometry promotion checks decision type, permission key, institution/scope metadata, observation/evidence linkage and quality actor; public-code and version chains have reciprocal/cycle controls; the multi-unit fixture contains distinct records, versions, aliases and release items; runtime scope remains clean.

The design is not acceptance-ready because several evidence mechanisms still certify metadata presence rather than the claimed behavior. Most importantly, the F02 transformation runner does not transform a source fixture into target rows; it finds expected assertion IDs and writes `status: passed`. Dynamic API 2xx responses remain generic reviewed envelopes rather than field-complete projections. Scenario assertions are calculated from in-memory fixture dictionaries rather than querying the inserted target state and reconstructing exact public/operator outputs. The semantic mutation script checks custom predicates on mutated objects instead of executing the real pipeline/checker against those mutations. These defects propagate into convergence and ADR evidence.

This review does not authorize NLI-WO-002B, executable schema convergence, production deployment, official publication, public-code issuance, or real-data migration.

## 2. Review 07 finding disposition

| Finding | Review 08 disposition | Assessment |
|---|---|---|
| F02 | **OPEN — BLOCKER** | Registry/fixture coverage and semantic metadata improved, but `execute_transformation_fixtures()` does not execute transformations, insert target rows, or compare source/target values, relationships, hashes, archives, exceptions or final FKs. It marks assertions passed when matching assertion IDs exist. |
| F04 | **PARTIALLY RESOLVED — OPEN** | Canonical record types, role matrix, native-subject validation, min/max rules, multi-unit records and required-role triggers are meaningful improvements. Evidence remains incomplete for all record-type positive/negative compositions, missing required roles, invalid role/entity pairs, maxima, retirement/merge effects and multilingual name history. |
| F05 | **PARTIALLY RESOLVED — OPEN** | Version and alias reciprocal/cycle triggers, geometry supersession controls, exclusions and object-link containment exist. Complete temporal classification and executed historical reconstruction/cycle/mismatch/backdated tests across every authoritative mutable entity/relationship remain incomplete. |
| F06 | **PARTIALLY RESOLVED — OPEN** | Geometry promotion technical checks are strong. Actor permission, institution and territorial scope are represented as JSON claims rather than typed/authoritative relationships, and the negative suite does not prove every actor/institution/quality/observation/supersession mismatch required by the finding. |
| F07 | **PARTIALLY RESOLVED — OPEN** | The lifecycle policy table is populated and all 96 authored allowed edges execute positively. Complete graph validation—reachability, intended initial/terminal states, re-entry, orphan states, conflicting edges and executable permission/evidence/public-effect denial for every lifecycle family—is not established. |
| F08 | **OPEN — BLOCKER** | Method/path/handler/role identity is improved and credential fields are excluded from business migration. Dynamic successful responses still use `response.body.reviewed_payload` and explicitly defer field-level expansion until before WO-002B; many target projections remain generic. The expected policy/projection owners remain pending and field classifications are not fully authoritative. |
| F09 | **OPEN — REQUIRED** | Reviewed units are richer and tied to F02 assertion IDs, but those assertions do not execute source-to-target transforms. The convergence units therefore inherit unproved values/FKs/no-loss and cannot authorize implementation sequencing. |
| F10 | **PARTIALLY RESOLVED — OPEN** | The false-pass negative helper is fixed and invalid actions now produce expected database/policy exceptions. Positive scenario assertions are still calculated from generated in-memory fixture dictionaries and mostly test entity presence, record type and non-empty projection payloads rather than exact persisted scenario histories and public/operator projections. |
| F11 | **OPEN — ARCHITECTURE DECISION REQUIRED** | ADRs remain proposed and are linked to assertion IDs, which is correct. Their acceptance evidence inherits the unresolved F02/F04–F10/F12 guarantees; they cannot yet be accepted. |
| F12 | **OPEN — BLOCKER** | CI is deterministic and database-backed, but the eight mutation probes test their own local predicates rather than running the actual design pipeline/checker against mutated source artefacts. F02 passing without executing a transformation demonstrates the remaining false-positive risk. |
| F13 | **RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN** | The runtime race fix remains isolated in PR #8 and is absent from PR #7. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence/condition |
|---|---|---|
| AC-01 — Complete current-state inventory | CONDITION | Live pg_catalog coverage is strong; field-specific semantic authority, readers/writers and classification remain partly generic or owner-pending. |
| AC-02 — One canonical registry authority | CONDITION | `location_record` remains the intended sole anchor; relationship and transformation proof remains incomplete. |
| AC-03 — Administrative geography explicit | CONDITION | Identity/version/code-history structure is coherent; institutional boundary/hierarchy authority and complete temporal proof remain conditional. |
| AC-04 — Operational areas separate | CONDITION | Separation is represented; full geometry/temporal/migration authority remains pending. |
| AC-05 — Addressable-object coverage | FAIL | Model coverage exists, but complete record-type/cardinality/lifecycle scenario proof is absent. |
| AC-06 — Identifier separation | FAIL | Separation is documented; executable crosswalk-to-final-FK proof is absent. |
| AC-07 — Lifecycle separation | FAIL | Positive edges execute, but full graph and denial semantics are not proved. |
| AC-08 — Temporal reconstruction | FAIL | Core triggers exist; complete as-of reconstruction and all authoritative temporal strategies/chains are not proved. |
| AC-09 — Geometry provenance and quality | FAIL | Strong technical trigger; institutional actor/permission/scope lineage and full negative proof remain incomplete. |
| AC-10 — Multilingual and naming integrity | CONDITION | Reusable name model/current-name constraint exists; complete multilingual history and subject lifecycle proof remain incomplete. |
| AC-11 — Source and authority lineage | FAIL | Source/archive structures exist; transformations do not execute and reconcile lineage into target facts. |
| AC-12 — Data classification | FAIL | Reviewed files exist, but owners remain pending and API/current classifications remain partly generic. |
| AC-13 — Controlled vocabularies | CONDITION | Entity-specific vocabularies and transition rows exist; complete graph enforcement remains open. |
| AC-14 — Integrity constraints | FAIL | Many constraints execute, but full cardinality, temporal, lifecycle and geometry authority proof remains incomplete. |
| AC-15 — API projection compatibility | FAIL | Operation policy identity is improved; dynamic success fields and exact target projections are incomplete. |
| AC-16 — Current-to-target no-loss mapping | FAIL | 237 rows/90 fixture groups/1,370 assertion records exist, but no source-to-target transformation is executed. |
| AC-17 — Expand–migrate–contract plan | FAIL | Units depend on unproved F02 transformations and cannot yet govern implementation. |
| AC-18 — Representative records | FAIL | Seven datasets and real negative cases exist; exact persisted histories/projections and complete scenario-specific assertions remain incomplete. |
| AC-19 — Scale and index rationale | CONDITION | Planning ranges/indexes exist but remain owner-pending, unapproved assumptions. |
| AC-20 — Draft physical schema coherent | FAIL | Schema executes, but unresolved semantic guarantees and evidence gaps prevent coherence acceptance. |
| AC-21 — ADR decision pack | FAIL | ADRs correctly remain proposed; defining guarantees remain open. |
| AC-22 — No runtime behavior change | PASS | PR #7 is design/evidence only; maintenance work remains separate. |

## 4. Open findings

### NLI-WO-002-F02 — Transformation fixture report records assertion presence, not transformation execution

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-06, AC-11, AC-12, AC-16, AC-17

**Observation:** `transformation-fixtures-reviewed.json` contains fixture groups and expected assertion identifiers, but its `source_rows` are coverage metadata rather than complete source field values. `execute_transformation_fixtures()` checks group membership, required assertion IDs, review markers and metadata. For each matching ID it appends an assertion with `status: passed`. It does not create source rows, execute transform code/SQL, insert target rows, or query and compare target values, final foreign keys, archive objects, exception records, hashes or relationships. The report nevertheless states that fixtures and 1,370 assertions were executed.

**Risk/consequence:** A wrong mapping or transform can retain the expected assertion ID and receive a green no-loss report. NLI-WO-002B could then implement incorrect value translations, unresolved references or missing archives while appearing fully reconciled.

**Required resolution:** Build a disposable source-fixture schema/data set with actual representative values and a disposable target schema. Implement design-only executable transformation functions/SQL for every reviewed group. Run each transform and query target rows. Assert exact input/output values, row identity, controlled translations, source/target crosswalk joins, final canonical FKs, archive/evidence records, owned exceptions, counts, hashes and relationships. The report must be generated from database/test results, not expected assertion IDs. Add mutation tests that change an expected output or transformation and run the real transformation suite to prove failure.

**Disposition:** OPEN

### NLI-WO-002-F04 — Cardinality architecture exists, but record-type behavior is not fully exercised

**Class:** REQUIRED / ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-05, AC-10, AC-14, AC-20

**Observation:** The physical design now uses canonical record types and enforces subject type, maximum counts, required roles, subject existence and object-link interval containment. Positive fixtures include all canonical record types and the multi-unit scenario has distinct unit records, versions, aliases and release items.

The evidence does not execute a full matrix. It does not provide real negative cases for every record type, missing required roles, each invalid role/entity pairing, every maximum, retirement/merge behavior, or multilingual name-history behavior. Several scenario assertions verify that record types and matrix metadata are present rather than proving each composition through database outcomes.

**Required resolution:** Add independently authored positive and negative fixtures for every canonical record type. Execute missing-role, invalid-role/entity, minimum/maximum, retirement, merge, deleted/retired subject and multilingual-current/history cases. Query the inserted database state and assert the exact record/version/object/name results. Resolve or condition ADR-007 based on those outcomes.

**Disposition:** OPEN

### NLI-WO-002-F05 — Core temporal constraints are present, but complete historical reconstruction is not proved

**Class:** BLOCKER  
**Affected criteria:** AC-03, AC-07, AC-08, AC-14, AC-20

**Observation:** Location-version and public-alias chains have no-self, reciprocal, same-owner and recursive cycle rules. Geometry supersession and effective/recorded exclusions are improved. Object-link intervals are constrained by owning versions.

The submitted assertions primarily inspect fixture dictionaries for two versions, reciprocal pointers and interval values. They do not execute as-of queries proving what the registry believed, what was effective and what was released at named times. A complete temporal-strategy register for every mutable authoritative entity is not demonstrated, and equivalent executed cycle/cross-owner/backdated tests are not shown for every correction/supersession relationship.

**Required resolution:** Classify every authoritative mutable entity as immutable, effective-only, recorded-time versioned or bitemporal. Implement design queries for as-of registry/effective/public reconstruction. Execute positive histories and negative two-node/multi-node cycle, reciprocal mismatch, cross-owner, overlap, backdated correction and dependent-interval tests for every relevant chain/relationship.

**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry promotion checks metadata claims but not a typed institutional authority relationship

**Class:** REQUIRED  
**Affected criteria:** AC-04, AC-09, AC-11, AC-14, AC-20

**Observation:** The promotion trigger checks role/type/SRID/validity, source observation, evidence match, `approve-geometry` decision type/outcome, permission key, non-empty institution/scope values, quality actor and same-subject/role successor. This is substantial progress.

The permission, institution, territorial scope, evidence and quality actor are asserted through text/JSON values. The design does not establish a typed actor-membership-permission-scope relationship for the decision, nor does the submitted negative suite cover every mismatched actor, institution, scope, assessment, observation and supersession case.

**Required resolution:** Define a typed design relationship or explicit authority assertion connecting decision event, actor/service identity, institution membership, permission, territorial/data scope, source observation, evidence object and quality assessment. Make geometry promotion reference it. Execute the complete positive/negative matrix, including unauthorized actor, wrong institution, wrong scope, unrelated assessment/observation/evidence, cross-subject/role successor and multi-node cycle.

**Disposition:** OPEN

### NLI-WO-002-F07 — Lifecycle edges execute, but graph completeness and denial semantics remain unproved

**Class:** REQUIRED  
**Affected criteria:** AC-07, AC-13, AC-14

**Observation:** The transition-policy table is populated and all 96 authored allowed edges are successfully queried. Rows include permission, authority, evidence, audit and public-effect metadata.

The suite does not establish full graph validity: initial-state rules, reachability of every non-initial state, intended terminality, permitted re-entry, orphan states, conflicting/duplicate edges, or executable enforcement of permission/scope/evidence/public-effect denial for each lifecycle family.

**Required resolution:** Add a graph validator for every field-bound lifecycle. Prove initial states, reachability, terminality, re-entry and absence of orphan/conflicting edges. Execute representative allowed and denied transitions for every lifecycle family, including missing permission, scope, evidence and audit/public-effect prerequisite cases.

**Disposition:** OPEN

### NLI-WO-002-F08 — API field-projection evidence explicitly remains incomplete

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-10–AC-12, AC-15

**Observation:** Method/path/operation/handler identity, role extraction and credential exclusion are improved. The reviewed projection contracts still represent dynamic successful responses as `response.body.reviewed_payload` with type `reviewed-object-contract` and state that field-level expansion is required before WO-002B runtime implementation. Many targets use generic descriptions rather than exact target fields/projections. Review owners remain pending.

**Risk/consequence:** NLI-WO-002B would still need to discover or invent response fields, classifications and target adapters, risking sensitive-data exposure and compatibility breaks.

**Required resolution:** Independently author and approve the expected policy/projection registry. Generate executable response-shape fixtures from current handlers/tests for every dynamic success response. Enumerate every request, success and error field and map it to an exact canonical/read-model/release projection, classification owner, release prerequisite, compatibility/deprecation rule and test. Remove generic reviewed payload envelopes and unresolved target text. Continue explicitly excluding credentials/session material from business migration.

**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence units depend on non-executed transformation evidence

**Class:** REQUIRED  
**Affected criteria:** AC-17, AC-19

**Observation:** Reviewed migration units now include dependencies, version matrices, ownership, exceptions, idempotency, conflict, validation, recovery and gates. Their proof and validation references are F02 assertion IDs produced without executing source-to-target transformations.

**Required resolution:** Rebuild or revalidate every unit after F02 produces real transformed target rows and executable comparison evidence. Each unit must reference the exact transform command/test, final target rows/FKs, exception results, validation query/tolerance and recovery/cutover evidence. Keep owner-pending scale assumptions conditional.

**Disposition:** OPEN

### NLI-WO-002-F10 — Negative execution is fixed, but positive scenario proof remains fixture-presence based

**Class:** BLOCKER  
**Affected criteria:** AC-05, AC-08–AC-11, AC-14, AC-18, AC-20

**Observation:** The negative helper now catches only `psycopg.Error`, validates expected messages, rolls back state and raises `NegativeFixtureDidNotFail` outside the handler when an invalid action succeeds. This closes the Review 07 false-pass defect.

Positive scenario assertions are built from the in-memory fixture dictionaries after the database loop. They primarily verify record-type presence, required entity lists, interval fields and non-empty projection payload hashes. They do not query persisted target state for exact scenario histories or render/compare exact public and operator outputs. The scenario generator still starts each case with one row for every target entity and then adds selected scenario-specific changes.

**Required resolution:** Maintain independent scenario-specific source files/builders containing only relevant entities. After insertion, query the disposable target database and assert exact records, versions, relationships, evidence, geometry, authority decisions, lifecycle timeline and publication snapshots. Render expected public/operator projections and compare exact values at relevant dates for all seven scenarios. Retain the corrected negative harness.

**Disposition:** OPEN

### NLI-WO-002-F11 — ADR evidence remains dependent on unresolved guarantees

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21

**Observation:** ADRs remain proposed and reference named evidence, which is correct. Their evidence matrix depends on unresolved transformation, cardinality, temporal, geometry, API and semantic-checker guarantees.

**Required resolution:** Keep ADRs proposed. After F02/F04–F10/F12 close, update every acceptance statement to a specific passing executable assertion and list institutional RFIs/conditions. Do not cite aggregate check counts as decision evidence.

**Disposition:** OPEN

### NLI-WO-002-F12 — Mutation tests do not execute the actual validator against mutated artefacts

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21

**Observation:** `review07_semantic_mutation_tests.py` mutates in-memory objects and then uses custom local predicates to declare each mutation caught. It does not place mutated reviewed sources into a temporary workspace and run `review04_design_pipeline.py` or `design_consistency_check.py`. For example, it changes a final-FK string and directly checks whether the string is disallowed, removes a trigger and directly compares a required-name set, and removes a unit then directly counts units. These probes prove the probe predicates, not that the actual CI gates reject the mutated design.

The F02 report remaining green without transformation execution demonstrates the gap.

**Required resolution:** Build mutation tests that copy the design sources into a temporary workspace/database, apply one controlled mutation, and invoke the real generator/pipeline/checker. Each mutation must fail the actual relevant gate for the expected reason. Cover incorrect transformed output, missing archive/FK, wrong classification, missing cardinality/temporal/geometry/lifecycle constraint, wrong route policy/field projection, broken scenario output and negative-harness regression. Generate the assertion count from actual executed gates and disclose limitations.

**Disposition:** OPEN

### NLI-WO-002-F13 — Runtime maintenance remains correctly isolated

**Class:** RESOLVED FOR THIS WORK ORDER / EXTERNAL CONDITION  
**Affected criterion:** AC-22

**Observation:** PR #7 contains no runtime migration-runner change. Maintenance PR #8 remains separate.

**Condition:** PR #8 requires its own current-main synchronization, exact-head CI and NLI-WO-001 maintenance review before merge.

**Disposition:** RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN

## 5. Positive controls to preserve

- Exact-head GitHub and PostGIS-backed design validation.
- PR #7 draft/design-only boundary.
- Separate maintenance PR #8.
- Live current pg_catalog and actual OpenAPI generation.
- Reviewed field and transformation registries that reject unknown current fields.
- Canonical `location_record` anchor and identifier/public-alias separation.
- Administrative code history separate from identity.
- Canonical record-type role matrix and native-subject checks.
- Version/alias reciprocal and cycle triggers; object-link containment.
- Corrected negative-fixture helper and real database error matching.
- Geometry observation/version separation and stronger promotion checks.
- Populated lifecycle policy and positive execution of 96 edges.
- Immutable release payload/hash/manifest and exact version/alias links.
- ADRs remain proposed rather than overclaimed accepted.
- S16 scope/readiness self-audit and exact-head workflow evidence.
- NLI-WO-002B remains unauthorized.

## 6. Evidence quality

The exact-head CI is accepted as proof that the current pipeline and assertions pass. It is not accepted as proof of the claims that the pipeline does not execute. Counts such as `1,370 transformation assertions`, `49 scenario assertions`, `1,164 projection assertions`, `5,016 generated checks` and `8/8 mutations caught` are not acceptance evidence by themselves. The reviewed source shows that material assertions are metadata/presence predicates rather than transformed values, exact API fields, persisted scenario outputs or real checker mutations.

The S16 self-audit is useful but remains phrased as a pre-push checklist with external gates pending; PR body and controlled evidence also retain stale Review 06/pre–Review 08 framing. These are documentation corrections required at the next final head, but not the primary architectural blockers.

## 7. Decision

`REWORK REQUIRED`

The current design pack is substantially more mature and several important controls are credible. Acceptance would nevertheless transfer the remaining transformation, API projection, scenario and assurance decisions to NLI-WO-002B—the exact outcome the design-authority phase is intended to prevent.

Keep PR #7 draft and unmerged. NLI-WO-002B remains unauthorized.

## 8. Required follow-up sequence

1. Replace F02 assertion-presence reporting with actual disposable source-to-target transformation execution and reconciliation.
2. Replace generic API success envelopes with exact independently reviewed field projections.
3. Convert scenario assertions into post-insert database queries and exact public/operator historical outputs.
4. Convert mutation probes into real pipeline/checker mutation tests.
5. Complete record-type negative/cardinality/name/retirement cases and full temporal reconstruction tests.
6. Complete typed geometry authority linkage and lifecycle graph validation.
7. Revalidate convergence units and ADRs only after the above evidence passes.
8. Update S16, PR body, controlled evidence and Review 08 resolution rows at the new exact head; run green exact-head CI and request SDA Review 09.
9. Handle PR #8 separately under NLI-WO-001 maintenance controls.

## 9. Review 08 resolution log

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
| F13 | Separate maintenance PR #8 | PR #8 remains separate | RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN | 2026-07-14 |
