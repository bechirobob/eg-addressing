# NLI Request for Information — RFI-NLI-WO-002-006-existing-published-looking-pilot-records

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-14`  
**Required by:** `Before executable NLI-WO-002B implementation for affected area`  
**Status:** `OPEN`

## 1. Decision question

Treatment of existing published-looking pilot or fixture records

## 2. Why this decision is required

Current data may have publication-like labels without institutional release authority.

## 3. Current evidence

- NLI-WO-002 work order.
- SDA Review 02 findings.
- `target-model.json`, ADRs 005-009, and current-to-target map.

## 4. Options considered

### Option A — Snapshot as release

- Behavior: Create publication_release items
- Benefits: Preserves public history
- Risks/costs: Requires authority evidence
- Migration/compatibility effect: Only if authority exists
- Security/authority/operations effect: explicit owner required before implementation.
### Option B — Downgrade to internal

- Behavior: Map as internal-registry
- Benefits: Safe by default
- Risks/costs: May surprise users
- Migration/compatibility effect: Needs operator notice
- Security/authority/operations effect: explicit owner required before implementation.
### Option C — Exception queue

- Behavior: Hold until review
- Benefits: No false claim
- Risks/costs: Manual workload
- Migration/compatibility effect: Use migration_exception
- Security/authority/operations effect: explicit owner required before implementation.

## 5. Agent recommendation

Default to exception queue unless explicit publication authority is attached.

## 6. Consequence of no decision

Design placeholders and safety boundaries can remain. Executable WO-002B work must stop for this decision area rather than guessing.

## 7. Requested decision authority

`SDA / Publication Authority`

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
