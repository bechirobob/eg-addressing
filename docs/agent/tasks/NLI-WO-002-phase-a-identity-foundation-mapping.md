# NLI-WO-002 Phase A Identity-Foundation Mapping Pack

**Checkpoint type:** mapping-only identity foundation pack  
**Reviewer-controlled head synchronized:** `510989f0be928038ce5fed7474ef4274e6f57ad2`  
**Source instruction:** PR #7 latest SDA comment `4984974446`  
**Formal geometry status:** `NLI-WO-002-PA-GEO-03-ACCEPTANCE` accepted with recorded privacy conditions  

## Scope

Prepare a mapping-only pack for exactly:

1. `WO002-R06-identity-crosswalk-addresses`
2. `WO002-R06-identity-crosswalk-address_points`
3. `WO002-R06-identity-crosswalk-address_records`
4. `WO002-R06-identity-crosswalk-citizen_geotag_submissions`

No implementation, binding, harness, CI, oracle, acceptance-record, runtime, migration, deployment, publication or PR #8 path is modified by this pack.

## Inputs read

- `docs/sda/reviews/NLI-WO-002-phase-a-citizen-geotag-geometry-pattern-acceptance.md`
- `docs/sda/reviews/NLI-WO-002-phase-a-address-points-geometry-pattern-acceptance.md`
- `docs/sda/reviews/NLI-WO-002-phase-a-address-records-geometry-pattern-acceptance.md`
- `docs/sda/data-model/fixtures/transform-specs/phase-a-transform-specs.json`
- `docs/sda/data-model/fixtures/current-source/phase-a-complete-source-records.json`
- `docs/sda/data-model/current-to-target-mapping.json`
- `docs/sda/data-model/schema-convergence-units-reviewed.json`
- `docs/sda/data-model/draft-physical-schema.sql`
- Reviewer-owned geometry expected oracles for accepted geometry prerequisites.

## Shared identity rules proposed for SDA decision

### Semantic uniqueness rule

For `canonical_target.proposed_legacy_crosswalk`, semantic uniqueness should be enforced at least across:

```text
(source_table, source_field, legacy_id, target_entity)
```

Within an active identity-crosswalk set, the tuple above must resolve to **zero or one active target_id**. Re-running an accepted transform may re-observe the same row idempotently, but must not create a second semantic row for the same source identity/target entity.

Recommended future implementation guard:

```sql
SELECT source_table, source_field, legacy_id, target_entity, COUNT(DISTINCT target_id)
FROM canonical_target.proposed_legacy_crosswalk
WHERE source_table = $1
  AND source_field = $2
  AND legacy_id = $3
  AND target_entity = $4
GROUP BY source_table, source_field, legacy_id, target_entity
HAVING COUNT(DISTINCT target_id) > 1;
```

Result must be empty before any dependent transform resolves a subject.

### Shared multiple-resolution rule

A dependent transform must fail closed when a source identity resolves to:

- zero active target identities;
- more than one active target identity;
- a target whose entity is not the reviewed `target_entity`;
- a retired target location record or retired registry subject;
- a target whose classification or lifecycle violates the accepted geometry privacy condition.

### Shared source/evidence rule

Every group must derive source lineage from the queried source row, not from fixture suffixes:

```text
source_key = <source_table>:<queried primary id>
```

A future implementation should resolve exactly one `proposed_source_record` and exactly one `proposed_evidence_object` for that source key before target writes. Classification requirements follow the source domain:

- public/government-internal address registry sources: at minimum non-public projection until publication authority exists;
- citizen_geotag source/evidence: strictly `restricted`.

### Shared publication rule

Identity crosswalks are internal migration infrastructure. They do not authorize:

- public-code issuance;
- publication release items;
- certificates;
- signage;
- partner release;
- pilot or production deployment;
- canonical geometry promotion.

## Group 1 — `WO002-R06-identity-crosswalk-addresses`

### Current transform-spec row

```text
source_table: addresses
source_record_key: addresses:phase-a-addresses-001
idempotency_key: addresses.phase-a-addresses-001::WO002-R06-identity-crosswalk-addresses
implementation_unit: impl_wo002_r06_identity_crosswalk_addresses
covered_source_fields:
  - addresses.building_id
  - addresses.id
  - addresses.road_id
  - addresses.superseded_by_address_id
  - addresses.territory_id
target_entities:
  - legacy_crosswalk
  - migration_exception
```

### Complete source row and identity

Fixture metadata:

```text
source_record_id: phase-a-source-record-addresses-001
current metadata source_key: addresses:phase-a-addresses-001
corrected ID-derived source_key proposal: addresses:phase-a-addresses-id
classification: government-internal
primary identity field: addresses.id
primary identity value: phase-a-addresses-id
```

Representative row fields:

```text
id = phase-a-addresses-id
formatted = Controlled Phase A address label
territory_id = phase-a-territory-id
road_id = phase-a-road-id
building_id = phase-a-building-id
province_code = BN
public_code = PHASE-A-NONOFFICIAL-001
superseded_by_address_id = phase-a-superseded-by-address-id
status = submitted
publication_state = phase-a addresses publication_state
is_archived = false
created_at = 2026-07-15T00:00:00Z
updated_at = 2026-07-15T00:00:00Z
```

### Field-by-field semantic disposition

| Field | Disposition | Rule |
|---|---|---|
| `addresses.id` | source entity identity | Creates/reuses address-level location-record crosswalk if SDA confirms target identity. |
| `addresses.building_id` | reference/context | Resolve through building crosswalk when building family is authorized; unresolved reference creates owned exception, not alternate address identity. |
| `addresses.road_id` | reference/context | Resolve through road crosswalk when road family is authorized; unresolved reference creates owned exception, not alternate address identity. |
| `addresses.territory_id` | reference/context | Resolve through territories → operational_area crosswalk when authorized; unresolved reference creates owned exception. |
| `addresses.superseded_by_address_id` | self-reference / lifecycle | Should not create a new target identity inside this group; unresolved supersession relationship creates owned exception pending lifecycle/supersession authority. |
| `public_code` | context only for this group | Non-official fixture code must not create public-code alias or publication output in this identity-crosswalk group. |

### Target identity proposal

SDA question to confirm: `addresses.id` is the address-level location identity used by accepted address-points geometry.

Proposed target:

```text
target_entity = location_record
target_id = phase-a-location-address-reference
registry_subject = phase-a-subject-phase-a-location-address-reference
identity meaning = canonical/provisional address-level location identity for the legacy addresses row
```

The accepted `address_points` geometry oracle already requires this address-level crosswalk as a precondition:

```json
{
  "legacy_crosswalk_id": "phase-a-crosswalk-addresses-id-to-location-record",
  "source_table": "addresses",
  "source_field": "id",
  "legacy_id": "phase-a-addresses-id",
  "target_entity": "location_record",
  "target_id": "phase-a-location-address-reference",
  "created_at": "2026-07-15T00:00:00Z"
}
```

### Proposed expected rows

#### Crosswalk row

```json
{
  "table": "proposed_legacy_crosswalk",
  "values": {
    "legacy_crosswalk_id": "phase-a-crosswalk-addresses-id-to-location-record",
    "source_table": "addresses",
    "source_field": "id",
    "legacy_id": "phase-a-addresses-id",
    "target_entity": "location_record",
    "target_id": "phase-a-location-address-reference",
    "created_at": "2026-07-15T00:00:00Z"
  }
}
```

#### Owned exception rows

Mapping pack proposal only — exact IDs require SDA oracle before implementation:

- `addresses.building_id`: owned unresolved-reference exception if building crosswalk is absent.
- `addresses.road_id`: owned unresolved-reference exception if road crosswalk is absent.
- `addresses.territory_id`: owned unresolved-reference exception if territories/operational-area crosswalk is absent.
- `addresses.superseded_by_address_id`: owned lifecycle/supersession exception unless the referenced address identity and supersession relation are explicitly authorized.

### Expected absences

- No crosswalk using `building_id`, `road_id`, `territory_id`, `superseded_by_address_id`, `public_code`, `province_code` or labels as `addresses.id` replacement.
- No public-code alias from `addresses.public_code`.
- No publication release item.
- No geometry observation/version/quality output.
- No location-record creation unless the identity unit is explicitly authorized to create the prerequisite target row; otherwise require target row pre-existence.

### Ambiguity and duplicate rules

- `addresses.id` must resolve to at most one active `location_record` target.
- `building_id`, `road_id` and `territory_id` must not be accepted as alternate location-record identities for the address row.
- `superseded_by_address_id` must not cause multiple active location targets; if supersession is active, the lifecycle relationship belongs to a lifecycle/supersession group, not this identity-crosswalk group.

### Open decisions / RFIs

1. SDA must confirm `phase-a-location-address-reference` is the target location record for `addresses.id`.
2. SDA must decide whether this identity group may create the prerequisite location record/subject or only resolve existing target rows.
3. SDA must decide exact owned-exception IDs/details for unresolved building, road, territory and supersession references.
4. SDA must decide whether metadata `source_record_key` should be corrected from `addresses:phase-a-addresses-001` to `addresses:phase-a-addresses-id` before implementation.

## Group 2 — `WO002-R06-identity-crosswalk-address_points`

### Current transform-spec row

```text
source_table: address_points
source_record_key: address_points:phase-a-address-points-001
idempotency_key: address_points.phase-a-address-points-001::WO002-R06-identity-crosswalk-address_points
implementation_unit: impl_wo002_r06_identity_crosswalk_address_points
covered_source_fields:
  - address_points.address_id
  - address_points.id
target_entities:
  - legacy_crosswalk
```

### Complete source row and identity

```text
source_record_id: phase-a-source-record-address-points-001
current metadata source_key: address_points:phase-a-address-points-001
corrected ID-derived source_key proposal: address_points:phase-a-address-points-id
classification: government-internal
primary source row identity: address_points.id = phase-a-address-points-id
address reference: address_points.address_id = phase-a-address-id in fixture metadata; normalized DB path uses phase-a-addresses-id
```

Representative row fields:

```text
id = phase-a-address-points-id
address_id = phase-a-address-id / normalized phase-a-addresses-id
latitude = 3.752
longitude = 8.783
accuracy_meters = 4.5
source_method = phase-a address_points source_method
is_active = false
created_at = 2026-07-15T00:00:00Z
updated_at = 2026-07-15T00:00:00Z
```

### Field-by-field semantic disposition

| Field | Disposition | Rule |
|---|---|---|
| `address_points.id` | observation/source-row identity | Identifies the source point observation/evidence row. It should not create a separate `location_record` crosswalk unless SDA explicitly declares point identities as location identities. |
| `address_points.address_id` | reference to address identity | Must resolve through `addresses.id -> location_record`; accepted geometry already uses the address subject. |
| `latitude`, `longitude`, `accuracy_meters`, `source_method` | observation geometry/provenance | Owned by geometry-observation family, not identity foundation. |
| `is_active` | lifecycle/context | Does not create location identity; may affect later point lifecycle/quality decisions only after SDA authorization. |

### Target identity proposal

Decision proposal: `address_points.id` is **observation-only**, not a canonical/provisional `location_record` identity.

Accepted geometry pattern proves the subject path:

```text
address_points.address_id -> addresses.id crosswalk -> phase-a-location-address-reference -> phase-a-subject-phase-a-location-address-reference
```

Therefore this mapping pack proposes:

- no `target_entity = location_record` crosswalk for `address_points.id`;
- require address reference resolution through the `addresses` identity-crosswalk group;
- if a legacy crosswalk is still required for traceability, classify it as non-location/evidence or observation identity, not as a location-record subject. Current target schema only exposes `target_entity` as text, so exact non-location target entity requires SDA decision.

### Proposed expected rows

#### Preferred proposal: expected absence for location-record crosswalk

```text
No proposed_legacy_crosswalk row where:
source_table = address_points
source_field = id
legacy_id = phase-a-address-points-id
target_entity = location_record
```

#### Required reference path

```json
{
  "reference": "address_points.address_id",
  "must_resolve_through": {
    "source_table": "addresses",
    "source_field": "id",
    "legacy_id": "phase-a-addresses-id",
    "target_entity": "location_record",
    "target_id": "phase-a-location-address-reference"
  }
}
```

#### If SDA requires an explicit row

Use one of these, pending SDA decision:

1. `target_entity = geometry_observation` with `target_id = phase-a-geometry-address-points-phase-a-address-points-id` after geometry observation exists; or
2. `target_entity = source_record` with `target_id = phase-a-source-record-address-points-001`; or
3. formal owned exception declaring `address_points.id` is observation-only and excluded from location-record identity crosswalk.

### Expected absences

- No `location_record` crosswalk from `address_points.id`.
- No registry subject for `address_points.id`.
- No second location identity for the same address point.
- No public-code alias, publication item, geometry version or geometry quality approval.
- No use of `address_points.id` as geometry subject when `address_points.address_id` is resolvable.

### Ambiguity and duplicate rules

- Multiple address_points rows may reference the same `addresses.id`; they must share the same address-level subject, not create duplicate address identities.
- One `address_points.id` may produce multiple observations only if future observation-versioning is authorized; this identity-crosswalk group must not create that versioning.
- Missing or ambiguous `address_points.address_id -> addresses.id` resolution must fail closed or create an owned exception; it must not fall back to `address_points.id` as a location identity.

### Open decisions / RFIs

1. SDA must decide whether `address_points.id` receives any legacy crosswalk at all.
2. If yes, SDA must choose target entity: `geometry_observation`, `source_record`, another non-location entity, or formal exception-only.
3. SDA must decide whether the existing transform-spec target entity `legacy_crosswalk` should be narrowed with explicit `target_entity != location_record` before implementation.
4. SDA must decide whether metadata source keys should be corrected to `address_points:phase-a-address-points-id`.

## Group 3 — `WO002-R06-identity-crosswalk-address_records`

### Current transform-spec row

```text
source_table: address_records
source_record_key: address_records:phase-a-address-records-001
idempotency_key: address_records.phase-a-address-records-001::WO002-R06-identity-crosswalk-address_records
implementation_unit: impl_wo002_r06_identity_crosswalk_address_records
covered_source_fields:
  - address_records.id
  - address_records.source_submission_id
  - address_records.territory_id
target_entities:
  - legacy_crosswalk
  - migration_exception
```

### Complete source row and identity

```text
source_record_id: phase-a-source-record-address-records-001
current metadata source_key: address_records:phase-a-address-records-001
corrected ID-derived source_key proposal: address_records:phase-a-address-records-id
classification: government-internal
primary source identity: address_records.id = phase-a-address-records-id
```

Representative row fields:

```text
id = phase-a-address-records-id
address_code = PHASE-A-NONOFFICIAL-001
source_submission_id = phase-a-source-submission-id in fixture metadata; accepted geometry normalized path uses phase-a-geotag-001
territory_id = phase-a-territory-id
status = submitted
publication_state = phase-a address_records publication_state
latitude = 3.752
longitude = 8.783
accuracy_meters = 4.5
is_archived = false
created_at = 2026-07-15T00:00:00Z
updated_at = 2026-07-15T00:00:00Z
```

### Field-by-field semantic disposition

| Field | Disposition | Rule |
|---|---|---|
| `address_records.id` | source entity identity | Maps to address-record location identity used by accepted address_records geometry. |
| `address_records.source_submission_id` | provenance/reference only | Must not select target subject. If unresolved, create owned exception or preserve provenance. |
| `address_records.territory_id` | context/reference | Resolve through territories/operational_area when authorized; unresolved reference creates owned exception. |
| `address_code` / publication fields | context/privacy | Non-official fixture code must not create public-code alias or publication output. |
| geometry fields | observation data | Owned by accepted geometry slice, not identity-crosswalk implementation. |

### Target identity proposal

Accepted address_records geometry oracle already requires:

```json
{
  "legacy_crosswalk_id": "phase-a-crosswalk-address-records-id-to-location-record",
  "source_table": "address_records",
  "source_field": "id",
  "legacy_id": "phase-a-address-records-id",
  "target_entity": "location_record",
  "target_id": "phase-a-location-address-records-id",
  "created_at": "2026-07-15T00:00:00Z"
}
```

Target subject:

```text
phase-a-subject-phase-a-location-address-records-id
```

Identity meaning: registry-record/provisional address location identity. It is distinct from citizen-geotag source identity and must not be selected through `source_submission_id`.

### Proposed expected rows

#### Crosswalk row

```json
{
  "table": "proposed_legacy_crosswalk",
  "values": {
    "legacy_crosswalk_id": "phase-a-crosswalk-address-records-id-to-location-record",
    "source_table": "address_records",
    "source_field": "id",
    "legacy_id": "phase-a-address-records-id",
    "target_entity": "location_record",
    "target_id": "phase-a-location-address-records-id",
    "created_at": "2026-07-15T00:00:00Z"
  }
}
```

#### Owned exceptions

Mapping pack proposal only — exact IDs/details require SDA oracle:

- `address_records.source_submission_id`: if it references a citizen submission, resolve as provenance only; if missing/ambiguous, create an owned provenance-reference exception, not a replacement target subject.
- `address_records.territory_id`: if territories/operational-area crosswalk is absent or ambiguous, create owned unresolved-reference exception.

### Expected absences

- No crosswalk where `source_submission_id` becomes a `location_record` subject for address_records geometry.
- No use of `territory_id`, `address_code`, `publication_state`, `province_code` or geometry field as location identity.
- No public-code alias from `address_code`.
- No publication release item.
- No canonical geometry version/quality/transformation rows from this identity group.

### Ambiguity and duplicate rules

- `address_records.id` must resolve to exactly one active `location_record` target.
- `source_submission_id` must resolve, if at all, through citizen provenance/reference; it must not create multiple subject candidates for the address-record source row.
- Two address_records identities must create two distinct `source_table=address_records/source_field=id/legacy_id` rows with no semantic duplicates.

### Open decisions / RFIs

1. SDA should confirm `phase-a-location-address-records-id` as the only target location identity for `address_records.id`.
2. SDA should decide whether target location classification for address_records identity is `government-internal` or should be hardened to `restricted` to match accepted restricted geometry observations.
3. SDA must define exact owned exception IDs/details for unresolved `source_submission_id` and `territory_id` references.
4. SDA must decide whether metadata source keys should be corrected to `address_records:phase-a-address-records-id` before implementation.

## Group 4 — `WO002-R06-identity-crosswalk-citizen_geotag_submissions`

### Current transform-spec row

```text
source_table: citizen_geotag_submissions
source_record_key: citizen_geotag_submissions:phase-a-citizen-geotag-submissions-001
idempotency_key: citizen_geotag_submissions.phase-a-citizen-geotag-submissions-001::WO002-R06-identity-crosswalk-citizen_geotag_submissions
implementation_unit: impl_wo002_r06_identity_crosswalk_citizen_geotag_submissions
covered_source_fields:
  - citizen_geotag_submissions.field_submission_id
  - citizen_geotag_submissions.id
  - citizen_geotag_submissions.territory_id
target_entities:
  - legacy_crosswalk
  - migration_exception
```

### Complete source row and identity

```text
source_record_id: phase-a-source-record-citizen-geotag-submissions-001
current metadata source_key: citizen_geotag_submissions:phase-a-citizen-geotag-submissions-001
corrected ID-derived source_key: citizen_geotag_submissions:phase-a-geotag-001
classification: restricted
primary source identity: citizen_geotag_submissions.id = phase-a-geotag-001
```

Representative sensitive fixture values are synthetic only and must not be replaced with real citizen data. Relevant identity/context fields:

```text
id = phase-a-geotag-001
territory_id = phase-a-territory-id
field_submission_id = phase-a-field-submission-id
capture_method = browser-gps
grid_code = PHASE-A-NONOFFICIAL-001
status = submitted
created_at = 2026-07-15T00:00:00Z
updated_at = 2026-07-15T00:00:00Z
```

### Field-by-field semantic disposition

| Field | Disposition | Rule |
|---|---|---|
| `citizen_geotag_submissions.id` | provisional restricted source entity identity | Maps only to provisional restricted location record used by accepted citizen-geotag geometry. |
| `citizen_geotag_submissions.field_submission_id` | context/reference/provenance | Must not select target subject; unresolved mapping creates owned exception. |
| `citizen_geotag_submissions.territory_id` | context/reference | Resolve through territories/operational_area only when authorized; unresolved reference creates owned exception. |
| citizen identity/contact/DIP fields | restricted evidence/context | Must never be public or target identity output. |
| `grid_code` | non-official context | Must not become public code or publication alias. |
| geometry/capture fields | observation data | Owned by accepted geometry slice, not identity-crosswalk implementation. |

### Target identity proposal

Accepted citizen-geotag geometry oracle requires:

```json
{
  "legacy_crosswalk_id": "phase-a-crosswalk-citizen-geotag-id-to-location-record",
  "source_table": "citizen_geotag_submissions",
  "source_field": "id",
  "legacy_id": "phase-a-geotag-001",
  "target_entity": "location_record",
  "target_id": "phase-a-location-citizen-geotag-001",
  "created_at": "2026-07-15T00:00:00Z"
}
```

Target subject:

```text
phase-a-subject-phase-a-location-citizen-geotag-001
```

Identity meaning: provisional restricted non-official citizen-submitted location identity. It is not publication-ready and does not authorize public code, signage, certificate or partner release.

### Proposed expected rows

#### Crosswalk row

```json
{
  "table": "proposed_legacy_crosswalk",
  "values": {
    "legacy_crosswalk_id": "phase-a-crosswalk-citizen-geotag-id-to-location-record",
    "source_table": "citizen_geotag_submissions",
    "source_field": "id",
    "legacy_id": "phase-a-geotag-001",
    "target_entity": "location_record",
    "target_id": "phase-a-location-citizen-geotag-001",
    "created_at": "2026-07-15T00:00:00Z"
  }
}
```

#### Owned exceptions

Mapping pack proposal only — exact IDs/details require SDA oracle:

- `citizen_geotag_submissions.field_submission_id`: owned provenance-reference exception if no authorized field-submission identity crosswalk exists.
- `citizen_geotag_submissions.territory_id`: owned unresolved-reference exception if no authorized territories/operational-area crosswalk exists.

### Expected absences / privacy boundary

- No public-code alias from `grid_code`.
- No publication release item.
- No public classification for citizen geometry or identity evidence.
- No target identity derived from `territory_id`, `field_submission_id`, `grid_code`, citizen name, citizen contact, D.I.P., identity-verification fields, `field_verified_at` or map labels.
- No certificate, signage, partner release, pilot deployment or production deployment effect.
- No additional location-record identity beyond the provisional restricted target unless SDA explicitly authorizes merge/promotion later.

### Ambiguity and duplicate rules

- `citizen_geotag_submissions.id` must resolve to exactly one active restricted `location_record` target and one active registry subject.
- A citizen source row must never resolve to both citizen-geotag target and address_records target through `source_submission_id`.
- Second-source tests should create distinct source IDs and distinct provisional restricted targets while proving zero duplicate crosswalks and zero multiple subject resolution.

### Open decisions / RFIs

1. SDA should confirm the identity unit may create `phase-a-location-citizen-geotag-001` and its registry subject, or whether those target rows remain separate prerequisites.
2. SDA must define exact owned exception IDs/details for unresolved `field_submission_id` and `territory_id` references.
3. SDA should confirm transform-spec metadata must be corrected from descriptive suffix to `citizen_geotag_submissions:phase-a-geotag-001` before implementation, consistent with accepted geometry C17.
4. SDA must confirm required `restricted` classification for source record, evidence object, target location record and registry subject in the identity-crosswalk oracle.

## Proposed tests by group

Each future identity-crosswalk implementation should receive a reviewer-owned expected oracle before code changes. Proposed test families:

### `addresses`

- Positive exact crosswalk to `phase-a-location-address-reference`.
- Second-run idempotency: zero inserts/updates.
- Second-source identity: two addresses create two distinct target identities or explicitly shared target only when SDA authorizes merge.
- Missing source row.
- Missing target location record/subject if target rows are prerequisites.
- Multiple target resolution for the same `(source_table, source_field, legacy_id, target_entity)`.
- Wrong reference-field use: `building_id`, `road_id`, `territory_id`, `superseded_by_address_id` cannot replace `addresses.id` as the source identity.
- Missing/ambiguous building, road, territory and supersession references create owned exceptions.
- Unexpected extra crosswalk or public-code/publication row.
- Wrong independently expected target.
- Transform-spec source-key/idempotency drift.
- Same-database rollback proof for every failing mutation.

### `address_points`

- Positive expected absence of `location_record` crosswalk for `address_points.id`, unless SDA chooses a non-location crosswalk target.
- Positive address reference path through `addresses.id` crosswalk.
- Second-run idempotency.
- Second-source observation identity: two point IDs referencing same address must not create duplicate address location identities.
- Missing `address_points` source row.
- Missing `addresses.id` reference crosswalk.
- Wrong fallback to `address_points.id` as geometry/location subject.
- Unexpected extra location-record crosswalk for point ID.
- Wrong independently expected target/reclassification.
- Transform-spec drift.
- Same-database rollback proof.

### `address_records`

- Positive exact crosswalk from `address_records.id` to `phase-a-location-address-records-id`.
- Second-run idempotency.
- Second-source identity: two address_records IDs create two distinct crosswalks and no duplicates.
- Missing source row.
- Missing target location record/subject.
- Multiple target resolution.
- Wrong subject through `source_submission_id`.
- Missing/ambiguous `source_submission_id` and `territory_id` references create owned exceptions, not alternate subject identity.
- Classification/privacy drift if SDA requires restricted target identity.
- Unexpected extra row or public-code/publication row.
- Wrong independently expected target.
- Transform-spec source-key/idempotency drift.
- Same-database rollback proof.

### `citizen_geotag_submissions`

- Positive exact restricted crosswalk from `citizen_geotag_submissions.id` to `phase-a-location-citizen-geotag-001`.
- Required restricted source/evidence/target-location/subject preconditions.
- Second-run idempotency.
- Second-source identity: two citizen geotags create two provisional restricted identities without duplicate/multiple resolution.
- Missing source row.
- Missing target location record/subject if target rows are prerequisites.
- Multiple target resolution.
- Wrong subject through `territory_id`, `field_submission_id`, `grid_code`, identity/contact fields or `field_verified_at`.
- Missing/ambiguous `field_submission_id` and `territory_id` references create owned exceptions.
- Classification/privacy drift.
- Unexpected public-code alias/publication item/non-restricted identity row.
- Wrong independently expected target.
- Transform-spec source-key/idempotency drift.
- Same-database rollback proof.

## Deviations from existing generic identity-crosswalk behavior to resolve before implementation

1. Current transform-spec rows use descriptive fixture source keys for all four groups; accepted geometry evidence increasingly relies on queried ID-derived source keys. SDA should decide whether to correct all four identity rows before implementation.
2. `address_points.id` should not blindly follow the generic identity-crosswalk pattern to a location record because accepted geometry resolves subject through `address_points.address_id -> addresses.id`.
3. `citizen_geotag_submissions.id` requires stricter privacy validation than the generic government-internal default: restricted source/evidence/target identity and no public-code/publication output.
4. `source_submission_id`, `field_submission_id`, `territory_id`, `building_id`, `road_id` and supersession references need explicit exception/reference behavior; none should silently become the source row's location identity.
5. The shared semantic uniqueness and multiple-resolution rules should be treated as acceptance-critical before dependent geometry/canonical transforms rely on identity outputs.

## Stop condition

This pack is mapping-only. The next required action is an SDA decision/oracle authorizing exactly one identity-crosswalk implementation, or explicitly revising this mapping. No identity-crosswalk group should be implemented from this pack without that next instruction.
