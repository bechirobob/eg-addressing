# NLI Request for Information — RFI-NLI-WO-002-005-parcel-reference-authority

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-14`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

Parcel/cadastre reference authority

## 2. Why this decision is required

Parcel references must not imply ownership or title.

## 3. Current evidence

- NLI-WO-002 work order.
- SDA Review 02 findings.
- `target-model.json`, ADRs 005-009, and current-to-target map.

## 4. Options considered

### Option A — No parcels

- Behavior: Exclude parcels
- Benefits: Lowest legal risk
- Risks/costs: Less integration value
- Migration/compatibility effect: No migration needed
- Security/authority/operations effect: explicit owner required before implementation.
### Option B — Restricted external references

- Behavior: Store external ID/source only
- Benefits: Supports future linkage
- Risks/costs: Needs strict projection
- Migration/compatibility effect: Model already supports
- Security/authority/operations effect: explicit owner required before implementation.
### Option C — Official cadastre integration

- Behavior: Treat as authoritative
- Benefits: High value
- Risks/costs: Requires legal authority
- Migration/compatibility effect: Separate work order
- Security/authority/operations effect: explicit owner required before implementation.

## 5. Agent recommendation

Use restricted external references only until official authority exists.

## 6. Consequence of no decision

Design placeholders and safety boundaries can remain. Executable WO-002B work must stop for this decision area rather than guessing.

## 7. Requested decision authority

`Legal/Privacy Authority / GIS Authority`

## 8. Decision

**Decision:** `<completed by authority>`  
**Rationale:**  
**Conditions:**  
**Affected standards/ADR/work order:**  
**Decision date and authority:**

## 9. Implementation acknowledgment

- [ ] Plan updated.
- [ ] Acceptance-criterion map updated.
- [ ] New risks/conditions recorded.
- [ ] ADR or standard update created where the decision is durable.
