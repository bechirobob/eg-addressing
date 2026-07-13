# SDA Standard — GIS and Location Data

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** coordinates, geometries, maps, geocoding, administrative geography, spatial evidence, and national location identifiers

## 1. Spatial authority classes

Every geometry MUST be classified as one of:

- authoritative administrative geometry;
- authoritative registry geometry;
- verified field observation;
- unverified field observation;
- citizen-submitted evidence;
- imported/source geometry pending validation;
- map/geocoder-derived suggestion;
- generalized public geometry.

The class MUST be stored or deterministically derivable. A point displayed on a map is not automatically official.

## 2. Geometry provenance

Every material geometry or coordinate set MUST record:

- source organization or system;
- source record/reference;
- capture or effective time;
- capture method and device/source where applicable;
- actor or service identity;
- original CRS and transformations;
- stated or measured accuracy/quality;
- validation state and validating authority;
- version and supersession relationship;
- licensing/usage restrictions for external data.

Derived geometry MUST preserve lineage to its inputs and algorithm/version.

## 3. Coordinate reference systems

- WGS84 (`EPSG:4326`) is the exchange and API baseline unless a contract explicitly states otherwise.
- Latitude/longitude order MUST be unambiguous in contracts and tests.
- Database geometry/geography columns MUST enforce the expected SRID.
- Metric distance, area, buffering, and topology work MUST use a documented appropriate projected CRS or justified geodesic operation.
- Transformations MUST use maintained spatial libraries and be reproducible.
- Coordinates MUST be range validated; plausible-but-wrong national location checks SHOULD also be applied.

## 4. Canonical geometry model

The target model distinguishes at minimum:

- administrative boundaries as versioned polygons/multipolygons;
- roads/access networks as lines/multilines with segment identity;
- parcels as polygons where authorized;
- buildings as footprints or approved representative geometry;
- entrances/access points as points linked to buildings/roads;
- address/location points as explicit addressable access or delivery points;
- landmarks as typed point/area references;
- zones/campaign areas as operational geometry, not administrative authority.

A free-form JSON evidence field MUST NOT be the only authoritative geometry representation for a canonical entity.

## 5. Geometry lifecycle

Spatial evidence moves through explicit stages:

```text
observed/submitted → quality checked → reviewed → accepted canonical
→ corrected/superseded/disputed/retired
```

Promotion to canonical geometry MUST record:

- source evidence;
- reviewer and authority scope;
- quality result;
- accepted geometry version;
- decision time and reason;
- affected records or codes.

Official geometry is not overwritten silently. Corrections create version/event history and preserve prior effective state.

## 6. Accuracy and quality

Accuracy MUST NOT be inferred solely from decimal precision. Quality dimensions SHOULD include:

- horizontal/vertical accuracy where relevant;
- device-reported uncertainty;
- capture age;
- observation count;
- source authority;
- geometry completeness;
- topology result;
- consistency with administrative and registry context;
- reviewer confidence and unresolved discrepancy.

Quality thresholds MUST be defined by use case. Emergency dispatch, property, signage, statistics, and public wayfinding may require different standards.

## 7. Topology and consistency

Validation rules MUST be defined for each geometry class. Examples include:

- valid and non-self-intersecting polygons;
- expected containment within administrative units;
- no unintended overlaps/gaps for boundary datasets where coverage is required;
- road connectivity and segment consistency;
- building/entrance/address relationships;
- coordinate uniqueness and duplicate proximity review;
- geometries within reasonable national bounds;
- version effective-date consistency.

Automatic checks produce evidence and flags; they do not replace authorized review where institutional judgment is required.

## 8. Administrative geography

- Administrative units MUST use stable codes and explicit parent relationships.
- Names, aliases, language variants, legal source, effective dates, and status MUST be recorded.
- Boundary geometry and administrative identity are related but distinct; a unit may exist while a surveyed/approved boundary remains pending.
- External map boundaries MUST NOT be promoted to official administrative boundaries without source authority and approval.
- Boundary changes require impact analysis on scopes, records, statistics, integrations, and historical queries.

## 9. Address and national location identifiers

A national address/location code standard MUST define before national issuance:

- purpose and object represented;
- syntax and normalization;
- allocation authority;
- uniqueness and collision handling;
- check/error-detection behavior where used;
- relationship to geography and the consequences of boundary change;
- stability when names, roads, or occupancy change;
- public/internal identifier separation;
- correction, supersession, retirement, and non-reuse;
- privacy and enumeration risk;
- human readability, signage, transcription, and accessibility;
- compatibility and versioning.

No implementation convenience may silently become the national identifier standard.

## 10. Geocoding and external map services

- Geocoder and map results are suggestions unless the source is formally authoritative for the field concerned.
- External requests MUST minimize personal/sensitive data and comply with approved terms, attribution, privacy, caching, and rate limits.
- Production use requires an availability and continuity plan, including timeout, graceful degradation, and operator review.
- Source, response time, query precision, result, confidence, and human decision SHOULD be recorded when a suggestion materially affects a case.
- A third-party outage MUST NOT prevent storage of valid field evidence or cause false publication.

## 11. Public map projections

- Public maps MUST expose only approved data classes and appropriate precision.
- Sensitive sites, identity-linked locations, unpublished records, and evidence locations require explicit projection/redaction policy.
- Generalization or coordinate reduction MUST be documented and reproducible.
- Map labels MUST distinguish official names from local references and pending suggestions.

## 12. Spatial performance

- Canonical spatial columns require appropriate GiST/SP-GiST indexes and query-plan evidence.
- Bounding-box, nearest-neighbor, containment, and distance queries MUST state geometry/geography semantics.
- National-scale tile or feature delivery SHOULD use a dedicated read model or tile service when measured load justifies it; it MUST NOT bypass authorization or become authoritative.
- Large spatial imports and transformations MUST be staged, resumable, and validated.

## 13. Required evidence

A spatially material change MUST include:

- data-source and licensing record;
- CRS and transformation description;
- geometry class and lifecycle effect;
- representative valid, invalid, boundary, and duplicate tests;
- database constraint and spatial-index evidence;
- query plans and scale sample where relevant;
- map/workflow screenshots with source/confidence labels;
- public-precision/privacy review;
- rollback/supersession approach;
- unresolved authority or boundary RFIs.
