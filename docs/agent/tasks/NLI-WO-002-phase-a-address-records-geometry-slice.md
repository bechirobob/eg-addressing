# NLI-WO-002 Phase A Address Records Geometry Slice

**Checkpoint type:** one explicit transform implementation slice  
**Reviewer-controlled head synchronized:** `48f0bd0ca444256a42409c0f504b1c21ab993daf`  
**Reviewed mapping commit:** `838845f7bbbb72b41df0955a7a3902dc198b46d2`  
**Authorized group:** `WO002-R06-geometry-observation-address_records`  
**Required binding:** `impl_wo002_r06_geometry_observation_address_records -> transform_address_records_geometry`  
**Reviewer-owned oracle:** `docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-expected.json`

## Scope

Implement the address_records geometry vertical slice only. `citizen_geotag_submissions` remains deferred and must not be changed.

## Required controls

- Query complete `current_source.address_records` row by `id`, including `ST_AsText(geom::geometry)` and `ST_SRID(geom::geometry)`.
- Derive `source_key = address_records:<queried id>`.
- Resolve subject only through the address-record identity crosswalk.
- Treat `source_submission_id` as provenance only.
- Use numeric longitude/latitude as primary transform inputs; require `geom` SRID 4326 and parity.
- Create exactly one geometry observation and one conditional authority exception.
- Keep observed-output code free of reviewer oracle reads.
- Use a separate read-only comparator after committed observed state.
- Run all reviewer-required tests and same-database rollback proof.

## Boundary

No other transform group, accepted address_points controls, citizen-geotag spec/implementation, runtime code, executable migrations, Docker runtime, production/pilot data, secrets, `.env*`, F04-F12, PR #8, broad Phase A reassessment, or SDA Review 12.


## C12-C14 correction checkpoint

- C12: capture method now uses authoritative target vocabulary value `derived-from-source`; harness vocabulary insertion is prohibited.
- C13: invalid-coordinate probe mutates the actual `current_source.address_records` row inside the isolated test transaction and proves same-database rollback.
- C14: distinct created/updated timing proves `observed_at <- created_at` and `recorded_at <- updated_at`; swapped implementation mutation must fail independent timing comparison.
