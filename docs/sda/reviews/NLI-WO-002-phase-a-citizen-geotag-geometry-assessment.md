# SDA Assessment — Citizen-Geotag Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-03-ASSESSMENT`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `7687a654de7c8584e2be0ceca69c65e562b52c8d`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `CORRECTION REQUIRED — FINAL PRIVACY AND IDENTITY-PRECONDITION CONTROLS ONLY`

## 1. Review boundary

Reviewed the exact citizen-geotag implementation delta from reviewer authorization head `4cac539757561461a91700d8b14601118e64cd2a`, including changed paths, explicit callable and binding, complete source query, reviewed transform specification, authoritative capture-method translation, provisional identity setup and resolution, restricted source/evidence lineage, typed geometry output, authority exception, privacy/publication exclusions, read-only comparator, idempotency, normal-path mutations, second-source identity, rollback evidence and exact-head CI.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- The implementation is one commit after the reviewer authorization head.
- Changed paths are limited to the existing non-authoritative CI checkpoint, one task record, the single citizen-geotag transform-spec row, one evidence report and `authoritative_harness.py`.
- The citizen-geotag parent oracle and the accepted `address_points` and `address_records` controls were not changed.
- Exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend workflows completed successfully.

## 2. Controls accepted for this slice

The following implementation controls are accepted and must be preserved:

1. `transform_citizen_geotag_geometry()` is explicitly bound to `impl_wo002_r06_geometry_observation_citizen_geotag_submissions`.
2. The slice does not route through the generic all-groups transform.
3. The complete current-source row is queried by `citizen_geotag_submissions.id`.
4. Covered and context fields, capture translation, timing, classification, identity and target entity are checked against the actual transform-spec row.
5. `browser-gps` resolves through the existing authoritative capture-method vocabulary without harness vocabulary insertion.
6. Source key, target IDs, source record and evidence IDs derive from the queried citizen-geotag identity.
7. The target subject resolves through a citizen-geotag ID crosswalk rather than territory, field submission, grid code or citizen identity/contact fields.
8. Typed PostGIS insertion preserves coordinate precision with SRID 4326.
9. Both `observed_at` and `recorded_at` follow `created_at`; `field_verified_at` remains verification context.
10. Exactly one restricted geometry observation and one owned conditional authority exception are created per source row.
11. No geometry version, quality approval, CRS transform, substitute per-field assertion, public-code alias, publication item or non-restricted observation is created.
12. Observed output commits before separate read-only complete-set comparison.
13. Second execution creates zero inserts and zero updates.
14. Existing negative probes demonstrate implementation, source, specification, identity, evidence, expected-result, surplus-row and timing failures with same-database rollback.
15. Two citizen-geotag identities produce two observations, two exceptions and two distinct crosswalks without semantic duplicates or multiple subject resolution.

## 3. Corrections required before pattern acceptance

### C15 — Restricted source and evidence preconditions are read but not enforced

`require_citizen_geotag_lineage()` queries `raw_payload_classification` and evidence `classification`, but returns them without requiring both to be `restricted`.

The parent oracle requires the source record and evidence object to remain restricted. A misclassified source/evidence row currently permits the transform to continue and still create a restricted target observation, allowing a green result while the privacy precondition is false.

**Required correction:** Validate both classifications before target writes and add normal-path classification-drift tests with same-database rollback evidence.

### C16 — Target location-record and subject state are not fully validated

The identity resolver joins the crosswalk to `proposed_registry_subject`, but it does not join or validate the referenced `proposed_location_record`. It also returns `subject_state` without requiring `active`.

The parent oracle requires:

- a real target location record;
- `record_type = address`;
- `classification = restricted`;
- `retired_at IS NULL`;
- an active, non-retired registry subject for the same native location-record identity.

**Required correction:** Resolve and validate the complete identity precondition before target writes. Add classification, record-type and subject-state drift tests.

### C17 — The reviewed transform specification carries stale source identity metadata

The citizen-geotag transform-spec row still declares:

```text
source_record_key =
citizen_geotag_submissions:phase-a-citizen-geotag-submissions-001
```

and an idempotency key using the same descriptive fixture suffix. The running implementation and reviewer oracle correctly derive the identity from `id = phase-a-geotag-001`.

The binding validator currently does not validate either metadata value.

**Required correction:** Align both values to the queried source identity and add binding-drift tests for `source_record_key` and `idempotency_key`.

## 4. Evidence handling condition

The complete source-row evidence currently includes synthetic restricted citizen fixture values. That is acceptable only inside this disposable design harness.

The command must never be run against pilot or production citizen data, and no real citizen identity/contact value may be committed to repository evidence.

## 5. Decision

`CORRECTION REQUIRED — FINAL PRIVACY AND IDENTITY-PRECONDITION CONTROLS ONLY`

The geometry transformation itself is materially credible. No architecture redesign or new transform group is required. Corrections are limited to the same citizen-geotag callable, its precondition validation, the single reviewed transform-spec row, its tests and evidence.

## 6. Authorization boundary

Authorized:

- C15–C17 corrections for `WO002-R06-geometry-observation-citizen_geotag_submissions` only;
- the single citizen-geotag transform-spec row;
- the one-slice harness, evidence, task record and existing non-authoritative CI step.

Not authorized:

- any additional transform group;
- modifications to accepted `address_points` or `address_records` controls;
- broad Phase A reassessment or closure of F02/F14;
- Phase B, F04–F12, SDA Review 12 or NLI-WO-002B;
- runtime application/frontend changes, executable migration or migration-runner changes;
- Docker runtime, production/pilot data, secrets, `.env*`, publication, public-code issuance, certificates, signage, partner release or PR #8 changes.

## 7. Reviewer-owned correction oracle

The implementation must obey and must not modify:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-correction-oracle.json
```

SHA-256:

```text
f2cbb6689154616955b330c068b4bdfcdaac4b18642799fcca1f94270fe0d7f2
```

The parent citizen-geotag oracle remains unchanged and authoritative.

## 8. Next checkpoint

Implement C15–C17 only, push the exact head, run exact-head CI and stop for the final citizen-geotag pattern assessment. Do not implement another transform group.
