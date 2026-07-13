# Canonical location record and addressable objects

**Status:** Proposed  
**Date:** 2026-07-13  
**Related work order:** `NLI-WO-002`  

## Context

Current addresses, geotags, and address_records overlap.

## Decision

Use one canonical location record authority with addressable object references; intake remains evidence.

## Alternatives considered

1. Keep current tables and status fields unchanged. Rejected because NLI-WO-002 requires canonical authority clarity.
2. Copy the proposal schema wholesale. Rejected because it conflicts with current migrations and could create a second canonical authority.
3. Use the proposed model in this ADR and defer executable implementation to NLI-WO-002B.

## Consequences

Avoids second canonical address authority and supports roads, buildings, units, landmarks, parcels, and non-building objects.

No executable migration, API contract, runtime code, infrastructure, or production data change is authorized by this proposed ADR.

## Follow-up

Requires SDA review and later implementation work order before runtime adoption.
