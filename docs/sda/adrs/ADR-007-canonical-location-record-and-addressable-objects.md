# Canonical location record and addressable object relationships

**Status:** Proposed  
**Date:** 2026-07-14  
**Decision authority:** System Design Authority  
**Related work order:** `NLI-WO-002`

## Context

SDA Review 02 requires actual architecture decisions rather than generated or heuristic metadata. The design phase must decide implementation-shaping questions while leaving institutional policy decisions as RFIs.

## Decision drivers

- one canonical registry authority;
- no silent data loss in convergence;
- insertable roots and first versions;
- no circular creation dependencies;
- reconstructable effective, recorded, and public release state;
- PostgreSQL/PostGIS integrity;
- no runtime or executable migration authorization in this phase.

## Decision

Use `location_record` as sole registry anchor. Link versions to addressable/context objects through `location_record_object_link` with record-type/object-role cardinality. Buildings, entrances, and units are creation-safe.

## Alternatives considered

### Alternative — Legacy addresses as canonical

- Benefit: simpler initial implementation.
- Cost/risk: fails one or more WO-002 authority, reconstruction, or no-loss requirements.
- Rejection reason: Supports urban/rural/multi-unit/no-road cases without false data.

### Alternative — One nullable FK per object type

- Benefit: simpler initial implementation.
- Cost/risk: fails one or more WO-002 authority, reconstruction, or no-loss requirements.
- Rejection reason: Supports urban/rural/multi-unit/no-road cases without false data.

### Alternative — Always make units sub-fields instead of records

- Benefit: simpler initial implementation.
- Cost/risk: fails one or more WO-002 authority, reconstruction, or no-loss requirements.
- Rejection reason: Supports urban/rural/multi-unit/no-road cases without false data.

## Consequences

- Positive: Supports urban/rural/multi-unit/no-road cases without false data.
- Constraint: WO-002B must implement database and service checks matching `target-model.json`.
- Migration effect: current fields map through `current-to-target-mapping.md`; conflicts become `migration_exception` records.
- Failure mode if ignored: future implementers create incompatible authorities while claiming WO-002 compliance.

## Acceptance checks

- `python3 docs/sda/data-model/scripts/generate_design_catalog.py` leaves deterministic artifacts.
- `python3 docs/sda/data-model/scripts/design_consistency_check.py` validates typed field metadata, mappings, vocabularies, representative records, ADR/RFI coverage, SQL, and Mermaid.
