# S06 — Canonical Data Model and Convergence

## Invoke when

- designing entities, fields, identifiers, lifecycles, geometry, provenance, or publication models;
- producing an ERD or data dictionary;
- mapping current data to a target model;
- planning expand–migrate–contract convergence;
- validating a non-executable physical schema.

## Required inputs

- S05 authoritative current-state inventory;
- active data-model work order;
- accepted ADRs and open RFIs;
- data, GIS, API, audit, privacy, and migration standards;
- observed current value domains and workflows.

## Procedure

### 1. Define one authoritative typed target model

Every field must declare:

```text
entity
field name
semantic definition
PostgreSQL type
nullability
default
primary/foreign relationship
controlled vocabulary
source/authority owner
classification
projection eligibility
temporal behavior
integrity constraints
```

No suffix-based inference may substitute for field-specific metadata.

### 2. Separate identity from mutable facts

Define:

- immutable canonical identity;
- effective-dated names/codes/attributes;
- recorded-time history;
- public aliases separately from internal IDs;
- evidence/candidate observations separately from canonical state;
- publication snapshots separately from mutable registry records.

### 3. Define complete relationship cardinality

For each record or object type specify:

- required relationship roles;
- minimum and maximum counts;
- allowed subject/entity types;
- interval containment;
- merge, supersession, retirement, and deletion behavior;
- creation-order-safe relationship design.

The physical design must use actual vocabulary values, not an unreferenced placeholder type.

### 4. Define lifecycle and temporal models

For each stateful entity:

- bind exactly one lifecycle vocabulary and graph;
- define every valid transition and terminal state;
- record permission, institution/territory scope, authority, evidence, audit event, public effect, reversal, and denial behavior;
- decide whether the entity is immutable, effective-only, recorded-time versioned, or bitemporal;
- define interval, overlap, current-row, reciprocal-chain, and cycle rules.

### 5. Define source, evidence, and geometry promotion

A canonical fact or geometry must trace to:

- source record/package;
- evidence object or observation;
- quality result;
- authorized decision event;
- actor, institution, scope, and permission;
- effective and recorded time.

Technical validity alone must not grant canonical authority.

### 6. Build the reviewed transformation registry

Every current field must have one conscious disposition:

- exact typed target;
- grouped transform to one or more exact target rows;
- reference crosswalk with source and target entity/key;
- governed raw archive;
- owned exception/RFI;
- migration-ledger/control retention;
- explicit accepted loss, approved by the proper authority.

Each transformation requires:

- stable source row key;
- source fields and semantics;
- exact target rows/fields;
- input/output example;
- controlled-value map where applicable;
- ID-generation/crosswalk algorithm;
- executable transform and validation;
- no-loss/value/relationship assertion;
- exception owner and SLA;
- compatibility and retirement condition.

No heuristic fallback may approve unknown fields.

### 7. Produce executable disposable design SQL

The draft schema must:

- execute in disposable PostgreSQL/PostGIS;
- use dependency-safe creation;
- express FKs, checks, unique/exclusion constraints, indexes, and triggers;
- match typed metadata field-by-field;
- support positive and negative semantic fixtures.

It remains non-executable against runtime environments until a later work order authorizes migrations.

### 8. Validate representative national scenarios

Author independent scenarios for:

- urban street address;
- rural landmark location;
- multi-unit building;
- no-formal-road location;
- corrected/superseded record and releases;
- disputed geometry and resolution;
- administrative boundary change.

Each scenario must include only relevant entities and prove IDs, relationships, histories, geometry, evidence, authority, release payloads, and public/operator projections.

### 9. Build convergence units

For each migration unit specify:

- source and target fields/rows;
- dependency order;
- read/write ownership and compatible app versions;
- crosswalk and exception schema;
- idempotency and conflict precedence;
- executable validation and tolerance;
- backup and forward-recovery boundary;
- monitoring window;
- cutover/abort gate;
- retirement proof.

## Outputs

- typed target model;
- conceptual model and ERD;
- data dictionary and vocabularies;
- lifecycle and temporal specification;
- reviewed transformation registry;
- executable disposable draft schema;
- scenario fixtures and expected projections;
- convergence-unit plan;
- ADR/RFI coverage matrix.

## Stop or RFI conditions

Stop when:

- two target entities both claim canonical authority;
- a current field has no reviewed disposition;
- a controlled map does not match observed source values or target vocabulary;
- a relationship uses polymorphism without enforceable native identity;
- a lifecycle field is not bound to one graph;
- a public code or administrative code decision lacks authority;
- a no-loss assertion is not executable;
- the scenario generator also generates expected scenario outcomes;
- the draft schema executes only because semantic constraints are omitted.

## Evidence gate

Before requesting SDA review:

- current inventory is catalog-derived;
- every current field has a validated reviewed disposition;
- all target metadata matches physical catalog type, nullability, defaults, FKs, vocabularies, checks, exclusions, indexes, and triggers;
- positive scenarios and real negative cases execute;
- every lifecycle graph is complete and bound;
- every ADR claim links to a named assertion;
- convergence units are derived only from accepted transformations.

## Anti-patterns

- Copying a proposal schema wholesale.
- Generating target semantics from field names.
- Mapping every ID to one generic crosswalk field without the final target join.
- Calling `ASSERT ...` text executable evidence.
- Generating one row per target entity for every scenario.
- Using aggregate constraint counts as proof of domain integrity.
- Treating a green self-consistency check as independent validation.
