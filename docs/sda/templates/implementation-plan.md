# Implementation Plan — <WORK-ORDER-ID>

**Work order:** `<ID and link>`  
**Implementation branch:** `<branch>`  
**Planning commit:** `<sha>`  
**Prepared by:** `<agent/person>`  
**Status:** `PROPOSED | REVISED | ACCEPTED FOR IMPLEMENTATION`

> Complete this plan before modifying implementation files. Map every acceptance criterion. Do not remove sections; use `NOT APPLICABLE` with a reason.

## 1. Objective understood

Summarize the required outcome in implementation terms. State what will be observably different after acceptance.

## 2. Current implementation inspected

List the relevant files, modules, schema/migrations, tests, scripts, APIs, UI routes, and operational behavior inspected.

## 3. Acceptance-criterion map

| Criterion | Planned change | Evidence/test | Files/domains | Dependency or RFI |
|---|---|---|---|---|
| AC-01 | | | | |

Every criterion must appear once. A criterion may map to several changes/tests.

## 4. Proposed file and module changes

### Add

- `<path>` — purpose

### Modify

- `<path>` — purpose

### Remove or deprecate

- `<path>` — purpose and transition

## 5. Data and migration impact

- Schema changes:
- New/changed migration files:
- Reference-data changes:
- Fixture changes:
- Existing-data transition:
- Compatibility/deployment sequence:
- Rollback or forward recovery:
- Empty-database and upgrade test approach:

## 6. API and integration impact

- Routes/contracts changed:
- OpenAPI/generated types:
- Compatibility classification:
- Idempotency/concurrency:
- Public/operator/partner projections:
- External dependencies:

## 7. Identity, security, privacy, and audit impact

- Authentication/session effect:
- Roles/permissions/scopes:
- Sensitive data/classification:
- Threats or abuse cases:
- Secrets/keys:
- Audit events:
- Security tests/scans:

## 8. GIS/location impact

- Geometry classes/CRS/provenance:
- Address/location identifiers:
- Map/geocoder behavior:
- Spatial constraints/indexes/tests:

## 9. Workflow, accessibility, and localization impact

- Roles and workflows affected:
- Before/after steps:
- Spanish/English changes:
- Accessibility checks:
- Required screenshots/viewports/states:

## 10. Operations and recovery impact

- Environment/configuration:
- Deployment sequence:
- Health/readiness/metrics/logs/alerts:
- Backup/restore effect:
- Failure behavior:
- Runbooks:

## 11. Test plan

List exact commands and evidence planned for:

- static/type/build;
- unit/domain;
- database/migration;
- authorization allow/deny;
- API contract;
- workflow/browser;
- accessibility/localization;
- security/abuse;
- performance/failure/recovery;
- repository quality guards.

## 12. Implementation sequence

1. `<bounded step and checkpoint>`
2. `<bounded step and checkpoint>`

Call out any expand–migrate–contract stages or commits that must remain independently deployable.

## 13. RFIs and decisions required

- `NONE`, or link each RFI. Do not bury decisions in prose.

## 14. Risks and assumptions

| Risk/assumption | Effect | Mitigation/validation | Owner |
|---|---|---|---|
| | | | |

## 15. Completion declaration

- [ ] Every acceptance criterion is mapped.
- [ ] No prohibited approach is planned.
- [ ] Database/API/security/workflow/operations effects are explicit.
- [ ] Required RFIs have been raised.
- [ ] The plan does not claim SDA acceptance.
