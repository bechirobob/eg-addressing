# Administrative hierarchy, localities, and operational areas

**Status:** Proposed  
**Date:** 2026-07-13  
**Related work order:** `NLI-WO-002`  

## Context and drivers

Review 01 requires the design pack to decide real architecture questions before executable WO-002B work. Drivers: single canonical authority, no silent data loss, reconstructable time/publication state, PostGIS integrity, and compatibility with current pilot data.

## Decision

Use generic `administrative_unit` with controlled `admin_level`, separate `locality`, boundary versions, and separate `operational_area`/coverage.

## Alternatives considered

Alternatives: level-specific tables; treating territories as admin geography; treating locality as operational area. Rejected due to hierarchy changes and legal ambiguity.

## Consequences and implementation constraints

Migration: provinces/admin_units map to admin units; territories map to operational areas; localities require authority review. No runtime behavior or executable migration is authorized by this ADR.

## Validation

The decision is reflected in `target-model.json`, ERD, data dictionary, draft SQL, current-to-target mapping, representative records, and consistency checker.
