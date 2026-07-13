# Canonical Data Dictionary

**Status:** Draft for SDA review

## Field metadata standard

Each target field must carry: meaning, type family, nullability intent, classification, source authority, lifecycle, and projection eligibility.

## Administrative geography

| Entity.field | Meaning | Type | Required | Classification | Source authority | Projection |
|---|---|---|---|---|---|---|
| `country.country_id` | Stable internal country identifier. | text/uuid | yes | Government internal | Registry/system | Operator/partner safe. |
| `country.iso2_code` | ISO country code. | text | yes | Public | External standard | Public safe. |
| `administrative_unit.admin_unit_id` | Stable internal admin-unit ID. | text/uuid | yes | Government internal | Registry/system | Operator/partner safe. |
| `administrative_unit.parent_admin_unit_id` | Parent hierarchy link. | text/uuid FK | nullable for root | Government internal | GIS/admin authority | Public if approved. |
| `administrative_unit.admin_level` | Controlled level such as province/district/municipality/locality. | controlled text | yes | Public when approved | SDA/GIS authority | Public when approved. |
| `administrative_unit.official_code` | Legal/reference code. | text | yes when authority exists | Public when approved | Government/GIS authority | Public when approved. |
| `administrative_unit.status` | active/proposed/retired/superseded/disputed. | controlled text | yes | Government internal | GIS/admin authority | Public only for approved units. |
| `administrative_unit_name.name_es` | Official Spanish name, accents preserved. | text | yes | Public when approved | Government/GIS authority | Public. |
| `administrative_unit_name.name_en` | English display name when approved. | text | nullable | Public when approved | Translation authority | Public/partner. |
| `administrative_boundary_version.geom` | Boundary geometry. | geometry multipolygon | nullable until sourced | Restricted/Gov internal until approved | GIS authority | Generalized public boundary only after approval. |

## Operational areas

| Entity.field | Meaning | Type | Required | Classification | Source authority | Projection |
|---|---|---|---|---|---|---|
| `operational_area.operational_area_id` | Internal service/routing/work area ID. | text/uuid | yes | Government internal | Programme/operator | Operator only by default. |
| `operational_area.area_type` | routing_area, pilot_area, campaign_area, service_zone. | controlled text | yes | Government internal | SDA/operator | Operator. |
| `operational_area.purpose` | Why area exists. | text | yes | Government internal | Operator | Operator. |
| `operational_area.status` | draft/active/paused/retired. | controlled text | yes | Government internal | Operator | Operator. |

## Addressable objects

| Entity.field | Meaning | Type | Required | Classification | Source authority | Projection |
|---|---|---|---|---|---|---|
| `road.road_id` | Stable internal road identity. | text/uuid | yes | Government internal | Registry | Public only after name/geometry approval. |
| `road_segment.road_segment_id` | Stable road segment identity. | text/uuid | yes | Government internal | Registry/GIS | Operator/partner. |
| `road_name.name_text` | Road name text. | text | yes | Public when approved | Registry/name authority | Public if official/current. |
| `road_name.name_status` | candidate/under_review/official/retired/disputed. | controlled text | yes | Government internal | Registry/name authority | Public only official/current. |
| `landmark.landmark_id` | Stable landmark/place ID. | text/uuid | yes | Government internal | Registry | Public if approved. |
| `parcel_reference.external_parcel_id` | External cadastre reference if available. | text | nullable | Restricted until authority approves | Cadastre authority | Not public by default. |
| `building.building_id` | Stable building ID. | text/uuid | yes | Government internal | Registry/field evidence | Public only through record projection. |
| `entrance.entrance_id` | Entrance/access point ID. | text/uuid | nullable | Government internal | Field/GIS evidence | Public if required for addressing. |
| `unit.unit_id` | Unit/sub-address ID. | text/uuid | nullable | Restricted/Gov internal | Registry/operator | Public only when non-sensitive and approved. |
| `non_building_object.object_id` | Stable ID for addressable non-building object. | text/uuid | yes | Government internal | Registry | Public if approved. |

## Canonical location record

| Entity.field | Meaning | Type | Required | Classification | Source authority | Projection |
|---|---|---|---|---|---|---|
| `location_record.location_record_id` | Sole canonical record ID. | text/uuid | yes | Government internal | Registry/system | Not directly public unless allowed. |
| `location_record.lifecycle_state` | Candidate/canonical lifecycle. | controlled text | yes | Government internal | Registry authority | Operator; simplified public status. |
| `location_record.publication_state` | Public release state. | controlled text | yes | Government internal | Publication authority | Public only if released. |
| `location_record.current_version_id` | Current version pointer. | text/uuid FK | yes after first approval | Government internal | Registry/system | No. |
| `location_record_version.label_es` | Canonical Spanish display label. | text | yes | Public after release | Registry | Public if released. |
| `location_record_version.label_en` | English display label. | text | nullable | Public after release | Registry/translation | Public if released. |
| `location_record_version.admin_unit_id` | Administrative unit context. | text/uuid FK | yes when known | Government internal | GIS/admin authority | Public/partner if approved. |
| `location_record_version.operational_area_id` | Operational routing area. | text/uuid FK | nullable | Government internal | Operator | Operator only. |
| `location_record_version.addressable_object_refs` | References to building/unit/road/landmark/object context. | relational links | context-dependent | Government internal/restricted | Registry | Redacted projection. |

## Geometry and provenance

| Entity.field | Meaning | Type | Required | Classification | Source authority | Projection |
|---|---|---|---|---|---|---|
| `geometry_version.geom` | Geometry payload. | PostGIS geometry/geography | yes for current geometry | Restricted until approved | GIS/field/source | Generalized/point public only if approved. |
| `geometry_version.crs` | Coordinate reference system. | text | yes | Public | GIS authority | Public. |
| `geometry_version.capture_method` | browser_gps, field_gps, digitized, imported, derived, manual_estimate. | controlled text | yes | Government internal | Source/GIS | Operator. |
| `geometry_version.accuracy_meters` | Positional accuracy where known. | numeric | nullable | Government internal/restricted | Source/GIS | Public only if approved. |
| `geometry_version.quality_state` | unvalidated/valid/needs_review/rejected/superseded/disputed. | controlled text | yes | Government internal | GIS authority | Operator. |
| `source_record.source_record_id` | Raw source row/object identity. | text/uuid | yes | Classification inherited | Source package | Operator/audit. |
| `evidence_object.content_hash` | Evidence object hash. | text | yes | Restricted | Object/evidence store | Operator/audit. |

## Publication

| Entity.field | Meaning | Type | Required | Classification | Source authority | Projection |
|---|---|---|---|---|---|---|
| `public_code_alias.public_code` | Public lookup code. | text | yes when issued | Public after release | Registry/publication authority | Public. |
| `public_code_alias.code_state` | reserved/internal/active/retired/superseded/revoked. | controlled text | yes | Government internal | Registry | Public simplified. |
| `publication_release.release_id` | Publication approval package. | text/uuid | yes | Government internal | Publication authority | Public metadata if approved. |
| `publication_release.authority_reference` | Approving authority/reference. | text | yes for release | Government internal/restricted | Publication authority | Redacted public. |
| `publication_release_item.projection_type` | public_lookup, certificate, signage, partner_api, export. | controlled text | yes | Government internal | Publication authority | Projection-specific. |
