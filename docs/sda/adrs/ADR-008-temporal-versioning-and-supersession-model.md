# Temporal mechanics, correction, supersession, and immutable publication

**Status:** Proposed  
**Date:** 2026-07-13  
**Related work order:** `NLI-WO-002`  

## Context and drivers

Review 01 requires the design pack to decide real architecture questions before executable WO-002B work. Drivers: single canonical authority, no silent data loss, reconstructable time/publication state, PostGIS integrity, and compatibility with current pilot data.

## Decision

Use bitemporal effective/recorded intervals, immutable versions, explicit predecessor/successor/correction links, one-current enforcement, backdated decision rules, dispute states, and publication snapshots targeting exact version+alias.

## Alternatives considered

Alternatives: mutable current row only; release item points to current record; overwrite corrections. Rejected because reconstruction fails.

## Consequences and implementation constraints

Migration: create versions/events, snapshot current state, future corrections create new versions and releases. No runtime behavior or executable migration is authorized by this ADR.

## Validation

The decision is reflected in `target-model.json`, ERD, data dictionary, draft SQL, current-to-target mapping, representative records, and consistency checker.
