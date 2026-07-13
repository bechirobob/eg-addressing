# Geometry, Provenance, and Quality Model

**Status:** Draft for SDA review

## 1. CRS and storage

- Canonical CRS: EPSG:4326 for stored coordinates and geometry exchange unless a later ADR authorizes another storage CRS.
- PostGIS remains the target spatial system of record per ADR-002.
- Public map projections may transform for display but must not become stored canonical values.

## 2. Geometry roles

| Role | Geometry type | Subject examples |
|---|---|---|
| `location-point` | Point/geography | canonical location record, entrance, service point. |
| `access-point` | Point | entrance/access. |
| `building-footprint` | Polygon/MultiPolygon | building. |
| `road-centerline` | LineString/MultiLineString | road segment. |
| `admin-boundary` | MultiPolygon | administrative unit boundary version. |
| `operational-area-boundary` | Polygon/MultiPolygon | routing/pilot area. |
| `landmark-point` | Point/Polygon | landmark depending on source. |

## 3. Provenance fields

Each geometry version records: source class, source package/record, capture method, actor/system, captured_at, recorded_at, accuracy, device/source notes, validation method, validation actor, authority status, and classification.

## 4. Quality validation

Minimum validations for future implementation:

- CRS known and allowed.
- Coordinates within valid WGS84 ranges.
- Geometry type matches entity role.
- Geometry validity check passes or repair is documented.
- Point lies within expected administrative/operational context or exception is recorded.
- Road segment length is positive and not implausible.
- Boundary polygons are valid and non-self-intersecting.
- Current canonical geometry has one current version per subject/role.

## 5. Public geometry exposure

Precise citizen, identity, evidence, and unpublished geometry is restricted. Public projection can expose precise geometry only when publication authority allows it. Otherwise expose generalized area, redacted coordinates, or status-only response.

## 6. Current-to-target notes

- `address_records.geom` maps to canonical `geometry_version` for `location-point`.
- `address_records.latitude/longitude` remain source-compatible WGS84 fields during transition.
- `address_points` maps to legacy source geometry for old `addresses` records.
- `field_submissions.spatial_evidence` maps to evidence geometry observations, not canonical geometry.
- `citizen_geotag_submissions.latitude/longitude` maps to candidate geometry observation.
