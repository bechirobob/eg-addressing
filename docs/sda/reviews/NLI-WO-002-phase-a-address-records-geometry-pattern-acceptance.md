# SDA Pattern Acceptance — Address-Records Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-02-ACCEPTANCE`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `5d29ad24b9fd65089ca1dcdfcb0f13ee0967c46a`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `ACCEPTED WITH RECORDED CONDITIONS`

## 1. Review boundary

Reviewed the C12–C14 correction delta and the complete `address_records` vertical slice, including exact source query, numeric/PostGIS parity, reviewed transform specification, authoritative capture-method vocabulary, explicit callable/binding, identity resolution, source/evidence lineage, target rows, expected absences, read-only comparison, idempotency, precision, actual current-source coordinate mutation, distinct timing, swapped-timing implementation mutation, second-source behavior, same-database rollback evidence, changed paths and exact-head CI.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- Reviewed implementation head is `5d29ad24b9fd65089ca1dcdfcb0f13ee0967c46a`.
- The final delta changes only the one task record, the single `address_records` transform-spec row, the slice evidence report and `authoritative_harness.py`.
- The parent address-records oracle, correction oracle and accepted address-points controls were unchanged.
- No citizen-geotag implementation/specification, other transform group, runtime application, executable migration, migration runner, Docker runtime, production/pilot data, secret, `.env*`, F04–F12 or PR #8 path changed.
- Exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend workflows completed successfully.

## 2. Accepted behavior

The following `address_records` geometry transformation is accepted at the reviewed commit:

```text
complete current_source.address_records row
→ reviewed group-specific transform specification
→ explicit transform_address_records_geometry callable
→ numeric longitude/latitude validation
→ source geom SRID/equality parity check
→ address_records.id identity-crosswalk resolution
→ source/evidence lineage resolution
→ typed canonical_target geometry observation
→ conditional geometry-authority exception
→ committed observed state
→ separate read-only complete-set comparison
→ strict normal-path mutations and same-database rollback proof
```

Accepted controls:

1. `transform_address_records_geometry()` is explicitly bound to `impl_wo002_r06_geometry_observation_address_records`.
2. The group does not use the generic all-groups transform as acceptance evidence.
3. The complete source row is queried by ID with `ST_AsText(geom::geometry)` and `ST_SRID(geom::geometry)`.
4. Numeric longitude/latitude are primary inputs; source `geom` is a required SRID-4326 parity check.
5. Geometry mismatch fails before target writes.
6. Target subject resolution follows `address_records.id`, never `source_submission_id`.
7. Source-record and evidence-object lineage derive from the queried source identity.
8. Coordinate precision is preserved through typed PostGIS insertion.
9. The authoritative capture method is the existing target vocabulary value `derived-from-source`; the harness inserts or repairs no vocabulary row.
10. `observed_at` follows source `created_at`; `recorded_at` follows source `updated_at`.
11. The distinct-timestamp test proves the two timing rules and the swapped implementation fails independent comparison.
12. Exactly one geometry observation and one owned conditional authority exception are created per source record.
13. No geometry version, quality assessment, CRS transformation, substitute per-field assertion or citizen-submission subject is created.
14. The comparator uses a separate read-only connection and compares all source-attributable geometry and exception rows in both directions.
15. Second execution produces zero inserts and zero updates.
16. Two source records produce two observations, two exceptions and two distinct address-record identity crosswalks without duplicates or multiple subject resolution.
17. Negative probes prove equal pre-test and post-rollback target rows/hashes before reset.

## 3. Recorded conditions

- Acceptance is tied to implementation commit `5d29ad24b9fd65089ca1dcdfcb0f13ee0967c46a`, the reviewed `address_records` transform-spec row and the unchanged reviewer-owned oracle files.
- Any change to the accepted callable, binding, reviewed rule set or oracle invalidates this acceptance until further SDA review.
- `derived-from-source` is the canonical capture-method value. Source-table specificity remains in source/evidence lineage and must not be added as a test-only vocabulary value.
- The identity crosswalk, target location record and registry subject are prerequisites owned by the identity/crosswalk transformation, not geometry-transform outputs.
- The invalid-coordinate mutation transactionally removes the current latitude constraint only to seed an otherwise impossible invalid source row for design-harness testing. This is not evidence that runtime or production ingestion may bypass the current constraint. The transaction must roll back the row and catalog mutation before reset.
- The geometry observation remains restricted and non-official. No geometry promotion, publication or public release is authorized.

## 4. Scope of acceptance

Accepted:

- The `address_records` geometry transformation implementation and evidence pattern.
- Its use as a second accepted geometry-family vertical slice.

Not accepted or authorized:

- `citizen_geotag_submissions` implementation except under a separate reviewer-owned oracle and explicit task.
- Any other transform group.
- Broad Phase A reassessment or closure of F02/F14.
- Phase B, F04–F12, SDA Review 12 or NLI-WO-002B.
- Runtime application, executable migration, publication, public-code issuance, certificates, signage, partner release, pilot deployment or production deployment.

## 5. Decision

`ACCEPTED WITH RECORDED CONDITIONS`

The narrow method has now produced two accepted geometry-family transformations. The next controlled task may implement only the citizen-geotag geometry slice under its dedicated reviewer-owned expected-result oracle.
