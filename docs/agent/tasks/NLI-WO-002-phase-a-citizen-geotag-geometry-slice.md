# NLI-WO-002 Phase A Citizen Geotag Geometry Slice

**Checkpoint type:** one explicit transform implementation slice  
**Reviewer-controlled head synchronized:** `4cac539757561461a91700d8b14601118e64cd2a`  
**Authorized group:** `WO002-R06-geometry-observation-citizen_geotag_submissions`  
**Required binding:** `impl_wo002_r06_geometry_observation_citizen_geotag_submissions -> transform_citizen_geotag_geometry`  
**Reviewer-owned oracle:** `docs/sda/acceptance/NLI-WO-002-phase-a-citizen-geotag-geometry-expected.json`

## Scope

Implement the citizen-geotag geometry vertical slice only. Do not modify accepted address_points or address_records controls and do not implement any additional transform group.

## Required controls

- Query complete `current_source.citizen_geotag_submissions` row by `id=phase-a-geotag-001`.
- Derive `source_key = citizen_geotag_submissions:<queried id>`.
- Resolve subject only through `citizen_geotag_submissions.id` provisional restricted location-record crosswalk.
- Treat territory, field submission, grid code, citizen identity/contact and field verification fields as context only.
- Translate `browser-gps -> browser-gps` through reviewed spec and authoritative vocabulary without harness vocabulary insertion.
- Use typed `ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)` target geometry insertion.
- Set `observed_at` and `recorded_at` from `created_at`; `field_verified_at` is verification context only.
- Create exactly one restricted geometry observation and one conditional authority exception.
- Keep observed-output code free of reviewer oracle reads; compare after commit through a separate read-only connection.
- Prove privacy/publication boundary and same-database rollback for all failing probes.

## Boundary

No accepted address_points/address_records modifications, no other transform group, no F04-F12, no broad reassessment, no SDA Review 12, no runtime app/frontend/API code, executable migrations, migration runner, Docker runtime, production/pilot data, secrets, `.env*`, publication, public-code issuance, certificates, signage, partner release, or PR #8.

## C15-C17 correction checkpoint

Reviewer head synchronized: `0577ae56f63cec111fc57be082187aee53720e84`.

Corrections remain inside the existing citizen-geotag geometry slice only:

- C15: enforce restricted `proposed_source_record.raw_payload_classification` and restricted `proposed_evidence_object.classification` before target writes.
- C16: validate the resolved target `proposed_location_record` is an active restricted address and the resolved `proposed_registry_subject` is active/non-retired.
- C17: align reviewed transform-spec `source_record_key` and `idempotency_key` to `phase-a-geotag-001`; add validator coverage and drift probes.

No additional transform group is implemented. No parent/correction oracle is modified.
