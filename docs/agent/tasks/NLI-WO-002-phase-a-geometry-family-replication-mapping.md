# NLI-WO-002 Phase A Geometry Family Replication Mapping Pack

**Checkpoint type:** mapping-only / non-executable  
**Reviewer-controlled head synchronized:** `f247d1a9fbf57a6ee46159720330c76ffb6b89e5`  
**Accepted implementation commit:** `2f9373ef0481af498638810d43a8008986c4697b`  
**Accepted pattern contract:** `docs/sda/acceptance/NLI-WO-002-phase-a-geometry-transform-pattern-contract.json`  
**Pattern acceptance:** `docs/sda/reviews/NLI-WO-002-phase-a-address-points-geometry-pattern-acceptance.md`

## Scope boundary

This pack prepares mapping proposals only for:

- `WO002-R06-geometry-observation-address_records`
- `WO002-R06-geometry-observation-citizen_geotag_submissions`

This pack does **not** implement, activate, bind, or execute either transform group. The SDA must create group-specific reviewer-owned expected-result controls before implementation.

## Accepted pattern controls that must survive replication

The accepted address_points pattern is reusable only as a control baseline:

1. Query the complete current-source row by source identity.
2. Validate an independently reviewed transform-spec row for that exact group.
3. Use an explicit per-group callable and binding; do not use the generic all-groups implementation as acceptance evidence.
4. Do not let observed-output code read reviewer-owned acceptance oracles.
5. Resolve target subject through reviewed identity/crosswalk preconditions; do not hard-code target identity in the geometry transform.
6. Resolve source-record and evidence-object lineage from the queried source row identity.
7. Insert geometry from typed numeric coordinate parameters with SRID 4326; do not truncate precision through preformatted WKT.
8. Create exactly one geometry observation and one owned conditional authority exception per source row.
9. Create no canonical geometry version, quality approval, CRS transformation, or substitute per-field geometry assertion.
10. Compare complete source-attributable target-row sets through a separate read-only comparator.
11. Prove idempotency and negative-test rollback in the same database before reset.

## Shared unresolved replication boundary

The accepted `address_points` slice resolved through an already-reviewed address identity crosswalk. These two groups do **not** yet have reviewer-owned group-specific expected-result controls. Therefore this mapping names the required identity preconditions and candidate deterministic IDs, but implementation must not proceed until SDA publishes the exact expected-result oracle.

---

# Group 1 — `WO002-R06-geometry-observation-address_records`

## 1. Complete current source record

| Field | Value |
|---|---|
| Source table | `address_records` |
| Actual source primary/natural identity | primary key `id = phase-a-address-records-id` after current-source fixture normalization |
| Current-source reported source key | `address_records:phase-a-address-records-001` in the existing fixture metadata |
| Pattern-required derived source key proposal | `address_records:phase-a-address-records-id` derived from the queried `id` |
| Source record ID | `phase-a-source-record-address-records-001` |
| Classification | `government-internal` |

Complete fixture row as currently declared:

```json
{
  "id": "phase-a-address-records-id",
  "address_code": "PHASE-A-NONOFFICIAL-001",
  "source_submission_id": "phase-a-source-submission-id",
  "province_code": "BN",
  "territory_id": "phase-a-territory-id",
  "address_label": "Controlled Phase A address label",
  "status": "submitted",
  "publication_state": "phase-a address_records publication_state",
  "latitude": 3.752,
  "longitude": 8.783,
  "accuracy_meters": 4.5,
  "search_text": "phase-a address_records search_text",
  "record_bundle": "phase-a address_records record_bundle",
  "is_archived": false,
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z",
  "geom": "phase-a address_records geom"
}
```

Queried current-source row after fixture normalization, from `phase-a-current-source-execution-report.json`:

```json
{
  "id": "phase-a-address-records-id",
  "address_code": "PHASE-A-NONOFFICIAL-001",
  "source_submission_id": "phase-a-geotag-001",
  "province_code": "phase-a-provinces-code",
  "territory_id": "phase-a-territories-id",
  "address_label": "Controlled Phase A address label",
  "status": "submitted",
  "publication_state": "phase-a address_records publication_state",
  "latitude": 3.752,
  "longitude": 8.783,
  "accuracy_meters": 4.5,
  "search_text": "phase-a address_records search_text",
  "record_bundle": { "phase_a_value": "phase-a address_records record_bundle" },
  "is_archived": false,
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z",
  "geom": "0101000020E610000037894160E59021406ABC749318040E40"
}
```

### Covered source fields

Declared by the existing transform-spec row:

```json
[
  "address_records.accuracy_meters",
  "address_records.latitude",
  "address_records.longitude"
]
```

### Required context fields

Proposed for the group-specific reviewed transform-spec row:

```json
[
  "address_records.id",
  "address_records.source_submission_id",
  "address_records.created_at",
  "address_records.updated_at",
  "address_records.status",
  "address_records.publication_state",
  "address_records.geom"
]
```

Rationale:

- `id` is required for derived source key, target row IDs, and idempotency.
- `source_submission_id` is required because this record has an existing FK to `citizen_geotag_submissions`; SDA must decide whether geometry subject resolves through the address-record identity itself or through the source submission.
- `created_at` is the proposed observed/recorded time when no stronger observation timestamp exists.
- `updated_at`, `status`, and `publication_state` are context for non-official and publication-lock decisions.
- `geom` is a conditional input because the source also carries geometry bytes in addition to numeric latitude/longitude.

### Nullable and conditional inputs

| Input | Nullability / condition | Mapping note |
|---|---|---|
| `latitude` | Required for this geometry observation path | Missing/null must fail as invalid current-source coordinate. |
| `longitude` | Required for this geometry observation path | Missing/null must fail as invalid current-source coordinate. |
| `accuracy_meters` | Nullable in general; fixture value `4.5` | If null, observation may omit horizontal accuracy or require oracle-defined null handling. |
| `geom` | Conditional cross-check input | Existing source has PostGIS geometry; oracle must decide whether numeric lat/lon is authority, `geom` is cross-check, or mismatch is fatal. |
| `source_submission_id` | FK context | If present, may provide identity lineage to geotag submission; if missing/unresolved, geometry transform must fail or raise owned identity RFI per SDA oracle. |
| `publication_state` / `status` | Controlled-status context | Must not promote to official/public geometry during this checkpoint. |

### Existing source foreign keys

From current execution FK inventory:

| Column | Referenced table | Referenced column | Normalized fixture value |
|---|---|---|---|
| `province_code` | `provinces` | `code` | `phase-a-provinces-code` |
| `source_submission_id` | `citizen_geotag_submissions` | `id` | `phase-a-geotag-001` |
| `territory_id` | `territories` | `id` | `phase-a-territories-id` |

## 2. Subject and identity resolution

| Item | Mapping proposal |
|---|---|
| Exact target subject type | `registry_subject` for a `location_record` subject |
| Candidate fixture subject | `phase-a-subject-phase-a-location-geotag`, **only if** the reviewer-owned address_records identity oracle resolves the record to `phase-a-location-geotag` |
| Required crosswalk | `proposed_legacy_crosswalk` owned by `WO002-R06-identity-crosswalk-address_records` or a separate SDA-approved identity precondition |
| Candidate identity crosswalk | `source_table=address_records`, `source_field=id`, `legacy_id=phase-a-address-records-id`, `target_entity=location_record`, `target_id=<reviewer-oracle-location-record-id>` |
| Crosswalk ownership | Identity/crosswalk transform owner, not the geometry transform |
| Exists now? | Not accepted for this geometry slice. Existing generic/base fixtures are not enough; group-specific reviewer oracle required. |
| Requires separate transform? | YES — required before geometry implementation can be accepted. |
| Identity failure behavior | Fail closed with `address_records.id cannot resolve target location record` or SDA-owned equivalent; no fallback to `phase-a-location-geotag` by code. |

Important deviation from `address_points`: `address_points` resolved through `address_points.address_id -> addresses.id -> address identity crosswalk`. `address_records` has no `address_id`; it has its own `id` plus `source_submission_id`. SDA must decide whether the geometry subject is the address-record identity or the linked source geotag identity.

## 3. Source and evidence lineage

| Item | Mapping proposal |
|---|---|
| Derived source key | `address_records:<queried id>` → `address_records:phase-a-address-records-id` |
| Existing fixture source key | `address_records:phase-a-address-records-001`; this differs from the accepted pattern and must be corrected in group-specific setup/oracle. |
| Source-record resolution | `SELECT source_record_id, source_key FROM proposed_source_record WHERE source_key = 'address_records:phase-a-address-records-id'` |
| Candidate source-record ID | `phase-a-source-record-address-records-001` if its source key is reviewer-aligned to the queried ID |
| Evidence-object resolution | exactly one `proposed_evidence_object` by resolved `source_record_id` |
| Candidate evidence-object ID | `phase-a-evidence-address-records` for the primary fixture; second-source test must use a distinct derived evidence ID |
| Capture/source method | No explicit capture method field exists on `address_records`; proposed translation is `address-record-derived` from persisted registry record geometry/numeric coordinates. |
| Accuracy | `horizontal_accuracy_m = 4.5` from `accuracy_meters` |
| Timing | `observed_at = created_at`; `recorded_at = created_at`; `updated_at` retained only as context unless SDA oracle decides recorded time should be `updated_at` |
| Classification | `government-internal` from source fixture classification; target geometry observation may remain `restricted` only if reviewer oracle requires parity with address_points |
| Provenance/licence | `licence_id = null`; provenance through `source_record_id` and evidence object; no public licence or official release implied |

## 4. Proposed target output

These are mapping proposals only. Exact expected rows must be owned by the future reviewer oracle.

### Proposed `proposed_geometry_observation`

```json
{
  "geometry_observation_id": "phase-a-geometry-address-records-phase-a-address-records-id",
  "subject_id": "<resolved registry_subject.subject_id from required address_records identity crosswalk>",
  "geometry_role": "location-point",
  "observed_geom": "ST_SetSRID(ST_MakePoint(8.783, 3.752), 4326)",
  "observed_geom_wkt_for_review": "POINT(8.783 3.752)",
  "observed_geom_srid_for_review": 4326,
  "capture_method": "address-record-derived",
  "horizontal_accuracy_m": 4.5,
  "source_record_id": "phase-a-source-record-address-records-001",
  "evidence_object_id": "phase-a-evidence-address-records",
  "licence_id": null,
  "observed_at": "2026-07-15T00:00:00Z",
  "recorded_at": "2026-07-15T00:00:00Z",
  "classification": "government-internal"
}
```

### Proposed conditional `proposed_migration_exception`

```json
{
  "migration_exception_id": "phase-a-exception-geometry-authority-address-records-phase-a-address-records-id",
  "batch_id": "phase-a-address-records-geometry-slice",
  "source_table": "address_records",
  "source_field": null,
  "source_key": "address_records:phase-a-address-records-id",
  "exception_type": "authority-rfi",
  "severity": "medium",
  "owner": "SDA",
  "created_at": "2026-07-15T00:00:00Z",
  "resolved_at": null,
  "details_json": {
    "target_entity": "geometry_observation",
    "target_id": "phase-a-geometry-address-records-phase-a-address-records-id",
    "reason": "Canonical geometry promotion authority unresolved; address_records observation preserved without canonical promotion",
    "open_authority_rfi": "geometry-promotion-authority",
    "non_official": true
  }
}
```

### Expected absent rows

- No `proposed_geometry_version`.
- No geometry quality approval.
- No CRS transformation unless the reviewer oracle determines source `geom` is not SRID 4326 or conflicts with numeric coordinates.
- No substitute per-field assertions for `latitude`, `longitude`, `accuracy_meters`, or `geom`.

## 5. Authority and unresolved decisions

- Source may create an observation only; it must not promote canonical/current geometry.
- Canonical promotion authority remains unresolved.
- Required RFI: SDA must decide whether `address_records.geom` or numeric `latitude`/`longitude` is authoritative when both are present.
- Required RFI: SDA must decide whether `address_records` geometry resolves to its own identity crosswalk or to `source_submission_id` / citizen geotag identity.
- Fixture remains non-official and must not authorize publication, signage, certificate, or partner release.

## 6. Capture-method translation

Proposed independently reviewable translation:

```json
{
  "address_records": {
    "source_field": "<none>",
    "source_context": "persisted address record numeric coordinates plus geom field",
    "translation": "address-record-derived"
  }
}
```

Do **not** copy `address_points` → `derived-from-source` automatically. `address_records` is a persisted registry/current record with both numeric coordinates and `geom`, not an explicit point-capture table.

## 7. Test plan

For `WO002-R06-geometry-observation-address_records`, future implementation must include:

1. Positive target output compared against reviewer-owned oracle.
2. Precision preservation using higher-precision temporary latitude/longitude and typed `ST_MakePoint` insertion.
3. Second-run idempotency: first run inserts 2 rows, second run inserts 0 and updates 0.
4. Second-source identity: a second `address_records.id` resolves by derived source key and evidence; shared identity only if the identity crosswalk is truly shared by oracle.
5. Wrong transform calculation: mutate post-query longitude calculation and fail expected geometry comparison.
6. Invalid current-source coordinate: update actual `current_source.address_records` coordinate and fail normal path.
7. Missing source: delete/omit current-source row and prove same-database rollback evidence.
8. Missing identity crosswalk: remove required `address_records` identity crosswalk and fail closed.
9. Missing evidence: remove evidence object for resolved source record and fail closed.
10. Wrong independently expected geometry: comparator-only expected mutation fails.
11. Unexpected extra target row: comparator catches surplus source-attributable geometry/exception rows.
12. Same-database rollback evidence for every failed database mutation before reset.

## 8. Pattern deviations from accepted `address_points`

| Deviation | Impact |
|---|---|
| No `address_id`; has `source_submission_id` FK instead | Identity path is not the accepted address identity path. SDA oracle must decide whether subject follows address_records identity or source geotag identity. |
| Existing fixture source key uses `address_records:phase-a-address-records-001`, not queried `id` | Must be corrected in setup/oracle before implementation to preserve derived-lineage control. |
| Has both numeric coordinates and `geom` | Requires authority/cross-check rule; address_points had only numeric coordinates. |
| No explicit capture method field | Needs source-specific translation; cannot reuse address_points translation silently. |
| Source classification is `government-internal` | Target classification may differ from address_points `restricted`; reviewer oracle must decide. |
| Identity-crosswalk group for address_records includes formal-exception behavior | Geometry implementation must not own those exceptions or hide unresolved identity decisions. |

---

# Group 2 — `WO002-R06-geometry-observation-citizen_geotag_submissions`

## 1. Complete current source record

| Field | Value |
|---|---|
| Source table | `citizen_geotag_submissions` |
| Actual source primary/natural identity | primary key `id = phase-a-geotag-001` |
| Current-source reported source key | `citizen_geotag_submissions:phase-a-citizen-geotag-submissions-001` in existing fixture metadata |
| Pattern-required derived source key proposal | `citizen_geotag_submissions:phase-a-geotag-001` derived from the queried `id` |
| Source record ID | `phase-a-source-record-citizen-geotag-submissions-001` |
| Classification | `restricted` |

Complete fixture row as currently declared:

```json
{
  "id": "phase-a-geotag-001",
  "territory_id": "phase-a-territory-id",
  "address_label": "Controlled Phase A household near Malabo civic office",
  "citizen_name": "Phase A Fixture Citizen",
  "citizen_contact": "+240****0000",
  "dip_last4": "phase-a citizen_geotag_submissions dip_last4",
  "identity_verification_status": "phase-a citizen_geotag_submissions identity_verification_status",
  "identity_document_verified": false,
  "identity_verified_at": "2026-07-15T00:00:00Z",
  "landmark": "phase-a citizen_geotag_submissions landmark",
  "latitude": 3.752,
  "longitude": 8.783,
  "accuracy_meters": 4.5,
  "capture_method": "browser-gps",
  "grid_code": "PHASE-A-NONOFFICIAL-001",
  "status": "submitted",
  "duplicate_hint": "near-controlled-address",
  "reviewer_note": "phase-a citizen_geotag_submissions reviewer_note",
  "suggested_road_name": "phase-a citizen_geotag_submissions suggested_road_name",
  "suggested_local_area": "phase-a citizen_geotag_submissions suggested_local_area",
  "suggested_place_name": "phase-a citizen_geotag_submissions suggested_place_name",
  "map_display_name": "phase-a citizen_geotag_submissions map_display_name",
  "road_suggestion_source": "phase-a citizen_geotag_submissions road_suggestion_source",
  "road_suggestion_attribution": "phase-a citizen_geotag_submissions road_suggestion_attribution",
  "road_suggestion_status": "phase-a citizen_geotag_submissions road_suggestion_status",
  "reviewed_road_name": "phase-a citizen_geotag_submissions reviewed_road_name",
  "field_submission_id": "phase-a-field-submission-id",
  "field_status": "phase-a citizen_geotag_submissions field_status",
  "field_note": "phase-a citizen_geotag_submissions field_note",
  "field_verified_at": "2026-07-15T00:00:00Z",
  "signage_batch": "phase-a citizen_geotag_submissions signage_batch",
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z"
}
```

Queried current-source row after fixture normalization:

```json
{
  "id": "phase-a-geotag-001",
  "territory_id": "phase-a-territories-id",
  "address_label": "Controlled Phase A household near Malabo civic office",
  "citizen_name": "Phase A Fixture Citizen",
  "citizen_contact": "+240****0000",
  "dip_last4": "phase-a citizen_geotag_submissions dip_last4",
  "identity_verification_status": "phase-a citizen_geotag_submissions identity_verification_status",
  "identity_document_verified": false,
  "identity_verified_at": "2026-07-15T00:00:00Z",
  "landmark": "phase-a citizen_geotag_submissions landmark",
  "latitude": 3.752,
  "longitude": 8.783,
  "accuracy_meters": 4.5,
  "capture_method": "browser-gps",
  "grid_code": "PHASE-A-NONOFFICIAL-001",
  "status": "submitted",
  "duplicate_hint": "near-controlled-address",
  "reviewer_note": "phase-a citizen_geotag_submissions reviewer_note",
  "suggested_road_name": "phase-a citizen_geotag_submissions suggested_road_name",
  "suggested_local_area": "phase-a citizen_geotag_submissions suggested_local_area",
  "suggested_place_name": "phase-a citizen_geotag_submissions suggested_place_name",
  "map_display_name": "phase-a citizen_geotag_submissions map_display_name",
  "road_suggestion_source": "phase-a citizen_geotag_submissions road_suggestion_source",
  "road_suggestion_attribution": "phase-a citizen_geotag_submissions road_suggestion_attribution",
  "road_suggestion_status": "phase-a citizen_geotag_submissions road_suggestion_status",
  "reviewed_road_name": "phase-a citizen_geotag_submissions reviewed_road_name",
  "field_submission_id": "phase-a-field-submissions-id",
  "field_status": "phase-a citizen_geotag_submissions field_status",
  "field_note": "phase-a citizen_geotag_submissions field_note",
  "field_verified_at": "2026-07-15T00:00:00Z",
  "signage_batch": "phase-a citizen_geotag_submissions signage_batch",
  "created_at": "2026-07-15T00:00:00Z",
  "updated_at": "2026-07-15T00:00:00Z"
}
```

### Covered source fields

Declared by the existing transform-spec row:

```json
[
  "citizen_geotag_submissions.accuracy_meters",
  "citizen_geotag_submissions.latitude",
  "citizen_geotag_submissions.longitude"
]
```

### Required context fields

Proposed for the group-specific reviewed transform-spec row:

```json
[
  "citizen_geotag_submissions.id",
  "citizen_geotag_submissions.capture_method",
  "citizen_geotag_submissions.created_at",
  "citizen_geotag_submissions.field_verified_at",
  "citizen_geotag_submissions.status",
  "citizen_geotag_submissions.territory_id",
  "citizen_geotag_submissions.field_submission_id"
]
```

Rationale:

- `id` is required for source key, target row IDs, and idempotency.
- `capture_method` has real source semantics and must drive translation.
- `created_at` and `field_verified_at` compete as observation timing; SDA must decide precedence.
- `status`, `territory_id`, and `field_submission_id` are identity/context constraints.

### Nullable and conditional inputs

| Input | Nullability / condition | Mapping note |
|---|---|---|
| `latitude` | Required | Missing/null must fail as invalid coordinate. |
| `longitude` | Required | Missing/null must fail as invalid coordinate. |
| `accuracy_meters` | Nullable in general; fixture value `4.5` | Null handling must be oracle-defined. |
| `capture_method` | Required for translation | Unknown value must fail a controlled translation test or create an SDA-owned RFI, depending on oracle. |
| `field_verified_at` | Nullable in real data; fixture present | Candidate observed time when field verification exists. |
| `identity_verified_at` | Context only for identity review, not geometry timing unless SDA says otherwise. |
| `field_submission_id` | FK-like fixture context | Identity transform owns unresolved final reference/exception behavior. |
| `territory_id` | Existing FK | Operational-area identity unresolved by geometry transform. |

### Existing source foreign keys

From current execution FK inventory:

| Column | Referenced table | Referenced column | Normalized fixture value |
|---|---|---|---|
| `territory_id` | `territories` | `id` | `phase-a-territories-id` |

The reviewed convergence unit also treats `field_submission_id` and `territory_id` as identity/crosswalk inputs with final FK/RFI implications, even though only `territory_id` appears in the current DB FK inventory.

## 2. Subject and identity resolution

| Item | Mapping proposal |
|---|---|
| Exact target subject type | `registry_subject` for a `location_record` subject |
| Candidate fixture subject | `phase-a-subject-phase-a-location-geotag`, **only if** the reviewer-owned citizen_geotag_submissions identity oracle resolves the submission to `phase-a-location-geotag` |
| Required crosswalk | `proposed_legacy_crosswalk` owned by `WO002-R06-identity-crosswalk-citizen_geotag_submissions` or a separate SDA-approved identity precondition |
| Candidate identity crosswalk | `source_table=citizen_geotag_submissions`, `source_field=id`, `legacy_id=phase-a-geotag-001`, `target_entity=location_record`, `target_id=<reviewer-oracle-location-record-id>` |
| Crosswalk ownership | Identity/crosswalk transform owner, not geometry transform |
| Exists now? | Not accepted for this geometry slice. Group-specific reviewer oracle required. |
| Requires separate transform? | YES — required before geometry implementation can be accepted. |
| Identity failure behavior | Fail closed with `citizen_geotag_submissions.id cannot resolve target location record` or SDA-owned equivalent; no fallback to `phase-a-location-geotag` by code. |

## 3. Source and evidence lineage

| Item | Mapping proposal |
|---|---|
| Derived source key | `citizen_geotag_submissions:<queried id>` → `citizen_geotag_submissions:phase-a-geotag-001` |
| Existing fixture source key | `citizen_geotag_submissions:phase-a-citizen-geotag-submissions-001`; this differs from the accepted pattern and must be reviewer-aligned before implementation. |
| Source-record resolution | `SELECT source_record_id, source_key FROM proposed_source_record WHERE source_key = 'citizen_geotag_submissions:phase-a-geotag-001'` |
| Candidate source-record ID | `phase-a-source-record-citizen-geotag-submissions-001` if source key is aligned to queried ID |
| Evidence-object resolution | exactly one `proposed_evidence_object` by resolved `source_record_id` |
| Candidate evidence-object ID | `phase-a-evidence-citizen-geotag-submissions`; second-source test must use a distinct derived evidence ID |
| Capture/source method | `capture_method = browser-gps`; proposed translation `browser-gps` → `browser-gps` or `citizen-browser-gps` pending SDA vocabulary choice |
| Accuracy | `horizontal_accuracy_m = 4.5` |
| Timing | Preferred proposal: `observed_at = field_verified_at` when present; fallback `created_at`; `recorded_at = created_at`. SDA oracle must confirm. |
| Classification | `restricted` |
| Provenance/licence | `licence_id = null`; source/evidence lineage only; contains citizen/identity/contact context so no public release implied |

## 4. Proposed target output

These are mapping proposals only. Exact expected rows must be owned by the future reviewer oracle.

### Proposed `proposed_geometry_observation`

```json
{
  "geometry_observation_id": "phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001",
  "subject_id": "<resolved registry_subject.subject_id from required citizen_geotag_submissions identity crosswalk>",
  "geometry_role": "location-point",
  "observed_geom": "ST_SetSRID(ST_MakePoint(8.783, 3.752), 4326)",
  "observed_geom_wkt_for_review": "POINT(8.783 3.752)",
  "observed_geom_srid_for_review": 4326,
  "capture_method": "browser-gps",
  "horizontal_accuracy_m": 4.5,
  "source_record_id": "phase-a-source-record-citizen-geotag-submissions-001",
  "evidence_object_id": "phase-a-evidence-citizen-geotag-submissions",
  "licence_id": null,
  "observed_at": "2026-07-15T00:00:00Z",
  "recorded_at": "2026-07-15T00:00:00Z",
  "classification": "restricted"
}
```

### Proposed conditional `proposed_migration_exception`

```json
{
  "migration_exception_id": "phase-a-exception-geometry-authority-citizen-geotag-submissions-phase-a-geotag-001",
  "batch_id": "phase-a-citizen-geotag-submissions-geometry-slice",
  "source_table": "citizen_geotag_submissions",
  "source_field": null,
  "source_key": "citizen_geotag_submissions:phase-a-geotag-001",
  "exception_type": "authority-rfi",
  "severity": "medium",
  "owner": "SDA",
  "created_at": "2026-07-15T00:00:00Z",
  "resolved_at": null,
  "details_json": {
    "target_entity": "geometry_observation",
    "target_id": "phase-a-geometry-citizen-geotag-submissions-phase-a-geotag-001",
    "reason": "Canonical geometry promotion authority unresolved; citizen geotag observation preserved without canonical promotion",
    "open_authority_rfi": "geometry-promotion-authority",
    "non_official": true
  }
}
```

### Expected absent rows

- No `proposed_geometry_version`.
- No geometry quality approval.
- No CRS transformation unless SDA publishes a source CRS requirement.
- No substitute per-field assertions for `latitude`, `longitude`, `accuracy_meters`, or `capture_method`.

## 5. Authority and unresolved decisions

- Source may create an observation only; it must not promote canonical/current geometry.
- Canonical promotion authority remains unresolved.
- Required RFI: SDA must decide whether `field_verified_at` or `created_at` is authoritative for `observed_at`.
- Required RFI: SDA must publish accepted capture-method vocabulary for `browser-gps`.
- Required RFI: identity/crosswalk ownership for citizen geotag submission must be accepted before geometry implementation.
- Fixture remains non-official/restricted and must not authorize publication, signage, certificate, or partner release.

## 6. Capture-method translation

Proposed independently reviewable translation:

```json
{
  "citizen_geotag_submissions": {
    "source_field": "capture_method",
    "source_value": "browser-gps",
    "translation": "browser-gps",
    "alternate_if_vocabulary_requires_normalization": "citizen-browser-gps"
  }
}
```

Do **not** copy `address_points` → `derived-from-source`. This source has a direct capture-method value from a citizen-submitted browser GPS workflow.

## 7. Test plan

For `WO002-R06-geometry-observation-citizen_geotag_submissions`, future implementation must include:

1. Positive target output compared against reviewer-owned oracle.
2. Precision preservation using higher-precision temporary latitude/longitude and typed `ST_MakePoint` insertion.
3. Second-run idempotency: first run inserts 2 rows, second run inserts 0 and updates 0.
4. Second-source identity: second citizen geotag ID resolves by derived source key/evidence and proves identity crosswalk semantics.
5. Wrong transform calculation: mutate post-query longitude calculation and fail expected geometry comparison.
6. Invalid current-source coordinate: update actual `current_source.citizen_geotag_submissions` coordinate and fail normal path.
7. Missing source: delete/omit current-source row and prove same-database rollback evidence.
8. Missing identity crosswalk: remove required citizen geotag identity crosswalk and fail closed.
9. Missing evidence: remove evidence object for resolved source record and fail closed.
10. Wrong independently expected geometry: comparator-only expected mutation fails.
11. Unexpected extra target row: comparator catches surplus source-attributable geometry/exception rows.
12. Same-database rollback evidence for every failed database mutation before reset.

## 8. Pattern deviations from accepted `address_points`

| Deviation | Impact |
|---|---|
| Direct `capture_method` source field exists | Translation must be source-specific; do not reuse `derived-from-source`. |
| Existing fixture source key does not equal queried ID-derived source key | Must be reviewer-aligned before implementation. |
| Source classification is `restricted` with citizen identity/contact context | Stronger privacy constraints than address_records; no public release implication. |
| Observation timing may be `field_verified_at`, not just `created_at` | SDA oracle must define timing precedence. |
| Identity group has unresolved `field_submission_id`/`territory_id` exception behavior | Geometry transform must not own or hide identity exceptions. |
| Subject likely geotag location, not address reference | Requires group-specific identity crosswalk; no hard-coded subject fallback. |

---

## Blocking decisions/RFIs before implementation

1. SDA must publish reviewer-owned expected-result controls for both groups.
2. SDA must confirm exact target `location_record_id` / `registry_subject.subject_id` for each source identity.
3. SDA must confirm whether `address_records` geometry subject follows `address_records.id` identity or `source_submission_id`/citizen geotag identity.
4. SDA must confirm source-key correction/alignment for both groups because existing fixture metadata uses `*-001` source keys while the accepted pattern derives source keys from queried primary IDs.
5. SDA must decide `address_records.geom` vs numeric coordinate authority and mismatch behavior.
6. SDA must confirm capture-method vocabulary for `address_records` and `citizen_geotag_submissions.browser-gps`.
7. SDA must confirm timing precedence for citizen geotag `field_verified_at` vs `created_at`.

## Implementation status

No implementation code changed. No transform binding changed. No reviewer-owned control changed. This pack stops at mapping and waits for SDA-owned expected-result controls.
