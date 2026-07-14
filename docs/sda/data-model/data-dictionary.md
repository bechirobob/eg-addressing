# Semantic Data Dictionary

Every target field is defined by the authoritative metadata in `target-model.json`; this document renders that metadata for review.

This is the controlled typed metadata source for NLI-WO-002 Review 02 remediation. No field metadata is inferred from suffixes. Optional IDs, roots, first versions, predecessor/successor links, correction links, evidence links, and geometry supersession links remain nullable where creation requires it.

| Entity | Field | PostgreSQL type | Nullable | Default | FK/relationship | Vocabulary | Authority owner | Classification | Projection | Temporal behavior | Integrity constraints | Semantic definition |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `country` | `country_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | ULID-compatible text or reserved country key | Stable internal country identifier. |
| `country` | `iso2_code` | `char(2)` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | UNIQUE; CHECK iso2_code = upper(iso2_code) | ISO-3166 alpha-2 country code. |
| `country` | `official_name_es` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Official Spanish country name. |
| `country` | `official_name_en` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Approved English presentation name. |
| `country` | `lifecycle_state` | `text` | no | 'active' | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Reference lifecycle state. |
| `country` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Authority that issued this country reference. |
| `country` | `created_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded creation time. |
| `administrative_unit` | `administrative_unit_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Stable opaque internal ID for an administrative unit. |
| `administrative_unit` | `country_id` | `text` | no | — | country.country_id | — | Registry Authority | `government-internal` | operator | current fact | — | Owning country. |
| `administrative_unit` | `stable_code` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | UNIQUE within country and authority package | Stable official or provisional administrative code. |
| `administrative_unit` | `created_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded identity creation time. |
| `administrative_unit` | `retired_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded retirement time for the identity; historical versions remain queryable. |
| `administrative_unit_version` | `administrative_unit_version_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Version identity. |
| `administrative_unit_version` | `administrative_unit_id` | `text` | no | — | administrative_unit.administrative_unit_id | — | Registry Authority | `government-internal` | operator | current fact | — | Administrative identity being versioned. |
| `administrative_unit_version` | `parent_administrative_unit_id` | `text` | yes | — | administrative_unit.administrative_unit_id | — | Registry Authority | `government-internal` | operator | current fact | — | Parent administrative unit; NULL for root country/province rows where permitted. |
| `administrative_unit_version` | `admin_level` | `text` | no | — | — | admin_level | Registry Authority | `government-internal` | operator | current fact | — | Administrative hierarchy level. |
| `administrative_unit_version` | `lifecycle_state` | `text` | no | 'active' | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Version lifecycle state. |
| `administrative_unit_version` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Time this version became legally/effectively valid. |
| `administrative_unit_version` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Exclusive end of legal/effective interval. |
| `administrative_unit_version` | `recorded_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | When the system recorded this version. |
| `administrative_unit_version` | `recorded_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | one recorded_to IS NULL version per administrative_unit_id | When this recorded version was closed; NULL is the sole authoritative current-version mechanism. |
| `administrative_unit_version` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Authority for this hierarchy/status version. |
| `administrative_unit_version` | `classification` | `text` | no | 'public-after-release' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Visibility classification for this version. |
| `name_record` | `name_record_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Name row identity. |
| `name_record` | `subject_entity` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | CHECK subject_entity in configured named subjects | Named entity table. |
| `name_record` | `subject_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Named entity ID; validated by subject registry/checks in WO-002B. |
| `name_record` | `language_code` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | CHECK language_code <> '' | BCP-47 language code, e.g. es-GQ or en. |
| `name_record` | `name_kind` | `text` | no | — | — | name_kind | Registry Authority | `government-internal` | operator | current fact | — | Kind of name. |
| `name_record` | `name_status` | `text` | no | — | — | name_status | Registry Authority | `government-internal` | operator | current fact | — | Name lifecycle status. |
| `name_record` | `name_text` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Authoritative or candidate written name preserving accents/spelling. |
| `name_record` | `normalized_text` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Search-only normalized form; never replaces name_text. |
| `name_record` | `source_record_id` | `text` | yes | — | source_record.source_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source/evidence for the name. |
| `name_record` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Name effective start. |
| `name_record` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Name effective end. |
| `operational_area` | `operational_area_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Operational area identity. |
| `operational_area` | `area_type` | `text` | no | — | — | operational_area_type | Registry Authority | `government-internal` | operator | current fact | — | Purpose class. |
| `operational_area` | `name_record_id` | `text` | yes | — | name_record.name_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Optional display name. |
| `operational_area` | `purpose` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Operational purpose statement. |
| `operational_area` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Operational area lifecycle. |
| `operational_area` | `authority_owner` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Named operational owner. |
| `operational_area` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Operational effective start. |
| `operational_area` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Operational effective end. |
| `operational_area` | `classification` | `text` | no | 'government-internal' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Area visibility classification. |
| `operational_area_coverage` | `coverage_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Coverage row identity. |
| `operational_area_coverage` | `operational_area_id` | `text` | no | — | operational_area.operational_area_id | — | Registry Authority | `government-internal` | operator | current fact | — | Operational area. |
| `operational_area_coverage` | `administrative_unit_id` | `text` | yes | — | administrative_unit.administrative_unit_id | — | Registry Authority | `government-internal` | operator | current fact | — | Administrative unit covered, if applicable. |
| `operational_area_coverage` | `geometry_version_id` | `text` | yes | — | geometry_version.geometry_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Operational boundary geometry, if applicable. |
| `operational_area_coverage` | `coverage_role` | `text` | no | — | — | coverage_role | Registry Authority | `government-internal` | operator | current fact | — | Coverage role. |
| `operational_area_coverage` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Coverage start. |
| `operational_area_coverage` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Coverage end. |
| `road` | `road_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Road identity. |
| `road` | `road_class` | `text` | no | 'unknown' | — | road_class | Registry Authority | `government-internal` | operator | current fact | — | Road class. |
| `road` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Road lifecycle. |
| `road` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Road authority/source. |
| `road` | `created_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded creation. |
| `road_segment` | `road_segment_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Segment identity. |
| `road_segment` | `road_id` | `text` | no | — | road.road_id | — | Registry Authority | `government-internal` | operator | current fact | — | Owning road. |
| `road_segment` | `sequence_number` | `integer` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Optional ordering within road. |
| `road_segment` | `measured_length_m` | `numeric(12,2)` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Measured length in meters; NULL until geometry validated. |
| `road_segment` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Segment lifecycle. |
| `road_segment` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Segment effective start. |
| `road_segment` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Segment effective end. |
| `parcel_reference` | `parcel_reference_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Parcel reference identity. |
| `parcel_reference` | `external_parcel_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | External source parcel identifier. |
| `parcel_reference` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | External parcel authority/source. |
| `parcel_reference` | `classification` | `text` | no | 'restricted' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Parcel reference classification. |
| `parcel_reference` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Reference effective start. |
| `parcel_reference` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Reference effective end. |
| `building` | `building_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Building identity. |
| `building` | `usage_class` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Building usage class where known. |
| `building` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Building lifecycle. |
| `building` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Building source/authority. |
| `building` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Building effective start. |
| `building` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Building effective end. |
| `entrance` | `entrance_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Entrance identity. |
| `entrance` | `building_id` | `text` | no | — | building.building_id | — | Registry Authority | `government-internal` | operator | current fact | — | Building served by entrance. |
| `entrance` | `entrance_role` | `text` | no | 'access-point' | — | object_role | Registry Authority | `government-internal` | operator | current fact | — | Entrance/access role. |
| `entrance` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Entrance lifecycle. |
| `entrance` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Entrance effective start. |
| `entrance` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Entrance effective end. |
| `building_primary_entrance` | `building_primary_entrance_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Assignment identity. |
| `building_primary_entrance` | `building_id` | `text` | no | — | building.building_id | — | Registry Authority | `government-internal` | operator | current fact | — | Building. |
| `building_primary_entrance` | `entrance_id` | `text` | no | — | entrance.entrance_id | — | Registry Authority | `government-internal` | operator | current fact | — | Primary entrance. |
| `building_primary_entrance` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Primary assignment start. |
| `building_primary_entrance` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Primary assignment end. |
| `unit` | `unit_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Unit identity. |
| `unit` | `building_id` | `text` | no | — | building.building_id | — | Registry Authority | `government-internal` | operator | current fact | — | Parent building. |
| `unit` | `parent_unit_id` | `text` | yes | — | unit.unit_id | — | Registry Authority | `government-internal` | operator | current fact | — | Optional parent unit for nested units. |
| `unit` | `unit_label` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Human-readable unit label. |
| `unit` | `unit_type` | `text` | no | 'unit' | — | record_type | Registry Authority | `government-internal` | operator | current fact | — | Unit type. |
| `unit` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Unit lifecycle. |
| `unit` | `classification` | `text` | no | 'government-internal' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Unit visibility classification. |
| `unit` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Unit effective start. |
| `unit` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Unit effective end. |
| `landmark` | `landmark_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Landmark identity. |
| `landmark` | `landmark_type` | `text` | no | 'landmark' | — | record_type | Registry Authority | `government-internal` | operator | current fact | — | Landmark type. |
| `landmark` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Landmark lifecycle. |
| `landmark` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Landmark source. |
| `landmark` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Landmark effective start. |
| `landmark` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Landmark effective end. |
| `locality` | `locality_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Locality identity. |
| `locality` | `administrative_unit_id` | `text` | no | — | administrative_unit.administrative_unit_id | — | Registry Authority | `government-internal` | operator | current fact | — | Containing or governing administrative unit. |
| `locality` | `locality_type` | `text` | no | — | — | locality_type | Registry Authority | `government-internal` | operator | current fact | — | Locality type. |
| `locality` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Locality lifecycle. |
| `locality` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Locality source/authority. |
| `locality` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Locality effective start. |
| `locality` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Locality effective end. |
| `non_building_object` | `object_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Object identity. |
| `non_building_object` | `object_type` | `text` | no | — | — | record_type | Registry Authority | `government-internal` | operator | current fact | — | Object type. |
| `non_building_object` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Object lifecycle. |
| `non_building_object` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Object source. |
| `non_building_object` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Object effective start. |
| `non_building_object` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Object effective end. |
| `location_record` | `location_record_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Canonical record identity; never reused. |
| `location_record` | `record_type` | `text` | no | — | — | record_type | Registry Authority | `government-internal` | operator | current fact | — | Record type. |
| `location_record` | `created_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Record creation time. |
| `location_record` | `retired_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Record retirement time, if identity retired. |
| `location_record` | `classification` | `text` | no | 'government-internal' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Maximum classification for the record identity. |
| `location_record_version` | `location_record_version_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Version identity. |
| `location_record_version` | `location_record_id` | `text` | no | — | location_record.location_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Canonical record being versioned. |
| `location_record_version` | `version_number` | `integer` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | UNIQUE(location_record_id, version_number) | Monotonic per-record version number. |
| `location_record_version` | `lifecycle_state` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Registry lifecycle state for this version. |
| `location_record_version` | `display_label_es` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Spanish display label for this version. |
| `location_record_version` | `display_label_en` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | English display label where approved. |
| `location_record_version` | `administrative_unit_version_id` | `text` | no | — | administrative_unit_version.administrative_unit_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Effective administrative context version. |
| `location_record_version` | `locality_id` | `text` | yes | — | locality.locality_id | — | Registry Authority | `government-internal` | operator | current fact | — | Optional locality context. |
| `location_record_version` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Official effective start. |
| `location_record_version` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Official effective end. |
| `location_record_version` | `recorded_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded transaction start. |
| `location_record_version` | `recorded_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | one recorded_to IS NULL per location_record_id | Recorded transaction end; NULL is the single current-version mechanism. |
| `location_record_version` | `predecessor_version_id` | `text` | yes | — | location_record_version.location_record_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Optional prior version in correction/supersession chain. |
| `location_record_version` | `successor_version_id` | `text` | yes | — | location_record_version.location_record_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Optional later version once superseded/corrected. |
| `location_record_version` | `correction_case_id` | `text` | yes | — | correction_case.correction_case_id | — | Registry Authority | `government-internal` | operator | current fact | — | Correction case that produced this version, if applicable. |
| `location_record_version` | `supersession_reason` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Reason for supersession/correction/retirement. |
| `location_record_version` | `source_decision_event_id` | `text` | no | — | decision_event.decision_event_id | — | Registry Authority | `government-internal` | operator | current fact | — | Decision event authorizing this version. |
| `location_record_object_link` | `link_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Object link identity. |
| `location_record_object_link` | `location_record_version_id` | `text` | no | — | location_record_version.location_record_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Version that owns the link. |
| `location_record_object_link` | `object_entity` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | CHECK object_entity in allowed object subjects | Linked object table. |
| `location_record_object_link` | `object_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | validated by object_entity-specific rule | Linked object ID; checked by object-role validation. |
| `location_record_object_link` | `object_role` | `text` | no | — | — | object_role | Registry Authority | `government-internal` | operator | current fact | — | Role of object for this record version. |
| `location_record_object_link` | `cardinality_rank` | `integer` | no | 1 | — | — | Registry Authority | `government-internal` | operator | current fact | UNIQUE(location_record_version_id, object_role, cardinality_rank) | Rank/order where multiple links have same role. |
| `location_record_object_link` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Link effective start. |
| `location_record_object_link` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Link effective end. |
| `location_record_relationship` | `relationship_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Relationship identity. |
| `location_record_relationship` | `from_location_record_id` | `text` | no | — | location_record.location_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source record. |
| `location_record_relationship` | `to_location_record_id` | `text` | no | — | location_record.location_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Target record. |
| `location_record_relationship` | `relationship_type` | `text` | no | — | — | relationship_type | Registry Authority | `government-internal` | operator | current fact | — | Relationship type. |
| `location_record_relationship` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Relationship effective start. |
| `location_record_relationship` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Relationship effective end. |
| `location_record_relationship` | `source_decision_event_id` | `text` | no | — | decision_event.decision_event_id | — | Registry Authority | `government-internal` | operator | current fact | — | Decision event authorizing relationship. |
| `public_code_alias` | `public_code_alias_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Alias identity. |
| `public_code_alias` | `location_record_id` | `text` | no | — | location_record.location_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Record owning the alias. |
| `public_code_alias` | `public_code` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | UNIQUE; not reused for another location_record_id | Human public code. Grammar remains RFI-controlled. |
| `public_code_alias` | `code_scheme` | `text` | no | 'nli-reserved-v1' | — | — | Registry Authority | `government-internal` | operator | current fact | — | Code scheme/version. |
| `public_code_alias` | `code_state` | `text` | no | — | — | public_code_state | Registry Authority | `government-internal` | operator | current fact | — | Alias lifecycle. |
| `public_code_alias` | `reserved_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Reservation time. |
| `public_code_alias` | `issued_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Public issue time. |
| `public_code_alias` | `retired_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Retirement time. |
| `public_code_alias` | `predecessor_alias_id` | `text` | yes | — | public_code_alias.public_code_alias_id | — | Registry Authority | `government-internal` | operator | current fact | — | Prior alias if superseded. |
| `public_code_alias` | `successor_alias_id` | `text` | yes | — | public_code_alias.public_code_alias_id | — | Registry Authority | `government-internal` | operator | current fact | — | Successor alias after supersession. |
| `geometry_observation` | `geometry_observation_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Observation identity. |
| `geometry_observation` | `subject_hint_entity` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Optional intended subject entity before approval. |
| `geometry_observation` | `subject_hint_id` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Optional intended subject ID before approval. |
| `geometry_observation` | `observed_geom` | `geometry(Geometry,4326)` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | CHECK ST_SRID(observed_geom)=4326; CHECK ST_IsValid(observed_geom) | Observed source geometry in EPSG:4326. |
| `geometry_observation` | `geometry_role` | `text` | no | — | — | geometry_role | Registry Authority | `government-internal` | operator | current fact | — | Intended role of geometry. |
| `geometry_observation` | `capture_method` | `text` | no | — | — | capture_method | Registry Authority | `government-internal` | operator | current fact | — | Capture/source method. |
| `geometry_observation` | `horizontal_accuracy_m` | `numeric(10,2)` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Horizontal accuracy/uncertainty in meters. |
| `geometry_observation` | `source_record_id` | `text` | no | — | source_record.source_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source record carrying the observation. |
| `geometry_observation` | `evidence_object_id` | `text` | yes | — | evidence_object.evidence_object_id | — | Registry Authority | `government-internal` | operator | current fact | — | Supporting evidence object. |
| `geometry_observation` | `licence_id` | `text` | yes | — | licence.licence_id | — | Registry Authority | `government-internal` | operator | current fact | — | Licence governing the source geometry. |
| `geometry_observation` | `observed_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | observed time | — | Capture/observation time. |
| `geometry_observation` | `recorded_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded time. |
| `geometry_observation` | `classification` | `text` | no | 'restricted' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Observation classification. |
| `geometry_version` | `geometry_version_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Approved geometry version identity. |
| `geometry_version` | `subject_entity` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | CHECK subject_entity allowed for geometry_role | Approved subject table. |
| `geometry_version` | `subject_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Approved subject ID validated by subject_entity rule. |
| `geometry_version` | `geometry_role` | `text` | no | — | — | geometry_role | Registry Authority | `government-internal` | operator | current fact | — | Geometry role. |
| `geometry_version` | `geom` | `geometry(Geometry,4326)` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | CHECK ST_SRID(geom)=4326; CHECK ST_IsValid(geom); CHECK GeometryType(geom) allowed for geometry_role | Approved geometry. |
| `geometry_version` | `source_observation_id` | `text` | no | — | geometry_observation.geometry_observation_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source observation promoted to approved geometry. |
| `geometry_version` | `transformation_id` | `text` | yes | — | geometry_transformation.transformation_id | — | Registry Authority | `government-internal` | operator | current fact | — | Transformation lineage, if geometry was transformed/derived. |
| `geometry_version` | `validation_method` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Validation method or rule set. |
| `geometry_version` | `validated_by_actor_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Actor/system approving geometry. |
| `geometry_version` | `quality_state` | `text` | no | — | — | geometry_quality_state | Registry Authority | `government-internal` | operator | current fact | — | Geometry quality/lifecycle state. |
| `geometry_version` | `effective_from` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Geometry effective start. |
| `geometry_version` | `effective_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Geometry effective end. |
| `geometry_version` | `recorded_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded approval time. |
| `geometry_version` | `recorded_to` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | one recorded_to IS NULL per subject_entity, subject_id, geometry_role | Recorded closure time; NULL means current approved version for subject/role. |
| `geometry_version` | `superseded_by_geometry_version_id` | `text` | yes | — | geometry_version.geometry_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Later geometry version that supersedes this one. |
| `geometry_version` | `dispute_case_id` | `text` | yes | — | dispute_case.dispute_case_id | — | Registry Authority | `government-internal` | operator | current fact | — | Active/resolved dispute case if applicable. |
| `geometry_version` | `classification` | `text` | no | 'restricted' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Geometry classification. |
| `geometry_transformation` | `transformation_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Transformation identity. |
| `geometry_transformation` | `source_crs` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Original CRS. |
| `geometry_transformation` | `target_crs` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Target CRS; normally EPSG:4326. |
| `geometry_transformation` | `algorithm` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Transformation algorithm/library. |
| `geometry_transformation` | `algorithm_version` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Algorithm/library version. |
| `geometry_transformation` | `parameters_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Transformation parameters. |
| `geometry_transformation` | `performed_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Transformation time. |
| `geometry_quality_assessment` | `quality_assessment_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Assessment identity. |
| `geometry_quality_assessment` | `geometry_version_id` | `text` | no | — | geometry_version.geometry_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Assessed geometry version. |
| `geometry_quality_assessment` | `check_name` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Quality check name. |
| `geometry_quality_assessment` | `check_result` | `text` | no | — | — | geometry_quality_state | Registry Authority | `government-internal` | operator | current fact | — | Result value. |
| `geometry_quality_assessment` | `tolerance_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Tolerance/config used. |
| `geometry_quality_assessment` | `measured_value_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Measured results. |
| `geometry_quality_assessment` | `assessed_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Assessment time. |
| `geometry_quality_assessment` | `assessed_by_actor_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Actor/system running assessment. |
| `licence` | `licence_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Licence identity. |
| `licence` | `licence_name` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Licence name. |
| `licence` | `licence_uri` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Licence URL/reference. |
| `licence` | `usage_restriction` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Usage/publication restrictions. |
| `licence` | `classification` | `text` | no | 'government-internal' | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Licence metadata classification. |
| `source_authority` | `source_authority_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Authority identity. |
| `source_authority` | `authority_name` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Authority name. |
| `source_authority` | `authority_class` | `text` | no | — | — | source_authority_class | Registry Authority | `government-internal` | operator | current fact | — | Authority class. |
| `source_authority` | `legal_basis` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Legal/institutional basis if known. |
| `source_authority` | `status` | `text` | no | — | — | lifecycle_state | Registry Authority | `government-internal` | operator | current fact | — | Authority lifecycle. |
| `source_package` | `source_package_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Package identity. |
| `source_package` | `source_authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Package authority. |
| `source_package` | `package_name` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Package name. |
| `source_package` | `package_checksum` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Package checksum. |
| `source_package` | `licence_id` | `text` | yes | — | licence.licence_id | — | Registry Authority | `government-internal` | operator | current fact | — | Licence for package. |
| `source_package` | `loaded_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Load time. |
| `source_package` | `load_context` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Controlled load context. |
| `source_record` | `source_record_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Source record identity. |
| `source_record` | `source_package_id` | `text` | no | — | source_package.source_package_id | — | Registry Authority | `government-internal` | operator | current fact | — | Owning package. |
| `source_record` | `source_key` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Source system key. |
| `source_record` | `raw_payload_hash` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Hash of raw source payload. |
| `source_record` | `raw_payload_classification` | `text` | no | — | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Raw source classification. |
| `source_record` | `recorded_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded time. |
| `evidence_object` | `evidence_object_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Evidence identity. |
| `evidence_object` | `source_record_id` | `text` | no | — | source_record.source_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source record for evidence. |
| `evidence_object` | `storage_uri` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Object-storage URI/key/version. |
| `evidence_object` | `content_hash` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Content hash. |
| `evidence_object` | `media_type` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | MIME/media type. |
| `evidence_object` | `classification` | `text` | no | — | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Evidence classification. |
| `evidence_object` | `captured_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | observed time | — | Capture time where known. |
| `evidence_object` | `retention_state` | `text` | no | — | — | retention_state | Registry Authority | `government-internal` | operator | current fact | — | Retention/legal-hold state. |
| `decision_event` | `decision_event_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Decision event identity. |
| `decision_event` | `decision_type` | `text` | no | — | — | decision_type | Registry Authority | `government-internal` | operator | current fact | — | Decision type. |
| `decision_event` | `actor_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Actor/system making decision. |
| `decision_event` | `authority_id` | `text` | no | — | source_authority.source_authority_id | — | Registry Authority | `government-internal` | operator | current fact | — | Responsible authority. |
| `decision_event` | `reason_code` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Controlled or authority reason code. |
| `decision_event` | `details_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Supplemental non-authoritative details. |
| `decision_event` | `effective_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Decision effective time. |
| `decision_event` | `recorded_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Decision recorded time. |
| `location_record_assertion` | `assertion_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Assertion identity. |
| `location_record_assertion` | `location_record_version_id` | `text` | no | — | location_record_version.location_record_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Version containing asserted fact. |
| `location_record_assertion` | `target_entity` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Target entity for asserted field. |
| `location_record_assertion` | `target_field` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Target field name. |
| `location_record_assertion` | `value_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Typed value snapshot or redacted marker. |
| `location_record_assertion` | `source_record_id` | `text` | no | — | source_record.source_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source record supporting assertion. |
| `location_record_assertion` | `evidence_object_id` | `text` | yes | — | evidence_object.evidence_object_id | — | Registry Authority | `government-internal` | operator | current fact | — | Evidence object supporting assertion. |
| `location_record_assertion` | `decision_event_id` | `text` | no | — | decision_event.decision_event_id | — | Registry Authority | `government-internal` | operator | current fact | — | Decision authorizing assertion. |
| `location_record_assertion` | `classification` | `text` | no | — | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Assertion classification. |
| `intake_case` | `intake_case_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Intake case identity. |
| `intake_case` | `source_record_id` | `text` | no | — | source_record.source_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source submission/import record. |
| `intake_case` | `submitted_label` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Submitted address/location label. |
| `intake_case` | `intake_state` | `text` | no | — | — | intake_state | Registry Authority | `government-internal` | operator | current fact | — | Intake lifecycle. |
| `intake_case` | `provisional_code` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Offline/grid/provisional code, not canonical public code. |
| `intake_case` | `created_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Case creation time. |
| `intake_case` | `closed_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Case closure time. |
| `field_assignment` | `assignment_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Assignment identity. |
| `field_assignment` | `operational_area_id` | `text` | no | — | operational_area.operational_area_id | — | Registry Authority | `government-internal` | operator | current fact | — | Operational area for assignment. |
| `field_assignment` | `task_type` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Task type. |
| `field_assignment` | `team` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Team label or ID. |
| `field_assignment` | `priority` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Priority. |
| `field_assignment` | `assignment_state` | `text` | no | — | — | field_verification_state | Registry Authority | `government-internal` | operator | current fact | — | Assignment/verification state. |
| `field_assignment` | `created_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Assignment creation. |
| `field_assignment` | `closed_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Assignment closure. |
| `field_observation` | `field_observation_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Observation identity. |
| `field_observation` | `intake_case_id` | `text` | yes | — | intake_case.intake_case_id | — | Registry Authority | `government-internal` | operator | current fact | — | Related intake case. |
| `field_observation` | `assignment_id` | `text` | yes | — | field_assignment.assignment_id | — | Registry Authority | `government-internal` | operator | current fact | — | Related assignment. |
| `field_observation` | `observation_type` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Observed thing/type. |
| `field_observation` | `verification_state` | `text` | no | — | — | field_verification_state | Registry Authority | `government-internal` | operator | current fact | — | Verification lifecycle. |
| `field_observation` | `source_record_id` | `text` | no | — | source_record.source_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Source record for observation. |
| `field_observation` | `geometry_observation_id` | `text` | yes | — | geometry_observation.geometry_observation_id | — | Registry Authority | `government-internal` | operator | current fact | — | Captured geometry observation. |
| `field_observation` | `notes_classification` | `text` | no | — | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Classification of notes/details. |
| `field_observation` | `recorded_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Recorded time. |
| `correction_case` | `correction_case_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Correction case identity. |
| `correction_case` | `target_location_record_id` | `text` | yes | — | location_record.location_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Target record, if resolved. |
| `correction_case` | `target_public_code` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Submitted/target public code, if applicable. |
| `correction_case` | `correction_type` | `text` | no | — | — | correction_type | Registry Authority | `government-internal` | operator | current fact | — | Correction type. |
| `correction_case` | `case_state` | `text` | no | — | — | case_state | Registry Authority | `government-internal` | operator | current fact | — | Correction case state. |
| `correction_case` | `submitted_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Submission time. |
| `correction_case` | `resolved_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Resolution time. |
| `correction_case` | `resolution_event_id` | `text` | yes | — | decision_event.decision_event_id | — | Registry Authority | `government-internal` | operator | current fact | — | Decision resolving case. |
| `dispute_case` | `dispute_case_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Dispute identity. |
| `dispute_case` | `target_entity` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Target entity. |
| `dispute_case` | `target_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Target ID. |
| `dispute_case` | `dispute_type` | `text` | no | — | — | dispute_type | Registry Authority | `government-internal` | operator | current fact | — | Dispute type. |
| `dispute_case` | `case_state` | `text` | no | — | — | case_state | Registry Authority | `government-internal` | operator | current fact | — | Dispute state. |
| `dispute_case` | `opened_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Opened time. |
| `dispute_case` | `resolved_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Resolved time. |
| `dispute_case` | `resolution_event_id` | `text` | yes | — | decision_event.decision_event_id | — | Registry Authority | `government-internal` | operator | current fact | — | Resolution decision. |
| `publication_release` | `publication_release_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Release identity. |
| `publication_release` | `release_state` | `text` | no | — | — | publication_release_state | Registry Authority | `government-internal` | operator | current fact | — | Release lifecycle. |
| `publication_release` | `authority_reference` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Named approval/authority reference. |
| `publication_release` | `projection_type` | `text` | no | — | — | projection_type | Registry Authority | `government-internal` | operator | current fact | — | Projection audience/type. |
| `publication_release` | `effective_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | effective time | — | Release effective time. |
| `publication_release` | `recorded_at` | `timestamptz` | no | — | — | — | Registry Authority | `government-internal` | operator | recorded time | — | Release recorded time. |
| `publication_release` | `immutable_manifest_hash` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Hash of full release manifest. |
| `publication_release` | `manifest_storage_uri` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Durable complete projection/manifest artifact reference. |
| `publication_release` | `created_by_actor_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Actor/system creating release. |
| `publication_release_item` | `publication_release_item_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Release item identity. |
| `publication_release_item` | `publication_release_id` | `text` | no | — | publication_release.publication_release_id | — | Registry Authority | `government-internal` | operator | current fact | — | Release header. |
| `publication_release_item` | `location_record_id` | `text` | no | — | location_record.location_record_id | — | Registry Authority | `government-internal` | operator | current fact | — | Canonical record identity. |
| `publication_release_item` | `location_record_version_id` | `text` | no | — | location_record_version.location_record_version_id | — | Registry Authority | `government-internal` | operator | current fact | — | Exact version released. |
| `publication_release_item` | `public_code_alias_id` | `text` | no | — | public_code_alias.public_code_alias_id | — | Registry Authority | `government-internal` | operator | current fact | — | Exact alias released. |
| `publication_release_item` | `projection_payload_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Complete immutable public/partner/export payload snapshot. |
| `publication_release_item` | `projection_payload_hash` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Hash of immutable payload. |
| `publication_release_item` | `projection_state` | `text` | no | — | — | publication_item_state | Registry Authority | `government-internal` | operator | current fact | — | Release item state. |
| `publication_release_item` | `published_label` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Exact label released. |
| `publication_release_item` | `published_geometry_policy` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Geometry precision/generalization policy for release. |
| `partner_projection` | `partner_projection_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Projection identity. |
| `partner_projection` | `publication_release_item_id` | `text` | no | — | publication_release_item.publication_release_item_id | — | Registry Authority | `government-internal` | operator | current fact | — | Release item being projected. |
| `partner_projection` | `partner_scope` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Partner/institution/use-case scope. |
| `partner_projection` | `response_field_set` | `jsonb` | no | '[]'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Allowlisted response fields. |
| `partner_projection` | `classification` | `text` | no | — | — | classification | Registry Authority | `government-internal` | operator | current fact | — | Projection classification. |
| `partner_projection` | `expires_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Projection expiry. |
| `migration_exception` | `migration_exception_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Exception identity. |
| `migration_exception` | `batch_id` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Migration/backfill batch. |
| `migration_exception` | `source_table` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Source table. |
| `migration_exception` | `source_field` | `text` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Source field. |
| `migration_exception` | `source_key` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Source record key. |
| `migration_exception` | `exception_type` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Exception type. |
| `migration_exception` | `severity` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Severity. |
| `migration_exception` | `details_json` | `jsonb` | no | '{}'::jsonb | — | — | Registry Authority | `government-internal` | operator | current fact | — | Details. |
| `migration_exception` | `owner` | `text` | no | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Responsible owner. |
| `migration_exception` | `created_at` | `timestamptz` | no | now() | — | — | Registry Authority | `government-internal` | operator | current fact | — | Exception creation. |
| `migration_exception` | `resolved_at` | `timestamptz` | yes | — | — | — | Registry Authority | `government-internal` | operator | current fact | — | Resolution time. |
