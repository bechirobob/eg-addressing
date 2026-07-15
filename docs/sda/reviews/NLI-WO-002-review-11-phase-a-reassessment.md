# SDA Corrected Phase A Reassessment — NLI-WO-002 Review 11 Authoritative Assurance Harness

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed corrected Phase A commit:** `882a0f08758d8ec714c1d8b2c62628f986b8fd5d`  
**Prior Phase A assessment:** `docs/sda/reviews/NLI-WO-002-review-11-phase-a-assessment.md`  
**Reviewer:** System Design Authority  
**Assessment date:** 2026-07-15  
**Decision:** `PHASE A CORRECTION REQUIRED — A1 REMAINS ACCEPTED WITH CONDITIONS; A2/A3 STILL INCOMPLETE; PHASE B NOT AUTHORIZED`  
**NLI-WO-002:** `REWORK REQUIRED`  
**NLI-WO-002B:** `UNAUTHORIZED`

## 1. Reassessment boundary

Reviewed the exact corrected Phase A head, PR state, one-commit changed-path scope, exact-head workflows, Phase A correction plan and S16 self-audit, the complete current-source fixture, expected-target fixture, transform-spec registry, negative-probe fixture, `authoritative_harness.py`, coverage/target/idempotency/FK/archive/exception/cleanup reports, Review 11 F02/F14 agent-response cells, and the prior checkpoint authorization and assessment exit gate.

Independent verification:

- PR #7 is open, draft, mergeable, and unmerged.
- Corrected Phase A head: `882a0f08758d8ec714c1d8b2c62628f986b8fd5d`.
- The correction is one commit after reviewer-owned assessment head `2671ee9dfd6fa6312dadbb4033834bd3a2c5900d`.
- Changed paths are limited to Phase A plans, fixtures, harness code, generated evidence, S16, and the Review 11 resolution-log agent cells.
- No `services/api/**`, `apps/**`, executable migration, `infra/scripts/migrate.py`, Docker runtime configuration, production/pilot data, `.env*`, secret, or PR #8 runtime path changed.
- Agent-skills CI run `29403757859`: success.
- API CI run `29403757442`: success.
  - `sda-design-model` job `87314168146`: success.
  - `api-tests` job `87314168085`: success.
  - `migration-lifecycle` job `87314168018`: success.
  - `api-image-runtime` job `87314168016`: success.
- Frontend CI run `29403757666`, job `87314168606`: success.
- PR #8 remains separate.
- No SDA Review 12 request was made.

## 2. Decision summary

| Phase | Decision | Reassessment |
|---|---|---|
| A1 — Harness skeleton and topology | **ACCEPTED WITH CONDITIONS — PRESERVED** | `current_source`, `canonical_target`, `test_control`, controlled migrations, target application, schema isolation, explicit cleanup/recreate and non-authoritative CI remain valid. |
| A2 — Independent fixture authority | **REWORK REQUIRED** | Separate complete-source, expected-target and transform-spec files now exist and claim all 237 fields, but the expected target semantics are not consistently aligned with the reviewed registry and are used directly as observed output. |
| A3 — Authoritative F02 execution | **REWORK REQUIRED** | The harness does not execute the 90 transform specifications or derive target rows from current-source fixture values. It inserts `expected_rows` directly into `canonical_target`; the reported implementation and execution counts are metadata counts, not executed transforms. |
| Phase B | **NOT AUTHORIZED** | F02 and F14 remain open. F04–F12 remain outside current authorization. |

## 3. Accepted controls to preserve

- One disposable PostgreSQL/PostGIS topology with `current_source`, `canonical_target`, and `test_control`.
- Accepted migrations applied through `infra/scripts/migrate.py` using `search_path=current_source,public`.
- Draft target schema applied into `canonical_target`.
- `test_control` restricted to harness-control tables and public restricted to extension objects.
- Machine-readable fixture directories and required-file fail-closed behavior.
- Current catalog and reviewed registry both contain 237 fields.
- Source fixture structurally groups all 237 fields into 25 table-level records.
- Expected target fixture contains explicit target rows rather than only aggregate counts.
- Query-based unexpected-row and duplicate checks exist.
- Second direct-row insertion adds zero rows and changes no target-state hash.
- Strict expected-reason matching and unchanged-state check are retained for the current probe runner.
- Explicit cleanup after success/failure and recreation proof.
- Legacy guardrails remain green and labelled legacy.
- PR #7 design-only boundary, PR #8 separation, draft status, and NLI-WO-002B lock.

## 4. Blocking findings

### PA2-F02-01 — The harness inserts the expected fixture instead of executing transformations

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-02, AC-06, AC-11, AC-16, AC-17, AC-20

`run_transform()` loads the source fixture, transform specifications, and expected target fixture. The source and specifications are passed only to `coverage_matrix()`. The execution call is `apply_rows(cur, expected)`. `apply_rows()` converts `expected_rows` into table rows and inserts them directly into `canonical_target`.

No complete source fixture is loaded into the migrated `current_source` tables for transformation. No group implementation reads source values. No implementation function or SQL unit named by the 90 `implementation_unit` values exists or is dispatched. The observed target state is therefore the expected fixture itself.

**Risk/consequence:** Expected and observed truth are identical by construction. A wrong transform specification, source value, grouping rule, controlled translation, ID algorithm, archive rule, exception rule, or relationship algorithm can remain green because none of those rules produces the observed target rows.

**Required correction:** Implement a real transform dispatcher keyed by the reviewed transform-group ID and implementation unit. Load complete source fixture records into `current_source` using the actual current table schemas. Each group implementation must query its source record(s), construct target values independently, and insert into actual `canonical_target` tables. The comparator alone may read the expected target fixture. CI must fail if a named implementation is missing, cannot be invoked, produces undeclared target rows, or ignores declared source fields.

### PA2-F02-02 — “Transform implementations” and “executed dispositions” are metadata counts

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-01, AC-11, AC-16

The coverage report counts unique `implementation_unit` strings as transform implementations. It does not resolve those strings to callable functions or executable SQL. Repository search finds no implementation function corresponding to representative names such as `impl_wo002_r06_correction_case_address_corrections`.

`authoritative_executed_dispositions` is calculated from `proposed_location_record_assertion.value_json.current_field` entries in the expected target fixture. It therefore proves that the expected fixture contains one assertion label per current field, not that each field was consumed by an executed transform.

**Required correction:** Resolve every implementation-unit identifier to one executable implementation and invoke it. Generate field execution coverage from transform-run telemetry: source record/key read, fields consumed, implementation invoked, observed target rows/FKs/archive/exception/relationship outputs, and comparison result. An expected assertion row cannot itself constitute execution evidence.

### PA2-F02-03 — Transform specifications do not control target production

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-11, AC-16, AC-17

The 90 transform groups contain source keys, fields, target entities/fields, ID algorithms, crosswalk rules, archive/exception behavior and implementation-unit labels. None of these values is used by `apply_rows()` to construct observed target state.

The coverage gate checks set equality and unique labels, but not spec-to-observed row parity. For example, the specifications declare three geometry-observation groups for `address_points`, `address_records`, and `citizen_geotag_submissions`, while the expected-target count contains only one `proposed_geometry_observation`. The gate still reports 90 implementations and zero unexecuted groups.

**Required correction:** Make transform specifications authoritative for dispatch and expected output classes. For each run, compare declared source fields, target tables/fields, child rows, relationships, crosswalks, archives, exceptions, and ID algorithms with observed outputs. Fail on declared-versus-observed target mismatch.

### PA2-F02-04 — Expected target rows are also used as transform input

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-11, AC-16, AC-20

The expected fixture is now explicit and hashable, but it is not independent in execution because it is the sole source of rows inserted into `canonical_target`. The subsequent bidirectional row comparison and target-state hash merely prove that rows read from the fixture were inserted and read back.

The idempotency evidence likewise proves that inserting the same expected primary keys twice creates no additional rows. It does not prove that a source-to-target transform is idempotent, because no transform is executed.

**Required correction:** Separate the implementation path and comparison path completely. The transform path may read only current-source fixtures, transform specifications, and reviewed authority inputs. The expected fixture may be read only after observed target state exists.

### PA2-F02-05 — Expected target semantics are overgeneralized and conflict with reviewed dispositions

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-06, AC-11, AC-12, AC-16

The expected fixture creates 237 archive rows, 237 field assertion rows, and 238 crosswalk rows—approximately one of each per current field. This is not consistent with the reviewed registry, which distinguishes typed targets, grouped transforms, archives, exceptions, crosswalks and non-migrated operational controls.

For example, the reviewed correction-type row states that a raw archive is not required when the exact typed value is preserved, yet the expected fixture contains `phase-a-archive-address-corrections-correction-type`. The expected crosswalk set also contains per-field values such as timestamps, booleans and names mapped to generic target IDs; crosswalk identity should normally describe source records/identifiers and actual target identities, not every field value.

The expected target uses `proposed_location_record_assertion` rows as a universal no-loss witness for all 237 fields, including fields whose reviewed targets are geometry, event time, names, archives or migration exceptions. These assertion rows do not substitute for the actual target transform.

**Required correction:** Re-author expected target rows from the reviewed registry at transform-group/entity level. Create archives only where required, exceptions only for owned unresolved conditions, crosswalks only for source-record/identifier-to-real-target identity, and field assertions only where the target model genuinely calls for an assertion. Preserve operational-control records through an explicit retained/non-migrated disposition rather than artificial location-record assertions.

### PA2-F02-06 — Complete source fixtures are not executed against current_source

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-01, AC-11, AC-16

The 25 fixture records are structurally complete and cover all current fields, but the harness does not insert them into the actual migrated current tables or query them during transformation. `current_source` proves the migration topology only; the F02 run is disconnected from its data.

**Required correction:** Load fixture rows into the actual current tables in dependency-safe order, with values that satisfy the current schema and current controlled domains. Query those rows by actual primary/natural keys during group transforms. Report inserted source records and source-field values from PostgreSQL, not only JSON fixture metadata.

### PA2-F02-07 — Negative probes still do not mutate a transform implementation

**Class:** REQUIRED  
**Affected finding/criteria:** F02, F14; AC-14, AC-16

The wrong-transform-implementation probe modifies the expected fixture and invokes the comparator. The invalid-controlled-translation probe raises `HarnessError` directly. Missing identity/archive/exception/relationship probes mutate expected-row keys. These demonstrate comparator/error matching, not failure of an actual transform implementation.

The unresolved-FK and duplicate-output probes use real PostgreSQL constraints/queries and should be preserved.

**Required correction:** After real group implementations exist, mutate implementation/spec/source inputs and invoke the same normal transformation path. Require the observed target output or database constraint to fail for the named semantic reason. Do not manually raise the expected reason. Preserve savepoint rollback and unchanged-state verification.

### PA2-F02-08 — Current expected target relationships and crosswalks contain incoherent targets

**Class:** REQUIRED  
**Affected finding/criteria:** F02, F14; AC-02, AC-06, AC-11, AC-16

The expected fixture creates per-field crosswalk entries that point many unrelated field values to generic IDs such as the geotag location record. Examples include operational fixture timestamps mapped to a decision-event label but targeting a location-record ID, and fixture metadata fields mapped to migration-exception/name targets using the same generic ID. These rows can satisfy table-level FKs or text fields while failing the intended source-record-to-target-identity semantics.

**Required correction:** Validate every crosswalk against its actual target entity/table and inserted target primary key. Crosswalks must be created at the correct source identity granularity and target identity, with reference-field joins resolved separately. Add query-based target-entity consistency checks, not only non-null or generic FK checks.

### PA2-F14-01 — Cleanup and A1 topology remain accepted

**Class:** ACCEPTED CONTROL WITH CONDITION  
**Affected finding/criteria:** F14; AC-14, AC-20

The correction adds explicit cleanup after success and failure and proves recreation with the same target-state hash. A1 topology remains accepted with conditions.

**Condition:** Once real transformations replace direct expected-row insertion, cleanup/recreate must prove the same current/target catalogs and independently observed target-state hash for the real transform path.

## 5. Exit-gate assessment

| Corrected Phase A exit gate | Result |
|---|---|
| 237 reviewed fields represented in source/spec/expected metadata | PASS |
| 25 current tables represented in source fixture | PASS |
| Missing/duplicate/conflicting field labels | PASS |
| Complete source records loaded into actual current_source tables | **FAIL** |
| 90 reviewed transform groups resolved to executable implementations | **FAIL** |
| Source values drive observed target rows | **FAIL** |
| Expected fixture used only as independent comparator | **FAIL** |
| Group-level target rows/children/relationships match specifications | **FAIL** |
| Real target FKs/crosswalks semantically reference correct target identities | **FAIL** |
| Archive/exception/crosswalk rows follow reviewed dispositions | **FAIL** |
| Actual/expected comparison queries target database both ways | PASS, but circular because expected rows are inserted directly |
| Second-run zero inserts/updates | PASS, but proves direct-row insertion idempotency only |
| Queried duplicate count | PASS for current generic keys |
| Distinct normal-path transform negative probes | **FAIL** |
| Cleanup/recreate | PASS |
| Legacy guardrails green and labelled legacy | PASS |
| Scope/draft/exact-head controls | PASS |

## 6. F02 and F14 disposition

| Finding | Corrected Phase A reassessment | SDA disposition |
|---|---|---|
| F02 | Full metadata coverage is present, but no source-to-target transformation implementation is executed. Expected rows are inserted directly and contain overgeneralized/incoherent archive, assertion and crosswalk semantics. | **OPEN — PHASE A CORRECTION REQUIRED** |
| F14 | A1 topology and cleanup implementation are accepted. The authoritative assurance architecture remains incomplete because A3 is still a fixture-loader/comparator rather than a transform harness. | **OPEN — A1 ACCEPTED; A2/A3 REWORK REQUIRED** |
| F04–F12 | Intentionally untouched by Phase A. | **OPEN / OUTSIDE CURRENT AUTHORIZATION** |
| F13 | PR #8 remains separate. | **RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN** |

## 7. Phase B decision

`NOT AUTHORIZED`

The agent must correct the execution architecture and return for another Phase A reassessment. Do not implement F04–F12, retire legacy guardrails, switch CI authority, request SDA Review 12, or create another review-specific shadow framework.

## 8. Required correction sequence

1. Preserve accepted A1 topology, cleanup/recreate, scope controls and non-authoritative CI step.
2. Load all 25 complete fixture records into actual migrated `current_source` tables.
3. Implement an explicit transform dispatcher and real implementation function/SQL unit for every reviewed transform group.
4. Make transform specifications drive source reads, target rows, IDs, crosswalks, archives, exceptions and relationships.
5. Re-author expected target rows to follow reviewed entity/group dispositions; remove universal per-field assertion/archive/crosswalk generation.
6. Execute all transforms from current_source into canonical_target without reading expected rows.
7. Compare observed target state with expected rows only after execution.
8. Validate real target-entity crosswalk semantics and group-level geometry/correction/operational-control behavior.
9. Replace manual/comparator-only negative probes with real source/spec/implementation mutations.
10. Re-run cleanup/recreate against the real transform path.
11. Update Phase A S16, F02/F14 agent-response cells and PR body at a new exact head.
12. Run legacy and Phase A exact-head CI and request another **Phase A reassessment**, not SDA Review 12.

## 9. Next reassessment exit gate

Before returning:

- all 25 source fixtures are inserted into current_source and queried by real keys;
- all 90 reviewed groups resolve to executable functions/SQL units and are invoked;
- transform implementations never read expected target rows;
- expected rows are independently maintained and used only by the comparator;
- expected archives/exceptions/crosswalks/assertions match reviewed dispositions rather than universal per-field generation;
- grouped geometry and correction transforms produce coherent target rows and valid lineage;
- real target FKs and crosswalk target entities/IDs are validated semantically;
- actual target rows, children, relationships, archives, exceptions and crosswalks are queried and compared both ways;
- second-run inserts/updates and queried semantic duplicates are zero for the actual transform path;
- distinct source/spec/implementation mutations fail the normal transform path for expected reasons with unchanged state;
- cleanup/recreate passes against the actual transform path;
- legacy guardrails remain green and labelled legacy;
- PR #7 remains draft/unmerged and prohibited paths remain absent;
- exact-head workflow/job evidence is recorded;
- F02/F14 agent status is `READY FOR SDA PHASE A REASSESSMENT`;
- no Review 12 request is made.
