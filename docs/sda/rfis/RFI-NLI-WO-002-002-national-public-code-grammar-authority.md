# NLI Request for Information — RFI-NLI-WO-002-002-national-public-code-grammar-authority

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-14`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

National public-code grammar and issuance authority

## 2. Why this decision is required

WO-002 can model aliases/non-reuse but cannot approve national public-code grammar.

## 3. Current evidence

- NLI-WO-002 work order.
- SDA Review 02 findings.
- `target-model.json`, ADRs 005-009, and current-to-target map.

## 4. Options considered

### Option A — Structured human code

- Behavior: Province/locality prefix + sequence/checksum
- Benefits: Human friendly; signage-friendly
- Risks/costs: Boundary/name changes can mislead
- Migration/compatibility effect: Requires migration if grammar changes
- Security/authority/operations effect: explicit owner required before implementation.
### Option B — Opaque code

- Behavior: Random/checksummed public alias
- Benefits: Stable and privacy-preserving
- Risks/costs: Less human meaningful
- Migration/compatibility effect: Low migration coupling
- Security/authority/operations effect: explicit owner required before implementation.
### Option C — Grid-derived

- Behavior: Code embeds spatial cell
- Benefits: Useful in field
- Risks/costs: Privacy/enumeration and boundary-change risk
- Migration/compatibility effect: High policy impact
- Security/authority/operations effect: explicit owner required before implementation.

## 5. Agent recommendation

Choose grammar before public issuance; until then keep `nli-reserved-v1` aliases internal.

## 6. Consequence of no decision

Design placeholders and safety boundaries can remain. Executable WO-002B work must stop for this decision area rather than guessing.

## 7. Requested decision authority

`Programme Owner / Registry Authority`

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
