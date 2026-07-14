# Canonical record identity and addressable object cardinality

**Status:** Proposed  
**Date:** 2026-07-13  
**Related work order:** `NLI-WO-002`  

## Context and drivers

Review 01 requires the design pack to decide real architecture questions before executable WO-002B work. Drivers: single canonical authority, no silent data loss, reconstructable time/publication state, PostGIS integrity, and compatibility with current pilot data.

## Decision

`location_record` is the sole canonical address/location anchor; object links are many-role rows; unit records are independent only when separately addressable; road and road_segment identities are separate; entrance is access geometry/context.

## Alternatives considered

Alternatives: one nullable FK per object; building/unit hierarchy as record identity; road segment as road identity. Rejected due to multi-object and unit/sub-address ambiguity.

## Consequences and implementation constraints

Migration: normalize `address_records` first, add object links, preserve legacy `addresses` as compatibility source. No runtime behavior or executable migration is authorized by this ADR.

## Validation

The decision is reflected in `target-model.json`, ERD, data dictionary, draft SQL, current-to-target mapping, representative records, and consistency checker.
