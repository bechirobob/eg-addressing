# SDA Pattern-Validation Checkpoint — Address-Points Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-01`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Agent-reported broad execution head:** `9bc824c0fff1ed4d968c5b886218bfd99fa4f740`  
**Reviewer-owned oracle commit:** `edda59f8fbfb59cd5f89709229e2b5168451cf82`  
**Status:** `ONE VERTICAL SLICE AUTHORIZED — BROAD PHASE A REASSESSMENT PAUSED`

## 1. Purpose

The next checkpoint validates one implementation pattern before any further replication across the 90 transformation groups.

The current harness reports 90 invoked groups, but every group is dispatched through the same generic `transform_group()` function. For geometry groups, that generic function hard-codes target identity and subject behavior. A green aggregate report is therefore not sufficient to authorize the pattern.

This checkpoint is intentionally narrow:

```text
current_source.address_points complete source row
→ one explicit address-points geometry implementation
→ canonical_target.proposed_geometry_observation
→ reviewer-owned independent comparison
```

## 2. Reviewer-owned acceptance oracle

The immutable acceptance oracle is:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json
```

The implementation agent must not modify, regenerate, repair, normalize, or replace that file.

Any change to that file during the implementation task invalidates the checkpoint.

## 3. Authorized implementation scope

Only this transform group is authorized:

```text
WO002-R06-geometry-observation-address_points
```

Required executable implementation:

```python
def transform_address_points_geometry(...):
    ...
```

It must be registered explicitly against that group and implementation unit:

```text
impl_wo002_r06_geometry_observation_address_points
```

The transform must not route through the generic all-groups implementation as its acceptance path.

## 4. Required source behavior

The implementation must query the complete row from:

```text
current_source.address_points
WHERE id = 'phase-a-address-points-id'
```

It must consume only the reviewed covered fields and declared context fields listed in the reviewer-owned oracle.

It must resolve `address_id` through the reviewed address-identity crosswalk precondition rather than hard-coding a target subject.

It must fail closed when the source row, target identity crosswalk, target subject, source-record lineage, or evidence object is missing.

## 5. Required target behavior

The implementation must create exactly the target rows defined by the reviewer-owned oracle:

- one `proposed_geometry_observation`;
- one owned conditional `proposed_migration_exception` because canonical geometry promotion authority remains unresolved.

It must not create:

- a canonical geometry version;
- a quality approval;
- a CRS transformation row;
- per-field location assertions as a substitute for the grouped geometry observation.

The observed point must use longitude first and latitude second:

```text
POINT(8.783 3.752), SRID 4326
```

## 6. Separation of duties

The transformation code may read:

- `current_source` data;
- the reviewed transform specification;
- approved fixture/setup preconditions.

It may not read the reviewer-owned expected oracle.

Only the comparator may read the expected oracle, and only after the observed target state has been created.

The comparator must have no target-write capability during comparison.

## 7. Required evidence

The checkpoint must provide raw evidence for:

- exact source SQL and returned row;
- exact transform function invoked;
- exact fields consumed;
- target identity resolution query and result;
- exact SQL inserts or equivalent typed target writes;
- queried geometry WKT and SRID;
- queried accuracy, capture method, lineage and evidence values;
- queried conditional exception;
- expected absent-row queries;
- first-run and second-run row counts;
- exact negative-test failures;
- unchanged state after every failed test.

A summary containing only `passed`, counts, hashes, or assertion IDs is insufficient.

## 8. Required tests

Run only the tests specified in the reviewer-owned oracle:

1. Positive authoritative slice.
2. Second-run idempotency.
3. Wrong-longitude implementation mutation.
4. Invalid source coordinate.
5. Missing source row.
6. Missing address crosswalk.
7. Missing evidence object.
8. Wrong independent expected geometry.

Every negative test must use the normal execution/comparison path. The implementation must not directly raise the expected error merely to satisfy the test.

## 9. Prohibited work

Do not:

- implement or modify the other 89 transformation groups;
- update aggregate Phase A claims to imply all groups are accepted;
- request another broad Phase A reassessment;
- request SDA Review 12;
- modify F04–F12;
- modify the reviewer-owned oracle;
- create another review-numbered schema or validation framework;
- change runtime application/frontend code;
- change executable migrations or `infra/scripts/migrate.py`;
- change Docker runtime configuration;
- touch production/pilot data, secrets, `.env*`, or PR #8.

## 10. Checkpoint completion

When complete, stop. Do not replicate the pattern.

Return:

```text
Implementation commit:
Current PR head:
Local/remote equality:
PR state:

Reviewer-owned oracle changed: YES / NO
Exact function implemented:
Exact registry binding:
Generic transform_group used for this slice: YES / NO

Source row query:
Source row returned:
Fields consumed:
Target identity resolution:

Geometry observation row:
Geometry WKT/SRID:
Accuracy/capture method:
Source/evidence lineage:
Conditional exception row:
Expected absent rows verified:

First-run inserts:
Second-run inserts:
Second-run updates:
Geometry-observation duplicates:

Positive test:
Wrong-longitude mutation:
Invalid-coordinate mutation:
Missing-source mutation:
Missing-crosswalk mutation:
Missing-evidence mutation:
Wrong-expected-geometry mutation:
Failed-test state unchanged:

Exact-head workflow/job IDs:
Prohibited-path result:

Current instructed action:
One address_points geometry vertical slice.

Next instruction required from SDA:
YES — before any additional transform group is implemented or accepted.
```

## 11. Readiness boundary

This checkpoint does not accept Phase A, F02, F14, NLI-WO-002, or NLI-WO-002B. It validates one implementation pattern only.
