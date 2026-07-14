# Geometry, Provenance, and Quality Model

Observation and approval are separate. `geometry_observation` stores raw/candidate evidence; `geometry_version` stores approved canonical geometry with role-to-subject/type validation, source observation, optional transformation, licence, quality, dispute, supersession, and bitemporal recorded/effective intervals.

## Role-to-subject/type rules

| Geometry role | Allowed subjects | Allowed PostGIS geometry types | Integrity strategy | Current rule |
|---|---|---|---|---|
| `admin-boundary` | `administrative_unit_version` | Polygon, MultiPolygon | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `operational-boundary` | `operational_area` | Polygon, MultiPolygon | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `road-centerline` | `road_segment` | LineString, MultiLineString | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `building-footprint` | `building` | Polygon, MultiPolygon | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `building-point` | `building` | Point | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `entrance-point` | `entrance` | Point | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `location-point` | `location_record_version` | Point | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `landmark-point` | `landmark` | Point | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `landmark-area` | `landmark` | Polygon, MultiPolygon | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |
| `parcel-boundary` | `parcel_reference` | Polygon, MultiPolygon | validated by checker and WO-002B trigger/check | one open recorded interval per subject/role |

## Boundary handling

Administrative boundaries are approved `geometry_version` rows with role `admin-boundary` against `administrative_unit_version`. Operational boundaries are approved `geometry_version` rows with role `operational-boundary` against `operational_area`. Both retain observations, transformations, licence lineage, quality assessments, disputes, and supersession.
