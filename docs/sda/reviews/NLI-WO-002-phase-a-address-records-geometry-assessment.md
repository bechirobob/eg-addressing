# SDA Pattern Assessment — Address-Records Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-02-ASSESSMENT`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `85ebbc931bc7090c0446657e01c94886fe17209b`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `CORRECTION REQUIRED — SAME ADDRESS_RECORDS SLICE ONLY`

## 1. Review boundary

Reviewed the one-commit `address_records` geometry implementation delta, including the explicit callable and binding, complete PostgreSQL source query, numeric/PostGIS parity check, identity and lineage resolution, target geometry/exception rows, transform-spec additions, expected-absence checks, read-only comparator, idempotency, negative tests, second-source behavior, workflow change, changed paths and exact-head CI.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- Reviewed implementation head is `85ebbc931bc7090c0446657e01c94886fe17209b`.
- The delta contains only the permitted workflow support, one task record, the single `address_records` transform-spec row, one evidence report and `authoritative_harness.py`.
- The reviewer-owned address-records oracle and accepted address-points controls were not changed.
- No citizen-geotag implementation/specification, other transform group, runtime application, executable migration, migration runner, Docker runtime, production/pilot data, secret, `.env*`, F04–F12 or PR #8 path changed.
- Exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend workflows completed successfully.

## 2. Controls accepted in this implementation

The following behavior is materially correct and must be preserved:

1. `transform_address_records_geometry()` is explicit and bound to `impl_wo002_r06_geometry_observation_address_records`.
2. The slice does not use the generic all-groups transformation function.
3. The complete `current_source.address_records` row is queried by ID, including source geometry WKT and SRID.
4. Numeric longitude/latitude are used as the transform inputs and current `geom` is checked with `ST_Equals` under SRID 4326.
5. Identity resolves through an `address_records.id` crosswalk, not through `source_submission_id`.
6. Source-record and evidence lineage derive from the queried source identity.
7. Typed PostGIS insertion preserves coordinate precision.
8. Exactly one geometry observation and one conditional geometry-authority exception are created for the primary slice.
9. The expected prohibited target rows remain absent.
10. The comparator uses a separate read-only connection and compares the source-attributable target set.
11. Second execution produces zero inserts and zero updates.
12. The second-source fixture produces two source identities, two observations, two exceptions and two distinct identity crosswalks without duplicate or multiple resolution.
13. The principal negative probes record same-database rollback evidence before reset.

These controls establish that the accepted address-points pattern has been transferred substantially correctly.

## 3. Required corrections

### C12 — Capture-method success currently depends on a harness-only vocabulary mutation

**Class:** BLOCKER / AUTHORITATIVE MODEL DIVERGENCE

The canonical target model and generated draft schema define these `capture_method` values:

- `browser-gps`
- `derived-from-source`
- `field-device-gps`
- `imported-geometry`
- `manual-map-point`
- `surveyed`

They do not define `address-record-derived`.

The slice passes only because `ensure_address_records_capture_method_vocab()` inserts `address-record-derived` directly into `canonical_target.vocab_capture_method` before the transformation. This makes the harness extend the authoritative target vocabulary at test time.

This repeats the assurance-divergence problem F14 is intended to remove: a shadow/test-only semantic value can pass while the checked-in target model does not support it.

The SDA also corrects its own prior mapping decision here. The authoritative target value for this slice is:

```text
derived-from-source
```

Source-table specificity is already preserved through source-record/evidence lineage. A new source-specific capture-method value is unnecessary.

**Required resolution:**

- remove `ensure_address_records_capture_method_vocab()`;
- remove every harness insert or repair of `vocab_capture_method`;
- change only the `address_records` transform-spec capture-method value to `derived-from-source`;
- have the transformation consume that value from the reviewed spec;
- prove the value exists immediately after `apply_target`, before any slice preconditions;
- add a test proving the slice passes without any harness vocabulary insertion.

### C13 — The invalid-coordinate test does not mutate `current_source`

**Class:** REQUIRED TEST CORRECTION

`transform_address_records_geometry()` currently handles `invalid_coordinate_current_source` by copying the queried Python dictionary and replacing `latitude` with `91.0` in memory.

The submitted test therefore proves coordinate validation after a query, but it does not prove the normal transform path rejects an invalid row stored in `current_source.address_records`.

**Required resolution:**

- remove the in-transform coordinate override;
- update the actual `current_source.address_records` row inside the isolated negative-test transaction;
- invoke the ordinary source query and transform without a special in-memory coordinate path;
- require `coordinate out of range`;
- measure identical pre-test and post-rollback target rows and hashes before reset.

### C14 — Timing rules are not independently demonstrated

**Class:** REQUIRED EVIDENCE CORRECTION

The reviewed specification correctly declares:

```text
observed_at = address_records.created_at
recorded_at = address_records.updated_at
```

The transform currently writes those fields accordingly. However, the primary fixture gives `created_at` and `updated_at` the same timestamp, so a swapped or duplicated implementation would still satisfy the expected target row.

**Required resolution:**

- add a timing test with `created_at = 2026-07-15T00:00:00Z` and `updated_at = 2026-07-15T01:23:45Z` in the actual current-source row;
- require target `observed_at = 2026-07-15T00:00:00Z` and `recorded_at = 2026-07-15T01:23:45Z`;
- add a transform-implementation mutation that swaps the two target assignments and fails the independent comparison for the expected timing reason;
- preserve same-database rollback proof for the failing implementation mutation.

## 4. Reviewer-owned correction control

The correction oracle is:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-correction-oracle.json
```

Control ID:

```text
NLI-WO-002-PA-GEO-02-C1
```

SHA-256 of the reviewer-authored content:

```text
ed5afa99495234a609762117c102793644529b5b1dfcdf784528a67a3c2ddee2
```

The implementation agent must not modify, regenerate, repair or normalize the parent oracle or this correction oracle. Observed-output code must not read either oracle.

## 5. Decision

`CORRECTION REQUIRED — SAME ADDRESS_RECORDS SLICE ONLY`

The core geometry transformation is close to acceptance. No architectural redesign is required. Correct C12–C14, retain all accepted controls, obtain exact-head evidence and stop for final pattern assessment.

## 6. Authorization boundary

Authorized:

- removal of the harness-only capture-method vocabulary insertion;
- correction of the single `address_records` transform-spec capture-method value;
- correction of the invalid-coordinate source mutation;
- distinct-timestamp positive and swapped-implementation tests;
- one-slice harness/evidence/task/CI updates strictly necessary for C12–C14.

Not authorized:

- modifying either reviewer-owned address-records oracle;
- adding `address-record-derived` to the target vocabulary;
- changing the accepted address-points callable, spec row, oracles or pattern contract;
- citizen-geotag implementation/specification/oracle work;
- any other transform group;
- broad Phase A reassessment, F02/F14 closure, Phase B, F04–F12 or SDA Review 12;
- runtime application/frontend changes, executable migration or migration-runner changes;
- Docker runtime, production/pilot data, secrets, `.env*` or PR #8 changes.
