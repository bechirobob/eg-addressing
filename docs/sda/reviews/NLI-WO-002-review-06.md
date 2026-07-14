# SDA Review — NLI-WO-002 — Review 06

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `46371d41c64fb21c06e99fd120b19e55de11d571`  
**Primary remediation commit:** `76a006f6472272be44f9b10750af7200c75d7c3c`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact draft-PR head, all three commits after the Review 05 record, the Review 05 resolution log, current PostGIS catalog, review-owned transformation registry, typed target model, lifecycle field bindings and transition registry, subject/cardinality/temporal/geometry design SQL, independently stored route-policy and projection-contract registries, seven scenario datasets, negative-test execution, convergence/scale outputs, ADRs 005–009, controlled evidence, the migration-runner race fix, and exact-head workflows.

Independent workflow verification at `46371d41c64fb21c06e99fd120b19e55de11d571`:

- API CI run `29328987176`: **success**
  - `sda-design-model` job `87072079264`: success
  - `migration-lifecycle` job `87072079318`: success
  - `api-image-runtime` job `87072079319`: success
  - `api-tests` job `87072079323`: success
- Frontend CI run `29328987240`: **success**
  - `frontend` job `87072079667`: success

Independent PR-state verification:

- PR #7 remains open, draft, mergeable, and unmerged.
- NLI-WO-002B remains unauthorized.
- The working design branch contains no executable schema migration or production-data change.
- The branch **does contain a runtime release-tool change** to `infra/scripts/migrate.py`, moving migration-ledger initialization under the advisory lock. That change is technically reasonable and its tests pass, but it is outside the design-only authority of NLI-WO-002 and contradicts AC-22 and the submitted changed-path evidence.

The Review 06 remediation is materially stronger. Entity-specific lifecycle binding is corrected; route analysis is keyed by method/path; all role arguments are parsed; logout is explicitly session-required; a separately committed route-policy registry and projection-contract registry exist; subject/native, role/cardinality, temporal, geometry and publication triggers have expanded; seven scenario namespaces run separately; and all seven negative cases now invoke SQL or an executable policy validator.

The design remains below acceptance because multiple artifacts still satisfy structural checks while carrying incorrect domain semantics. The most consequential defects are a still-invalid reviewed transformation registry, a record/cardinality matrix disconnected from the actual record-type vocabulary, incomplete chain/promotion guarantees, demonstrably incorrect “reviewed” route-policy rows, generic rather than field-complete projection contracts, scenario shells that do not prove the required national cases, and CI assertions that do not detect those defects. The runtime migration-runner change is also a work-order boundary violation and must be separated before this PR can be accepted.

This review does not authorize NLI-WO-002B, executable schema convergence, production deployment, official publication, public-code issuance, or real-data migration.

## 2. Review 05 finding disposition

| Finding | Review 06 disposition | Assessment |
|---|---|---|
| F01 | RESOLVED WITH DOCUMENTATION ADVISORY | Exact implementation head and jobs are independently anchored in this review and the PR timeline. The PR body and controlled evidence remain stale and must be corrected before final acceptance. |
| F02 | OPEN — BLOCKER | Registry coverage and grouping improved, but controlled maps, target semantics, source-key/crosswalk algorithms and “executable” no-loss assertions remain incorrect or non-executable for material fields. |
| F03 | RESOLVED | The generic lifecycle overwrite was removed. Final fields such as `building.lifecycle_state` and `source_authority.status` are bound to their entity-specific vocabularies and lifecycle graphs. |
| F04 | PARTIALLY RESOLVED — OPEN | Native subject existence is now checked in deferred SQL. The role/cardinality matrix is hard-coded to `standard-address`, which is not a target `record_type`, and complete record-type requirements remain unenforced. |
| F05 | PARTIALLY RESOLVED — OPEN | Location-version reciprocal/acyclic and object-link containment checks improved. Public-code alias cycles, complete chain classes and comprehensive bitemporal treatment remain incomplete. |
| F06 | PARTIALLY RESOLVED — OPEN | Observation/version subject and role/type checks now execute. Promotion still does not require an actual authorized decision/evidence chain, and cross-subject/role supersession consistency is incomplete. |
| F07 | PARTIALLY RESOLVED — OPEN | Transition records now contain useful permission/scope/authority metadata and fields are bound to graphs. SQL enforcement covers only a small subset of canonical transitions, and CI does not prove graph reachability, terminality, re-entry or complete field-to-graph behavior. |
| F08 | OPEN — BLOCKER | Method/path and multi-role parsing improved, but the independently “reviewed” policy registry contains wrong method/handler associations, and response/projection contracts remain generic or empty for dynamic successful responses. |
| F09 | PARTIALLY RESOLVED — OPEN | Complete field lists and grouped units are present. Units still inherit defective transformations, pseudo-assertions and repeated generic migration controls; scale assumptions remain unapproved planning hypotheses. |
| F10 | PARTIALLY RESOLVED — OPEN | All seven negatives are now executed and selected scenarios have added rows/history. The seven datasets remain generated one-row-per-entity shells with limited scenario-specific semantics and incomplete expected public/operator projection validation. |
| F11 | PARTIALLY RESOLVED — OPEN | ADRs are no longer overwritten by the generator and contain evidence sections. They remain based on the prior shared body, are stale in status, and claim checks or guarantees not yet demonstrated. |
| F12 | OPEN — BLOCKER | Semantic CI is broader but still passes the defects in F02, F04–F10 and overstates field, policy, scenario, constraint and transformation validation. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 — Complete current-state inventory | FAIL | live pg_catalog plus generated semantic inventory | Physical schema coverage is accurate; field-specific readers, writers, authority, retention, source and projection meaning remain inferred or incomplete. F02/F08/F12. |
| AC-02 — One canonical registry authority | CONDITION | `location_record`, subject registry and crosswalk design | Sole-anchor intent is retained, but record/object role integrity and reference migration semantics remain incomplete. F02/F04. |
| AC-03 — Administrative geography explicit | CONDITION | identity/version/code-history model | Code-history authority and lifecycle binding are improved; hierarchy/history and full temporal behavior still require closure. F05. |
| AC-04 — Operational areas separate | CONDITION | operational-area model | Separation remains sound; migration, geometry and temporal authority are not implementation-authority ready. F06/F09. |
| AC-05 — Addressable-object coverage | FAIL | object model/cardinality/scenarios | Entities exist, but the matrix uses a non-existent `standard-address` type and required roles/cardinalities are not proven for actual record types. F04/F10. |
| AC-06 — Identifier separation | FAIL | ADR-005, crosswalk model, transformation registry | Separation is stated; material FK/ID transforms still resolve only to generic crosswalk fields without a complete canonical join algorithm. F02/F11. |
| AC-07 — Lifecycle separation | FAIL | field bindings and lifecycle-transitions.json | Vocabulary overwrite is fixed, but complete workflow enforcement and graph semantics are not proven. F07/F12. |
| AC-08 — Temporal reconstruction | FAIL | exclusions, chain triggers and release snapshots | Stronger than Review 05, but alias cycles, complete chain/interval classes and comprehensive recorded-time reconstruction remain incomplete. F05. |
| AC-09 — Geometry provenance and quality | FAIL | observation/version model, role matrix and triggers | Role/type checks execute; authorization/evidence promotion and complete supersession consistency remain incomplete. F06. |
| AC-10 — Multilingual and naming integrity | CONDITION | `name_record`, subject FK and current-name index | Reusable naming and current-name uniqueness are present; full subject/cardinality/history policy is not proven. F04/F05. |
| AC-11 — Source and authority lineage | FAIL | source/archive/assertion model and transformations | Archive concept is sound; mapping rows and exception/crosswalk joins do not consistently connect original facts to target authority. F02. |
| AC-12 — Data classification | FAIL | catalog, transformation and API contracts | Many classifications remain generated by keywords or broad defaults rather than explicit field-owner decisions. F02/F08. |
| AC-13 — Controlled vocabularies | CONDITION | entity-specific bindings and transition registry | Binding defect is fixed; graph completeness and enforcement remain partial. F07. |
| AC-14 — Integrity constraints | FAIL | executed target schema and negative harness | Selected constraints run, but actual record-type cardinality, all chain classes, promotion authority and lifecycle enforcement remain incomplete. F04–F07/F12. |
| AC-15 — API projection compatibility | FAIL | OpenAPI/AST policies and reviewed contracts | Route inventory exists, but reviewed policies contain wrong handler/method metadata and dynamic response fields/target projections remain unresolved. F08. |
| AC-16 — Current-to-target no-loss mapping | FAIL | 237-row reviewed registry | Row coverage is exact, but material controlled maps, grouped outputs, executable assertions and reference joins remain incorrect. F02. |
| AC-17 — Expand–migrate–contract plan | FAIL | migration-unit/scale plan | Units are more complete but inherit unaccepted transformations and generic controls. F02/F09. |
| AC-18 — Representative records | FAIL | seven positive and seven negative executions | Actual negative execution is improved; positive scenarios still do not prove each required national history, cardinality and projection. F10. |
| AC-19 — Scale and index rationale | CONDITION | scale ranges and target indexes | Ranges and workload notes exist; sources, confidence, calculations and approving owners remain pending. F09. |
| AC-20 — Draft physical schema coherent | FAIL | executable design SQL/catalog | SQL executes, but domain cardinality, chain, geometry-promotion and lifecycle semantics remain incomplete or disconnected. F04–F07/F12. |
| AC-21 — ADR decision pack | FAIL | ADRs 005–009/RFIs | Source-document handling improved; several ADR claims remain stale or exceed passing evidence. F11. |
| AC-22 — No runtime behavior change | **FAIL** | changed paths and `infra/scripts/migrate.py` patch | The PR changes migration-runner behavior. The fix must be isolated into a separately governed maintenance PR and removed from PR #7. F13. |

## 4. Open findings

### NLI-WO-002-F02 — Reviewed transformation rows still encode invalid or non-executable migration decisions

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-06, AC-11, AC-12, AC-16, AC-17

**Observation:** The registry now has stable row keys, group IDs, examples and archive references. Material rows remain semantically invalid:

- `address_corrections.correction_type` targets `correction_case.correction_type`, but its controlled map uses current status-like values (`active`, `approved`, `pending`, `rejected`) and its example says `approved -> decision-approved`. Neither source values nor outputs match the target correction-type vocabulary (`administrative-context`, `classification`, `duplicate`, `geometry`, `label`). The current public UI sends values such as `record-update`.
- Many ID-reference transforms target only `legacy_crosswalk.legacy_id`; the row describes a future canonical lookup but does not identify the referenced source entity, target entity, source crosswalk key and target FK output required to insert the relation.
- The “executable no-loss assertions” are strings such as `ASSERT count(...)`; they are not PostgreSQL statements and are never executed.
- Several validation statements are row-count SELECTs followed by comments instructing a future comparison rather than performing that comparison.
- Grouped coordinate rows now share an ID, but each field separately claims one output geometry and no executed transform test proves one source row becomes exactly one correctly attributed geometry observation.

**Risk/consequence:** WO-002B could pass registry coverage while generating invalid controlled values, ambiguous foreign-key joins, duplicate geometries and unproved no-loss claims.

**Required resolution:** Correct each controlled map from observed current values to valid target vocabulary values. For every reference, define source entity/key, target entity/key, crosswalk lookup and final target FK. Replace pseudo-assertions with executable SQL or executable transformation fixtures that populate a disposable target and compare expected rows/values. Execute grouped transform tests for coordinates, IDs, status translations, archives and exceptions. CI must reject an approved row whose example, map, target vocabulary, target type or expected output disagree.

**Disposition:** OPEN

### NLI-WO-002-F04 — Record/object cardinality is disconnected from the canonical record-type vocabulary

**Class:** BLOCKER / ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-05, AC-10, AC-14, AC-20, AC-21

**Observation:** The shared subject registry now verifies that a declared native row exists, which resolves an important part of Review 05. The physical `record_object_role_matrix` contains only `record_type='standard-address'`, and `enforce_object_role_cardinality()` hard-codes that value. The canonical `record_type` vocabulary contains `address`, `building`, `entrance`, `landmark`, `non-building-object`, `service-location` and `unit`; it contains no `standard-address`.

The trigger therefore does not enforce a model keyed to actual record types. It also validates maximum counts but the deferred “required role” trigger checks only the presence of `primary-subject`, not the complete record-type matrix. The subject registry’s type/native checks do not by themselves establish all valid record-role combinations or multilingual-name history rules.

**Risk/consequence:** Records may be accepted under a matrix key that cannot occur in the canonical model, while required roles and type-specific composition remain undefined.

**Required resolution:** Replace `standard-address` with a complete matrix for every canonical record type or formally reduce the record-type vocabulary through an ADR. Make the trigger read the owning `location_record.record_type`; enforce minimums, maximums, allowed subject types and retirement/merge rules per type. Add scenario and negative tests for every record type, missing required roles, invalid role/entity pairs, excessive counts and retired/merged subjects.

**Disposition:** OPEN

### NLI-WO-002-F05 — Temporal guarantees remain incomplete outside the location-version chain

**Class:** BLOCKER  
**Affected criteria:** AC-07, AC-08, AC-14, AC-20

**Observation:** Location-record version triggers now require reciprocal same-owner pointers and include recursive cycle detection. Object-link interval containment is also enforced in the object-role trigger. Public-code aliases require reciprocal same-owner pointers but do not include recursive multi-node cycle detection. The model does not demonstrate equivalent chain guarantees for every claimed supersession relationship, and recorded-time history remains uneven across mutable authoritative objects.

**Risk/consequence:** Alias or other supersession chains may form cycles or inconsistent historical paths even though location versions pass. Historical reconstruction remains incomplete for mutable entities represented only by effective dates/current rows.

**Required resolution:** Apply no-self, reciprocal, same-owner and acyclic rules to aliases, geometry and every record relationship that represents supersession/correction. Catalogue each mutable authoritative entity as bitemporal, effective-only or immutable and justify the choice. Add executed tests for two- and multi-node cycles, backdated corrections, reciprocal mismatches, cross-owner links and contained/uncontained object intervals.

**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry promotion is not bound to an authorized decision/evidence chain

**Class:** BLOCKER  
**Affected criteria:** AC-09, AC-11, AC-14, AC-20

**Observation:** Role-to-subject, role-to-type, SRID, validity, dimensionality, source-observation and accepted-quality checks now execute for observations and versions. `geometry_role_matrix` stores a promotion permission, but the geometry trigger does not use an actor, permission, decision event, evidence link or approving authority. A version can be inserted with an accepted quality state once a matching observation exists. Supersession cycle logic does not explicitly require the successor to share subject and role.

**Risk/consequence:** A technically valid geometry can become canonical without the required institutional promotion decision or can supersede geometry belonging to a different subject/role.

**Required resolution:** Add explicit promotion decision/evidence/authority references to the model and require them in the trigger/policy validator. Enforce same-subject and same-role supersession. Execute negative tests for wrong subject type, wrong role/type, invalid SRID/3D/geometry, duplicate current geometry, missing or unauthorized promotion, cross-subject supersession and multi-node cycles.

**Disposition:** OPEN

### NLI-WO-002-F07 — Lifecycle metadata is richer, but complete graph behavior is not enforced or proven

**Class:** REQUIRED  
**Affected criteria:** AC-07, AC-13, AC-14

**Observation:** Entity-specific lifecycle bindings are now correct, and transitions include permission, scope, authority, evidence, audit and public-effect metadata. The executable `validate_lifecycle_transition()` function recognizes only selected canonical-record transitions. CI checks field binding, required edge metadata and a short forbidden-edge list; it does not prove graph reachability, declared terminality, intended re-entry, orphan-state absence, permission uniqueness or that every stateful entity uses the correct executable policy.

**Risk/consequence:** The design documents valid-looking graphs but leaves WO-002B to decide how most transitions are enforced and how invalid transitions are denied/audited.

**Required resolution:** Generate or maintain one executable transition-policy table/function from the reviewed graph registry for every bound lifecycle. Add graph reachability, terminality, re-entry, duplicate-edge, orphan-state and field-binding tests. Execute positive and negative transitions for every lifecycle family and verify permission, scope, evidence, audit and public-effect requirements.

**Disposition:** OPEN

### NLI-WO-002-F08 — Independently reviewed route policies and projection contracts remain inaccurate or generic

**Class:** BLOCKER  
**Affected criteria:** AC-10–AC-12, AC-15

**Observation:** Method/path keys, all `_require_role` arguments and session-required logout handling are implemented. The separately committed expected registry nevertheless contains incorrect associations. For example, the row keyed `GET /api/v1/addresses` records handler `create_address_endpoint` and method `POST`; the row keyed `GET /api/v1/addresses/{address_id}` records handler `archive_address_endpoint` and method `DELETE`. CI checks expected auth/roles for selected rows but does not verify method, handler, operation ID and source span against the actual route.

Dynamic successful responses remain represented as `<empty/error envelope>`. Their contracts use generic targets such as “current API adapter -> reviewed target field or release snapshot” and “target field/projection resolved in NLI-WO-002 adapter contract,” rather than enumerating actual response fields and exact target projections. Classification still originates from keyword defaults before being copied into reviewed contracts.

**Risk/consequence:** Current API authority, compatibility and sensitive-field projections can be recorded incorrectly while both the derived and expected artifacts remain green.

**Required resolution:** Verify every expected row against exact method, path, operation ID, function/handler, source span, auth mode and complete role set. Store the expected registry independently and fail on any mismatch. Create controlled response-contract inventories for all dynamic dictionary responses, based on implementation-return shapes and tests. Map every request, successful response and error field to an exact target field/projection, explicit owner-approved classification, release prerequisite, compatibility impact, adapter, deprecation and test.

**Disposition:** OPEN

### NLI-WO-002-F09 — Migration units are more complete but still inherit unaccepted transformations and pseudo-validation

**Class:** REQUIRED  
**Affected criteria:** AC-17, AC-19

**Observation:** Migration units now list complete source fields and group IDs. They still repeat generic dual-read/write, idempotency, conflict, recovery, monitoring and cutover text. Validation cells contain non-executable `ASSERT count(...)` strings from the transformation registry. Reference-crosswalk units group primary IDs and foreign-reference IDs under one generic `legacy_crosswalk.legacy_id` target without an executable target-FK plan.

Scale ranges now identify a basis, date, horizon and pending approving owner, which is useful, but they remain unapproved planning hypotheses rather than a capacity model.

**Risk/consequence:** The future implementation work order cannot safely sequence references, execute validation, estimate effort or approve cutover from these units.

**Required resolution:** Rebuild units after F02 closes. Each unit must include executable transforms/validation, dependency order, distinct identity versus reference-crosswalk behavior, target row/FK outputs, application-version matrix, owner, exception schema/SLA, backup and forward-recovery point, measurable cutover/abort thresholds and retirement proof. Preserve scale assumptions as explicitly unapproved inputs until owners approve them.

**Disposition:** OPEN

### NLI-WO-002-F10 — Scenario-specific proof remains incomplete despite real negative execution

**Class:** BLOCKER  
**Affected criteria:** AC-05, AC-08–AC-11, AC-18, AC-20

**Observation:** All seven negative cases now invoke SQL or an executable transition validator, resolving the prior simulated-result defect. Seven positive namespaces also execute separately. Each positive scenario still begins with one row for every target entity and only selected modifications:

- multi-unit adds a second unit and subject but does not create a separate canonical unit location, object link, public alias and expected projection for each unit;
- corrected/superseded adds two record versions and a second release, but does not clearly prove that the prior release item remains tied to the old version and that public historical reconstruction returns the correct payload at both dates;
- administrative-boundary adds old/new administrative versions but not corresponding old/new boundary geometry versions and public/authority behavior;
- disputed geometry marks a dispute resolved but does not exercise the full dispute/open/hold/resolution/public-effect timeline.

**Risk/consequence:** Aggregate insertion proves schema permissiveness, not support for the seven defining national scenarios.

**Required resolution:** Maintain seven independently authored scenario source files or explicit scenario builders containing only relevant records. For each, assert scenario-specific IDs, relationships, history, geometry, lifecycle, release payload and expected public/operator projections. Add explicit validators for the multi-unit, correction history, dispute and boundary-change requirements—not only row counts.

**Disposition:** OPEN

### NLI-WO-002-F11 — ADR source handling is fixed, but decisions remain stale or evidence-inconsistent

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21

**Observation:** ADRs are no longer generated during CI, which is a positive control. The documents retain much of the former common structure, remain labelled “Proposed for SDA Review 05,” and make acceptance claims not demonstrated by the current suite. ADR-005, for example, says a negative fixture rejects a duplicate current public alias, but that negative case is not among the seven executed negative fixtures. Other ADRs claim complete chain, subject or promotion guarantees that remain open in F04–F06.

**Risk/consequence:** A later implementer may cite an ADR as settled authority even though its evidence conditions are stale or false.

**Required resolution:** Update each ADR as an individually reviewed source document for the current review. Remove shared boilerplate where it obscures decision-specific consequences. Link every acceptance statement to a named passing assertion/test and mark open findings/RFIs explicitly. An ADR cannot move to accepted status while its defining guarantee remains open.

**Disposition:** OPEN

### NLI-WO-002-F12 — Semantic CI still reports PASS for defects it does not test

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21

**Observation:** The pipeline performs real database execution, route parsing, type/nullability parity and seven negative executions. Its final semantic check remains a short count/presence test. The secondary checker verifies selected known fields and metadata presence but does not detect the invalid correction-type map, the `standard-address` matrix mismatch, alias-cycle gap, missing geometry-promotion authority, wrong expected route handlers/methods, generic dynamic response contracts or scenario-history gaps.

Metadata-to-catalog comparison still focuses on column type/nullability plus aggregate constraint/index/trigger presence. It does not establish field-by-field default, FK, vocabulary FK, check, unique/exclusion, index, trigger and trigger-behavior parity. The report therefore says `Errors: 0` while material findings remain reproducible.

**Risk/consequence:** A national model receives a green government-design signal despite unresolved semantics and work-order noncompliance.

**Required resolution:** Add specific tests for every open finding: target-vocabulary/value examples, executable transformations and no-loss comparisons, actual record-type matrix keys, alias cycles, promotion authority, graph behavior, expected route method/handler/roles, dynamic response fields, scenario-specific outputs and complete metadata-to-catalog parity. The report must name each executed assertion and must not summarize unchecked guarantees as PASS.

**Disposition:** OPEN

### NLI-WO-002-F13 — Runtime migration-runner change violates the design-only work-order boundary

**Class:** BLOCKER  
**Affected criterion:** AC-22; work-order scope and prohibited approaches

**Observation:** The final remediation commit changes `infra/scripts/migrate.py` so ledger initialization occurs after acquiring the advisory migration lock. This fixes a real race and exact-head tests are green. NLI-WO-002 explicitly authorizes architecture/model documentation and CI design evidence only; it prohibits runtime code changes. The controlled evidence still states that no runtime code changed and that `.github/workflows/api-ci.yml` is the only permitted non-docs change.

**Risk/consequence:** Merging PR #7 would combine a runtime release-control change with an unaccepted model-design PR, defeating the work-order boundary, obscuring ownership and making AC-22 factually false.

**Required resolution:** Move the migration-runner race fix into a separate, tightly scoped maintenance branch/PR governed under the accepted NLI-WO-001 lifecycle controls, with the existing regression test and its own review. Restore `infra/scripts/migrate.py` in PR #7 to the current `main` version. Update the changed-path/evidence record and rerun exact-head CI.

**Disposition:** OPEN

## 5. Positive controls to preserve

- Exact-head PostGIS-backed design validation and all application workflows are green.
- Live current-schema catalog includes the migration ledger.
- Unknown current fields fail the review-owned transformation registry.
- Entity-specific lifecycle vocabulary overwrite is resolved.
- `location_record` remains the intended sole canonical anchor.
- Administrative code history is separated from identity.
- Shared subject FK and deferred native-target check exist.
- Method/path route keys and complete `_require_role` argument extraction exist.
- Lifecycle edge metadata is materially richer.
- Location-version chain and object-link containment checks are improved.
- Observation/version geometry distinction and role/type checks are implemented in disposable SQL.
- All seven named negative cases now use SQL or an executable transition validator.
- ADRs are no longer generated output.
- PR remains draft and NLI-WO-002B remains explicitly unauthorized.
- The migration-ledger race fix and regression evidence should be preserved in a separate maintenance PR.

## 6. Evidence quality

The exact-head workflow results are accepted as proof that the current design pipeline, application tests, migration lifecycle, image runtime and frontend checks pass. They also exposed and validated a real migration-ledger race fix. They are not proof that F02–F12 are closed: the mapping, route, scenario and model defects above are visible in the exact artifacts that CI accepts. The controlled PR evidence is also not accepted as accurate for AC-22 because it denies a runtime change that is present in the diff.

## 7. Decision

`REWORK REQUIRED`

Review 06 confirms sustained progress in the validation harness and in several important model controls. The pack is not yet safe to authorize for executable convergence. Accepting it would approve invalid controlled transformations, a cardinality matrix disconnected from canonical record types, incomplete temporal and geometry authority, incorrect reviewed route metadata, generic response projections and scenarios, overbroad PASS claims, and a runtime change outside the work-order boundary.

Keep PR #7 draft and unmerged. NLI-WO-002B remains unauthorized.

## 8. Required follow-up sequence

1. Split the migration-ledger race fix into a separate maintenance PR and remove it from PR #7.
2. Correct and execute the reviewed transformation registry, including controlled-value examples and reference crosswalk joins.
3. Align the record-type vocabulary and complete role/cardinality enforcement.
4. Close alias/relationship temporal chains and geometry-promotion authority.
5. Make lifecycle graphs fully executable/tested or explicitly implementation-ready with complete graph validation.
6. Correct the independent route-policy registry and complete dynamic response projection contracts.
7. Replace scenario shells with scenario-specific assertions and outputs.
8. Rebuild migration units from accepted executable transformations.
9. Reconcile ADR statements with passing evidence.
10. Expand semantic CI to detect every Review 06 finding, correct the evidence/PR body, rerun exact-head CI and request SDA Review 07.

## 9. Review 06 resolution log

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
| F13 | Pending | — | OPEN | 2026-07-14 |
