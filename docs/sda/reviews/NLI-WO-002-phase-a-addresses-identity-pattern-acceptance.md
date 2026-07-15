# SDA Acceptance — Addresses Identity Foundation

**Control:** `NLI-WO-002-PA-ID-01-ACCEPTANCE`  
**Reviewed commit:** `4a8767a727cd1aeae64328af8f6ea33cdef21814`  
**Date:** 2026-07-15  
**Outcome:** `ACCEPTED WITH INTEGRATION CONDITIONS`

## Accepted behavior

The reviewed slice is accepted:

```text
current_source.addresses
→ transform_addresses_identity_crosswalk
→ proposed_location_record
→ proposed_registry_subject
→ proposed_legacy_crosswalk
→ separate read-only comparison
```

Accepted controls:

- exact binding `impl_wo002_r06_identity_crosswalk_addresses -> transform_addresses_identity_crosswalk`;
- identity derives only from `addresses.id`;
- source and evidence classification remain `government-internal`;
- first run inserts exactly three identity rows;
- second run inserts zero and updates zero;
- absolute uniqueness for `(source_table, source_field, legacy_id, target_entity)`;
- no extra version, geometry, alias, release, exception or reference-field crosswalk output;
- surplus crosswalk, location and subject rows are rejected;
- second-source identity and twenty rollback probes pass;
- exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend jobs pass.

## Broad harness condition

Broad generic execution uses:

```text
docs/sda/data-model/fixtures/transform-specs/phase-a-broad-generic-transform-specs-frozen.json
```

Git blob SHA:

```text
443de54b6bacf6a12106fdbba5dba1a07955eec4
```

Broad commands use `broad_registry_groups()`. Narrow reviewed slices use live `registry_groups()`.

## Binding conditions

Acceptance is tied to:

- implementation `4a8767a727cd1aeae64328af8f6ea33cdef21814`;
- parent oracle SHA-256 `518af277e96c94c55808f9ac1e7992059c371bd225d906cf77156c478b0497cd`;
- correction control SHA-256 `22d06863e6aacc31379812b965aa5e34e0c5fee6b8537474498c691dc218b497`;
- the reviewed live addresses specification;
- the frozen broad-spec boundary.

This acceptance does not approve another transform group, broad Phase A, Phase B, deployment or merge.

## Next checkpoint

The next authorized candidate is `WO002-R06-identity-crosswalk-address_points`. `address_points.id` is an observation identity and must map to the accepted geometry observation, not to a new location identity.
