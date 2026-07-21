# SDA Phase A Assessment — NLI-WO-002 Review 11 Authoritative Assurance Harness

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Pull request:** `#7 — NLI-WO-002 canonical national location data model`  
**Reviewed Phase A implementation commit:** `25de8fb258ee0b45c18eced979e39d6d54df99ac`  
**Prior architecture checkpoint:** `docs/sda/reviews/NLI-WO-002-review-11-harness-checkpoint.md`  
**Reviewer:** System Design Authority  
**Assessment date:** 2026-07-15  
**Decision:** `PHASE A CORRECTION REQUIRED — A1 TOPOLOGY ACCEPTED WITH CONDITIONS; A2/A3 INCOMPLETE; PHASE B NOT AUTHORIZED`  
**NLI-WO-002:** `REWORK REQUIRED`  
**NLI-WO-002B:** `UNAUTHORIZED`

## 1. Assessment boundary

Reviewed the exact Phase A implementation head, PR state and changed paths, exact-head workflows, Phase A plan and S16 self-audit, `authoritative_harness.py`, current-source/expected-target/transform-spec/mutation fixtures, current-source and target catalogs, topology leakage report, transform and FK/crosswalk reports, archive/exception evidence, idempotency evidence, strict negative probes, Review 11 resolution-log changes and the original Phase A authorization.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- Reviewed Phase A head: `25de8fb258ee0b45c18eced979e39d6d54df99ac`.
- Phase A is one implementation commit after the reviewer-owned harness checkpoint.
- Changed paths are limited to approved documentation/evidence/harness/workflow-support paths.
- No `services/api/**`, `apps/**`, executable migration, `infra/scripts/migrate.py`, Docker runtime configuration, production/pilot data, `.env*`, secret or PR #8 runtime path changed.
- Agent-skills CI run `29399798659`: success.
- API CI run `29399798643`: success.
  - `sda-design-model` job `87301500097`: success, including the non-authoritative Phase A harness step.
  - `api-tests` job `87301500123`: success.
  - `api-image-runtime` job `87301500132`: success.
  - `migration-lifecycle` job `87301500166`: success.
- Frontend CI run `29399798627`, job `87301498159`: success.
- PR #8 remains separate.
- No SDA Review 12 request was made.

## 2. Decision summary

| Phase | Decision | Assessment |
|---|---|---|
| A1 — Harness skeleton and topology | **ACCEPTED WITH CONDITIONS** | Accepted migrations are applied into `current_source`; the draft target schema is applied into `canonical_target`; `test_control` contains control tables only; public contains approved extension tables; the CI step remains non-authoritative. An explicit cleanup command/result and stronger catalog-parity assertions remain required before final harness cutover. |
| A2 — Independent fixture authority | **REWORK REQUIRED** | Stable directories exist, but the source fixture contains only two current records and declares coverage for 22 of 237 reviewed fields. The expected-target fixture contains aggregate counts, one opaque state hash and FK-edge names—not complete independently reviewable typed target rows, child rows, relationships, archives, exceptions and real FK values. |
| A3 — Authoritative F02 execution | **REWORK REQUIRED** | The harness writes real rows to `canonical_target` and the second run adds zero rows, but only two source tables/two records are transformed. Transform specifications are loaded but do not drive or validate the hard-coded transform implementation. Several included-field mappings are semantically incomplete or incoherent. |
| Phase B | **NOT AUTHORIZED** | F02 and F14 remain open. F04–F12 remain outside the current implementation scope. |

## 3. Accepted Phase A controls to preserve

- One disposable PostgreSQL/PostGIS topology with `current_source`, `canonical_target` and `test_control`.
- Current migrations executed through the accepted migration runner with `search_path=current_source,public`.
- Migration ledger and 25 operational tables located in `current_source`.
- `draft-physical-schema.sql` applied into `canonical_target` with 100 tables and 141 FKs.
- `test_control` restricted to `phase_a_run`, `phase_a_assertion` and `phase_a_fixture_manifest`.
- No business table in `public` beyond approved extension objects.
- Real inserts into proposed target tables rather than a new `r11_*` shadow schema.
- Existing-row comparison and zero second-run inserts/updates for the currently implemented sample.
- Strict expected-reason matching in the negative-probe runner.
- Legacy guardrails retained and labelled separately.
- Non-authoritative Phase A CI step; existing required jobs preserved.
- PR #7 design-only boundary and PR #8 separation.

## 4. Blocking findings

### PA-F02-01 — Phase A covers 22 of 237 reviewed current fields

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-01, AC-11, AC-16, AC-17

The accepted architecture checkpoint requires the F02 suite to cover every reviewed current field through complete-record groups. The current design-consistency inventory contains 237 current pg_catalog fields and 237 reviewed transformation rows. Phase A declares two source records and 22 covered fields. Twenty-three current tables and 215 reviewed fields therefore have no authoritative complete-record transform execution in the new harness.

The counter trusts each fixture's `covered_fields` list; it does not reconcile that list against `current-pg-catalog.json` and `transformation-registry-reviewed.json`, detect duplicate field claims, or fail on an omitted reviewed field.

**Required correction:** Add complete source-record fixtures and transform groups sufficient to account for all 237 reviewed current fields. Every field must resolve to an actual typed target field/row, grouped transform, governed archive, owned exception, retained operational-control record or explicit approved non-migrated disposition. Generate a machine-checked coverage matrix from the current catalog and reviewed registry. Fail on missing, duplicated, conflicting or unexecuted field coverage. Report source-record count separately from field count.

### PA-F02-02 — Expected target fixture is not a complete independently reviewable target data set

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-06, AC-11, AC-16, AC-20

`phase-a-expected-target-records.json` contains aggregate counts, one target-state hash and a list of FK edge names. It does not contain the complete expected target entity rows, typed values, child rows, relationships, archive records, exception records, crosswalk values and real target key values required by the architecture checkpoint.

An opaque hash detects drift but does not let the SDA review the expected target semantics. The expected FK-edge list is not consumed by the harness comparison.

**Required correction:** Replace the aggregate-only expected file with independently maintained complete expected target records. Include exact target table, primary key, typed field values, expected nullable/absent values, child/relationship rows, crosswalk target IDs, archive/exception contents and expected conditions. Derive a hash from those reviewed expected rows only after they are reviewable. Compare the actual database rows and every expected FK edge against that source.

### PA-F02-03 — Transform specifications do not control or validate the transform implementation

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-11, AC-16, AC-17

The harness loads `phase-a-transform-specs.json` and passes it to `build_target_rows()`, but the implementation is hard-coded by source-table name and does not consume or validate the transform-group definitions. A spec can change without changing observed behavior, and a hard-coded transform can create rows not declared by its group.

**Required correction:** Make transform specifications authoritative inputs to dispatch, grouping, target entities/children, ID/crosswalk algorithms, archive/exception requirements and expected coverage. Each reviewed transform group must map to one explicit implementation function or SQL unit, and CI must fail when a group lacks an implementation, an implementation lacks a reviewed group, declared/observed target rows differ, or group source keys/fields differ from current catalog coverage.

### PA-F02-04 — Included geotag and correction transforms are semantically incomplete

**Class:** BLOCKER  
**Affected finding/criteria:** F02, F14; AC-02, AC-09, AC-11, AC-16, AC-20

The geotag fixture declares latitude, longitude, accuracy and capture method covered, but the transform stores them inside `location_record_assertion.value_json`; it does not create the target geometry observation/provenance/quality rows expected for spatial evidence. Several current geotag fields present in the complete record are not declared covered or explicitly disposed.

The correction transform creates a `correction_case` with no target location record and creates no correction-case crosswalk. The harness then creates a `corrects` relationship from the geotag location record to itself, using the geotag promotion decision rather than a correction decision/source. The transform spec assigns that relationship to the geotag group while the correction group declares no relationship. This is not a coherent correction lineage.

**Required correction:** Follow the reviewed transformation registry for every included field. Transform coordinate/evidence facts into the appropriate target geometry/evidence/provenance structures or route them to an explicit conditional exception where a later authority decision blocks the target. Create one correction-case identity and its source crosswalk. Resolve its target through a real address/location crosswalk or retain an owned unresolved-reference exception. Remove the self-correction relationship; create only semantically valid relationships grounded in the correction source and decision.

### PA-F02-05 — Administrative reference rows use the citizen-submitted authority as official source

**Class:** REQUIRED  
**Affected finding/criteria:** F02, F14; AC-03, AC-11, AC-12

The harness seeds one source authority classified `citizen-submitted` and uses it as the source authority for the country and an `official` administrative-unit version. A citizen submission cannot be the source authority for official administrative geography, even in a controlled fixture.

**Required correction:** Use separate synthetic, conditional authority fixtures. Citizen-submitted evidence must remain distinct from an administrative authority reference. Administrative rows must be tied to a conditional/provisional government-authority reference consistent with the checkpoint's expected-truth decision and open administrative-authority RFI. Preserve `non_official=true` and do not imply that the institutional authority is resolved.

### PA-F02-06 — Comparison and idempotency reports rely partly on intended in-memory rows

**Class:** REQUIRED  
**Affected finding/criteria:** F02, F14; AC-14, AC-16, AC-20

`compare_expected()` queries every intended row by primary key, but aggregate counts are computed from the in-memory `rows` dictionary rather than from schema-qualified database queries. Unexpected extra Phase A rows are therefore not included in the count comparison. `duplicate_count` is written as a constant zero rather than queried from target/crosswalk/archive/exception/relationship uniqueness and semantic keys. The expected FK-edge list is not checked.

**Required correction:** Generate actual counts, duplicate checks, FK/crosswalk evidence, target-state rows and typed hashes entirely from database queries after each run. Compare actual and expected row sets both ways so unexpected rows fail. Query semantic duplicate keys and real FK targets. Prove second-run zero inserts/updates and unchanged hashes from database state, not counters alone.

### PA-F02-07 — Negative-probe inventory contains duplicate mechanisms and several manual failure shortcuts

**Class:** REQUIRED  
**Affected finding/criteria:** F02, F14; AC-14, AC-16

The ten probe labels do not represent ten independent mechanisms: wrong-transform-operation and invalid-controlled-translation use the same mutation; wrong-independent-expected-value and mismatched-typed-hash use the same mutation. Missing identity/archive/exception/FK failures are partly raised manually by the harness rather than always arising from the target insert/comparator or independently mutated fixture/spec.

**Required correction:** Keep strict expected-reason matching, but implement distinct probes that mutate the transform implementation, independently expected target fixture, source fixture/spec or target relationship and then run the same normal transform/comparison path. Each probe must identify the exact failing gate and prove transaction rollback/unchanged authoritative state.

### PA-F14-01 — Cleanup and final topology lifecycle are not explicitly proved

**Class:** REQUIRED  
**Affected finding/criteria:** F14; AC-14, AC-20

The harness resets schemas at the start and CI creates a fresh database, which supports deterministic reruns. The approved Phase A evidence also requires cleanup. No explicit cleanup command/report proves that the disposable schemas/database and fixture artifacts are removed or left in a documented final state.

**Required correction:** Add `cleanup` or an equivalent explicit lifecycle action. Prove cleanup after success and failure, and prove a subsequent empty run recreates the same catalogs and target-state hash. The CI job should clean its disposable database/schema or document runner-level disposal and emit cleanup evidence.

## 5. F02 and F14 disposition

| Finding | Phase A assessment | SDA disposition |
|---|---|---|
| F02 | Real target-schema execution demonstrated for a narrow two-record sample; full reviewed mapping and expected-target authority incomplete. | **OPEN — PHASE A CORRECTION REQUIRED** |
| F14 | A1 topology direction demonstrated and accepted with conditions; authoritative assurance architecture remains incomplete until A2/A3 cover the full F02 domain and retire no safeguards. | **OPEN — PARTIAL ARCHITECTURE IMPLEMENTATION ACCEPTED** |
| F04–F12 | Intentionally untouched by Phase A. | **OPEN / OUTSIDE CURRENT AUTHORIZATION** |
| F13 | PR #8 remains separate. | **RESOLVED FOR PR #7 / EXTERNAL MAINTENANCE OPEN** |

## 6. Phase B decision

`NOT AUTHORIZED`

The agent must correct Phase A2/A3 and return for a Phase A reassessment. Do not implement F04–F12, retire legacy guardrails, switch the CI authority, request SDA Review 12, or create another shadow framework.

## 7. Required correction sequence

1. Preserve the accepted A1 topology and non-authoritative CI step.
2. Add machine-checked 237-field/25-table coverage against the authoritative current catalog and reviewed transformation registry.
3. Replace aggregate expected evidence with complete independent typed target rows and conditions.
4. Connect every reviewed transform group to one explicit implementation and execute all groups.
5. Correct geotag geometry/evidence and correction-case/crosswalk/relationship semantics.
6. Separate citizen and conditional administrative source authorities.
7. Generate actual counts, duplicates, hashes and FK evidence from database queries.
8. Replace duplicate/manual probes with distinct normal-path mutations and unchanged-state checks.
9. Add explicit cleanup/recreate evidence.
10. Update Phase A S16, F02/F14 agent-response cells and PR body at a new exact head.
11. Run legacy and Phase A exact-head CI and request **Phase A reassessment**, not SDA Review 12.

## 8. Phase A reassessment exit gate

Before returning:

- all 237 reviewed current fields have exactly one executed complete-record/group disposition;
- every current table is covered or explicitly classified as control/non-migrated with evidence;
- complete expected typed target records are independently reviewable;
- transform-spec/implementation parity is exact;
- actual target rows/FKs/archives/exceptions/relationships are queried and reconciled;
- included spatial and correction semantics are coherent;
- second-run inserts/updates and queried duplicate counts are zero;
- all distinct negative probes fail for expected reasons with unchanged state;
- cleanup/recreate passes;
- legacy guardrails remain green and labelled legacy;
- PR #7 remains draft/unmerged and prohibited paths remain absent;
- exact-head workflow/job evidence is recorded;
- F02 and F14 agent status is `READY FOR SDA PHASE A REASSESSMENT`, not resolved.

## 9. Non-claims

This assessment does not:

- accept NLI-WO-002;
- close F02, F14 or any other open finding;
- authorize Phase B;
- authorize NLI-WO-002B;
- authorize executable production migrations;
- authorize official publication, public-code issuance, certificates/signage or partner release;
- authorize production deployment or national-production readiness.
