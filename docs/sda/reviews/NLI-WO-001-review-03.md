# SDA Review — NLI-WO-001 — Review 03

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Pull request:** `#4 — Draft: Implement controlled database lifecycle`  
**Reviewed implementation commit:** `547a02c23a9f1ebb45f4494163dd348ff79edd54`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-13  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact PR head, Review 02 resolution log, shared schema/data invariant generator, migration runner and shared migration-state evaluator, operator and production-readiness status, fixture package and loader, runtime data module, clean-bootstrap script, restore drill, lifecycle integration tests, API workflow, frontend workflow, and API container packaging.

Independent workflow verification at the reviewed head:

- API CI run `29284434579`: **success**
  - `api-tests`: success
  - `migration-lifecycle`: success
- Frontend CI run `29284434573`: **success**

The Review 02 remediation is technically substantial and resolves four of the six open findings. Two production-path findings remain. One is an immediate runtime packaging defect that the host-based CI path does not exercise.

This review does not authorize merge, production deployment, official publication, real citizen data transition, broad agency onboarding, or retirement of an existing recovery path.

## 2. Review 02 finding disposition

| Finding | Review 03 disposition | Assessment |
|---|---|---|
| F03 | RESOLVED | API startup is compared against a deterministic full schema/data manifest covering extensions, tables, columns/types/nullability/defaults, constraints, indexes, controlled row counts, hashes, and relationships. |
| F05 | RESOLVED WITH OPERATIONAL CONDITION | Transition now validates selected structural specifications before ledger bootstrap and the representative fixture proves preservation of the AC-05 entity classes, counts, hashes, selected canonical-record fields, relationships, and ledger state. A real pilot transition still requires the prescribed backup and before/after evidence. |
| F06 | RESOLVED | Fixture reload is deterministic for owned records, non-owned collisions fail closed, cleanup follows ownership, and runtime `app.data` retains only the module inventory. |
| F08 | OPEN | The default containerized bootstrap/runtime path is not valid: the API imports `infra/scripts/migration_state.py`, but the API Docker image does not copy that module. Host-based CI and host API smoke bypass the defect. |
| F09 | RESOLVED | Source and restored invariant manifests are compared in both the restore drill and CI dump/restore lane; migration ledger and PostGIS state are also checked. |
| F10 | PARTIALLY RESOLVED — OPEN | Pending, checksum, filename, unknown-ledger, unreadable database, and missing database configuration are handled consistently. Missing, empty, or invalid migration-package configuration can still evaluate as current on an empty database. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 | PASS | Empty PostGIS database is created by ordered migrations and exercised by API/lifecycle CI. | — |
| AC-02 | PASS | Complete ordered ledger includes filenames, checksums, applied time/context and reports current. | — |
| AC-03 | PASS | Applied content and filename drift fail closed without rewriting ledger. | — |
| AC-04 | PASS | Failure rollback/later-stop and concurrent runner behavior are DB-backed and green. | — |
| AC-05 | PASS WITH OPERATIONAL CONDITION | Representative transition preserves named entity classes, hashes, relationships, and canonical fields. | A real pilot transition must use backup plus captured before/after manifests. |
| AC-06 | PASS | Full schema/data fingerprint is unchanged around real API startup. | — |
| AC-07 | FAIL | Known pending migration behavior is correct. | F10: missing/empty migration-package state can be falsely current on an empty configured database. |
| AC-08 | PASS WITH CONDITION | Reference package is explicit, idempotent, history-backed, conflict-aware, and drift-rejecting. | Institutional authority remains provisional as recorded. |
| AC-09 | PASS | Fixtures are explicit, environment-restricted, deterministic, ownership-tracked, collision-safe, and cleanable. | — |
| AC-10 | PASS | Existing user credential/session state is preserved by migration/reference/startup paths. | — |
| AC-11 | FAIL | Host-based lifecycle and smoke paths pass. | F08: the documented/default Compose API image cannot import its new runtime dependency and is not tested in the workflow. |
| AC-12 | PASS | Real PostgreSQL/PostGIS API and lifecycle jobs are green. | — |
| AC-13 | PASS | Dump/restore compares source/restored invariant manifests and verifies ledger/PostGIS state. | — |
| AC-14 | FAIL | Lifecycle sequencing and host-safe behavior are documented. | F08/F10: the default container path is broken and missing migration-package configuration is not fail-closed. |
| AC-15 | CONDITION | Current API/frontend gates are green. | They do not build/import/boot the actual API runtime image. |

## 4. Open findings

### NLI-WO-001-F08 — Actual API container omits the shared migration-state runtime module

**Class:** BLOCKER  
**Affected criteria:** AC-11, AC-14, AC-15  
**Observation:** `services/api/app/ops_status.py` adds `<repo>/infra/scripts` to `sys.path` and imports `migration_state` during application import. `services/api/Dockerfile` copies `services/api/app`, `infra/migrations`, and tests, but does not copy `infra/scripts/migration_state.py` or an equivalent installed package. The final API workflow starts Uvicorn directly from the checked-out repository, and the recorded local bootstrap proof uses the host API path, so both have access to repository scripts and bypass the image defect.  
**Risk/consequence:** The normal Compose API container can fail at startup with `ModuleNotFoundError: migration_state`, despite all current workflows being green. This invalidates the default bootstrap/runtime path.  
**Required resolution:** Package the shared evaluator as a real runtime dependency—either move it into an importable application/shared package used by both API and CLI, or explicitly copy/install it in the API image. Add a CI gate that builds the actual API Dockerfile and at minimum imports `app.main`; preferably boot the image against the PostGIS service and verify health plus migration/production-readiness endpoints. Prove the default `HOST_API=0` bootstrap path or equivalent Compose path.  
**Disposition:** OPEN

### NLI-WO-001-F10 — Missing or empty migration package can still be reported current

**Class:** BLOCKER  
**Affected requirements:** R2, R5, R9, R14; AC-07, AC-14  
**Observation:** `migration_state.migration_files()` returns an empty expected list when the migration directory is missing. `ops_status._migration_files()` also converts parsing errors into an empty list. With a configured but empty database and no ledger, `evaluate_migration_state(conn, [])` returns `current`; `production_readiness_status()` can therefore mark explicit migrations ready if other production settings are supplied. The CLI runner likewise permits an empty migrations directory to create only its ledger and report current.  
**Risk/consequence:** A fresh deployment with a missing, empty, or invalid migration package can be falsely represented as migration-ready even though no operational schema exists.  
**Required resolution:** Treat missing, empty, duplicate-version, or invalid migration packages as an explicit non-current/error state. Do not collapse migration-file parsing failures into an empty expected set. Make CLI apply/status fail non-zero before ledger creation when no valid migrations exist. Add DB/API tests proving production readiness remains non-ready for missing, empty, and invalid migration directories.  
**Disposition:** OPEN

## 5. Resolved controls worth preserving

- Migration-only runtime authority and throwing `init_db()` guard.
- Shared checksum/filename/unknown/pending evaluator for normal valid packages.
- Full startup schema/data invariance manifest.
- Representative transition no-loss evidence and pre-ledger drift rejection.
- Deterministic package-owned fixture reload and cleanup.
- Runtime removal of legacy seed and operational example constants.
- Reference-data history and package-drift rejection.
- Smoke-capable lifecycle CI.
- Source/restored invariant equality checks.
- Green API and frontend workflows at the reviewed implementation head.

## 6. Evidence assessment

The evidence is now acceptance-grade for the controls it exercises. The remaining defects are outside the exercised host-based runtime boundary: one is packaging of a required module into the actual API image; the other is fail-closed treatment of absent/invalid migration packages. Both are narrow and directly testable.

## 7. Decision

`REWORK REQUIRED`

The work order is close to acceptance. Resolve F08 and F10 only; preserve the already accepted behavior. Do not merge until an exact-head Review 04 verifies the actual API image/runtime and fail-closed missing-package behavior.

## 8. Required follow-up

1. Resolve F08 and F10 on the same branch.
2. Add actual API image build/import/boot evidence and missing/empty/invalid migration-package tests.
3. Update the evidence and Review 03 resolution log to the final implementation head.
4. Obtain green API and frontend workflows at that head.
5. Request SDA Review 04.

## 9. Review 03 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F08 | Resolved in implementation: migration-state evaluator moved into the runtime package as `app.migration_state`; API/operator code imports it directly without `infra/scripts` path injection; `infra/scripts/migration_state.py` is only a compatibility entrypoint; API CI now builds `services/api/Dockerfile`, imports `app.main` inside the image, boots the image against PostGIS, and verifies `/api/v1/health`, `/api/v1/operator/migrations/status`, and `/api/v1/operator/production-readiness`. `.dockerignore` excludes local runtime `data/` from the image build context. | Fixing commit `6207d1338f477bca361e3bb09b8744e63184d9ee`; local evidence: `python3 -m py_compile ...` passed; full API suite `200 passed`; frontend `npm --prefix apps/admin-portal run test:ci` passed; local Docker image proof built `services/api/Dockerfile`, ran `docker run --rm eg-addressing-api-review03 python -c "import app.main"`, booted image on port 8120, and returned 200 for health, migrations status (`current`), and production-readiness (`needs_work`). | READY FOR SDA REVIEW 04 | 2026-07-13 |
| F10 | Resolved in implementation: missing, empty, invalid-name, and duplicate-version migration packages now raise explicit `MigrationPackageError` states; `migrate.py status/apply` exit non-zero before connecting/creating the ledger when the package is invalid; API operator status and production-readiness return non-current/non-ready for all four states instead of converting parse failures to an empty expected set. | Fixing commit `6207d1338f477bca361e3bb09b8744e63184d9ee`; local evidence: lifecycle integration suite `23 passed`; new parameterized tests `test_cli_fails_before_ledger_for_invalid_migration_packages` and `test_operator_and_production_readiness_fail_closed_for_invalid_migration_packages`; full API suite `200 passed`. | READY FOR SDA REVIEW 04 | 2026-07-13 |
