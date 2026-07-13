# Internal identifiers and public-code separation

**Status:** Proposed  
**Date:** 2026-07-13  
**Related work order:** `NLI-WO-002`  

## Context

Public codes must not be confused with database identity or candidate grid codes.

## Decision

Separate immutable internal IDs from public code aliases; final public-code grammar remains reserved by RFI.

## Alternatives considered

1. Keep current tables and status fields unchanged. Rejected because NLI-WO-002 requires canonical authority clarity.
2. Copy the proposal schema wholesale. Rejected because it conflicts with current migrations and could create a second canonical authority.
3. Use the proposed model in this ADR and defer executable implementation to NLI-WO-002B.

## Consequences

Prevents code reuse and false publication; requires migration adapters later.

No executable migration, API contract, runtime code, infrastructure, or production data change is authorized by this proposed ADR.

## Follow-up

Requires SDA review and later implementation work order before runtime adoption.
