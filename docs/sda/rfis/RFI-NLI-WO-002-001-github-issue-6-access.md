# NLI Request for Information — RFI-NLI-WO-002-001-github-issue-6-access

**Related work order:** `NLI-WO-002`  
**Raised by:** `Implementation Agent`  
**Date:** `2026-07-13`  
**Required by:** `Before executable NLI-WO-002B schema/API implementation`  
**Status:** `OPEN`

## 1. Decision question

GitHub issue #6 access

## 2. Why this decision is required

The implementation agent could not access GitHub issue #6 via gh/API during planning.

## 3. Current evidence

Reviewed `AGENTS.md`, NLI-WO-002, accepted ADRs 001–004, SDA standards, migrations 000–007, current API persistence/publication/geospatial behavior, and source proposal schema as non-authoritative input.

## 4. Options considered

### Option A — Decide now

- Behavior: SDA/authority records the rule before implementation.
- Benefits: future migrations and API contracts can be specific.
- Risks/costs: requires authority review.
- Migration/compatibility effect: reduces future rework.
- Security/authority/operations effect: strongest authority posture.

### Option B — Reserve decision

- Behavior: design pack uses placeholders and avoids executable commitment.
- Benefits: safe for WO-002 design phase.
- Risks/costs: WO-002B cannot fully implement affected area.
- Migration/compatibility effect: adapters may need reserved fields.
- Security/authority/operations effect: avoids false claims.

## 5. Agent recommendation

Use Option B for NLI-WO-002 and require Option A before NLI-WO-002B implements the affected runtime behavior.

## 6. Consequence of no decision

The design can remain explicit about the reserved decision, but executable migrations/API changes that depend on it must stop.

## 7. Requested decision authority

`SDA/GitHub owner`

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
