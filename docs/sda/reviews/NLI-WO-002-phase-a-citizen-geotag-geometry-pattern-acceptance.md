# SDA Pattern Acceptance — Citizen-Geotag Geometry Transformation

**Control ID:** `NLI-WO-002-PA-GEO-03-ACCEPTANCE`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed implementation commit:** `33a6010709d373d2b49fc370dc5dc8a32e652d2f`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `ACCEPTED WITH RECORDED PRIVACY CONDITIONS`

## 1. Review boundary

Reviewed the C15–C17 correction delta and the complete citizen-geotag geometry vertical slice, including changed paths, immutable parent/correction oracles, complete current-source query, reviewed transform specification, explicit callable and binding, authoritative capture-method vocabulary, provisional restricted identity resolution, target location-record and registry-subject validation, restricted source/evidence lineage, typed geometry output, authority exception, privacy/publication exclusions, read-only comparison, idempotency, precision, timing, second-source identity, specification/precondition mutations, same-database rollback evidence and exact-head CI.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- The correction is exactly one commit after reviewer-controlled head `0577ae56f63cec111fc57be082187aee53720e84`.
- The correction changes only the citizen-geotag task record, the single citizen-geotag transform-spec row, the citizen-geotag evidence report and `authoritative_harness.py`.
- The parent citizen-geotag oracle, correction oracle and accepted `address_points` and `address_records` controls were unchanged.
- Exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend workflows completed successfully.

## 2. Accepted behavior

The following citizen-geotag geometry transformation is accepted at the reviewed commit:

```text
complete current_source.citizen_geotag_submissions row
→ reviewed group-specific transform specification
→ explicit transform_citizen_geotag_geometry callable
→ coordinate and capture-method validation
→ provisional restricted location-record identity resolution
→ target location-record and active subject validation
→ restricted source/evidence lineage validation
→ typed restricted geometry observation
→ conditional geometry-authority exception
→ committed observed state
→ separate read-only complete-set comparison
→ privacy/publication exclusions
→ strict normal-path mutations and same-database rollback proof
```

Accepted controls:

1. `transform_citizen_geotag_geometry()` is explicitly bound to `impl_wo002_r06_geometry_observation_citizen_geotag_submissions`.
2. The group does not use the generic all-groups transform as acceptance evidence.
3. The complete source row is queried by `citizen_geotag_submissions.id`.
4. The reviewed transform specification validates covered/context fields, capture translation, timing, classification, identity, target entity, source-record key and idempotency key.
5. `browser-gps` resolves through the existing authoritative target vocabulary; the harness inserts or repairs no vocabulary value.
6. The geometry subject follows a citizen-geotag ID crosswalk to a provisional restricted location record and active registry subject.
7. Territory, field-submission, grid-code, citizen identity/contact fields and `field_verified_at` do not determine the geometry subject.
8. The target location record must be an unretired restricted address record, and its registry subject must be active and unretired.
9. Source-record raw payload classification and evidence classification must both be `restricted`.
10. Coordinate precision is preserved through typed PostGIS insertion with SRID 4326.
11. `observed_at` and `recorded_at` both follow source `created_at`; `field_verified_at` remains verification context.
12. Exactly one restricted geometry observation and one owned conditional authority exception are created per source row.
13. No canonical geometry version, quality assessment, CRS transformation, substitute per-field assertion, public-code alias, publication item or non-restricted observation is created.
14. The comparator uses a separate read-only connection and compares all source-attributable geometry and exception rows in both directions.
15. Second execution produces zero inserts and zero updates.
16. Two source identities produce two observations, two exceptions and two distinct identity crosswalks without semantic duplicates or multiple subject resolution.
17. Existing and C15–C17 negative probes prove the expected failure reason and same-database rollback before reset.

## 3. Recorded privacy and evidence conditions

- Acceptance is tied to implementation commit `33a6010709d373d2b49fc370dc5dc8a32e652d2f`, the reviewed citizen-geotag transform-spec row and the unchanged parent/correction oracle files.
- Any change to the callable, binding, reviewed rule set, source identity metadata, privacy preconditions or oracle files invalidates this acceptance until further SDA review.
- The provisional location-record identity is a design-harness precondition owned by the identity/crosswalk transformation; the geometry transform does not own or authorize production identity creation.
- The complete source-row evidence contains synthetic restricted fixture values only. The command must not be run against pilot or production citizen data, and no real citizen identity/contact value may be committed to repository evidence.
- The observation remains restricted and non-official. No geometry promotion, public-code issuance, publication, certificate, signage, partner release, pilot deployment or production deployment is authorized.

## 4. Geometry-family status

The narrow method has now produced three accepted geometry-family vertical slices:

- `WO002-R06-geometry-observation-address_points`;
- `WO002-R06-geometry-observation-address_records`;
- `WO002-R06-geometry-observation-citizen_geotag_submissions`.

This completes the currently reviewed geometry-observation transform family represented in the Phase A transform specification. It does not accept the broad generic Phase A execution or any non-geometry transform family.

## 5. Scope of acceptance

Accepted:

- The citizen-geotag geometry transformation implementation and evidence pattern.
- The three reviewed geometry-observation groups as separately controlled vertical slices.

Not accepted or authorized:

- Any additional transform group.
- Broad Phase A reassessment or closure of F02/F14.
- Phase B, F04–F12, SDA Review 12 or NLI-WO-002B.
- Runtime application, executable migration, publication, public-code issuance, certificates, signage, partner release, pilot deployment or production deployment.

## 6. Decision

`ACCEPTED WITH RECORDED PRIVACY CONDITIONS`

## 7. Next controlled checkpoint

The next task is mapping-only. Prepare the identity-foundation mapping pack for:

- `WO002-R06-identity-crosswalk-addresses`;
- `WO002-R06-identity-crosswalk-address_points`;
- `WO002-R06-identity-crosswalk-address_records`;
- `WO002-R06-identity-crosswalk-citizen_geotag_submissions`.

The pack must resolve whether each source identity represents a canonical/provisional location identity, a reference to another source identity, an observation/evidence identity, or an owned exception. It must identify crosswalk ownership, target identity, source/evidence lineage, privacy/classification, duplicate/ambiguity rules, expected rows, expected absences and unresolved authority decisions. It must not modify implementation code, transform bindings, reviewer-owned controls or CI.
