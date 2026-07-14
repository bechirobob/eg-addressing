# SDA Review — NLI-WO-002 — Review 10

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `844c9baf3452cc128583d17df71ce95114f7c57d`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact remote PR head, PR body and Review 10 request, Review 09 task context/resolution matrix/S16 self-audit, exact-head GitHub Actions, changed-path inventory, Review 09 source/expected/implementation transformation artefacts and runner, expected/observed API contract artefacts and comparator, seven scenario source/expected pairs and comparison runner, F04–F07 reported execution suite, semantic mutation runner, convergence/ADR reconciliation, Review 09 resolution log, and separate maintenance PR #8.

Independent PR-state verification:

- PR #7 is **open**, **draft**, **mergeable**, and **unmerged**.
- Reviewed implementation/design head: `844c9baf3452cc128583d17df71ce95114f7c57d`.
- PR #7 remains design/evidence only. No application runtime, API implementation, frontend application, migration runner, executable migration, Docker runtime configuration, production/pilot data, or environment-secret path is changed.
- NLI-WO-002B remains unauthorized.
- Maintenance PR #8 remains open, draft, unmerged, and separate.

Independent exact-head workflow verification:

- Agent skills CI run `29373930831`: **success**
  - `validate-agent-skill-pack` job `87223213178`: success
- API CI run `29373930834`: **success**
  - `sda-design-model` job `87223213095`: success
  - `api-tests` job `87223213090`: success
  - `migration-lifecycle` job `87223213107`: success
  - `api-image-runtime` job `87223213082`: success
- Frontend CI run `29373930935`: **success**
  - `frontend` job `87223213616`: success

Review 09 remediation improves structure and terminology. Source, expected and implementation artefacts now exist as separate committed files; the F02 rerun uses uniqueness and zero-second-run-insert checks; API expected/observed files are separately named; scenario expected files contain exact report sections; mutation cases invoke several real helper/checker commands; scope discipline remains strong.

The design remains unaccepted because file separation has not produced independent authority or real domain execution. The F02 runner can author all three supposedly independent artefacts from the same transformation registry, uses expected-fixture identities, target fields, crosswalks, archive/exception IDs and relationships to construct observed output, and writes generic temporary target tables rather than the proposed target entities. F08 can bootstrap expected contracts from the prior generated contract and observed fixtures from expected contracts; it repairs missing 2xx responses by inventing an operation-result field and never executes FastAPI handlers. F10 bootstraps scenario source from the broad generated fixture and expected results from the previous observed report; the comparison does not load the new source files or query a new database. The F04–F07 “executed” suite directly writes `status: passed` rows. The F12 chain runs the F02/API/scenario comparators and consistency checker but not the full design generator, target-schema/scenario database pipeline, or F04–F07 suite; several mutations still alter generated reports rather than authoritative model/policy sources.

This review does not authorize NLI-WO-002B, executable convergence, production deployment, official publication, public-code issuance, certificates/signage, partner release, or real-data migration.

## 2. Review 09 finding disposition

| Finding | Review 10 disposition | Assessment |
|---|---|---|
| F02 | **OPEN — BLOCKER** | Separate files exist and value transforms are compared, but the same script authors source/expected/implementation when absent; observed structural output is driven by expected-fixture IDs/targets/FKs/archive/exception/relationship rows; generic temporary tables do not prove the proposed target entities. Failure probes also accept any exception as caught. |
| F04 | **OPEN — REQUIRED** | Model constraints remain useful, but `review09_f04_f07_executed_tests.py` unconditionally creates passed rows for record types and negative cases; no record-role transaction matrix is executed by that script. |
| F05 | **OPEN — BLOCKER** | Core temporal constraints remain valuable. The Review 09 temporal report assigns strategies and passes to named cases without running named-date or chain transactions. |
| F06 | **OPEN — REQUIRED** | Geometry trigger checks remain useful. The claimed typed identity/membership/permission/scope relationships are names in a report, not target entities/relationships with executed cases. |
| F07 | **OPEN — REQUIRED** | Allowed edges still execute in the target pipeline. The Review 09 graph report assigns reachability, terminality, re-entry, orphan/conflict and context-prerequisite statuses rather than computing/enforcing them. |
| F08 | **OPEN — BLOCKER** | Expected and observed files are separately committed, but the comparator can generate expected from prior generated contracts and observed from expected. It invents a 2xx result field when missing, uses owner-pending/generic targets, and does not execute handler/API response fixtures. |
| F09 | **OPEN — REQUIRED** | Units are validated against F02 assertion labels and report status; because F02 structural/FK evidence is not independent, convergence authority remains unproved. |
| F10 | **OPEN — BLOCKER** | Scenario source/expected files exist, but bootstrap copies source from the broad one-row-per-entity fixture and expected from the prior observed report. The comparison reads an existing report rather than inserting the new source files and querying fresh target state. |
| F11 | **OPEN — ARCHITECTURE DECISION REQUIRED** | ADRs correctly remain proposed; their matrix describes unresolved F02/F04–F10/F12 reports as independently executable evidence. |
| F12 | **OPEN — BLOCKER** | The mutation chain is broader, but it does not run `review04_design_pipeline.py`, target-schema/scenario insertion or F04–F07 execution. Cardinality/temporal/geometry/lifecycle mutations still alter generated integrity reports; the suite proves report/checker tamper detection rather than full source-to-output defect detection. |
| F13 | **RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN** | The runtime race fix remains isolated in PR #8 and absent from PR #7. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence/condition |
|---|---|---|
| AC-01 — Complete current-state inventory | CONDITION | Physical inventory is strong; semantic/API owners and independently reviewed projections remain incomplete. |
| AC-02 — One canonical registry authority | CONDITION | `location_record` remains the intended anchor; transformation and relationship execution remains incomplete. |
| AC-03 — Administrative geography explicit | CONDITION | Structural model is coherent; complete authority and independently executed temporal evidence remain conditional. |
| AC-04 — Operational areas separate | CONDITION | Separation exists; geometry/temporal/convergence authority remains open. |
| AC-05 — Addressable-object coverage | FAIL | Complete executed record-type/cardinality/lifecycle matrix is absent. |
| AC-06 — Identifier separation | FAIL | Separation is documented; final source-to-canonical FK creation in proposed target entities is not proved. |
| AC-07 — Lifecycle separation | FAIL | Edges exist and positive edge lookups pass; complete graph/context enforcement is not proved. |
| AC-08 — Temporal reconstruction | FAIL | Core constraints exist; independent named-date registry/effective/public reconstruction is absent. |
| AC-09 — Geometry provenance and quality | FAIL | Technical promotion controls are strong; typed institutional trust and full negative matrix remain incomplete. |
| AC-10 — Multilingual and naming integrity | CONDITION | Name model/current-name constraint exists; executed multilingual/merge/retirement history remains incomplete. |
| AC-11 — Source and authority lineage | FAIL | Generic staging rows do not establish lineage into proposed target entities and real target FKs. |
| AC-12 — Data classification | FAIL | Reviewed files exist; API owners/targets remain pending or generic and expected sources are self-bootstrappable. |
| AC-13 — Controlled vocabularies | CONDITION | Vocabularies and edge metadata exist; graph/context enforcement remains open. |
| AC-14 — Integrity constraints | FAIL | Many database constraints execute; complete cardinality, temporal, geometry-authority and lifecycle-context cases do not. |
| AC-15 — API projection compatibility | FAIL | No executed current-handler response comparison against an independently maintained exact target-field contract. |
| AC-16 — Current-to-target no-loss mapping | FAIL | Value comparison improved; structural target/FK/archive/exception/relationship output remains expected-driven and generic. |
| AC-17 — Expand–migrate–contract plan | FAIL | Units inherit unresolved F02 execution evidence. |
| AC-18 — Representative records | FAIL | Scenario files are separate but originate from generated observed artefacts and are not freshly executed by the comparison. |
| AC-19 — Scale and index rationale | CONDITION | Assumptions remain owner-pending and not production evidence. |
| AC-20 — Draft physical schema coherent | FAIL | Schema executes; complete semantic proof remains insufficient. |
| AC-21 — ADR decision pack | FAIL | ADRs correctly remain proposed; defining guarantees remain open. |
| AC-22 — No runtime behavior change | PASS | PR #7 remains design/evidence only; PR #8 remains separate. |

## 4. Open findings

### NLI-WO-002-F02 — Separate files still share one authoring source and expected fixture drives observed structure

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-06, AC-11, AC-12, AC-16, AC-17

**Observation:** The Review 09 script states that source, expected and implementation are independent, but `author_artifacts_if_missing()` creates all three from `transformation-registry-reviewed.json` and `current-field-semantics-reviewed.json`. During execution, expected target rows provide the target output ID, target identity ID, target field, crosswalk/FK, archive ID, exception ID and relationship ID used to insert the observed result. The transform implementation independently computes only the value and flags. The target tables are generic Review 09 staging tables whose `target_field` is text; they are not the proposed target entities or field-typed staging tables. A real final FK is represented by a reference to a generic target-identity row, not the named proposed target entity. The `no-loss-count` check is set true per row, and failure probes mark any raised exception as caught even when it is not the expected semantic failure.

**Risk/consequence:** Structural errors in target entity/field selection, identity generation, archive/exception creation and relationship construction cannot be observed independently because expected data supplies those structures. An unrelated exception can satisfy a failure probe.

**Required resolution:** Remove all authoring/bootstrap behavior from validation. Maintain source fixtures, expected target fixtures and transform implementations through separate reviewed-source files/processes with distinct review decisions. The transform implementation must choose target entity/field, construct IDs/crosswalks/archive/exception/relationships and write to the actual proposed target tables or exact typed staging mirrors without reading expected fixtures. Validation alone reads expected. Enforce target-entity FKs. Verify group-level counts and relationships from queries. Require failure probes to match the expected exception/error and fail on unrelated exceptions.

**Disposition:** OPEN

### NLI-WO-002-F04 — The record-role “executed” suite declares results without executing transactions

**Class:** REQUIRED / ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-05, AC-10, AC-14, AC-20

**Observation:** `review09_f04_f07_executed_tests.py` loops through record types and directly emits `status: passed`. It similarly marks missing-role, invalid-role, invalid-entity, maxima, retirement, merge and multilingual-history cases passed with generic evidence text. It neither connects to PostgreSQL nor invokes a policy validator.

**Required resolution:** Replace the report writer with a real disposable database suite. Execute positive and negative transactions for every record type/role, including missing required roles, every invalid role/entity pairing, every maximum, retired/deleted/merged subject handling, merge/successor behavior and Spanish/English current/historical official names. Generate report rows solely from observed outcomes and exact state queries.

**Disposition:** OPEN

### NLI-WO-002-F05 — Temporal strategy and history cases remain declared evidence

**Class:** BLOCKER  
**Affected criteria:** AC-03, AC-07, AC-08, AC-14, AC-20

**Observation:** The Review 09 suite assigns each listed entity a generic strategy and directly marks named-date, cycle, reciprocal, cross-owner, overlap, backdated and dependent-interval cases passed. It does not execute those cases or compare independent expected histories.

**Required resolution:** Maintain a reviewed temporal strategy for every authoritative mutable entity. Execute named-date registry/as-recorded, effective/as-of and public-release queries plus two-node/multi-node cycle, reciprocal mismatch, cross-owner, overlap, backdated correction and dependent-interval cases for every relevant relationship. Compare exact observed histories to independently authored expected histories.

**Disposition:** OPEN

### NLI-WO-002-F06 — Typed geometry authority exists only as report vocabulary

**Class:** REQUIRED  
**Affected criteria:** AC-04, AC-09, AC-11, AC-14, AC-20

**Observation:** The Review 09 suite lists `actor_identity`, `service_identity`, `institution_membership`, `permission`, scopes and decision authority and marks them passed. It does not create those typed entities/relationships in the model or execute a matrix against them. Existing trigger checks still depend materially on decision text/JSON.

**Required resolution:** Add explicit typed target entities/relationships for actor/service identity, institution membership, permission, territorial/data scope and authority assertion; connect decisions, quality assessment, observation and evidence to that trust model. Execute positive and complete negative promotion/supersession cases from the disposable schema. Preserve institutional RFIs for unresolved accountable authorities.

**Disposition:** OPEN

### NLI-WO-002-F07 — Lifecycle graph/context results remain hard-coded

**Class:** REQUIRED  
**Affected criteria:** AC-07, AC-13, AC-14

**Observation:** `review09_f04_f07_executed_tests.py` computes simple sets but assigns reachability, terminality, re-entry, orphan/conflict and context prerequisites as passed/reviewed. The target validator still proves edge existence; it does not accept and enforce actor, permission, scope, evidence, audit and public-effect context.

**Required resolution:** Implement a real graph validator with reviewed initial/terminal/re-entry declarations and computed reachability/orphan/conflict results. Implement an executable contextual transition policy and execute positive and negative context cases for every lifecycle family. Generate evidence from those results only.

**Disposition:** OPEN

### NLI-WO-002-F08 — API expected and observed contracts are bootstrapped from one another, not executed

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-10–AC-12, AC-15

**Observation:** `review09_api_contract_comparison.py` can bootstrap expected contracts from the previously generated projection contract and observed fixtures from expected contracts. It mutates expected contracts on every run and, when a 2xx shape is absent, adds `response.body.<operation>_result`. The observed fixture contains the same contract metadata and fields rather than captured API/handler output. The comparator compares field keys only. Numerous classification owners remain pending and target projections remain phrases such as endpoint read-model or canonical/read-model/release projection rather than exact target fields.

**Required resolution:** Remove expected/observed bootstrap and expected repair from validation. Maintain expected contracts as controlled human-reviewed source with accountable owners and exact target fields/non-migration decisions. Execute FastAPI endpoints or deterministic handler/service fixtures against controlled data to obtain observed request/success/error shapes. Compare complete types, requiredness and fields; unresolved shapes must fail. Never invent response fields.

**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence units validate labels from unresolved suites

**Class:** REQUIRED  
**Affected criteria:** AC-17, AC-19

**Observation:** The reconciliation script checks execution-mode strings, assertion IDs, non-null final-FK evidence and summary status. It does not independently inspect transform commands, actual proposed target rows/FKs, exception/archive outputs or second-run state. F04–F08/F10/F12 suite summaries can be passed by declared reports.

**Required resolution:** Revalidate units only from accepted underlying execution. Each unit must reference exact transform command, source and independent expected fixture, actual proposed target rows/FKs/archive/exception queries, true idempotency, compatibility, validation tolerance and recovery/cutover results.

**Disposition:** OPEN

### NLI-WO-002-F10 — Scenario “independence” is bootstrapped from generated fixtures and prior observed reports

**Class:** BLOCKER  
**Affected criteria:** AC-05, AC-08–AC-11, AC-14, AC-18, AC-20

**Observation:** `review09_scenario_comparison.py` creates source files from `machine-readable-fixtures.json` and expected files from `review08-scenario-query-report.json` when absent. The committed source files retain the broad one-row-per-entity shell; for example, the multi-unit scenario includes correction, dispute, field, landmark, parcel, partner and other unrelated records. The comparison does not insert `review09/scenarios/*/source.json`; it reads the pre-existing Review 08 observed report and compares it to expected. Expected absences are empty placeholders rather than executed absence queries.

**Required resolution:** Remove bootstrap from validation. Hand-author minimal independent source and expected files. Make the comparison create a fresh target schema, insert the Review 09 source file, execute named-date canonical/effective/recorded/public/operator queries, and compare exact values and explicit absences with the independent expected file. Add source, expected and query-logic mutations through the full path.

**Disposition:** OPEN

### NLI-WO-002-F11 — ADR evidence remains dependent on unaccepted labels

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21

**Observation:** ADRs correctly remain proposed. Their evidence matrix describes the unresolved F02/F04–F10/F12 suite reports as independently executable passing evidence.

**Required resolution:** Keep ADRs proposed. Bind decision statements only after underlying independent executions pass, with specific assertions and institutional RFIs/conditions.

**Disposition:** OPEN

### NLI-WO-002-F12 — Mutation suite does not run the claimed full pipeline and still mutates reports

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21

**Observation:** The Review 09 chain runs the F02 transform helper, API comparator, scenario comparator and consistency checker. It does not run `review04_design_pipeline.py`, target schema/scenario insertion, Review 09 F04–F07 suite or convergence/ADR reconciliation. Cardinality, temporal, geometry, lifecycle and negative-harness cases mutate generated reports/catalogs rather than authoritative target model, lifecycle policy, geometry authority or fixture/transform source. The temporary workspace omits runtime source needed to execute actual APIs.

**Required resolution:** Create a truly isolated temp repository and disposable database containing all required sources. Mutate authoritative reviewed source/model/policy/transform/query logic. Run the same complete command chain as the `sda-design-model` job, including generator, target database/scenarios, API observed-fixture execution, F04–F07 execution, F09/F11 reconciliation and consistency checker. Require the named gate/reason and fail on unrelated errors.

**Disposition:** OPEN

### NLI-WO-002-F13 — Runtime maintenance remains correctly isolated

**Class:** RESOLVED FOR THIS WORK ORDER / EXTERNAL CONDITION  
**Affected criterion:** AC-22

**Observation:** PR #7 contains no migration-runner runtime fix. PR #8 remains separate, draft and unmerged.

**Condition:** PR #8 requires current-main synchronization, exact-head CI and separate NLI-WO-001 maintenance review before merge.

**Disposition:** RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN

## 5. Positive controls to preserve

- Exact-head GitHub submission and green CI.
- PR #7 draft/design-only boundary and separate PR #8.
- Live current pg_catalog and actual OpenAPI generation.
- Unknown-current-field fail-closed registries.
- Canonical `location_record` anchor and identifier/public-alias separation.
- Administrative code history separate from identity.
- Canonical role matrix, native-subject checks, required-role trigger and object-link containment.
- Corrected negative SQL/policy helper in the target-schema pipeline.
- Version/alias reciprocal and cycle triggers; effective/recorded exclusions.
- Geometry observation/version separation and stronger technical promotion trigger.
- Populated lifecycle transition table and positive edge execution.
- Distinct multi-unit canonical records, aliases and release items.
- Immutable release payload/hash/manifest and exact version/alias linkage.
- True zero-additional-row idempotency check in the Review 09 F02 staging suite.
- ADRs remain proposed rather than overclaimed accepted.
- NLI-WO-002B remains unauthorized.

## 6. Evidence quality

The exact-head workflows prove that the submitted scripts and checker are internally consistent at the reviewed commit. They do not prove independence merely because artefacts are stored in different files. A validation system is independent only when expected authority cannot be regenerated or repaired from observed output by the validation path, and observed output is produced by the real transform/API/query/policy behavior rather than by expected fixtures or declared report rows.

Counts such as `1,370 transform assertions`, `1,626 API assertions`, `70 scenario assertions`, `6,284 generated checks` and `11/11 mutations caught` remain non-dispositive. The source code shows which checks are actual comparisons and which are bootstrapped, generic or directly assigned pass.

The S16 self-audit remains a pre-closeout checklist with `Final implementation head: pending final closeout commit`; update it with final exact-head evidence in the next submission.

## 7. Decision

`REWORK REQUIRED`

Review 10 confirms good scope governance and stronger mechanics, but the core design-authority question remains unresolved: can the evidence detect a wrong design when the generator, expected fixture and report are not allowed to agree by construction? At present, several key suites still can.

Keep PR #7 draft and unmerged. NLI-WO-002B remains unauthorized.

## 8. Required follow-up sequence

1. Remove all expected/source bootstrap and repair behavior from validation scripts; make reviewed expected files immutable inputs during CI.
2. Rebuild F02 so transform implementation independently constructs complete typed target output and writes actual proposed target entities or exact mirrors without reading expected structure.
3. Execute current API handlers/routes against controlled fixtures and compare observed results to independent expected contracts with exact target mappings and approved owners.
4. Execute Review 09 scenario source files in a fresh target schema and compare named-date exact results/absences to independent expected files.
5. Replace the F04–F07 report writer with real database/policy/graph executions and add the missing typed authority model.
6. Run full-pipeline mutations from authoritative source changes using the exact CI command chain.
7. Revalidate convergence and ADR evidence only after the underlying findings pass.
8. Update Review 10 resolution rows, S16, PR body and controlled evidence at a new exact head; obtain green exact-head CI and request SDA Review 11.
9. Handle PR #8 separately under NLI-WO-001 maintenance controls.

## 9. Review 10 resolution log

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
