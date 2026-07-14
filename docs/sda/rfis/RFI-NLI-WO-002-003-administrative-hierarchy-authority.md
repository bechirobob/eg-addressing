# NLI Request for Information — RFI-NLI-WO-002-003-administrative-hierarchy-authority

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-14`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

Official administrative hierarchy and boundary source

## 2. Why this decision is required

The model supports hierarchy and boundary versions but cannot declare provisional data official.

## 3. Current evidence

- NLI-WO-002 work order.
- SDA Review 02 findings.
- `target-model.json`, ADRs 005-009, and current-to-target map.

## 4. Options considered

### Option A — Use current package provisionally

- Behavior: Internal routing only
- Benefits: Immediate compatibility
- Risks/costs: Not official
- Migration/compatibility effect: No public authority
- Security/authority/operations effect: explicit owner required before implementation.
### Option B — Gazette/legal source

- Behavior: Legal hierarchy source
- Benefits: Highest authority
- Risks/costs: May lack geometry
- Migration/compatibility effect: Requires source package
- Security/authority/operations effect: explicit owner required before implementation.
### Option C — GIS boundary source

- Behavior: Geometry-first source
- Benefits: Spatially useful
- Risks/costs: May not be legal hierarchy
- Migration/compatibility effect: Requires reconciliation
- Security/authority/operations effect: explicit owner required before implementation.

## 5. Agent recommendation

Keep current package provisional; require official source before publication.

## 6. Consequence of no decision

Design placeholders and safety boundaries can remain. Executable WO-002B work must stop for this decision area rather than guessing.

## 7. Requested decision authority

`GIS/Data Authority`

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
