# Pull Request Evidence — NLI-WO-001

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Implementation plan:** `docs/sda/implementation-plans/NLI-WO-001-controlled-database-lifecycle.md`  
**Branch:** `nli/wo-001-controlled-database-lifecycle`  
**Head commit:** `TBD after commit`  
**Prepared by:** Hermes implementation agent

> This evidence does not claim SDA acceptance. The SDA must review the exact PR head commit against all 15 acceptance criteria.

## 1. Outcome

Implemented controlled database lifecycle for the NLI pilot:

- API startup no longer creates schema or seeds users/reference data.
- Empty PostGIS databases can be built by ordered migrations.
- Existing `001–006` migration files were preserved byte-for-byte and checksum-stable.
- Added `000_current_operational_schema.sql` as an idempotent pre-baseline schema bridge.
- Added checksum-ledger migration runner with advisory lock and transition mode.
- Added governed reference-data loader and explicit non-production fixture loader/cleanup.
- Added CI PostGIS lifecycle rehearsal.
- Restore drill now validates migration ledger and PostGIS after restore.

Readiness boundary: this is implementation/evidence for SDA review. It is not SDA acceptance and not national production approval.

## 2. Acceptance criteria

| Criterion | Status | Implementation | Evidence/test | Residual condition |
|---|---|---|---|---|
| AC-01 | PASS | `000_current_operational_schema.sql` + runner creates schema from empty PostGIS DB. | Empty DB proof: ledger `7`, PostGIS `1`, required tables present. | SDA to review generated SQL bridge. |
| AC-02 | PASS | `infra/scripts/migrate.py` records version, filename, checksum, applied_at, execution_context. | `migrate.py apply/status`; live status current. | None known. |
| AC-03 | PASS | Runner fails on checksum mismatch before applying pending work. | Source test checks checksum-mismatch controls; runner status exposes mismatch. | Add future negative DB fixture if SDA requests. |
| AC-04 | PASS | Per-migration transaction and advisory lock. | Source test verifies `pg_advisory_lock`; empty DB apply successful. | Concurrency stress can be expanded later. |
| AC-05 | PASS | `transition-pilot` validates existing pilot tables, executes idempotent `000`, preserves data, applies/skips rest. | Transition proof preserved before/after counts and ledger `7`. Live pilot transitioned successfully. | Existing pilot drift outside tested tables still fails closed. |
| AC-06 | PASS | FastAPI lifespan no longer calls `init_db()`. | `test_api_lifespan_does_not_call_init_db`; backend suite passed. | None. |
| AC-07 | PASS | API startup does not run migration runner. Status remains read-only via `ops_status.py`. | Startup invariance test; code inspection. | Pending-status DB negative integration can be expanded later. |
| AC-08 | PASS | `infra/reference-data/` package + idempotent loader + metadata table. | First reference load `74`, second load `0`. | Formal source authority may need government signoff. |
| AC-09 | PASS | Fixtures behind explicit `EG_ALLOW_DEV_FIXTURES=YES`, allowed `APP_ENV`, and external password. Cleanup provided. | Production fixture refusal; allowed test load/cleanup. | Operational sample records remain controlled by command path; further fixture package expansion possible. |
| AC-10 | PASS | Fixture loader preserves existing password hash/is_active on conflict; startup/migrate/reference do not alter credentials. | Backend tests pass; loader SQL preserves hash/status; production refusal proof. | Add explicit credential-preservation DB test if requested. |
| AC-11 | PASS | Added `infra/scripts/bootstrap_local.sh` for migrate + reference data + optional fixtures. | Shell syntax check passed. | Full clean-machine bootstrap depends on local env values. |
| AC-12 | PASS | GitHub API CI uses `postgis/postgis:16-3.4` service and lifecycle rehearsal. | Workflow YAML validates. Local equivalent lifecycle commands passed. | GitHub CI still must run on PR. |
| AC-13 | PASS | Restore drill validates migration ledger rows/checksums and PostGIS. | Restore drill passed with matching live/restored counts and ledger rows `7`. | Backup artifact remains local/ignored. |
| AC-14 | PASS | README/env templates/implementation plan updated with controlled lifecycle. | Docs changed in PR. | Additional operator runbook polish may be useful after SDA review. |
| AC-15 | PASS | Existing backend/frontend gates preserved; new lifecycle tests added. | Backend `175 passed`; frontend `test:ci` passed. | Warnings from existing httpx cookie deprecation remain. |

## 3. Change inventory

### Added

- `infra/migrations/000_current_operational_schema.sql` — migration-only schema bridge before legacy baseline.
- `infra/scripts/migrate.py` — controlled migration runner.
- `infra/scripts/load_reference_data.py` — governed reference data loader/status.
- `infra/scripts/load_development_fixtures.py` — explicit non-production fixture load/cleanup.
- `infra/scripts/bootstrap_local.sh` — local lifecycle bootstrap.
- `infra/reference-data/manifest.json` — reference-data manifest.
- `infra/reference-data/eg-admin-units-v1.json` — province/admin-unit reference package.
- `services/api/tests/test_database_lifecycle.py` — lifecycle/startup/source controls.
- `docs/sda/implementation-plans/NLI-WO-001-controlled-database-lifecycle.md` — formal plan.
- `docs/sda/evidence/NLI-WO-001-pull-request-evidence.md` — this evidence file.

### Modified

- `.github/workflows/api-ci.yml` — real PostGIS service and lifecycle rehearsal.
- `README.md` — controlled lifecycle commands and transition note.
- `env/.env.example` — fixture guidance.
- `env/.env.production.example` — fixture disabled flag.
- `infra/scripts/run_migrations.sh` — wrapper delegates to Python runner.
- `infra/scripts/restore_drill.sh` — validates ledger/PostGIS after restore.
- `services/api/app/main.py` — startup no longer runs `init_db()`.
- `services/api/app/data.py` — removed source-controlled demo-user passwords.
- `services/api/app/db.py` — default legacy demo passwords disabled/rejected; deprecated bootstrap assigns inaccessible random hashes unless explicit fixture password supplied.

### Removed/deprecated

- Application startup schema/data mutation deprecated. `init_db()` remains only as legacy/pre-transition helper and is no longer called by FastAPI lifespan.

## 4. Architecture alignment

- ADRs followed: ADR-001 modular monolith, ADR-002 PostgreSQL/PostGIS system of record, ADR-003 migration-only schema lifecycle.
- Standards followed: data/migrations, security, testing/release, operations/DR, documentation/records.
- Domain boundaries affected: database lifecycle, reference data, fixture data, API startup, operations/CI.
- Deviations/RFIs: `RFI-001` — GitHub issue #3 was inaccessible via unauthenticated API (`404`), so repo work-order docs governed implementation.
- New dependencies/services: no new runtime dependency; CI uses PostGIS service image.

## 5. Database and migrations

- Existing `001–006` checksums preserved:
  - `001` `cca14e756c74f4820634cfc3a8c0c2de09b3645cfcd79822bcfe111635dfd2bb`
  - `002` `591f96fb3a0f723a9c5858cd390dd1994d9aa7815f43ac0942d689786684d919`
  - `003` `26cf76bfdf1ba634579e55f924d5e978606e195cd6a33bd65f1a1f284621f215`
  - `004` `1d6c30eedcb6111703a62d2595aa4700cdb8bb8d79f2a3eb307ad1f5b5cb8e39`
  - `005` `b97febc89d5bc94b3dd5d0d1a0f77f03395aee5616eeae755f3ad30872d003c5`
  - `006` `e6c0f3dd0508ff32ae5f12e52bfa6f68b065e356424c335e440bcd96b3161408`
- Empty database result: `{"case":"empty","ledger":7,"postgis":1}`.
- Previous-version upgrade result: transition proof before/after counts identical; ledger `7`; PostGIS `1`.
- Data/backfill validation: live transition and representative transition preserved counts for users, territories, roads, buildings, addresses, address_records, geotag submissions, field submissions, audit logs.
- Lock/duration evidence: runner uses `pg_advisory_lock` and transaction per migration.
- Reference/fixture behavior: reference first load `74`, second load `0`; production fixture load refused; allowed fixture load/cleanup worked.
- Rollback/forward recovery: failed migration transactions are not ledgered; restore drill validates backup recoverability.
- Backup/restore effect: restore drill passed after transition; restored counts matched live counts.

## 6. API and contracts

- OpenAPI diff: no intentional API contract changes.
- Generated type/client diff: `npm --prefix apps/admin-portal run generate:api-types`; `git diff --exit-code apps/admin-portal/components/apiTypes.ts` passed.
- Compatibility classification: operational behavior change only; API startup must be preceded by lifecycle commands.
- Validation/error/idempotency/pagination tests: existing backend suite passed.
- Public/protected/partner projection tests: existing backend/frontend guard suites passed.

## 7. Identity and authorization

- Permissions/scopes changed: none.
- Allow tests: existing auth/role tests passed.
- Deny and cross-scope tests: existing auth/role tests passed.
- Session/credential effects: no startup/migration/reference overwrite of existing credentials; fixture loader preserves existing hashes/status on conflict and refuses production-like environments.
- Segregation-of-duty/step-up tests: not changed.

## 8. Security and privacy

- Threat/abuse analysis: removed startup mutation; explicit lifecycle reduces accidental schema/data mutation and default credential creation.
- Secret scan: no source-controlled demo passwords in `DEMO_USERS`; old password strings appear only in tests/rejection assertions.
- Dependency/SAST/container scan: no dependency added. CI service image added for PostGIS test.
- Data-classification/privacy effect: no production personal data committed.
- File/evidence protections: backup/restore artifacts remain local/ignored.
- Residual security risk: legacy rejection list contains known old passwords as deny-list test data; not usable unless `ALLOW_DEFAULT_DEMO_PASSWORDS=true`, which templates disable.

## 9. GIS/location evidence

- Geometry/CRS/provenance effect: schema bridge includes PostGIS extension before existing geometry migration.
- Spatial constraints/index/query evidence: existing `005` PostGIS migration remains unchanged and applied.
- Address/location-code effect: no public code generation change.
- External map/geocoder effect: none.

## 10. Workflow, accessibility, and localization

- Roles/workflows changed: operator workflow changed from startup bootstrap to explicit lifecycle commands.
- Before/after steps: README documents `migrate -> reference data -> optional fixtures -> status`.
- Spanish/English result: no UI text change.
- Keyboard/accessibility result: no UI control change.
- Screenshots: not applicable; non-UI infrastructure work order.

## 11. Audit, evidence, and publication

- Events added/changed: migration ledger and lifecycle metadata records.
- Audit redaction/integrity tests: no audit-log schema behavior changed.
- Evidence hash/version/access tests: migration checksums and reference package checksum recorded.
- Approval/publication-state tests: not changed.
- Export/manifest/retention effect: reference-data manifest added.

## 12. Operations and resilience

- Configuration/environment changes: `EG_ALLOW_DEV_FIXTURES` documented; production template disables fixtures.
- Deployment sequence: backup, `transition-pilot` for existing pilot DB, `apply`, `load_reference_data`, API start.
- Health/readiness/metrics/logs/alerts: migration status remains read-only; CI rehearses lifecycle.
- Failure-mode test: malformed migration names remain rejected before SQL; production fixtures refuse.
- Backup/restore or DR evidence: restore drill passed with ledger validation.
- Runbook updates: README and implementation plan updated.

## 13. Test commands and results

| Command/check | Environment | Result | Evidence |
|---|---|---|---|
| `PYTHONPATH=. .venv/bin/python -m pytest -q tests/test_database_lifecycle.py` | local API venv | PASS | `5 passed` |
| `PYTHONPATH=. .venv/bin/python -m pytest -q` | local API venv | PASS | `175 passed, 5 warnings` |
| Empty DB migration proof | local Docker PostGIS | PASS | ledger `7`, PostGIS `1` |
| Reference idempotency | local Docker PostGIS | PASS | first `74`, second `0` |
| Fixture production refusal | local Docker PostGIS | PASS | refused with production app env |
| Fixture load/cleanup | local Docker PostGIS | PASS | users `4 -> 0`, batch cleaned |
| Transition proof | local Docker PostGIS | PASS | before/after counts identical, ledger `7` |
| Live pilot transition | local pilot Docker PostGIS | PASS | applied `000`, skipped `001–006`, status current |
| `infra/scripts/restore_drill.sh` | local pilot Docker PostGIS | PASS | restored/live counts match; ledger rows `7`; PostGIS `1` |
| `npm --prefix apps/admin-portal run generate:api-types` | local frontend | PASS | 105 operations generated |
| `git diff --exit-code apps/admin-portal/components/apiTypes.ts` | local frontend | PASS | no diff |
| `npm --prefix apps/admin-portal run test:ci` | local frontend | PASS | build and guards passed |
| `python3 -m py_compile ...` | local | PASS | no syntax errors |
| workflow YAML parse | local | PASS | `api-ci.yml yaml-ok` |

Skipped: GitHub Actions remote CI not yet run until PR is opened.

## 14. Known limitations and residual risks

| Item | Severity | Impact | Owner | Required follow-up/review date |
|---|---|---|---|---|
| GitHub issue #3 inaccessible from local unauthenticated API | Low | Repo work-order docs governed implementation; issue-specific hidden notes unknown | SDA / repo admin | Before final acceptance |
| Legacy `init_db()` remains in code as deprecated helper | Medium | Could be misused outside startup if called directly | SDA/backend | Review whether to remove in later WO |
| `000` generated from historical bootstrap DDL | Medium | Needs SDA review for exact schema fidelity and future cleanup | SDA/backend | This PR review |
| Existing old password strings remain only in tests/rejection deny-list | Low | Not usable under default config; supports regression tests | Security/SDA | This PR review |
| GitHub CI must run remotely | Medium | Local evidence is strong but not remote CI proof | GitHub Actions | PR validation |

## 15. Agent declaration

- [x] Every acceptance criterion is represented truthfully.
- [x] No required control was disabled to pass checks.
- [x] No secrets or production personal/evidence data were committed.
- [x] Documentation and generated contracts match implementation.
- [x] The PR does not claim SDA acceptance or national production approval.
