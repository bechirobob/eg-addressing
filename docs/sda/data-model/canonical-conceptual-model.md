# Canonical Conceptual Model

## One authoritative target model

NLI-WO-002 uses `docs/sda/data-model/target-model.json` and `target-entity-field-registry.md` as the authoritative entity-and-field list. Every other design artifact must trace to those entities or explicitly state non-goal status.

## Decided architecture

- `location_record` is the sole canonical registry anchor for addressable locations.
- `location_record_version` carries bitemporal effective and recorded intervals. It is immutable after closure; correction creates a new version.
- `location_record_object_link` supports multiple object relationships with explicit roles and ranks rather than one nullable object column per type.
- `road` is a named/civic corridor identity; `road_segment` is the geometry/routing identity.
- `entrance` is an access point linked to a building and can provide address geometry, but it is not the canonical record unless modelled as the addressable subject through an object link.
- `unit` is a sub-address object. A unit receives its own `location_record` only when it requires independent lookup/publication; otherwise it is a contextual object link on the building record.
- Administrative geography uses generic `administrative_unit` with controlled `admin_level`, boundary versions, and effective dates. Locality/settlement is modelled separately and is not automatically legal hierarchy.
- `geometry_observation` stores raw/candidate spatial evidence; `geometry_version` stores approved geometry for a typed subject and role.
- Publication releases snapshot exact `location_record_version` and `public_code_alias` values.

## Domain map

| Domain | Entities |
|---|---|
| Reference geography | `country`, `administrative_unit`, `administrative_unit_name`, `administrative_boundary_version`, `locality` |
| Operations | `operational_area`, `operational_area_coverage`, `field_assignment` |
| Addressable objects | `road`, `road_segment`, `road_name`, `parcel_reference`, `building`, `entrance`, `unit`, `landmark`, `non_building_object` |
| Canonical registry | `location_record`, `location_record_version`, `location_record_object_link`, `location_record_relationship`, `location_record_assertion`, `decision_event` |
| Geometry | `geometry_observation`, `geometry_version`, `geometry_quality_assessment` |
| Source/evidence | `source_authority`, `source_package`, `source_record`, `evidence_object`, `intake_case`, `field_observation` |
| Correction/dispute | `correction_case`, `dispute_case` |
| Publication | `public_code_alias`, `publication_release`, `publication_release_item`, `partner_projection` |
