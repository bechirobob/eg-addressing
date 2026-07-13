# Implementation Plan — NLI-WO-001

**Work order:** [`NLI-WO-001 — Controlled Database and Reference-Data Lifecycle`](../work-orders/NLI-WO-001-controlled-database-lifecycle.md)  
**Implementation branch:** `nli/wo-001-controlled-database-lifecycle`  
**Planning commit:** `216a55b`  
**Prepared by:** `Implementation Agent`  
**Status:** `ACCEPTED FOR IMPLEMENTATION`

> Complete this plan before modifying implementation files. Map every acceptance criterion. Do not remove sections; use `NOT APPLICABLE` with a reason.

## 1. Objective understood

Remove database schema creation, schema alteration, reference-data loading, and demonstration fixture mutation from ordinary API/worker startup. After implementation, a new empty PostgreSQL/PostGIS database is built through an explicit, ordered, checksummed migration process; reference data and fixtures are loaded by separate explicit commands; an existing pilot database has a documented transition path; API startup is non-mutating and reports migration/reference readiness truthfully.

## 2. Current implementation inspected

- Repository authority: `AGENTS.md`, `docs/sda/README.md`, active work order.
- Mandatory reading: `docs/sda/charter.md`, `architecture-baseline.md`, `target-reference-architecture.md`, `risk-register.md`, ADR-001, ADR-002, ADR-003, and required standards for data/migrations, security, testing/release, operations/DR, documentation/records.
- Startup/bootstrap: `services/api/app/main.py` lifespan calls `init_db()`; `services/api/app/db.py` has `_ensure_schema()` and `init_db()` with schema DDL plus reference/demo/pilot seed mutation.
- Migrations: `infra/migrations/001_schema_migration_baseline.sql` through `006_address_record_retirement_policy.sql`; `001` is marker only; `002–006` depend on bootstrap-created tables.
- Migration status: `services/api/app/ops_status.py` expects `schema_migrations`.
- Migration runner: `infra/scripts/run_migrations.sh` records version/filename/checksum/applied_at but lacks context, lock, empty schema creation, full status/drift handling, and transition support.
- Docker/local: `infra/docker/docker-compose.yml`, `infra/scripts/deploy_pilot_ready.sh`.
- CI: `.github/workflows/api-ci.yml`, `.github/workflows/frontend-ci.yml`.
- Tests: `services/api/tests/test_app.py`, especially migration/status/readiness/fixture tests.
- Reference/fixtures: `services/api/app/data.py` contains `PROVINCES`, `ADMIN_UNITS`, `DEMO_USERS`, operational seed examples.
- Backup/restore: `infra/scripts/backup_database.sh`, `restore_database.sh`, restore-drill references from tests.

## 3. Acceptance-criterion map

| Criterion | Planned change | Evidence/test | Files/domains | Dependency or RFI |
|---|---|---|---|---|
| AC-01 | Add `000_current_operational_schema.sql` and hardened explicit migration runner so empty PostGIS DB builds from migrations only. Remove startup DDL reliance. | Real PostGIS empty DB lifecycle test verifies tables/extensions/constraints/indexes and no API bootstrap. | `infra/migrations`, `infra/scripts`, `services/api/tests` | None |
| AC-02 | Ledger records all expected migrations with unique version, filename, SHA-256, timestamp, execution context. Status reports current. | DB integration asserts ledger rows/checksums/status. | runner/status/API ops | None |
| AC-03 | Runner/status reject checksum mismatch and never rewrite ledger. | Controlled tampered-copy test. | runner/status/tests | None |
| AC-04 | Migration apply uses transaction per migration and advisory lock; failures rollback and concurrent runner cannot double-apply. | Failure migration test; concurrency/lock test. | runner/tests | None |
| AC-05 | Add transition command for pre-WO pilot schema that verifies structure, baselines safely, applies pending migrations, and preserves data. | Representative pilot DB transition test with before/after row counts and relationships. | transition script/tests/docs | RFI only if real ledger ordering proves incompatible. |
| AC-06 | FastAPI startup no longer calls `init_db()` or DDL/refdata/fixture loaders. | Schema fingerprint + row-count snapshot before/after startup. | `main.py`, tests | None |
| AC-07 | API startup does not apply pending migration; readiness/status reports pending. | Pending migration startup test; ledger unchanged. | `main.py`, `ops_status.py`, tests | None |
| AC-08 | Reference data moved to versioned manifest/package and explicit idempotent load/status commands. | Load twice no-op; conflict/lower-authority overwrite rejected/surfaced. | `infra/reference-data`, scripts/tests | None |
| AC-09 | Development fixtures moved behind explicit allowlisted load/cleanup commands; production-labeled env refuses. | Allowed load/cleanup and production refusal tests. | `infra/fixtures`, scripts/tests | None |
| AC-10 | Migration/refdata/startup preserve existing user hash, role, active state, sessions. | Integration test around user/session snapshots. | scripts/db/tests | None |
| AC-11 | Local bootstrap command runs services → migrations → refdata → optional fixtures → health/readiness/smoke. | Local/CI equivalent bootstrap result. | `infra/scripts/bootstrap_local.sh`, README/runbooks | None |
| AC-12 | API CI uses real PostGIS service for lifecycle tests. | GitHub Actions config and local equivalent proof. | `.github/workflows/api-ci.yml` | None |
| AC-13 | Backup/restore validation includes migration-ledger current/checksum integrity. | Restore into disposable DB, ledger and row-count validation. | backup/restore scripts/tests | None |
| AC-14 | Docs/env/runbooks describe commands, sequencing, failure handling, no startup schema setup. | Docs diff and grep check. | README/env/docs | None |
| AC-15 | Existing backend/frontend/contract/guard checks preserved and pass. | pytest, frontend CI/contract when affected, shell syntax checks. | repo quality gates | None |

## 4. Proposed file and module changes

### Add

- `infra/migrations/000_current_operational_schema.sql` — initial executable schema migration for empty DBs.
- `infra/reference-data/manifest.json` — reference package metadata.
- `infra/reference-data/eg-admin-units-v1.json` — governed provinces/admin units package.
- `infra/fixtures/development-fixtures.json` — explicit non-production demo/training fixture package if useful.
- `infra/scripts/migrate.py` — maintained migration runner with lock, checksums, status, apply, transition support.
- `infra/scripts/migration_status.py` — CLI status wrapper if separate from runner.
- `infra/scripts/load_reference_data.py` — explicit reference-data load/status command.
- `infra/scripts/load_development_fixtures.py` — explicit allowlisted fixture load command.
- `infra/scripts/cleanup_development_fixtures.py` — explicit fixture cleanup command.
- `infra/scripts/bootstrap_local.sh` — local lifecycle bootstrap wrapper.
- `infra/scripts/transition_pilot_database.py` — existing pilot transition wrapper if not built into `migrate.py`.
- `services/api/tests/test_database_lifecycle.py` — real PostGIS lifecycle tests.
- `services/api/tests/test_startup_invariance.py` — startup mutation tests if split from lifecycle tests.
- `docs/sda/implementation-plans/NLI-WO-001-controlled-database-lifecycle.md` — this plan.

### Modify

- `services/api/app/main.py` — remove `init_db()` lifespan mutation and keep non-mutating startup.
- `services/api/app/db.py` — separate runtime DB functions from deprecated bootstrap helpers; remove normal startup dependency on seed mutation.
- `services/api/app/ops_status.py` — richer migration/reference readiness diagnostics.
- `services/api/app/security_posture.py` — report controlled lifecycle/default credential state accurately.
- `infra/scripts/run_migrations.sh` — delegate to or wrap the maintained runner.
- `infra/scripts/deploy_pilot_ready.sh` — call explicit lifecycle commands.
- `infra/scripts/backup_database.sh` — preserve compatibility if ledger validation is required.
- `infra/scripts/restore_database.sh` / `restore_drill.sh` if present — validate ledger after restore.
- `.github/workflows/api-ci.yml` — real PostGIS lifecycle CI.
- `.github/workflows/frontend-ci.yml` only if generated API contract changes require it.
- `README.md`, `env/.env.example`, `env/.env.production.example`, `env/.env.staging.example`, relevant runbooks — safe operator lifecycle docs.
- Existing tests that assert old bootstrap behavior — update to assert explicit lifecycle behavior.

### Remove or deprecate

- Deprecate normal use of `init_db()` for application startup. It may be retained temporarily only as a test/transition helper if not reachable from controlled startup. Final code must not rely on it for ordinary app startup.

## 5. Data and migration impact

- Schema changes: introduce migration-created full current operational schema through `000_current_operational_schema.sql`; no edits to `001–006`.
- New/changed migration files: add `000`; preserve `001–006` byte-for-byte.
- Reference-data changes: move provinces/admin units to explicit versioned package with manifest.
- Fixture changes: move demo identities and operational examples behind explicit environment-guarded fixture commands.
- Existing-data transition: backup first; verify structure; ledger-baseline compatible existing schema; preserve operational rows and sessions; apply only missing migrations.
- Compatibility/deployment sequence: backup → status → transition or migrate → reference-data load/status → app start → readiness/smoke.
- Rollback or forward recovery: no destructive migrations; recovery through restore backup or forward-fix migration; startup never repairs silently.
- Empty-database and upgrade test approach: real PostGIS empty DB plus representative pre-WO pilot DB transition.

## 6. API and integration impact

- Routes/contracts changed: likely operator migration/reference status fields may expand; no public API behavior change intended.
- OpenAPI/generated types: regenerate if operator response schema changes are reflected in FastAPI docs.
- Compatibility classification: backwards-compatible operational-readiness/status additions.
- Idempotency/concurrency: migration runner advisory lock; reference-data load idempotent.
- Public/operator/partner projections: no public/partner projection change planned.
- External dependencies: no new external service; Python stdlib/psycopg preferred.

## 7. Identity, security, privacy, and audit impact

- Authentication/session effect: startup/migration/refdata must preserve users/sessions.
- Roles/permissions/scopes: no new role or permission model.
- Sensitive data/classification: fixture data explicitly non-official; no production data copied into tests.
- Threats or abuse cases: unauthorized fixture load, migration drift, checksum tampering, concurrent migration, default credential creation.
- Secrets/keys: no secrets committed; environment templates only contain names and safe defaults.
- Audit events: fixture cleanup/load may log operator maintenance where run against app DB; migration ledger records execution context.
- Security tests/scans: fixture production refusal, default credential prevention, secret grep before PR.

## 8. GIS/location impact

- Geometry classes/CRS/provenance: preserve existing PostGIS address-record geometry migration `005`; no new geometry authority.
- Address/location identifiers: unchanged.
- Map/geocoder behavior: unchanged.
- Spatial constraints/indexes/tests: empty DB must validate PostGIS extension and existing geometry/index migrations.

## 9. Workflow, accessibility, and localization impact

- Roles and workflows affected: operator/developer lifecycle only; no citizen UI workflow change.
- Before/after steps: local/dev setup now explicit lifecycle before app readiness instead of API startup seeding.
- Spanish/English changes: not applicable except docs if touched; no UI localization change planned.
- Accessibility checks: no UI changes expected; existing guards still run if frontend touched.
- Required screenshots/viewports/states: not required unless operator UI changes; current plan is API/status/script/doc work.

## 10. Operations and recovery impact

- Environment/configuration: add explicit allowlist envs for fixtures and controlled lifecycle env names.
- Deployment sequence: backup/status/migrate/refdata/start/readiness/smoke.
- Health/readiness/metrics/logs/alerts: liveness remains connectivity/app process; readiness reflects pending/mismatched migrations/reference state.
- Backup/restore effect: restore drill validates ledger current and selected row invariants.
- Failure behavior: migration failure non-zero, no ledger record; pending/mismatch produces non-ready diagnostics.
- Runbooks: update local bootstrap, controlled transition, backup/restore, failure handling.

## 11. Test plan

- static/type/build: `python -m py_compile` for scripts; existing frontend build/CI if affected.
- unit/domain: runner filename/order/checksum parsing; reference-data conflict logic; fixture guard logic.
- database/migration: real PostGIS empty apply, mismatch, failure rollback, concurrency, transition, startup invariance, pending status.
- authorization allow/deny: operator status endpoints remain authenticated; fixture cleanup/load API if exposed remains admin-only.
- API contract: regenerate/check generated types if OpenAPI changes.
- workflow/browser: not planned unless operator UI changes.
- accessibility/localization: existing guards if frontend touched.
- security/abuse: production fixture refusal, no default credential creation/reset, no secret leakage.
- performance/failure/recovery: migration failure/concurrency and restore ledger validation.
- repository quality guards: backend tests, frontend contract/CI if affected, shell syntax checks, git diff review.

## 12. Implementation sequence

1. Add RED lifecycle tests that fail against current startup/bootstrap behavior.
2. Add `000` schema migration generated from current `_ensure_schema()` and verify `001–006` unchanged.
3. Replace/harden migration runner and status logic.
4. Remove API startup mutation.
5. Extract reference-data package and command.
6. Extract fixture package/load/cleanup commands and production refusal.
7. Add transition command and representative transition test.
8. Update local bootstrap/deploy/backup/restore scripts.
9. Update CI and docs/env/runbooks.
10. Run evidence suite, commit, push, open draft PR with required evidence.

## 13. RFIs and decisions required

- `NLI-RFI-001`: GitHub issue #3 is inaccessible from this environment (`404` via public API). The repository work-order docs are present and sufficient for implementation; if issue #3 contains private extra constraints, copy them into the repo or provide them. This does not block implementation under the current authoritative work-order text.

## 14. Risks and assumptions

| Risk/assumption | Effect | Mitigation/validation | Owner |
|---|---|---|---|
| Translating `_ensure_schema()` into `000` may miss a column/index | Empty DB could pass partial schema only | Real PostGIS table/column/index tests and app tests | Implementation Agent |
| Existing pilot DB may drift from repository-known schema | Transition may be unsafe | Fail closed with structure checks and backup requirement | Implementation Agent/SDA |
| Existing tests assume `init_db()` seed side effects | Test suite may need careful rewrite | Replace with explicit lifecycle fixtures; do not weaken assertions | Implementation Agent |
| Fixture cleanup can break FK chains | Data loss or failed cleanup | FK-safe deterministic cleanup tests | Implementation Agent |
| CI PostGIS increases runtime | Slower PR checks | Keep integration tests focused but real | Implementation Agent |

## 15. Completion declaration

- [x] Every acceptance criterion is mapped.
- [x] No prohibited approach is planned.
- [x] Database/API/security/workflow/operations effects are explicit.
- [x] Required RFIs have been raised.
- [x] The plan does not claim SDA acceptance.
