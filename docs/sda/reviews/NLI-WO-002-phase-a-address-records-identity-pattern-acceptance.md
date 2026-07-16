# SDA Acceptance — Address-Records Identity Foundation

**Control:** `NLI-WO-002-PA-ID-03-ACCEPTANCE`  
**Reviewed implementation:** `7c9b6c892c458dd48b72d3ae3ae79d4c2ad840d6`  
**Date:** 2026-07-16  
**Outcome:** `ACCEPTED WITH RECORDED CONDITIONS`

## Accepted behavior

```text
current_source.address_records.id
→ transform_address_records_identity_crosswalk
→ proposed_location_record
→ proposed_registry_subject
→ proposed_legacy_crosswalk
→ separate read-only comparison
```

Accepted controls:

- exact binding `impl_wo002_r06_identity_crosswalk_address_records -> transform_address_records_identity_crosswalk`;
- identity derives only from `address_records.id`;
- `source_submission_id`, territory, code, publication, labels and geometry are context or provenance only;
- source record, evidence object and identity shell remain `government-internal`;
- first run inserts exactly three identity rows;
- second run inserts zero and updates zero;
- absolute uniqueness applies to `(source_table, source_field, legacy_id, target_entity)`;
- no migration exception, version, geometry, public-code alias or publication output is created;
- surplus crosswalk, location and subject rows are rejected;
- second-source identity and sixteen rollback probes pass;
- exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend jobs pass.

## Binding conditions

Acceptance is tied to:

- implementation `7c9b6c892c458dd48b72d3ae3ae79d4c2ad840d6`;
- oracle SHA-256 `16d1034b786a77d31b6863774807e66d87a337fa78c1a4202e401fbcddecd06e`;
- accepted addresses and address-points identity controls;
- accepted geometry controls;
- frozen broad-spec blob `443de54b6bacf6a12106fdbba5dba1a07955eec4`;
- the reviewed live address-records identity specification.

This acceptance does not approve broad Phase A, Phase B, deployment, merge or another transform group.

## Next checkpoint

The final mapped identity group is `WO002-R06-identity-crosswalk-citizen_geotag_submissions`. It requires a reviewer-owned restricted-identity and no-PII evidence oracle before implementation.