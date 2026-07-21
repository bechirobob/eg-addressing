# SDA Assessment — Identity-Foundation Mapping

**Control ID:** `NLI-WO-002-PA-ID-MAP-01`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed mapping commit:** `908bc8b5a57e278314a05ebdc384513b85209f62`  
**Review date:** 2026-07-15  
**Outcome:** `ADDRESSES IDENTITY SLICE AUTHORIZED; OTHER THREE GROUPS DEFERRED`

## Review boundary

The reviewed delta is one mapping-only commit after `510989f0be928038ce5fed7474ef4274e6f57ad2` and adds only `docs/agent/tasks/NLI-WO-002-phase-a-identity-foundation-mapping.md`. PR #7 remains open, draft and unmerged.

## Shared decisions

1. `proposed_legacy_crosswalk` has no lifecycle columns. Therefore `(source_table, source_field, legacy_id, target_entity)` is absolutely unique and may resolve to one `target_id` or no row. Multiple rows or targets fail closed.
2. True identity groups for `addresses`, `address_records` and `citizen_geotag_submissions` own creation or idempotent reuse of exactly a `proposed_location_record`, `proposed_registry_subject` and `proposed_legacy_crosswalk` identity shell.
3. These slices do not create versions, names, assertions, geometry, public-code aliases, publication output or migration exceptions.
4. Building, road, territory, submission and supersession fields are context. They must not replace the primary source identity.
5. Source metadata must use `<source_table>:<queried primary id>` and an idempotency key based on that same queried ID.

## Group dispositions

### `addresses` — authorized next

`addresses.id = phase-a-addresses-id` owns:

```text
location_record = phase-a-location-address-reference
registry_subject = phase-a-subject-phase-a-location-address-reference
crosswalk = phase-a-crosswalk-addresses-id-to-location-record
```

The location record is an unretired `government-internal` address and the subject is active and unretired. Normalized `building_id`, `road_id`, `territory_id`, `superseded_by_address_id` and `public_code` are context only.

Required binding:

```text
impl_wo002_r06_identity_crosswalk_addresses
→ transform_addresses_identity_crosswalk
```

Reviewer oracle:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-addresses-identity-expected.json
```

### `address_points` — deferred observation crosswalk

`address_points.id` is not a location identity. Its future crosswalk must target the accepted geometry observation:

```text
target_entity = geometry_observation
target_id = phase-a-geometry-address-points-phase-a-address-points-id
```

It must not create a location record, registry subject or second address identity.

### `address_records` — mapping accepted, implementation deferred

`address_records.id` owns the existing internal address-record identity:

```text
phase-a-location-address-records-id
phase-a-subject-phase-a-location-address-records-id
phase-a-crosswalk-address-records-id-to-location-record
```

`source_submission_id` and `territory_id` remain context only.

### `citizen_geotag_submissions` — mapping accepted, implementation deferred

`citizen_geotag_submissions.id` owns the existing provisional restricted identity:

```text
phase-a-location-citizen-geotag-001
phase-a-subject-phase-a-location-citizen-geotag-001
phase-a-crosswalk-citizen-geotag-id-to-location-record
```

Source, evidence and target identity remain restricted. Citizen/contact, field-submission, territory, grid-code and verification fields remain context only.

## Addresses implementation requirements

The authorized slice must:

1. Query the complete normalized `current_source.addresses` row.
2. Validate the single reviewed transform-spec row.
3. Derive `source_key = addresses:<queried id>`.
4. Validate one government-internal source record and evidence object.
5. Create or idempotently reuse the exact three identity rows in the oracle.
6. Fail on conflicting existing rows or semantic crosswalk duplicates.
7. Create no other target rows.
8. Commit before a separate read-only complete-set comparison.
9. Run every positive, mutation, second-source, idempotency and rollback test in the oracle.

## Boundary

Only the `addresses` identity slice is authorized. No other identity group, accepted geometry control, broad Phase A reassessment, F02/F14 closure, Phase B, F04–F12, SDA Review 12, runtime implementation, executable migration, deployment, publication or PR #8 change is authorized.

## Decision

`ADDRESSES IDENTITY SLICE AUTHORIZED; OTHER THREE GROUPS DEFERRED`
