# NLI Request for Information — RFI-NLI-WO-002-004-publication-authority-and-effective-date

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-14`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

Publication approval authority and effective-date policy

## 2. Why this decision is required

Registry-ready remains separate from public release; authority must be named.

## 3. Current evidence

- NLI-WO-002 work order.
- SDA Review 02 findings.
- `target-model.json`, ADRs 005-009, and current-to-target map.

## 4. Options considered

### Option A — SDA internal only

- Behavior: Internal registry releases only
- Benefits: Safe for pilot
- Risks/costs: No public authority
- Migration/compatibility effect: No public release
- Security/authority/operations effect: explicit owner required before implementation.
### Option B — Named ministry/registry authority

- Behavior: Public release approval
- Benefits: Clear accountability
- Risks/costs: Requires institutional process
- Migration/compatibility effect: Enables release manifests
- Security/authority/operations effect: explicit owner required before implementation.
### Option C — Emergency owner

- Behavior: Temporary release
- Benefits: Fast response
- Risks/costs: High trust risk
- Migration/compatibility effect: Needs break-glass controls
- Security/authority/operations effect: explicit owner required before implementation.

## 5. Agent recommendation

No public/signage release without named authority and release manifest approval.

## 6. Consequence of no decision

Design placeholders and safety boundaries can remain. Executable WO-002B work must stop for this decision area rather than guessing.

## 7. Requested decision authority

`Publication Authority / Programme Owner`

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
