# Skill 10 — GIS and Geometry Governance

## Use when

Use for coordinates, geometry, administrative boundaries, roads, buildings, entrances, address points, CRS, geocoding, map suggestions, spatial imports, quality, or public maps.

## Objective

Keep observed, suggested, validated, canonical, disputed, and public geometry distinct and attributable, with enforceable spatial integrity and institutional promotion authority.

## Procedure

1. Classify the geometry:
   - authoritative administrative;
   - authoritative registry;
   - verified field observation;
   - unverified field/citizen evidence;
   - imported provisional;
   - external map/geocoder suggestion;
   - generalized public projection.
2. Define subject entity, geometry role, allowed PostGIS geometry type, CRS/SRID, dimensionality, and precision.
3. Record provenance: source, source record, capture method/device/actor, capture/effective time, original CRS, transformation, licence, accuracy/uncertainty, and classification.
4. Separate geometry observations from approved geometry versions.
5. Define quality checks and outcomes separately from lifecycle states.
6. Define promotion prerequisites:
   - matching subject and role;
   - accepted evidence/observation;
   - quality result;
   - authorized permission/actor/institution/scope;
   - decision/audit event;
   - effective and recorded time.
7. Define one-current, overlap, supersession, reciprocal/cycle, dispute, and retirement behavior.
8. Implement or specify enforceable constraints/triggers for:
   - subject existence/type;
   - role-to-subject compatibility;
   - role-to-geometry-type compatibility;
   - SRID, validity, dimensions;
   - one-current/effective interval;
   - same-subject/role supersession;
   - promotion authority.
9. Test positive examples and real negative cases for every geometry family.
10. Define public precision/generalization and non-map alternatives.
11. Record external map/geocoder licensing, privacy, availability, rate limits, cache, and fallback.

## Required evidence

- Role/subject/type matrix
- Source/provenance fields
- PostGIS constraints and spatial indexes
- Quality/promotion state model
- Positive and negative geometry tests
- Query plans for material spatial access
- Public precision/privacy review
- Supersession/dispute examples
- External-source authority/licensing record

## Stop and escalate when

- A boundary or geometry source is not institutionally authoritative.
- A public map would expose restricted precision.
- A CRS choice affects legal/metric claims.
- A citizen/map suggestion would become canonical automatically.
- Parcel geometry might imply ownership/title authority.

## Anti-patterns

- Treating decimal precision as accuracy.
- Using generic `Geometry` without role/type rules.
- Storing SRID as text without checking `ST_SRID`.
- Promoting geometry based only on a quality-state string.
- Checking self-supersession but not multi-node cycles.
- Allowing a valid subject registry row to stand for the wrong native entity.
- Calling external geocoder output official.
