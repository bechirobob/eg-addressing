# Skill 20 — Registry Operations and Case Management

## Use when

Use for protected operator workflows involving territories, roads, buildings, entrances, units, addresses/location records, case files, corrections, holds, search, approval preparation, staff administration, or bulk registry operations.

## Objective

Give authorized operators a complete, efficient, territorially scoped case-management environment while preserving canonical identity, evidence lineage, segregation of duties, auditability, and historical reconstruction.

## Procedure

1. Identify operator role, institution, territorial/data scope, permission, and record state.
2. Define the case/use case:
   - create candidate;
   - review evidence;
   - assign field work;
   - resolve duplicate/discrepancy;
   - create/update canonical record;
   - correct/supersede/retire;
   - prepare publication;
   - place/release hold;
   - manage reference objects.
3. Build a case-file view that co-locates:
   - canonical/internal/public identifiers;
   - administrative and operational context;
   - object relationships;
   - current and historical attributes;
   - geometry/provenance/quality;
   - evidence and source lineage;
   - duplicate/conflict signals;
   - correction/dispute/hold state;
   - timeline and prior decisions;
   - next valid actions.
4. Enforce authorization and territorial scope in data access, not after retrieval.
5. Validate state transitions and prevent self-approval or unauthorized publication.
6. Define optimistic/version concurrency or locking for high-value records.
7. Make bulk actions explicit, bounded, previewable, reversible/forward-recoverable, and independently approved where required.
8. Preserve immutable entity identity and version/event history.
9. Audit sensitive reads, changes, holds, exports, role changes, and administrative actions.
10. Provide queues, filters, sorting, pagination, counts, and SLA indicators without leaking out-of-scope totals.
11. Test role/scope/state allow and deny cases, concurrent edits, bulk limits, correction/supersession, and audit timelines.
12. Capture operator workflow evidence at supported desktop/mobile widths and both languages.

## Required evidence

- Role/permission/scope matrix
- Case-file information architecture
- State-transition and segregation-of-duty tests
- Cross-territory/institution denial tests
- Concurrency/lost-update behavior
- Bulk operation preview/approval/recovery evidence
- Audit timeline
- Search/filter/pagination/query-plan result
- Bilingual/accessibility screenshots
- Residual workflow and authority RFIs

## Stop and escalate when

- A new canonical entity, identifier, lifecycle state, or approval authority is required.
- A platform administrator would automatically gain registry/publication authority.
- A bulk action could alter or disclose many records without independent approval.
- A correction would overwrite official history.
- Operator scope cannot be expressed by the current authorization model.

## Anti-patterns

- Giant operator tables with hidden context and modal chains.
- Editing canonical state directly from raw evidence fields.
- One global admin role for registry, publication, platform, and audit.
- Applying scope only in the frontend.
- Silent last-write-wins on official records.
- Physical deletion of historical records.
- Bulk export/action controls without purpose, count, classification, and audit.
