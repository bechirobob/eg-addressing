# NLI-WO-002 — Canonical National Location Data Model

**Status:** ISSUED — DESIGN AUTHORITY PHASE  
**Priority:** P0 production blocker  
**Issued:** 2026-07-13  
**Authority:** System Design Authority  
**Implementation branch:** `nli/wo-002-canonical-location-model`  
**Primary risk:** SDA-RISK-004  
**Related risks:** SDA-RISK-007 and SDA-RISK-014  
**Related decisions:** ADR-001, ADR-002, ADR-003, ADR-004  
**Readiness boundary:** architecture and data-model authority only; this work order does not authorize executable schema migrations, national production, official publication, or public identifier issuance

## 1. Objective

Establish the single authoritative conceptual and logical data model for the Equatorial Guinea National Location Infrastructure (NLI), with the national addressing service as its first implementation.

The accepted outcome must eliminate ambiguity about:

- which entity is the canonical address/location record;
- how administrative geography differs from operational rollout areas;
- how roads, landmarks, parcels, buildings, entrances, units, and addressable objects relate;
- how observations and evidence are promoted into authoritative records;
- how internal identifiers differ from public codes;
- how records are versioned, corrected, superseded, disputed, retired, and published;
- how geometry source, accuracy, authority, and history are represented;
- how current operational tables converge without data loss or a second source of truth.

This is the **design-authority phase**. It must produce accepted ADRs, an ER model, data dictionary, controlled vocabularies, and a migration-convergence plan before executable schema implementation begins.

A later implementation directive, expected to be `NLI-WO-002B`, will authorize migrations and application convergence against the accepted model.

## 2. Current condition

At the accepted NLI-WO-001 baseline, the operational schema is reproducible through migrations `000–007` and includes:

- `provinces` and hierarchical `admin_units`;
- `territories` used for rollout/routing as well as location context;
- `roads`, `buildings`, `addresses`, and `address_points`;
- citizen geotag submissions;
- canonical-looking `address_records` and `address_record_events`;
- field assignments and submissions;
- corrections, imports, publication packs, users, sessions, and audit logs;
- PostGIS geometry for canonical address records and structured spatial evidence elsewhere.

Material model ambiguity remains:

- `addresses` and `address_records` both represent official-location concepts;
- `territories` mixes operational campaign/routing concepts with geographic context;
- identifiers are primarily free-form text and public-code semantics are not formally separated from internal identity;
- several lifecycle, source, publication, verification, and quality values are plain text with overlapping meanings;
- official geometry, observed geometry, citizen coordinates, and map-derived suggestions are not governed by one provenance model;
- buildings have no formal entrance/access-point or unit model;
- historical changes are represented inconsistently across events, mutable rows, and JSON bundles;
- the current administrative reference package is technically controlled but institutionally provisional.

A proposal schema under `docs/source-proposals/schema.sql` contains useful concepts—typed administrative levels, UUIDs, landmarks, parcels, building units, address versions, status events, scoped roles, agency clients, and richer audit—but it is a proposal, not the accepted model and must not be adopted wholesale.

## 3. Mandatory reading

Before modelling:

- repository `AGENTS.md`;
- `docs/sda/README.md`;
- `docs/sda/charter.md`;
- `docs/sda/architecture-baseline.md`;
- `docs/sda/target-reference-architecture.md`;
- `docs/sda/risk-register.md`;
- `docs/sda/work-orders/NLI-WO-001-closeout.md`;
- `docs/sda/reviews/NLI-WO-001-review-04.md`;
- `docs/sda/adrs/ADR-001-modular-monolith.md`;
- `docs/sda/adrs/ADR-002-postgresql-postgis-system-of-record.md`;
- `docs/sda/adrs/ADR-003-migration-only-schema-lifecycle.md`;
- `docs/sda/adrs/ADR-004-registry-ready-is-not-published.md`;
- `docs/sda/standards/data-and-migrations.md`;
- `docs/sda/standards/gis-and-location-data.md`;
- `docs/sda/standards/api-design.md`;
- `docs/sda/standards/audit-and-evidence.md`;
- `docs/sda/standards/security.md`;
- `docs/sda/standards/documentation-and-records.md`;
- `docs/source-proposals/schema.sql` as non-authoritative design input;
- all migrations `000–007` and the current API persistence/query behavior.

Use `docs/sda/templates/implementation-plan.md` for the modelling plan. In that template, “implementation” means controlled model/design production unless this work order explicitly authorizes code.

## 4. Work-order structure

### Phase A — Current-state model audit

Produce an evidence-based inventory of every current table, column, key, constraint, index, geometry, controlled/free-text value, public/API projection, writer, reader, and lifecycle responsibility.

### Phase B — Canonical model proposal

Produce the conceptual model, logical ERD, data dictionary, state machines, source/authority model, identifier strategy, geometry/provenance model, and ADRs.

### Phase C — Convergence design

Produce the physical-schema proposal, current-to-target mapping, compatibility strategy, data-quality gates, transition sequence, and implementation work breakdown.

No executable migration or production table change is authorized in any phase of this work order.

## 5. In scope

### 5.1 Current-state data inventory

Document:

- every operational table and relationship;
- authoritative, derived, evidence, cache/queue, fixture, and publication roles;
- every known writer and reader;
- current internal IDs, public codes, natural keys, and collision rules;
- lifecycle/status fields and their actual meanings;
- geometry fields, CRS, source, and promotion behavior;
- JSON fields and whether they contain canonical, evidence, derived, or ungoverned data;
- retention, correction, archive, supersession, and delete behavior;
- API/public/operator/export projections;
- current data-quality constraints and missing constraints;
- current duplication between `addresses`, `address_points`, `address_records`, submission records, and publication records.

### 5.2 Administrative geography

Define the model for:

- country;
- province;
- district;
- municipality;
- any legally recognized lower administrative level;
- names, aliases, language variants, official codes, effective dates, and status;
- parent/child hierarchy and historical reorganization;
- administrative identity separately from boundary geometry;
- authoritative boundary versions, provisional geometry, disputed geometry, and missing geometry;
- relationship between institutional scope and geographic scope.

The model must explicitly separate administrative units from operational zones, campaigns, rollout areas, enumerator assignments, or intake-routing territories.

### 5.3 Operational geography

Define operational areas used for:

- field campaigns;
- rollout sequencing;
- intake routing;
- work assignment;
- service coverage;
- temporary incident or project zones.

Operational areas must have their own authority, purpose, effective period, geometry/source, and relationship to administrative units. They must not silently become official administrative geography.

### 5.4 Addressable-object model

Define the canonical semantics and cardinality of:

- roads and road segments;
- alternative/local/provisional road names;
- landmarks;
- parcels or external parcel references where authorized;
- buildings and building footprints/representative points;
- entrances/access points;
- building units and sub-addresses;
- non-building addressable objects;
- addresses/location records;
- address/location points;
- public address/location codes.

The model must support urban, peri-urban, rural, informal, landmark-based, compound, multi-unit, and no-formal-road cases without forcing false data.

Parcel modelling must not claim ownership or land-title authority. Where parcel data is not legally available, the model must support an optional externally governed reference.

### 5.5 Canonical record versus evidence

Define one authoritative canonical location/address record and explicitly distinguish it from:

- citizen submissions;
- field observations;
- imported candidate records;
- map/geocoder suggestions;
- duplicate candidates;
- evidence objects;
- verification events;
- publication projections;
- analytical/read models.

There must not be two tables or services that both claim to be the canonical address registry.

### 5.6 Identifier architecture

Define:

- internal canonical entity IDs;
- public address/location codes;
- external-source identifiers;
- import/staging identifiers;
- human-readable labels;
- version/event identifiers;
- identifier issuance, immutability, supersession, retirement, and non-reuse;
- collision and duplicate handling;
- offline/field provisional identifiers and synchronization;
- the effect of administrative-boundary or name changes.

The work order requires an identifier-strategy ADR. It does **not** authorize final national public-code grammar or issuance without the Programme Owner and responsible data/GIS authority.

### 5.7 Lifecycle and temporal model

Define separate state machines for at least:

- evidence/candidate intake;
- field verification;
- canonical registry record;
- geometry validation;
- correction/dispute;
- publication;
- retirement/supersession;
- administrative geography and boundary versions;
- road/name approval.

For each state machine, define:

- valid transitions;
- required actor/authority context;
- required evidence/reason;
- whether the state is public, internal, or restricted;
- effective time and recorded time;
- reversal, correction, appeal, and supersession behavior.

Do not use one status field to represent validation, publication, archival, dispute, and geometry quality simultaneously.

### 5.8 Versioning and history

Define how the system preserves:

- immutable entity identity;
- mutable attributes;
- effective-dated versions;
- transaction/recorded time;
- before/after or snapshot history;
- geometry versions;
- name/code changes;
- supersession chains;
- correction and dispute timelines;
- public historical verification where authorized.

The model must support reconstructing what the registry believed, what was officially effective, and what was publicly released at a named time.

### 5.9 Geometry, provenance, and quality

Define model fields for:

- geometry class and geometry type;
- CRS and transformation history;
- source organization/system;
- source record/reference;
- capture method, device, and actor where applicable;
- capture and effective time;
- accuracy/uncertainty and quality class;
- validation status and validating authority;
- canonical versus observed/suggested/public-generalized geometry;
- supersession/dispute;
- topology or consistency-check results;
- external data licensing/usage restrictions.

The work order must accommodate the later GIS-governance work without pretending to finalize all CRS, topology, survey, or boundary-authority policy.

### 5.10 Names, language, and normalization

Define:

- official Spanish names;
- English presentation names where required;
- local/alternative/historical names;
- normalized search values;
- abbreviations and display formatting;
- name source and authority;
- effective dates and retirement;
- sorting/collation considerations;
- preservation of accents and original spelling.

A normalized search value must not replace the authoritative written form.

### 5.11 Source, authority, and data classification

Every canonical or candidate value must be attributable to a source and authority class. Define at minimum:

- official government source;
- institutionally approved registry decision;
- verified field observation;
- unverified field observation;
- citizen submission;
- imported provisional source;
- external map/geocoder suggestion;
- derived/system-calculated value;
- fixture/training data.

Classify data elements as public, government internal, restricted, or highly restricted and identify likely retention/visibility implications. This design classification does not replace later legal/privacy approval.

### 5.12 API and projection model

Map the canonical model to:

- public lookup/proof responses;
- citizen submission and tracking;
- operator case files;
- field synchronization;
- reports and exports;
- publication manifests;
- future partner APIs.

Define explicit audience projections. Public responses must not be described as internal entities with a few fields removed.

### 5.13 Constraints, quality, and scale

Specify:

- primary, foreign, unique, check, exclusion, and spatial constraints;
- one-current-version rules;
- no-cycle and hierarchy rules;
- coordinate/SRID and geometry-validity rules;
- duplicate/collision-review rules;
- required/optional fields by addressable-object type;
- publication prerequisites;
- archival/supersession invariants;
- expected access paths and indexes;
- initial national-scale volume assumptions and growth-sensitive tables;
- partitioning candidates, without implementing premature partitioning.

### 5.14 Schema convergence

Produce a no-loss mapping from current to target concepts, including:

- `provinces` and `admin_units`;
- `territories`;
- `roads`, `buildings`, `addresses`, and `address_points`;
- `citizen_geotag_submissions`;
- `address_records` and `address_record_events`;
- field assignments/submissions;
- corrections;
- imports;
- publication packs;
- audit and evidence references.

For each current field, identify:

- target entity/field;
- transformation or normalization;
- default/provisional handling;
- authority/classification;
- loss or ambiguity risk;
- validation query;
- compatibility period;
- retirement/deprecation condition.

The plan must use expand–migrate–contract and preserve the accepted NLI-WO-001 lifecycle controls.

## 6. Required deliverables

Create a controlled design pack under `docs/sda/data-model/`:

```text
docs/sda/data-model/
  README.md
  current-state-inventory.md
  canonical-conceptual-model.md
  canonical-logical-erd.mmd
  data-dictionary.md
  controlled-vocabularies.md
  lifecycle-state-machines.md
  identifiers-and-codes.md
  geometry-provenance-and-quality.md
  source-authority-and-classification.md
  api-projection-map.md
  current-to-target-mapping.md
  schema-convergence-plan.md
  draft-physical-schema.sql
  representative-records/
```

`draft-physical-schema.sql` is a design artifact only. It must be marked non-executable and must not be placed under `infra/migrations/`.

Create or propose ADRs covering at minimum:

- internal identifier strategy and public-code separation;
- administrative geography versus operational areas;
- canonical address/location entity and addressable-object relationships;
- temporal/versioning and supersession model;
- geometry/evidence/provenance separation.

ADR numbers must follow the repository sequence and begin as `Proposed` until accepted by SDA review.

## 7. Out of scope

This work order does not authorize:

- executable migrations or production DDL;
- modifying current operational tables or data;
- replacing migrations `000–007`;
- changing current API contracts or UI workflows;
- national RBAC/ABAC implementation;
- government identity federation or MFA;
- official publication authority or release enablement;
- final national address-code grammar or public issuance;
- legal land ownership, title, or cadastre claims;
- complete GIS operational policy, authoritative boundary acquisition, or survey standards;
- partner API/service-account implementation;
- production infrastructure or DR changes;
- deletion of current pilot data;
- a broad application rewrite.

## 8. Prohibited approaches

- Do not copy `docs/source-proposals/schema.sql` into migrations or rename it “canonical.”
- Do not treat current table names as automatically correct merely because code depends on them.
- Do not create a new canonical table while leaving another table with the same authority unexplained.
- Do not use JSONB as a substitute for modelled core relationships or controlled fields.
- Do not encode mutable administrative hierarchy, road names, or occupant identity into immutable internal IDs.
- Do not make public codes the primary foreign keys of the registry.
- Do not make geometry precision alone represent accuracy or authority.
- Do not promote citizen, field, import, or external-map geometry automatically to official geometry.
- Do not physically delete official record history.
- Do not combine publication, validation, archive, correction, and dispute into one uncontrolled status vocabulary.
- Do not assume parcels or ownership data are available or authoritative.
- Do not introduce a new database, event store, search engine, graph database, or microservice boundary for modelling convenience.
- Do not change runtime code in this design-authority work order.

## 9. Architecture questions requiring explicit decisions

The design pack must answer or raise an RFI for:

1. Generic hierarchical `administrative_units` versus separate level-specific tables.
2. Stable internal ID type and generation strategy.
3. One canonical `addresses` entity versus a broader `location_records`/addressable-object registry.
4. Relationship between address identity, address presentation, access point, building, and unit.
5. Whether roads are whole named features, segments, or both.
6. Operational-area model replacing or constraining current `territories`.
7. Event/snapshot/version-table strategy and temporal semantics.
8. Geometry storage by entity and geometry-version strategy.
9. Public-code aliasing, correction, supersession, and non-reuse.
10. Locality/settlement/neighbourhood modelling when not an official administrative unit.
11. Evidence-to-decision lineage.
12. Treatment of existing published-looking fixture/pilot records during future convergence.

Do not bury these decisions in the draft SQL.

## 10. Acceptance criteria

### AC-01 — Complete current-state inventory

Every current operational table and material field is classified by purpose, authority, writer, reader, lifecycle, source, sensitivity, geometry, and target disposition.

### AC-02 — One canonical registry authority

The model defines one canonical address/location authority and explicitly resolves the current overlap among `addresses`, `address_points`, `address_records`, submission records, and publication records.

### AC-03 — Administrative geography is explicit

The model represents legal/administrative identity, hierarchy, names, codes, effective dates, status, and boundary versions without conflating operational areas.

### AC-04 — Operational areas are separate

Campaign, routing, rollout, assignment, and temporary-service areas have their own model and purpose and cannot be mistaken for administrative authority.

### AC-05 — Addressable-object coverage

The model supports roads, landmarks, optional parcel references, buildings, entrances/access points, units, non-building objects, and addresses with documented cardinality and optionality for rural and informal cases.

### AC-06 — Identifier separation

Internal IDs, public codes, external IDs, provisional/offline IDs, and human labels are distinct, stable, non-reused according to policy, and covered by a proposed ADR.

### AC-07 — Lifecycle separation

Candidate/evidence, verification, canonical record, geometry, correction/dispute, publication, and retirement lifecycles are separate, controlled, and fully defined.

### AC-08 — Temporal reconstruction

The model can reconstruct entity attributes, registry belief, official effective state, and public release at a named time without silent overwrite.

### AC-09 — Geometry provenance and quality

Every material geometry can record source, method, CRS, time, accuracy/quality, validation, authority, version, and public/canonical/evidence classification.

### AC-10 — Multilingual and naming integrity

Official, alternative, local, historical, normalized, Spanish, and English names are represented without losing authoritative spelling or source history.

### AC-11 — Source and authority lineage

Canonical values and decisions are traceable to evidence/source, actor or system, institution, validation, and approval context.

### AC-12 — Data classification

The data dictionary assigns classification and public/operator/partner visibility intent to every sensitive or externally exposed field.

### AC-13 — Controlled vocabularies

All status/type/source/quality/publication values are documented with definitions, allowed transitions, and ownership. Overlapping current strings are mapped or retired.

### AC-14 — Integrity constraints

The proposed model identifies enforceable database invariants, including hierarchy, uniqueness, one-current-version, geometry/SRID, relationship, publication, and supersession rules.

### AC-15 — API projection compatibility

Current public and operator workflows are mapped to explicit target projections, and every breaking or ambiguous contract impact is identified.

### AC-16 — Current-to-target no-loss mapping

Every current field has a target, transformation, archival disposition, or explicit accepted-loss decision. Unknown/unmappable values are surfaced rather than silently dropped.

### AC-17 — Expand–migrate–contract plan

The convergence plan defines compatible expansion, dual-read/write or adapter strategy where required, backfill, validation, cutover, contract removal, and forward-recovery steps.

### AC-18 — Representative records

Representative examples cover urban street address, rural/landmark location, building with multiple units, no-formal-road case, corrected/superseded address, disputed geometry, and administrative-boundary change.

### AC-19 — Scale and index rationale

The design identifies high-growth entities, expected national access paths, required indexes, and any future partitioning candidates with assumptions stated.

### AC-20 — Draft physical schema is coherent

The non-executable draft SQL implements the accepted logical concepts consistently, contains no competing canonical authority, and is traceable to the data dictionary and ADRs.

### AC-21 — ADR decision pack

Every reserved architecture question has an accepted/proposed ADR or a formal RFI; no consequential decision exists only in a diagram or SQL file.

### AC-22 — No runtime behavior change

The design-authority PR changes only controlled architecture/model documentation and proposed ADRs. Runtime code, migrations, schemas, API contracts, and production data remain unchanged.

## 11. Required evidence

The pull request must include:

- acceptance-criterion-mapped modelling plan;
- automated or reproducible current-schema inventory output where used;
- current and target ER diagrams;
- data dictionary completeness report;
- current-to-target field mapping with no unexplained omissions;
- state-machine diagrams/tables;
- identifier and code decision analysis;
- geometry/source/provenance decision analysis;
- representative-record walkthroughs;
- proposed ADRs and all RFIs;
- physical-schema consistency checks;
- API projection impact matrix;
- migration-convergence risks and validation queries;
- explicit confirmation that no runtime or executable migration behavior changed;
- residual institutional decisions and risk-register implications.

## 12. Agent checkpoint before modelling

The agent's first response after reading this work order must provide:

1. a plan mapped to AC-01 through AC-22;
2. the exact current schema/code/API sources it will inspect;
3. proposed design-pack and ADR filenames;
4. the modelling notation and consistency-validation method;
5. a list of suspected duplicate authorities and status collisions;
6. the architecture questions expected to require RFIs;
7. confirmation that no runtime code or executable migration will be changed.

After producing the plan, the agent may begin the design-authority work without separate confirmation for choices already authorized here. Reserved decisions must be surfaced through proposed ADRs or RFIs, not silently finalized.

## 13. Branch, pull request, and review

Use branch:

```text
nli/wo-002-canonical-location-model
```

Open a **draft** pull request to `main` using the repository evidence template. The pull request must remain draft until the complete design pack and criterion matrix are present.

The SDA will review the exact head and record one of:

- `ACCEPTED`
- `ACCEPTED WITH RECORDED CONDITIONS`
- `REWORK REQUIRED`
- `REJECTED — ARCHITECTURAL REDESIGN REQUIRED`

Acceptance of this design phase authorizes preparation of the implementation work order. It does not itself authorize schema deployment.
