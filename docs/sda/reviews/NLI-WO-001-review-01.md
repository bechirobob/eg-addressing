# SDA Review — NLI-WO-001

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Pull request:** `#4 — Draft: Implement controlled database lifecycle`  
**Reviewed commit:** `affc2bf93ae2f44734f30eaa36af228e426383d8`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-13  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the pull-request metadata, current head, changed-file inventory, migration runner, initial schema migration, API startup change, reference-data and fixture loaders, lifecycle tests, CI workflow, local bootstrap/wrapper scripts, README instructions, and submitted implementation evidence.

The frontend workflow completed successfully. The API workflow for the reviewed head failed during `Run API tests`; the controlled migration lifecycle rehearsal was consequently skipped. Local results stated in the PR were considered implementation-agent evidence but are not independent SDA acceptance evidence.

This review does not authorize merge, national production, official publication, broad agency onboarding, real citizen data migration, or destructive pilot-data changes.

## 2. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 | CONDITION | `000` migration and runner exist; local empty-DB result claimed | Remote lifecycle rehearsal did not run; F01/F03 |
| AC-02 | CONDITION | Ledger records version, filename, checksum, time/context | No complete DB-backed assertion of all fields and drift; F03 |
| AC-03 | FAIL | Source-string assertion only | Required checksum-mismatch database test is absent; F03 |
| AC-04 | FAIL | Advisory-lock code and source-string assertion | Failed-migration and concurrent-runner tests are absent; F03/F05 |
| AC-05 | FAIL | Table-name transition check and claimed local counts | Structural compatibility validation is insufficient and not automated in CI; F05 |
| AC-06 | FAIL | Lifespan call removed; monkeypatch test | Required real schema/row fingerprint before/after startup is absent; F03 |
| AC-07 | FAIL | Code inspection only | Required pending-migration database/readiness test is absent; F03 |
| AC-08 | FAIL | Explicit loader and claimed idempotent local run | Loader/status can create schema outside migrations; package history/drift behavior incomplete; F04/F07 |
| AC-09 | FAIL | Environment refusal implemented | Fixture loader can create schema and cleanup can delete pre-existing reserved-ID users; legacy seed path remains; F04/F06 |
| AC-10 | FAIL | SQL inspection only | No DB-backed credential/session preservation test; legacy bootstrap remains executable; F03/F04 |
| AC-11 | FAIL | Script and shell syntax only | Normal `.env` uses Docker hostname while script runs on host; full bootstrap is not proven; F08 |
| AC-12 | FAIL | PostGIS service added to workflow | Current API workflow failed and lifecycle step was skipped; F01 |
| AC-13 | CONDITION | Restore script changed; local result claimed | Durable, reviewed-head recovery evidence is not attached/automated; F01/F09 |
| AC-14 | FAIL | README and templates changed | Instructions contain an unproven/broken host-vs-container connection path; F08/F09 |
| AC-15 | FAIL | Frontend passed | API CI failed; evidence claims all gates passed; F01/F02 |

## 3. Findings

### NLI-WO-001-F01 — Current reviewed head has failing API CI

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-12, AC-13, AC-15  
**Observation:** On head `affc2bf9`, GitHub Actions run `29272661679` completed with `api-ci` failure. The `Run API tests` step failed and the controlled migration lifecycle rehearsal was skipped. Frontend CI passed.  
**Risk/consequence:** The PR cannot demonstrate that the changed test suite or the required real-PostGIS lifecycle works in the controlled pipeline.  
**Required resolution:** Fix the API test failure, ensure the lifecycle rehearsal executes, and obtain successful remote API and frontend runs at the final reviewed head. Prefer a dedicated lifecycle job or ordering that prevents unrelated test failure from silently removing all migration evidence.  
**Disposition:** OPEN

### NLI-WO-001-F02 — Evidence is stale and materially overstates acceptance

**Class:** BLOCKER  
**Affected criteria:** all; `AGENTS.md` evidence contract  
**Observation:** The PR body names evidence head `edd2ce4`, while the actual reviewed head is `affc2bf9`. The evidence file still says `TBD after commit`. It marks all 15 criteria `PASS` despite the failed API workflow and explicitly admits that several required database tests were not performed.  
**Risk/consequence:** Review records cannot be tied to a reproducible commit, and programme readiness could be overstated.  
**Required resolution:** After all code/test changes, update the PR body and evidence file to the exact final head, replace unsupported `PASS` claims with truthful status, and link durable CI/artifact evidence.  
**Disposition:** OPEN

### NLI-WO-001-F03 — Required DB-backed negative and invariance tests are missing

**Class:** BLOCKER  
**Affected criteria:** AC-02, AC-03, AC-04, AC-06, AC-07, AC-10, AC-12  
**Observation:** `test_database_lifecycle.py` primarily checks source strings and file existence. The startup test only monkeypatches `init_db`. It does not exercise a real database. There are no automated tests that alter an applied migration and assert mismatch/non-readiness, inject a failing migration and prove no ledger entry/later execution, run concurrent migration processes, fingerprint schema and protected row counts around real API startup, leave a migration pending and verify no auto-apply plus non-ready status, or prove password/role/activation/session preservation.  
**Risk/consequence:** The most important acceptance controls can regress while source-text tests remain green.  
**Required resolution:** Add real PostgreSQL/PostGIS integration tests for every scenario named above and run them in CI. Tests must assert database state, return codes, readiness payloads, and invariants—not merely the presence of code strings.  
**Disposition:** OPEN

### NLI-WO-001-F04 — Migrations are not yet the sole executable schema authority

**Class:** BLOCKER  
**Affected criteria:** AC-01, AC-06, AC-08, AC-09, AC-10; ADR-003; data-and-migrations standard  
**Observation:** FastAPI no longer calls `init_db`, which is positive. However, `_ensure_schema()` and `init_db()` remain executable in the production application module and still create/alter schema and seed users/reference/operational examples. Both `load_reference_data.py` and `load_development_fixtures.py` also issue `CREATE TABLE IF NOT EXISTS`. Reference `status` therefore mutates schema.  
**Risk/consequence:** There remain multiple executable schema authorities, contrary to the work order and ADR-003. A direct or future call can silently reintroduce schema/fixture mutation.  
**Required resolution:** Remove the application bootstrap DDL/seed path or make it impossible to execute in controlled environments and remove it from ordinary application modules. Loaders/status commands must rely on migration-created tables and fail clearly when migrations are missing; they must not execute DDL. Add tests proving no non-migration command creates/alters schema.  
**Disposition:** OPEN

### NLI-WO-001-F05 — Existing-pilot transition does not fail closed on structural drift

**Class:** REQUIRED  
**Affected criteria:** AC-04, AC-05  
**Observation:** `transition-pilot` validates only the presence of a set of table names before applying the idempotent bridge. It does not validate required columns/types, constraints, indexes, extensions, existing migration filenames/checksums, or selected semantic invariants. It also releases its advisory lock after inspection and reacquires it inside the normal apply path, leaving a race between compatibility validation and application.  
**Risk/consequence:** A structurally incompatible database can be treated as safely transitionable, or state may change between validation and migration.  
**Required resolution:** Define and test an explicit compatibility fingerprint for the supported pre-WO-001 pilot schema. Hold one migration lock across validation and transition (or revalidate atomically under the apply lock). Reject drift before changing the database. Automate representative transition and before/after invariant checks in CI.  
**Disposition:** OPEN

### NLI-WO-001-F06 — Fixture ownership and cleanup are unsafe/incomplete

**Class:** BLOCKER  
**Affected criteria:** AC-09, AC-10  
**Observation:** Fixture cleanup deletes all users whose IDs match `DEMO_USERS`, regardless of whether the current fixture batch created them. On conflict, load may change username/full name/role while preserving credentials. The legacy `init_db()` path still imports those identities and operational example records from application data.  
**Risk/consequence:** Cleanup can delete or alter a pre-existing account that happens to use a reserved ID, and fixture behavior is not fully isolated from runtime application code.  
**Required resolution:** Maintain explicit batch-to-record ownership and clean only records created by that batch, or fail if reserved IDs pre-exist outside the batch. Move fixture definitions and all example operational records into the explicit non-production fixture package; remove the legacy seed route. Add collision, preservation, and cleanup tests.  
**Disposition:** OPEN

### NLI-WO-001-F07 — Reference-data status/history is not governed sufficiently

**Class:** REQUIRED  
**Affected criteria:** AC-08, AC-14  
**Observation:** `status()` creates the metadata table, so it is not read-only. Loading the same `package_id` overwrites checksum, version, source, authority, load time, and context rather than retaining immutable load history or rejecting same-ID content drift. Status lists any loaded package but does not compare the expected package file/checksum to database state.  
**Risk/consequence:** Reference package drift and past load history can be concealed, and a status check can change the database.  
**Required resolution:** Make status strictly read-only, preserve immutable package-load history or reject changed content under the same package identity, and report expected-versus-loaded checksum/version state. Add conflict, drift, second-load, and missing-migration tests.  
**Disposition:** OPEN

### NLI-WO-001-F08 — Documented local bootstrap path is not proven usable

**Class:** REQUIRED  
**Affected criteria:** AC-11, AC-14  
**Observation:** The standard `.env.example` uses `DATABASE_URL` with host `postgres`, intended for container-to-container access. `bootstrap_local.sh` and `run_migrations.sh` source that URL and execute Python on the host, so the README's normal host command can fail DNS/port resolution. The bootstrap script itself also does not start required services; only the surrounding README command does. Evidence is limited to shell syntax.  
**Risk/consequence:** A fresh developer/operator may receive a non-working setup or improvise unsafe commands.  
**Required resolution:** Choose and document one tested path: run lifecycle commands inside the API/utility container, or construct an explicit host connection URL using `127.0.0.1:${POSTGRES_PORT}` without leaking credentials. Add a clean-bootstrap CI or reproducible test that starts services, migrates, loads reference data, optionally loads fixtures, and reaches health/readiness/smoke success.  
**Disposition:** OPEN

### NLI-WO-001-F09 — Baseline migration/evidence details require correction

**Class:** REQUIRED  
**Affected criteria:** AC-01, AC-02, AC-13, AC-14  
**Observation:** `000_current_operational_schema.sql` describes itself as schema-only but contains an `UPDATE auth_tokens` statement. The runner checks applied checksum but not applied filename drift. Restore evidence is stated only as local prose and is not tied to a durable artifact for the reviewed head.  
**Risk/consequence:** The migration's actual data effects are obscured, ledger drift can go undetected, and recovery claims are not independently reproducible.  
**Required resolution:** Remove or isolate/justify the data mutation in an explicit data migration; validate filename as well as checksum; attach or produce CI evidence for restored ledger checksums, PostGIS, selected invariants, and cleanup at the final head.  
**Disposition:** OPEN

## 4. Architecture and standards assessment

- **ADR-001:** Direction remains compatible with the modular monolith.
- **ADR-002:** PostgreSQL/PostGIS remains the intended system of record.
- **ADR-003:** Not yet satisfied because application/loaders retain executable DDL paths.
- **Data/migrations:** Material progress, but sole authority, transition validation, negative testing, and evidence remain incomplete.
- **Identity/access:** No intended role model change; credential preservation is not proven.
- **Security/privacy:** Production fixture refusal is a positive control; unsafe fixture ownership and stale evidence remain concerns.
- **GIS/location:** Existing PostGIS migration is preserved; no new geometry authority decision was made.
- **API/contracts:** No intentional contract change identified.
- **Audit/evidence:** Migration/reference metadata introduced, but immutable evidence and reviewed-head traceability are incomplete.
- **Testing/release:** Fails because API CI is red and mandatory DB-backed criteria are not automated.
- **Operations/DR:** Restore path improved in source but lacks durable accepted evidence; local bootstrap is not proven.
- **UI/accessibility/localization:** No UI change in scope.
- **Documentation:** Substantial documentation exists, but it currently overclaims PASS and includes a likely broken bootstrap path.

## 5. Evidence quality

The evidence is useful as an implementation-agent report but is not yet acceptance-grade. It is stale relative to the PR head, relies heavily on uncommitted/local claims, and substitutes source inspection for several explicitly required real-database tests. Final evidence must be reproducible from the reviewed commit in CI or attached controlled artifacts.

## 6. Risks and conditions

No risk is accepted by this review. SDA-RISK-001 remains open. SDA-RISK-004 remains open by design until NLI-WO-002, and is also affected here by competing executable schema paths.

## 7. Decision

`REWORK REQUIRED`

The implementation has the right broad direction—explicit migration runner, migration bridge, separate reference/fixture commands, removed startup call, PostGIS CI service, and improved restore checks—but it does not yet satisfy the work order's proof and sole-authority requirements.

This review does **not** authorize merge, production deployment, official publication, real-data transition, agency onboarding, or retirement of the existing recovery path.

## 8. Required follow-up

1. Resolve findings F01–F09 on the same implementation branch.
2. Update the implementation plan if the solution shape changes.
3. Add all required DB-backed tests and obtain green remote workflows.
4. Update PR/evidence documents to the exact final head and truthful criterion status.
5. Request SDA re-review; the next record will be `NLI-WO-001-review-02.md` or an updated resolution log after a new exact-head assessment.

## 9. Resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F01–F09 | Pending | — | OPEN | 2026-07-13 |
