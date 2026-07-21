# SDA Pattern Assessment — Address-Points Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-01-ASSESSMENT`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `eff62b263abb3f5ea2ab24675afc05449e97b5cb`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `CORRECTION REQUIRED — SAME VERTICAL SLICE ONLY`

## 1. Review boundary

Reviewed the exact one-commit delta from reviewer-controlled head `5bd923875aa654d2831dd55c1f7164481d515d04`, the explicit address-points transform function, registry binding, complete source-row query, identity-crosswalk resolution, source/evidence lineage checks, geometry and conditional exception writes, exact target comparison, absent-row checks, idempotency, six negative cases, generated evidence, CI workflow update, changed-path boundary, oracle integrity and exact-head GitHub Actions.

Independent repository verification:

- PR #7 was open, draft, mergeable and unmerged at the reviewed implementation head.
- The change was exactly one implementation commit after the reviewer-controlled checkpoint.
- Changed paths were limited to:
  - `.github/workflows/api-ci.yml`;
  - one agent task-context document;
  - one geometry-slice evidence report;
  - `authoritative_harness.py`.
- The reviewer-owned parent oracle was not modified.
- No runtime application, executable migration, migration-runner, Docker runtime, production/pilot data, secret, `.env*`, PR #8 or other transform-group path changed.

Independent exact-head workflow verification:

- Agent-skills CI run `29423780780`: success.
- API CI run `29423780784`: success.
  - `sda-design-model` job `87380773279`: success.
  - `api-tests` job `87380773392`: success.
  - `migration-lifecycle` job `87380773293`: success.
  - `api-image-runtime` job `87380773387`: success.
- Frontend CI run `29423780823`, job `87380773129`: success.

## 2. Controls accepted for this slice

The following implementation characteristics are accepted and must be preserved:

1. `transform_address_points_geometry()` exists as an explicit callable.
2. `impl_wo002_r06_geometry_observation_address_points` is explicitly bound to that callable.
3. The slice does not route through the generic all-groups `transform_group()` function.
4. The complete `current_source.address_points` fixture row is queried from PostgreSQL by ID.
5. `address_id` is resolved through the reviewed address identity crosswalk and joined to a target registry subject rather than directly hard-coding the subject.
6. The transform creates one typed PostGIS geometry observation and one owned conditional geometry-authority exception.
7. The observed point uses longitude before latitude and SRID 4326.
8. Accuracy, capture method, source-record lineage and evidence linkage are represented.
9. No geometry version, quality approval, CRS transformation or per-field geometry assertion is created.
10. The second execution creates zero inserts and zero updates for the two slice outputs.
11. The reviewer-owned parent oracle hash is enforced and remained unchanged.
12. Exact-head CI runs the one-slice command as a non-authoritative design checkpoint.

## 3. Corrections required before pattern acceptance

### C01 — Coordinate precision is truncated by the implementation

The transform formats longitude and latitude with `:.3f` before constructing WKT. This silently reduces all future observations to three decimal places. At the Equator, that can represent approximately hundred-metre coordinate granularity while the fixture claims 4.5-metre accuracy.

**Required correction:** Preserve the source numeric precision through typed PostGIS insertion. Execute the reviewer-owned precision case in `NLI-WO-002-phase-a-address-points-geometry-correction-oracle.json` and prove the queried WKT is `POINT(8.7834567 3.7523456)`.

### C02 — Source and evidence lineage are hard-coded to the current fixture

`require_address_points_lineage()` queries fixed IDs rather than resolving lineage from the queried source row/source key. The migration-exception source key is also fixed. A second valid address-points row would be linked to the first row's source/evidence records unless code changed.

**Required correction:** Resolve the source record using the queried row's derived source key and resolve exactly one evidence object through that source record. Derive geometry ID, exception ID and exception source key from the queried source row. Prove the same function handles a temporary second source identity without code changes.

### C03 — The running slice is not bound to the reviewed transform specification

The explicit function and constants match the reviewed names, but the checkpoint does not load and validate the actual reviewed transform specification. A later spec change to the implementation unit, covered fields, context fields or target entity could occur without invalidating the slice.

**Required correction:** Load the reviewed group from `phase-a-transform-specs.json`, validate the group ID, implementation unit, covered fields, required context fields and target entity against the reviewer-owned correction oracle, then dispatch the explicit function. Add the binding-drift failure test.

### C04 — The comparator has target-write capability and does not compare the complete output set

Transformation and comparison use the same writable connection. This does not satisfy the required separation that the comparator have no target-write capability. The comparator queries only the two expected primary keys; an additional geometry observation or exception with a different ID would not be included in `actual` and could remain undetected.

**Required correction:** Commit the positive transform output, then compare through a separate read-only connection/transaction. Query all geometry observations and migration exceptions attributable to this source slice and compare expected and observed row sets in both directions. Add an unexpected-extra-row mutation that must fail.

### C05 — The wrong-longitude test mutates the queried source row, not the implementation

The test named `wrong-longitude-implementation` adds one degree to the in-memory source row after it is queried. That proves the comparator catches a changed input/output, not that it catches incorrect transform logic while the source record remains correct.

**Required correction:** Apply the wrong-longitude mutation inside the transform calculation after the unmodified source row is queried. Preserve the source query evidence and require the same expected failure.

### C06 — Invalid coordinate is not written to the current-source database

The invalid-coordinate test changes the returned Python dictionary rather than changing `current_source.address_points` and running the normal query path.

**Required correction:** In an isolated transaction, update the current-source row to an invalid coordinate, invoke the normal transform path and require `coordinate out of range`, then roll back.

### C07 — Failed-test state is proven only after database reset

After a negative exception, the test recreates the schemas and reruns the positive slice before comparing the hash. This demonstrates clean rebuild reproducibility, but it does not prove that the failed transaction left the same database state unchanged before reset.

**Required correction:** Immediately after each failed test and rollback, before any schema/database reset, query the same target schema and compare its pre-test and post-failure row sets/hash. Only then may the next test recreate its isolated database.

## 4. Decision

`CORRECTION REQUIRED — SAME VERTICAL SLICE ONLY`

The implementation is materially closer to an acceptable pattern and the core positive behavior is credible. The remaining corrections are intentionally narrow and confined to this one function, its comparator and its tests. No broad Phase A remediation or replication is authorized.

The pattern will be accepted only when the corrected slice demonstrates:

- precision preservation;
- derived lineage rather than fixture-specific hard-coding;
- binding to the reviewed transform specification;
- read-only, complete-set comparison;
- real implementation and database-source mutations;
- same-database rollback proof.

## 5. Authorization boundary

Authorized:

- Corrections C01–C07 for `WO002-R06-geometry-observation-address_points` only.
- Changes to the one-slice implementation, one-slice evidence, one-slice task record and the non-authoritative one-slice CI step.

Not authorized:

- Implementing or modifying any of the other 89 transform groups.
- Broad Phase A reassessment.
- SDA Review 12.
- F04–F12 remediation.
- Runtime application or frontend changes.
- Executable migrations or migration-runner changes.
- Docker runtime, production/pilot data, secret, `.env*` or PR #8 changes.

## 6. Reviewer-owned correction oracle

The next implementation must obey and must not modify:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-correction-oracle.json
```

The parent oracle remains authoritative and immutable:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-points-geometry-expected.json
```

## 7. Next checkpoint

After implementing only C01–C07, push the exact head, run exact-head CI, stop, and request SDA assessment of the corrected address-points geometry pattern. Do not replicate the pattern before that decision.
