# S09 — GIS, Evidence, and Publication

## Invoke when

- coordinates, geometry, CRS, maps, geocoding, boundaries, roads, buildings, entrances, or spatial queries change;
- evidence files, hashes, custody, retention, or access change;
- canonical geometry is promoted from observations;
- public lookup, publication releases, certificates, signage, or partner projections change.

## Required inputs

- GIS/location-data and audit/evidence standards;
- geometry role and subject model;
- source/evidence and quality model;
- publication ADR and authority state;
- current public/operator projections;
- external map/geocoder terms and continuity assumptions.

## Procedure

### 1. Classify spatial authority

Every geometry must be one of:

- authoritative administrative;
- authoritative registry;
- verified field observation;
- unverified field observation;
- citizen submission;
- imported candidate;
- external map/geocoder suggestion;
- generalized public geometry.

### 2. Record provenance and quality

For each geometry record:

- subject and geometry role;
- geometry type and CRS;
- source organization/system and source record;
- capture method, actor/device, capture time;
- accuracy/uncertainty and quality results;
- evidence objects;
- transformation and licence lineage;
- validating actor, institution, scope, and decision;
- effective/recorded intervals;
- dispute and supersession chain.

### 3. Enforce observation-to-canonical promotion

Promotion requires:

- existing compatible subject;
- permitted role and geometry type;
- valid SRID, dimensionality, and geometry;
- accepted quality result;
- evidence/source linkage;
- authorized permission and scope;
- recorded decision event;
- same-subject/same-role supersession consistency.

Technical validity alone cannot grant official authority.

### 4. Enforce spatial relationships

Test and constrain:

- administrative containment;
- boundary version intervals;
- building/entrance/address relationships;
- road/segment connectivity where required;
- duplicate proximity review;
- one-current geometry per subject/role;
- no-self, reciprocal, same-owner, and acyclic supersession;
- public precision/generalization rules.

### 5. Govern evidence objects

Every object requires metadata for:

- stable evidence ID;
- object key/version;
- media type, size, and content hash;
- source, uploader/collector, institution, and scope;
- classification;
- related case/record;
- retention, legal hold, disposition;
- access and decision history.

Evidence replacement creates a new version; it is not an invisible overwrite.

### 6. Protect publication authority

Keep these states distinct:

```text
candidate/evidence → reviewed → registry-ready
→ publication proposed → approved → published
→ suspended/withdrawn/corrected/superseded
```

Publication requires an exact immutable record version, alias, approved projection payload, manifest/hash, authority decision, effective time, and revocation path.

Registry-ready does not authorize public release, certificates, signage, or partner distribution.

### 7. Validate failure behavior

Negative tests must cover:

- wrong subject type;
- wrong geometry type/role;
- invalid SRID or dimensionality;
- invalid geometry;
- missing evidence or decision;
- unauthorized promotion;
- duplicate current geometry;
- cross-subject supersession;
- supersession cycle;
- publication without authority/manifest;
- public projection of restricted or unpublished data.

## Outputs

- spatial authority/provenance model;
- geometry and evidence constraints/tests;
- publication decision and release evidence;
- public/generalized projection rules;
- continuity/licensing notes for external services.

## Stop or RFI conditions

Stop when:

- administrative boundary or public-code authority is unknown;
- an external map is being treated as official without approval;
- a geometry can be promoted without actor/decision/evidence;
- a public precision rule is missing;
- an evidence retention/legal-hold decision is unresolved;
- publication authority is unnamed;
- signage/certificate generation would consume registry-ready rather than published state.

## Evidence gate

Before review:

- every role-to-subject/type rule is executable;
- positive and negative geometry cases execute;
- evidence chain can be reconstructed;
- release references exact immutable versions and payloads;
- public projections are allowlisted and publication-gated;
- external dependencies have privacy, licence, rate, timeout, and fallback treatment.

## Anti-patterns

- Inferring accuracy from decimal precision.
- Using generic `Geometry` without role/type constraints.
- Storing a promotion permission string but not enforcing actor/decision authority.
- Treating a pin shown on a map as official geometry.
- Directly exposing object-storage keys or evidence URLs.
- Publishing from a mutable record instead of an immutable release snapshot.
