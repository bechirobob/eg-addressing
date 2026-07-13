# Implementation Plan — NLI-WO-002 Canonical National Location Data Model

**Work order:** `docs/sda/work-orders/NLI-WO-002-canonical-national-location-data-model.md`  
**Implementation branch:** `nli/wo-002-canonical-location-model`  
**Planning commit:** `c4ac36ed0c1d74990c695c6cd6bdd358f7186273`  
**Prepared by:** `Implementation Agent`  
**Status:** `PROPOSED`

> Design-authority phase only. This plan authorizes documentation artifacts, proposed ADRs, RFIs, and non-executable schema proposal. It does not authorize schema deployment.

## 1. Objective understood

Produce a complete canonical national location data-model design pack for SDA review. The output must define the target logical model, data dictionary, identifiers, states, geometry/provenance, source authority, API projections, current-to-target mapping, representative records, non-executable physical proposal, proposed ADRs, RFIs, and expand–migrate–contract plan. Observable outcome: GitHub draft PR contains a docs-only design authority package and evidence that runtime code, migrations, API contracts, infrastructure, and production data were not changed.

## 2. Current implementation inspected

- Governance: `AGENTS.md`, `docs/sda/README.md`, `charter.md`, `architecture-baseline.md`, `target-reference-architecture.md`, `risk-register.md`.
- Work orders/reviews: `NLI-WO-002`, `NLI-WO-001-closeout`, `NLI-WO-001-review-04`.
- ADRs: `ADR-001` through `ADR-004`.
- Standards: data/migrations, GIS/location, API design, audit/evidence, security, documentation/records.
- Migrations: `infra/migrations/000_current_operational_schema.sql` through `007_lifecycle_metadata_hardening.sql`.
- API persistence and behavior: `services/api/app/db.py`, `main.py`, `address_codes.py`, `ops_status.py`, `security_posture.py`.
- Non-authoritative input: `docs/source-proposals/schema.sql`.

## 3. Acceptance-criterion map

| Criterion | Planned change | Evidence/test | Files/domains | Dependency or RFI |
|---|---|---|---|---|
| AC-01 | Create or update the design authority artifact covering AC-01. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | GitHub issue #6 access RFI |
| AC-02 | Create or update the design authority artifact covering AC-02. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-03 | Create or update the design authority artifact covering AC-03. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-04 | Create or update the design authority artifact covering AC-04. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-05 | Create or update the design authority artifact covering AC-05. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-06 | Create or update the design authority artifact covering AC-06. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-07 | Create or update the design authority artifact covering AC-07. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-08 | Create or update the design authority artifact covering AC-08. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-09 | Create or update the design authority artifact covering AC-09. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-10 | Create or update the design authority artifact covering AC-10. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-11 | Create or update the design authority artifact covering AC-11. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-12 | Create or update the design authority artifact covering AC-12. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-13 | Create or update the design authority artifact covering AC-13. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-14 | Create or update the design authority artifact covering AC-14. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-15 | Create or update the design authority artifact covering AC-15. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-16 | Create or update the design authority artifact covering AC-16. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-17 | Create or update the design authority artifact covering AC-17. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-18 | Create or update the design authority artifact covering AC-18. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-19 | Create or update the design authority artifact covering AC-19. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-20 | Create or update the design authority artifact covering AC-20. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-21 | Create or update the design authority artifact covering AC-21. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |
| AC-22 | Create or update the design authority artifact covering AC-22. | Data-model document section + PR evidence row. | `docs/sda/data-model/**`, proposed ADRs/RFIs. | None |

## 4. Proposed file and module changes

### Add

- `docs/sda/data-model/README.md` — pack index and AC trace.
- `docs/sda/data-model/current-state-inventory.md` — current schema/API inventory.
- `docs/sda/data-model/canonical-conceptual-model.md` — target domain model.
- `docs/sda/data-model/canonical-logical-erd.mmd` — logical ERD source.
- `docs/sda/data-model/data-dictionary.md` — field definitions, classifications, sources, visibility.
- `docs/sda/data-model/controlled-vocabularies.md` — controlled vocabulary definitions and current-string mapping.
- `docs/sda/data-model/lifecycle-state-machines.md` — state machines and allowed transitions.
- `docs/sda/data-model/identifiers-and-codes.md` — identifier/public-code model.
- `docs/sda/data-model/geometry-provenance-and-quality.md` — CRS, quality, provenance, geometry version model.
- `docs/sda/data-model/source-authority-and-classification.md` — source authority and data classification.
- `docs/sda/data-model/api-projection-map.md` — current API projection mapping.
- `docs/sda/data-model/current-to-target-mapping.md` — complete table/field disposition map.
- `docs/sda/data-model/schema-convergence-plan.md` — expand–migrate–contract plan for later WO-002B.
- `docs/sda/data-model/draft-physical-schema.sql` — non-executable design-only SQL proposal.
- `docs/sda/data-model/representative-records/*.md` — representative records.
- Proposed ADRs `ADR-005` through `ADR-009`.
- Formal RFIs for reserved architecture decisions.
- `docs/sda/evidence/NLI-WO-002-pull-request-evidence.md` — PR evidence artifact.

### Modify

- No runtime source files.
- No executable migrations.
- No API contract files.
- No infrastructure files.

### Remove or deprecate

- None in this phase.

## 5. Data and migration impact

- Schema changes: none.
- New/changed migration files: none.
- Reference-data changes: none.
- Fixture changes: none.
- Existing-data transition: design only, documented for future WO-002B.
- Compatibility/deployment sequence: documented expand–migrate–contract proposal only.
- Rollback or forward recovery: not applicable to runtime; docs can be reverted.
- Empty-database and upgrade test approach: future WO-002B only.

## 6. API and integration impact

- Routes/contracts changed: none.
- OpenAPI/generated types: none.
- Compatibility classification: documentation-only, non-breaking.
- Idempotency/concurrency: modeled as future requirements.
- Public/operator/partner projections: documented only.
- External dependencies: none.

## 7. Identity, security, privacy, and audit impact

No implemented auth/session changes. The model classifies restricted data, evidence, public projections, and audit requirements for later implementation. No secrets or production data are introduced.

## 8. GIS/location impact

Design defines EPSG:4326 authoritative storage, geometry versioning, source/method/accuracy fields, quality statuses, PostGIS spatial index expectations, and public/generalized geometry boundaries. No geometry migration is applied.

## 9. Workflow, accessibility, and localization impact

No UI workflow changes. Spanish/English naming strategy is documented in the data dictionary and vocabulary rules.

## 10. Operations and recovery impact

No environment/configuration/deployment impact. Future deployment sequencing is documented for WO-002B.

## 11. Test plan

- Static repository proof: `git diff --name-only origin/main...HEAD` must show docs-only paths.
- Search proof: no changed paths under `services/api`, `infra/migrations`, `apps`, `infra/docker`, or production data folders.
- Markdown/schema proof: read generated artifacts and verify required headings/ACs are present.
- GitHub proof: remote branch is ahead of `main`; draft PR to `main` is accessible.

## 12. Implementation sequence

1. Generate design pack and proposed ADR/RFI docs.
2. Generate PR evidence artifact.
3. Verify docs-only diff.
4. Commit with documentation-only message.
5. Push `nli/wo-002-canonical-location-model`.
6. Open draft PR to `main`.
7. Verify PR accessibility, draft status, changed files, and branch ahead count.

## 13. RFIs and decisions required

Formal RFIs are created for GitHub issue #6 access, national public-code grammar authority, administrative hierarchy authority, publication authority/effective date, and parcel/cadastre authority.

## 14. Risks and assumptions

| Risk/assumption | Effect | Mitigation/validation | Owner |
|---|---|---|---|
| GitHub issue #6 unavailable to agent | Possible missed instruction | Formal RFI, continue only from repository-controlled work order. | SDA/GitHub owner |
| Proposal schema is tempting to copy | Second authority or incompatible schema | Use only as non-authoritative design input; map concepts explicitly. | Implementation Agent |
| Current statuses collapse multiple workflows | Bad future migration | Separate state machines and vocabularies. | SDA |
| Administrative/legal source is not final | False official claims | Model source authority and RFIs; do not claim final data. | Programme/GIS authority |

## 15. Completion declaration

- [x] Every acceptance criterion is mapped.
- [x] No prohibited approach is planned.
- [x] Database/API/security/workflow/operations effects are explicit.
- [x] Required RFIs are raised.
- [x] The plan does not claim SDA acceptance.
