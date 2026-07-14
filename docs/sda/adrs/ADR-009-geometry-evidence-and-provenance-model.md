# Geometry observation, approval, and subject integrity

**Status:** Proposed  
**Date:** 2026-07-13  
**Related work order:** `NLI-WO-002`  

## Context and drivers

Review 01 requires the design pack to decide real architecture questions before executable WO-002B work. Drivers: single canonical authority, no silent data loss, reconstructable time/publication state, PostGIS integrity, and compatibility with current pilot data.

## Decision

Separate `geometry_observation` from approved `geometry_version`; use PostGIS Geometry(Geometry,4326); constrain subject_table values and add WO-002B triggers for subject integrity; enforce one-current per subject/role.

## Alternatives considered

Alternatives: one polymorphic geometry row; raw citizen GPS as approved geometry; one geometry column per entity. Rejected due to provenance/integrity gaps.

## Consequences and implementation constraints

Migration: backfill observations from geotags/field/legacy points and approved versions from address_records.geom where valid. No runtime behavior or executable migration is authorized by this ADR.

## Validation

The decision is reflected in `target-model.json`, ERD, data dictionary, draft SQL, current-to-target mapping, representative records, and consistency checker.
