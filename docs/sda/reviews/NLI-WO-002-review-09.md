# SDA Review — NLI-WO-002 — Review 09

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed implementation/design commit:** `aa77f4b512b7389152239d3eaa27d4ab703c6ad2`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-14  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact remote PR head, PR body and Review 09 request, Review 08 task context/resolution matrix/S16 self-audit, current PostGIS and OpenAPI inputs, Review 08 transformation execution code/report, API projection generator/contracts/assertions, persisted scenario query code/report, F04–F07 integrity report generator, semantic mutation runner/report, convergence/ADR reconciliation, Review 08 resolution log, controlled PR evidence, changed-path boundary, and exact-head GitHub Actions.

Independent PR-state verification:

- PR #7 is **open**, **draft**, **mergeable**, and **unmerged**.
- Reviewed implementation/design head: `aa77f4b512b7389152239d3eaa27d4ab703c6ad2`.
- PR #7 remains design/evidence only. No application runtime, API implementation, frontend application, migration runner, executable migration, Docker runtime configuration, production/pilot data, or environment-secret path is changed.
- NLI-WO-002B remains unauthorized.
- Maintenance PR #8 remains separate.

Independent exact-head workflow verification:

- Agent skills CI run `29369948566`: **success**
  - `validate-agent-skill-pack` job `87210635529`: success
- API CI run `29369948621`: **success**
  - `sda-design-model` job `87210635625`: success
  - `api-tests` job `87210635582`: success
  - `migration-lifecycle` job `87210635622`: success
  - `api-image-runtime` job `87210635731`: success
- Frontend CI run `29369948578`: **success**
  - `frontend` job `87210635505`: success

Review 08 remediation adds useful execution scaffolding: transformation rows are persisted to disposable PostgreSQL tables, scenario rows are queried back from the disposable target schema, the mutation suite runs the real consistency checker in copied workspaces, dynamic response envelopes no longer use the old `reviewed_payload` name, and the scope/evidence submission is exact-head and disciplined.

The model is still not safe to accept because the new assurance layers remain circular or declarative in the most consequential places. The F02 runner calculates the expected value, inserts that value as the actual target value, aliases actual as expected during query-back, and constructs source and target hashes from the same inputs. Its final canonical FK is a synthetic hash string rather than a proved FK into the proposed target schema. Its idempotency probe deliberately duplicates rows and calls the result idempotent when the total is exactly twice the distinct count. F08 regenerates its supposed expected contracts from observed OpenAPI/AST and invents `id`, `status`, path and request fields when a real success shape cannot be found. F10 queries persisted rows but compares them only with the same fixture IDs/counts and boolean presence, not independently reviewed expected outputs. F12 mutates generated evidence files and runs only the consistency checker; it does not mutate authoritative sources and run the full generator/pipeline/database/checker path. The F04–F07 rollup assigns many `passed` values from prose, trigger presence or unrelated negatives rather than executing the required cases.

This review does not authorize NLI-WO-002B, executable convergence, production deployment, official publication, public-code issuance, certificates/signage, partner release, or real-data migration.

## 2. Review 08 finding disposition

| Finding | Review 09 disposition | Assessment |
|---|---|---|
| F02 | **OPEN — BLOCKER** | PostgreSQL tables are used, but expected and actual values/hashes are produced by the same generic function; no reviewed group-specific transform is executed into the proposed target tables, final FKs are synthetic, and the idempotency proof accepts duplicated outputs. |
| F04 | **PARTIALLY RESOLVED — OPEN** | Canonical role/cardinality architecture and multi-unit representation are stronger. The Review 08 integrity rollup hard-codes positive status and substitutes invalid-subject evidence for missing-role/invalid-entity cases; retirement, merge and multilingual history remain declarative. |
| F05 | **PARTIALLY RESOLVED — OPEN** | Core version/alias/geometry constraints remain valuable. The temporal register and as-of evidence are labels over existing report sections; full as-of registry/effective/public queries and complete negative chain tests are not executed for every authoritative entity. |
| F06 | **PARTIALLY RESOLVED — OPEN** | Geometry trigger checks are materially improved. The claimed typed authority relationship is still text/JSON metadata, not an enforceable identity-membership-permission-scope relation, and the required actor/institution/assessment/observation/successor negative matrix is incomplete. |
| F07 | **PARTIALLY RESOLVED — OPEN** | Ninety-six allowed edges execute. Reachability, initial states, terminality, re-entry, orphan/conflicting edges and permission/scope/evidence denial are assigned `passed` in the rollup rather than computed and executed per lifecycle family. |
| F08 | **OPEN — BLOCKER** | The old generic envelope name is removed, but contracts are generated from observed OpenAPI/AST. When no real response shape exists, the generator invents operation-specific fields. Classifications are path/token heuristics, owners remain pending, target projections are generic prose, and assertions are marked passed without executing handler response contracts. |
| F09 | **OPEN — REQUIRED** | Units reference F02 assertion IDs labelled execution-backed, but the underlying F02 oracle is circular and final target rows/FKs are not proved. |
| F10 | **OPEN — BLOCKER** | Scenario rows are queried from PostGIS, but expected totals/IDs originate from the same input fixtures and assertions test boolean presence. Exact independently reviewed public/operator values and named-date historical reconstruction are not compared. Broad one-row-per-entity scenario generation remains. |
| F11 | **OPEN — ARCHITECTURE DECISION REQUIRED** | ADRs correctly remain proposed, but their evidence matrix inherits unresolved F02/F04–F10/F12 guarantees and describes them as executable passing evidence. |
| F12 | **OPEN — BLOCKER** | Mutation cases run the real consistency checker, which is an improvement. They mutate generated evidence outputs rather than authoritative sources and do not run the design generator/pipeline/database path, so they prove tamper detection in reports rather than detection of erroneous generation or transformation behavior. |
| F13 | **RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN** | The runtime race fix remains isolated in PR #8 and absent from PR #7. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence/condition |
|---|---|---|
| AC-01 — Complete current-state inventory | CONDITION | Physical inventory is strong; semantic ownership/classification and API projections are not fully independent or approved. |
| AC-02 — One canonical registry authority | CONDITION | `location_record` remains the intended anchor; transformation and relationship proof remains incomplete. |
| AC-03 — Administrative geography explicit | CONDITION | Structural model is coherent; institutional and complete temporal authority remain conditional. |
| AC-04 — Operational areas separate | CONDITION | Separation exists; geometry/temporal/convergence authority remains open. |
| AC-05 — Addressable-object coverage | FAIL | Complete independently executed record-type/cardinality/lifecycle evidence is absent. |
| AC-06 — Identifier separation | FAIL | Separation is documented; final source-to-canonical FK execution is not proved. |
| AC-07 — Lifecycle separation | FAIL | Allowed edges execute; complete graph and denial semantics are not proved. |
| AC-08 — Temporal reconstruction | FAIL | Core constraints exist; complete named-date registry/effective/public reconstruction is absent. |
| AC-09 — Geometry provenance and quality | FAIL | Technical trigger is strong; typed institutional authorization and full negative matrix remain incomplete. |
| AC-10 — Multilingual and naming integrity | CONDITION | Name model/current-name control exists; multilingual history/merge/retirement proof is incomplete. |
| AC-11 — Source and authority lineage | FAIL | Generic transform tables do not establish target-schema lineage or independent no-loss reconciliation. |
| AC-12 — Data classification | FAIL | Reviewed files exist, but API/current classification rules remain partially heuristic and owners pending. |
| AC-13 — Controlled vocabularies | CONDITION | Vocabularies/edges exist; full graph enforcement remains open. |
| AC-14 — Integrity constraints | FAIL | Many constraints execute; full cardinality, temporal, lifecycle and authority behavior is not independently tested. |
| AC-15 — API projection compatibility | FAIL | The contract generator does not establish actual independently reviewed response fields and exact target mappings. |
| AC-16 — Current-to-target no-loss mapping | FAIL | Row/table execution exists, but the expected/actual oracle is circular and no real target transform is run. |
| AC-17 — Expand–migrate–contract plan | FAIL | Units depend on unresolved F02 evidence. |
| AC-18 — Representative records | FAIL | Persisted rows are queried, but exact independent scenario outputs/histories are not compared. |
| AC-19 — Scale and index rationale | CONDITION | Assumptions remain owner-pending and not production evidence. |
| AC-20 — Draft physical schema coherent | FAIL | Schema executes; unresolved semantic proof prevents acceptance. |
| AC-21 — ADR decision pack | FAIL | ADRs correctly remain proposed; defining guarantees remain open. |
| AC-22 — No runtime behavior change | PASS | PR #7 remains design/evidence only; PR #8 remains separate. |

## 4. Open findings

### NLI-WO-002-F02 — Transformation execution uses a circular oracle and synthetic target outputs

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-06, AC-11, AC-12, AC-16, AC-17

**Observation:** The Review 08 runner creates disposable source, target, archive, exception, crosswalk and relationship tables. However:

- `review08_expected_target_value()` calculates the output used for target insertion;
- the target table is inserted directly with that same calculated output, not through a reviewed transform implementation;
- query-back aliases `actual_target_value AS expected_target_value`;
- source and target hashes are generated from the same `[source_row_key, current, source_value, expected_value]` tuple;
- final canonical FKs are synthetic `canonical-<hash>` strings and are not FKs to rows in the proposed target schema;
- the one-to-one count is guaranteed by generating one source and one target row per current field;
- the idempotency probe inserts the same target IDs a second time into a table without a uniqueness constraint and calls it idempotent when `total == 2 * distinct_total`;
- failure probes mutate the joined result rows after generation, not the transformation implementation or independently reviewed expected result.

**Risk/consequence:** An incorrect group transform can remain green because the same function defines both actual and expected output. Duplicate outputs are positively labelled idempotent. A synthetic final FK can pass even when no canonical target row exists.

**Required resolution:** Maintain an independently reviewed source fixture and expected target fixture per transform group. Implement a separate design transform command/function/SQL per group. Load actual source rows, run the transform into the proposed target-schema tables or schema-compatible staging tables, and compare actual output with the independently authored expected rows. Enforce real FKs/crosswalk joins to inserted target identities. Run the transform twice and assert the second run creates no duplicate target/archive/exception/crosswalk/relationship rows. Mutate the transform implementation and expected fixtures separately and run the full transform suite to prove wrong values, translations, archives, exceptions, FKs, hashes and relationships fail.

**Disposition:** OPEN

### NLI-WO-002-F04 — Record-role integrity report contains declared passes instead of executed matrix cases

**Class:** REQUIRED / ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-02–AC-05, AC-10, AC-14, AC-20

**Observation:** `review08_f04_f07_integrity_report.py` constructs every canonical record-type positive row with `status: passed` without executing a record-type-specific dataset. It maps `invalid-subject-reference` to both missing-role and invalid-entity proof, while no missing-required-role case is executed. Invalid-role, retirement, merge and multilingual-name-history entries are passed from trigger/prose presence.

**Required resolution:** Author and execute a matrix of positive and negative transactions for every record type and role. Include missing required role, every invalid role/entity pairing, each maximum, retired/deleted/merged subjects, merge/successor behavior, and Spanish/English official-name current/history rules. Query final persisted state and generate the report only from those outcomes.

**Disposition:** OPEN

### NLI-WO-002-F05 — Temporal register and reconstruction are descriptive rather than complete as-of execution

**Class:** BLOCKER  
**Affected criteria:** AC-03, AC-07, AC-08, AC-14, AC-20

**Observation:** The integrity rollup assigns one generic `recorded/effective reconstruction` strategy to seven entities and labels registry/effective/public queries passed because report sections exist. It does not classify every mutable authoritative entity or execute named-date queries for each strategy. Several cycle, reciprocal, cross-owner and backdated cases are inferred from trigger text rather than executed.

**Required resolution:** Create a reviewed temporal-strategy registry for every authoritative mutable entity. Implement and execute named-date registry/as-recorded, effective/as-of and public-release reconstruction queries. Execute two-node and multi-node cycle, reciprocal mismatch, cross-owner, overlap, backdated correction and dependent-interval cases for every relevant chain/relationship. Compare results with independent expected histories.

**Disposition:** OPEN

### NLI-WO-002-F06 — Geometry authority remains asserted through JSON/text rather than an enforceable trust model

**Class:** REQUIRED  
**Affected criteria:** AC-04, AC-09, AC-11, AC-14, AC-20

**Observation:** The trigger checks useful metadata, but permission, institution, scope, actor and quality authority are still JSON/text claims on a decision record. The integrity rollup calls this a typed connection without modelling a membership/permission/scope relation. The executed negative set covers decision type, permission text, territorial scope, evidence and geometry type, but not wrong actor membership, wrong institution independent of scope, unrelated quality assessment/actor, unrelated observation, cross-subject/role successor or multi-node cycle.

**Required resolution:** Define typed design entities/relationships for actor or service identity, institution membership, permission, territorial/data scope, decision authority, quality assessment, observation and evidence. Reference that authority assertion from promotion. Execute the complete positive/negative matrix and preserve institutional RFIs where the accountable authority is unresolved.

**Disposition:** OPEN

### NLI-WO-002-F07 — Lifecycle graph assurance is hard-coded and denial prerequisites are not executed

**Class:** REQUIRED  
**Affected criteria:** AC-07, AC-13, AC-14

**Observation:** All allowed edges are loaded and queried successfully. The integrity script sets `reachability_status` and `denial_status` to `passed` for every graph, derives initial states by set subtraction, and reports scope/evidence/orphan/re-entry passes from metadata presence. `validate_lifecycle_transition()` checks only whether a `(vocab, from, to)` row exists; it does not enforce permission, scope, evidence, audit or public-effect prerequisites.

**Required resolution:** Build a real graph validator for every bound vocabulary, with reviewed initial and terminal states, reachability, intended re-entry, orphan and conflict detection. Add an executable transition policy function that accepts actor/permission/scope/evidence/audit context and rejects missing or mismatched prerequisites. Execute positive and negative cases for every lifecycle family.

**Disposition:** OPEN

### NLI-WO-002-F08 — API projection contracts are regenerated from observed implementation and invent fallback response fields

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-10–AC-12, AC-15

**Observation:** `review08_api_projection_contracts.py` reads the current OpenAPI operation inventory and implementation AST, then rewrites the reviewed projection contract. This is not an independent expected source. When a dynamic success response cannot be resolved from OpenAPI or AST, the script invents `response.body.id`, `response.body.status`, path parameters and request fields. Classification is assigned from sensitive-name tokens and whether the path starts `/api/v1/public`; owners remain pending. Target projections are operation-level prose such as `exact canonical/read-model/release projection field`, not exact target fields. Every generated record is written to the assertion report with `status: passed`; no handler or response fixture is executed.

**Risk/consequence:** The design can publish a complete-looking contract that contains fields the API never returns, omits fields it does return, misclassifies sensitive data and leaves the actual target adapter unresolved.

**Required resolution:** Maintain expected route/field contracts as reviewed source not rewritten by the observed extractor. Execute current handlers or controlled API response fixtures to obtain observed success/error shapes. Compare observed shapes with the independent expected contracts. Every field must have a concrete target entity/read-model/release field or an explicit non-migrated/compatibility decision, approved classification owner, release prerequisite, adapter and test. Fail on unresolved dynamic fields; do not invent fallback fields.

**Disposition:** OPEN

### NLI-WO-002-F09 — Convergence validation inherits circular transformation evidence

**Class:** REQUIRED  
**Affected criteria:** AC-17, AC-19

**Observation:** The reconciliation script treats a unit as execution-backed when its referenced F02 assertions contain the expected execution-mode string. It does not verify real transform commands, target rows, FK constraints, exception results or idempotent reruns. Because F02 is circular, all 90 units can pass without executable convergence authority.

**Required resolution:** Revalidate each unit only after F02 closes. Reference exact source fixture, transform command, independently expected target fixture, observed target rows/FKs/archive/exception results, idempotency result, validation tolerance, compatibility and recovery/cutover evidence.

**Disposition:** OPEN

### NLI-WO-002-F10 — Persisted scenario queries remain self-referential presence checks

**Class:** BLOCKER  
**Affected criteria:** AC-05, AC-08–AC-11, AC-14, AC-18, AC-20

**Observation:** The pipeline now queries inserted rows, which is useful. It selects rows by the same fixture IDs used for insertion, compares queried count with the same fixture count, and marks each of nine scenario assertions true when collections are non-empty. It renders public/operator/history sections but does not compare any exact value with an independently authored expected result or query at named dates. The generator still builds one row for every target entity in every scenario before applying scenario-specific changes.

**Required resolution:** Split the seven scenarios into independent reviewed source datasets containing only relevant entities and separate expected-result files. After insertion, execute named queries for canonical state, relationships, geometry/provenance, evidence/authority, lifecycle timeline, and public/operator projections at relevant dates. Compare exact values and absences with the independent expected results. Add mutation tests that alter source data, projection logic and expected output separately.

**Disposition:** OPEN

### NLI-WO-002-F11 — ADR evidence remains ahead of executable guarantees

**Class:** ARCHITECTURE DECISION REQUIRED  
**Affected criteria:** AC-06, AC-08, AC-09, AC-21

**Observation:** ADRs correctly remain proposed. The reconciliation script describes F02, temporal, cardinality, geometry and scenario evidence as executable passing evidence even though the underlying findings remain open.

**Required resolution:** Keep ADRs proposed. After F02/F04–F10/F12 close, bind each decision statement to a specific independent executable assertion and preserve unresolved institutional RFIs/conditions. Do not use assertion counts or execution-mode labels as substitutes.

**Disposition:** OPEN

### NLI-WO-002-F12 — Mutation suite tests generated-report tampering, not erroneous source generation

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-03–AC-21

**Observation:** The suite now copies files to a temporary workspace and runs the actual `design_consistency_check.py`, which is an improvement. It does not run `review04_design_pipeline.py`, database generation or the Review 08 helper scripts. Most mutations edit generated reports/catalogs/contracts and prove that the checker rejects tampered evidence. They do not mutate authoritative transformation logic, reviewed expected contracts, target SQL/model or scenario builders and then regenerate the pack. The summary labels the mode `actual-pipeline-checker`, although only the checker is invoked.

**Required resolution:** Build isolated temporary repository/database runs that mutate authoritative source or transformation/generator logic, then execute the complete relevant generator/pipeline/helper/checker chain. Require failure at the named gate. Cover wrong group transform, independent expected-output mismatch, archive/FK omission, classification error, cardinality/temporal/geometry/lifecycle source defect, API observed-versus-expected drift, scenario query/projection defect and negative-harness regression. Report which full commands ran and their exit/output evidence.

**Disposition:** OPEN

### NLI-WO-002-F13 — Runtime maintenance remains correctly isolated

**Class:** RESOLVED FOR THIS WORK ORDER / EXTERNAL CONDITION  
**Affected criterion:** AC-22

**Observation:** PR #7 contains no migration-runner runtime fix. PR #8 remains separate.

**Condition:** PR #8 requires its own current-main synchronization, exact-head CI and NLI-WO-001 maintenance review before merge.

**Disposition:** RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN

## 5. Positive controls to preserve

- Exact-head GitHub submission and green CI.
- PR #7 draft/design-only boundary and separate PR #8.
- Live current pg_catalog and actual OpenAPI generation.
- Unknown-current-field fail-closed registries.
- Canonical `location_record` anchor and identifier/public-alias separation.
- Administrative code history separate from identity.
- Canonical role matrix, native-subject checks, required-role trigger and object-link containment.
- Corrected negative SQL/policy helper and real database error matching.
- Version/alias reciprocal and cycle triggers; effective/recorded exclusions.
- Geometry observation/version separation and stronger technical promotion trigger.
- Populated lifecycle transition table and positive execution of 96 edges.
- Distinct multi-unit canonical records, aliases and release items.
- Immutable release payload/hash/manifest and exact version/alias linkage.
- ADRs remain proposed rather than overclaimed accepted.
- S16 scope/readiness boundary and NLI-WO-002B lock.

## 6. Evidence quality

The exact-head workflows prove that the submitted generators, helpers and checker run successfully. They do not prove independently what those generators define as both expected and actual. Counts such as `237/237 source/target rows`, `1,370 transform assertions`, `1,709 API assertions`, `63 scenario assertions`, `6,436 generated checks` and `11/11 mutations caught` are not acceptance evidence when the source shows circular or declared pass conditions.

The Review 08 S16 record and resolution log truthfully preserve the authorization boundary, but they overstate evidence as actual/typed/independent where the implementation remains generic, self-derived or declarative. The next closeout must distinguish database persistence from independent semantic verification.

## 7. Decision

`REWORK REQUIRED`

Review 09 confirms meaningful progress in execution mechanics and scope discipline. The remaining work is no longer about adding more assertion counts. It is about separating the source of expected truth from the code that produces observed output and exercising the actual domain transformations, API responses, scenario histories and validation pipeline.

Keep PR #7 draft and unmerged. NLI-WO-002B remains unauthorized.

## 8. Required follow-up sequence

1. Redesign F02 around independent source fixtures, independent expected target fixtures and group-specific transforms into schema-compatible target rows; correct the idempotency test.
2. Make F08 expected contracts human-reviewed source, execute handler/API response fixtures and remove invented fallback fields/generic target prose.
3. Make F10 scenario datasets and expected outputs independent; query and compare exact named-date public/operator/history results.
4. Make F12 mutate authoritative sources/logic and execute the full pipeline/database/helpers/checker, not generated reports only.
5. Replace F04–F07 declared rollup passes with executed record-role, temporal, typed-authority and lifecycle-context tests.
6. Revalidate F09 and F11 only after the underlying findings pass.
7. Update Review 09 resolution rows, S16, controlled evidence and PR body at the new exact head; obtain green exact-head CI and request SDA Review 10.
8. Handle PR #8 separately under NLI-WO-001 maintenance controls.

## 9. Review 09 resolution log

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
