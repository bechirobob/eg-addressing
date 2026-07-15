# SDA Acceptance — Address-Points Observation Crosswalk

**Control:** `NLI-WO-002-PA-ID-02-ACCEPTANCE`  
**Reviewed implementation:** `58925f94c9f42623a0b49afb8c3913e7d98e06aa`  
**Date:** 2026-07-15  
**Outcome:** `ACCEPTED WITH RECORDED CONDITIONS`

## Accepted behavior

```text
current_source.address_points.id
→ transform_address_points_observation_crosswalk
→ proposed_legacy_crosswalk
→ existing proposed_geometry_observation
→ separate read-only comparison
```

Accepted controls:

- exact binding `impl_wo002_r06_identity_crosswalk_address_points -> transform_address_points_observation_crosswalk`;
- `address_points.id` is the legacy observation identity;
- `address_points.address_id` resolves the separate address location subject and cannot replace the legacy identity;
- source and evidence lineage are `government-internal`;
- the existing geometry observation must match source record, evidence, address subject, `location-point` role and `restricted` classification;
- exactly one crosswalk is inserted on first execution and zero rows are inserted or updated on second execution;
- the crosswalk targets `geometry_observation`, never `location_record`;
- no point-specific location record, registry subject, geometry observation, migration exception, version, code alias or publication row is created;
- absolute semantic uniqueness applies to `(source_table, source_field, legacy_id, target_entity)`;
- second-source identity, read-only complete-set comparison and thirteen rollback probes pass;
- exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend jobs pass.

## Binding conditions

Acceptance is tied to:

- implementation `58925f94c9f42623a0b49afb8c3913e7d98e06aa`;
- oracle SHA-256 `d1b695994ae774a6c54cc99c1e79a0bce023fd5a9a20ec2aee779cfeb10bfa82`;
- accepted addresses identity and geometry controls;
- frozen broad-spec blob `443de54b6bacf6a12106fdbba5dba1a07955eec4`;
- the reviewed live address-points observation-crosswalk specification.

This acceptance does not approve another identity group, broad Phase A, Phase B, deployment or merge.

## Next checkpoint

The next authorized candidate is `WO002-R06-identity-crosswalk-address_records`. The source identity is `address_records.id`; `source_submission_id`, territory, publication, code and geometry fields remain context or provenance only.
