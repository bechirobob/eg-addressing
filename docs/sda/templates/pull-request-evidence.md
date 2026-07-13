# Pull Request Evidence — <WORK-ORDER-ID>

**Work order:** `<ID and link>`  
**Implementation plan:** `<link>`  
**Branch:** `<branch>`  
**Head commit:** `<sha>`  
**Prepared by:** `<agent/person>`

> Do not delete sections. Use `NOT APPLICABLE` or `NOT PROVIDED` with a reason. A statement such as “done” is not evidence.

## 1. Outcome

Describe the implemented behavior and the user/operator/engineering effect. State the readiness boundary accurately.

## 2. Acceptance criteria

| Criterion | Status (`PASS`, `PARTIAL`, `FAIL`, `N/A`) | Implementation | Evidence/test | Residual condition |
|---|---|---|---|---|
| AC-01 | | | | |

## 3. Change inventory

### Added

- `<path>` — purpose

### Modified

- `<path>` — purpose

### Removed/deprecated

- `<path>` — transition and compatibility

## 4. Architecture alignment

- ADRs followed:
- Standards followed:
- Domain boundaries affected:
- Deviations/RFIs:
- New dependencies/services:

## 5. Database and migrations

- Migration versions/checksums:
- Empty-database result:
- Previous-version upgrade result:
- Data/backfill validation:
- Lock/duration evidence:
- Reference/fixture behavior:
- Rollback or forward recovery:
- Backup/restore effect:

Attach commands and concise outputs or links to durable CI artefacts.

## 6. API and contracts

- OpenAPI diff:
- Generated type/client diff:
- Compatibility classification:
- Validation/error/idempotency/pagination tests:
- Public/protected/partner projection tests:

## 7. Identity and authorization

- Permissions/scopes changed:
- Allow tests:
- Deny and cross-scope tests:
- Session/credential effects:
- Segregation-of-duty/step-up tests:

## 8. Security and privacy

- Threat/abuse analysis:
- Secret scan:
- Dependency/SAST/container scan:
- Data-classification/privacy effect:
- File/evidence protections:
- Residual security risk:

## 9. GIS/location evidence

- Geometry/CRS/provenance effect:
- Spatial constraints/index/query evidence:
- Address/location-code effect:
- External map/geocoder effect:

## 10. Workflow, accessibility, and localization

- Roles/workflows changed:
- Before/after steps:
- Spanish/English result:
- Keyboard/accessibility result:
- Screenshots by role, language, viewport, state, environment, commit, and date:

## 11. Audit, evidence, and publication

- Events added/changed:
- Audit redaction/integrity tests:
- Evidence hash/version/access tests:
- Approval/publication-state tests:
- Export/manifest/retention effect:

## 12. Operations and resilience

- Configuration/environment changes:
- Deployment sequence:
- Health/readiness/metrics/logs/alerts:
- Failure-mode test:
- Backup/restore or DR evidence:
- Runbook updates:

## 13. Test commands and results

| Command/check | Environment | Result | Evidence |
|---|---|---|---|
| | | | |

Record skipped checks and why.

## 14. Known limitations and residual risks

| Item | Severity | Impact | Owner | Required follow-up/review date |
|---|---|---|---|---|
| | | | | |

## 15. Agent declaration

- [ ] Every acceptance criterion is represented truthfully.
- [ ] No required control was disabled to pass checks.
- [ ] No secrets or production personal/evidence data were committed.
- [ ] Documentation and generated contracts match implementation.
- [ ] The PR does not claim SDA acceptance or national production approval.
