# S21 — Registry Operations and Case Management

## Invoke when

- changing protected registry, territories, roads, buildings, entrances, units, or addresses;
- adding operator case files, holds, corrections, search, queues, approvals, or bulk actions;
- changing staff/admin workflows or territorial case authority.

## Required inputs

- canonical data/lifecycle model;
- role, permission, institution, and territorial-scope rules;
- current operator workflows and API contracts;
- evidence, GIS, publication, audit, and UI standards;
- operational SLA/support expectations.

## Procedure

1. Identify operator role, institution, scope, permission, target record, and state.
2. Define the use case: create candidate, review, assign field work, resolve duplicate, create/update canonical record, correct/supersede/retire, hold, or prepare publication.
3. Build a case file that co-locates identifiers, geography, object relationships, versions, geometry/provenance, evidence, conflicts, disputes, timeline, and next valid actions.
4. Enforce scope in the database/query path before pagination, counts, or aggregation.
5. Validate transitions and prevent self-approval or unauthorized publication.
6. Define version concurrency or locking for high-value records.
7. Make bulk actions bounded, previewable, classified, auditable, and independently approved where required.
8. Preserve immutable identity and version/event history.
9. Audit sensitive reads, changes, holds, exports, staff/role changes, and administrative actions.
10. Test wrong role/institution/territory/state, concurrent edit, bulk limit, correction/supersession, hold, and audit behavior.
11. Capture bilingual accessible operator workflow evidence.

## Outputs

- role/permission/scope matrix;
- case-file information architecture;
- state and segregation rules;
- concurrency/bulk-operation design;
- search/filter/query evidence;
- audit timeline and workflow screenshots.

## Stop or RFI conditions

Stop when:

- a new canonical entity, identifier, state, or authority is required;
- platform administration would imply registry/publication authority;
- a bulk action could alter/disclose many records without approval;
- a correction would overwrite official history;
- current authorization cannot express the required institutional/territorial scope.

## Evidence gate

Before review:

- cross-scope and state-based denial cases execute;
- lost-update/concurrency behavior is demonstrated;
- bulk actions show preview, count, approval, audit, and recovery;
- history/correction/supersession remains reconstructable;
- role-language-viewport evidence is complete.

## Anti-patterns

- Giant operator tables with hidden context and modal chains.
- Editing canonical state directly from raw evidence.
- One global admin role for registry, publication, platform, and audit.
- Applying scope only in the frontend.
- Silent last-write-wins on official records.
- Physical deletion of official history.
