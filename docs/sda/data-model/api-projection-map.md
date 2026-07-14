# Current OpenAPI Operation and Response Projection Mapping

## Projection rule

No API contract changes are made in NLI-WO-002. This document maps current operations and response classes to target projections for WO-002B compatibility.

| Current operation/route group | Current source fields | Target projection | Compatibility/breaking impact |
|---|---|---|---|
| Public address-code lookup | `address_records.address_code/status/publication_state/address_label/latitude/longitude/geom`, legacy `addresses.public_code`, geotag `grid_code` fallback | `public_code_alias` + immutable `publication_release_item` for exact `location_record_version` | Fallbacks retained until canonical backfill and release parity pass. |
| Public verification lookup | legacy `addresses.formatted/public_code/publication_state/verification_status` | public verification projection from release item | Breaking only after endpoint migration work order. |
| Public geotag submission/tracking | `citizen_geotag_submissions.*` | `intake_case` + candidate tracking projection | Must not expose canonical fields before promotion/publication. |
| Operator address-record search/detail | `address_records.*`, `address_record_events.*`, `record_bundle` | operator canonical case-file projection: location record, version, assertions, geometry, events, source/evidence | Compatibility adapter must reproduce current fields. |
| Nearby spatial query | `address_records.geom/lat/lon/status/publication_state` | geometry_version current location-point over approved geometry | Public nearby requires release policy; operator nearby can include internal states. |
| Signage/export | `address_records` filtered by publication/status, publication packs | `publication_release_item` projection | Must target exact versions/aliases and immutable payload hash. |
| Publication packs | `publication_packs`, `publication_pack_addresses`, legacy `addresses` | `publication_release` + `publication_release_item` | Legacy address pack items converted to canonical release items. |
| Field assignments/submissions | `field_assignments`, `field_submissions` | `field_assignment`, `field_observation`, `geometry_observation`, evidence | Operational API remains protected. |
| Imports/reference loads | `import_jobs`, `import_rows`, reference load ledgers | `source_package`, `source_record` | Raw lineage preserved. |

## Response-field disposition

Public responses may include only released public code, released label, approved public status, and approved/generalized geometry per release item. Operator responses may include internal lifecycle, source/evidence metadata, quality, correction/dispute, and audit events subject to role. Partner/export responses use explicit release item `projection_type` and `partner_projection.response_field_set`.
