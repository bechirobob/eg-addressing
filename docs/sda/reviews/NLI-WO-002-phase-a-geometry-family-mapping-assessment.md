# SDA Mapping Assessment — Geometry-Family Replication

**Control ID:** `NLI-WO-002-PA-GEO-MAP-01`  
**Work order:** `NLI-WO-002`  
**Pull request:** `#7`  
**Reviewed mapping commit:** `838845f7bbbb72b41df0955a7a3902dc198b46d2`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-15  
**Outcome:** `ADDRESS_RECORDS SLICE AUTHORIZED; CITIZEN GEOTAG SLICE DEFERRED`

## 1. Review boundary

Reviewed the one-commit mapping-only delta after the accepted address-points geometry pattern, the complete current-source fixtures, current migration definitions, current PostGIS derivation for `address_records.geom`, reviewed transformation registry/specifications, target geometry-observation model, identity/crosswalk dependencies, source/evidence lineage, proposed target rows, expected absences, authority boundaries and proposed tests for:

- `WO002-R06-geometry-observation-address_records`;
- `WO002-R06-geometry-observation-citizen_geotag_submissions`.

Independent verification:

- PR #7 is open, draft, mergeable and unmerged.
- The reviewed delta adds only `docs/agent/tasks/NLI-WO-002-phase-a-geometry-family-replication-mapping.md`.
- No implementation, transform binding, CI, reviewer-owned control, runtime application, executable migration, migration runner, Docker runtime, production/pilot data, secret, `.env*` or PR #8 path changed.
- Exact-head agent-skills, SDA-design, API-test, migration-lifecycle, API-image and frontend workflows completed successfully.

The mapping pack is accepted as a useful design input. Only one of the two proposed groups is sufficiently resolved for the next implementation checkpoint.

## 2. Address-records decisions

The SDA resolves the technical mapping for `WO002-R06-geometry-observation-address_records` as follows.

### 2.1 Subject identity

The geometry subject follows the canonical current `address_records.id` identity, not `source_submission_id`.

Reason:

- current migration `003_canonical_address_records.sql` explicitly defines `address_records` as the canonical address-record case-file/registry-anchor layer;
- `source_submission_id` is provenance linking the record to citizen intake, not the identity of the resulting address record;
- using the submission identity as the geometry subject would merge evidence identity with registry identity.

Required precondition:

```text
address_records.id
→ proposed_legacy_crosswalk(source_table=address_records, source_field=id)
→ proposed_location_record
→ proposed_registry_subject
```

The geometry transform does not own or create this identity crosswalk. It must fail closed when the reviewed precondition is absent or ambiguous.

### 2.2 Coordinate and `geom` authority

Current migration `005_address_record_postgis_geometry.sql` derives `address_records.geom` from numeric longitude/latitude in EPSG:4326.

Therefore:

- numeric `longitude` and `latitude` are the transform inputs;
- `geom` is a required derived parity check;
- `geom` must be SRID 4326 and equal the point constructed from numeric coordinates;
- a mismatch fails before target writes with `address_records geom does not match latitude/longitude`;
- no CRS transformation row is created for a matching source row.

### 2.3 Capture method

The reviewed target capture method is:

```text
address-record-derived
```

It is a group-specific reviewed constant after numeric/`geom` parity succeeds. It must be declared by the transform-spec row and must not be copied from the accepted `address_points` source-method translation.

### 2.4 Timing and classification

```text
observed_at = address_records.created_at
recorded_at = address_records.updated_at
classification = restricted
```

The precise prepublication point remains restricted even though the source record is classified government-internal.

### 2.5 Source and evidence lineage

The source key is derived from the queried primary key:

```text
address_records:<address_records.id>
```

The transform must resolve exactly one `proposed_source_record` by that key and exactly one evidence object through the resolved source-record ID. IDs must derive from the queried source identity rather than fixed fixture constants.

### 2.6 Expected result authority

The reviewer-owned oracle is:

```text
docs/sda/acceptance/NLI-WO-002-phase-a-address-records-geometry-expected.json
```

Control ID:

```text
NLI-WO-002-PA-GEO-02
```

SHA-256 of the reviewer-authored content:

```text
7a5e68c4639fe290fd46c38d41c754ae25737bee8b260278817970e7758d20e2
```

The implementation agent must not modify, regenerate, normalize or repair this file. Observed-output code must not read it. Only the separate read-only comparator/test authority may read it after committed observed target state exists.

## 3. Address-records implementation authorization

Authorized transform group only:

```text
WO002-R06-geometry-observation-address_records
```

Required explicit implementation:

```text
impl_wo002_r06_geometry_observation_address_records
→ transform_address_records_geometry
```

The implementation must replicate the accepted address-points control pattern while preserving the address-record-specific decisions above.

Required behavior:

1. Query the complete `current_source.address_records` row by `id` and include `ST_AsText(geom::geometry)` and `ST_SRID(geom::geometry)` in the observed source evidence.
2. Validate the independently reviewed group specification, including covered fields, context fields, coordinate-authority/parity rule, capture-method rule, timing rules, classification and target entity.
3. Resolve the subject through exactly one reviewed `address_records.id` identity crosswalk.
4. Resolve source-record and evidence lineage from the derived source key.
5. Preserve coordinate precision using typed `ST_MakePoint(longitude, latitude)` insertion.
6. Validate current `geom` parity before target writes.
7. Create exactly one geometry observation and one conditional geometry-authority exception for each source record.
8. Create no geometry version, quality assessment, CRS transformation or substitute per-field assertion.
9. Commit observed state before a separate read-only complete-set comparison against the reviewer oracle.
10. Produce zero inserts and zero updates on a second execution.
11. Execute every required positive, drift, parity, identity, source, evidence, extra-row, expected-result and rollback test in the oracle.

## 4. Citizen-geotag mapping disposition

`WO002-R06-geometry-observation-citizen_geotag_submissions` remains mapping-only and is **not authorized for implementation**.

The mapping pack correctly identifies unresolved issues:

- whether the geometry subject is a new intake/provisional location identity or another target identity;
- ownership and timing of the citizen-submission identity crosswalk;
- whether `field_verified_at` or `created_at` governs `observed_at`;
- the accepted capture-method vocabulary for `browser-gps`;
- the relationship between `field_submission_id`, territorial scope and observation authority;
- stronger privacy/evidence constraints for citizen identity and contact context.

These decisions will be resolved only after the address-records pattern is inspected. The agent must not create an oracle, transform specification changes, implementation or CI path for the citizen-geotag group during the next task.

## 5. Authorization boundary

Authorized:

- one explicit `address_records` geometry callable and binding;
- modifications to the single `address_records` transform-spec row required by the reviewer oracle;
- one-slice harness, evidence, task record and non-authoritative CI step;
- prerequisite fixture setup for the reviewer-owned address-record identity crosswalk, source record, evidence object, location record and registry subject.

Not authorized:

- `citizen_geotag_submissions` implementation or spec modification;
- any other transform group;
- changes to the accepted `address_points` callable/spec/oracles/pattern contract;
- broad Phase A reassessment;
- closure of F02 or F14;
- Phase B or F04–F12;
- SDA Review 12;
- NLI-WO-002B;
- runtime application/frontend changes;
- executable migrations or migration-runner changes;
- Docker runtime, production/pilot data, secrets, `.env*` or PR #8 changes.

## 6. Decision

`ADDRESS_RECORDS SLICE AUTHORIZED; CITIZEN GEOTAG SLICE DEFERRED`

The next checkpoint is one explicit `address_records` geometry implementation only. Stop after exact-head evidence and request SDA pattern assessment before implementing the citizen-geotag group or any other transform group.
