# SDA Review — NLI-WO-001 — Review 02

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Pull request:** `#4 — Draft: Implement controlled database lifecycle`  
**Reviewed implementation commit:** `121c1bcf40518ebdcbf014f928d75fd5d3a39585`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-13  
**Outcome:** `REWORK REQUIRED`

## 1. Review boundary

Reviewed the exact PR head, Review 01 resolution log, submitted evidence, migration runner, `000` and `007` migrations, runtime database module, reference-data and fixture loaders, clean-bootstrap script, migration/operator readiness implementations, database lifecycle tests, API workflow, frontend workflow, and restore validation.

Independent workflow verification at the reviewed head:

- API CI run `29278381766`: **success**
  - `api-tests`: success
  - `migration-lifecycle`: success
- Frontend CI run `29278381911`: **success**

The second implementation is materially stronger and resolves several Review 01 findings. It is not yet acceptance-ready because explicit work-order criteria remain unproved or contradicted by the current implementation.

This review does not authorize merge, production deployment, official publication, real citizen data transition, broad agency onboarding, or retirement of an existing recovery path.

## 2. Review 01 finding disposition

| Finding | Review 02 disposition | Assessment |
|---|---|---|
| F01 | RESOLVED | API and lifecycle jobs are separate and green at the reviewed head. |
| F02 | RESOLVED | PR body identifies the exact reviewed head and uses `READY FOR SDA REVIEW`, not SDA-accepted `PASS`. |
| F03 | PARTIALLY RESOLVED — OPEN | Real DB tests now cover checksum/filename drift, failed migration, concurrency, pending state, and credential preservation. The required schema fingerprint remains incomplete. |
| F04 | RESOLVED | Runtime bootstrap DDL/seed behavior was removed; `init_db()` is now a throwing guard; loaders require migrated schema and do not create tables. |
| F05 | PARTIALLY RESOLVED — OPEN | One lock is held and columns are checked, but the compatibility fingerprint and representative transition evidence remain below AC-05. |
| F06 | PARTIALLY RESOLVED — OPEN | Ownership/collision tracking is improved, but fixture reload is not deterministic and legacy seed definitions remain in the runtime package. |
| F07 | RESOLVED | Reference status is schema-read-only; package checksum drift is rejected and load history is retained. |
| F08 | PARTIALLY RESOLVED — OPEN | Host-safe bootstrap and service startup are implemented, but the acceptance proof omits the required smoke checks and durable clean-bootstrap evidence. |
| F09 | PARTIALLY RESOLVED — OPEN | `000` is schema-only, data repair moved to `007`, and runner filename drift is detected. Restore validation still does not prove matching row counts/invariants. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence assessed | Finding/reference |
|---|---|---|---|
| AC-01 | CONDITION | Empty PostGIS migration and eight-row ledger execute in CI. | Full required constraint/index inventory is not directly asserted. |
| AC-02 | PASS | Ledger rows include version, filename, checksum, applied time/context; runner status reaches current. | — |
| AC-03 | PASS | DB-backed content checksum drift test fails closed without rewriting ledger. | — |
| AC-04 | PASS | Failed migration rollback/later-stop and concurrent runner behavior are DB-tested. | — |
| AC-05 | FAIL | Transition test and compatibility checks exist. | F05: test is not representative of all named operational entities; fingerprint omits types/constraints/indexes and selected relationship/hash proof. |
| AC-06 | FAIL | Real API startup test compares table count and selected row counts. | F03: this is not a schema fingerprint and would not detect column, constraint, or index mutation. |
| AC-07 | FAIL | Operator migration status reports a pending migration and startup does not apply it. | F10: production-readiness remains hardcoded migration-ready; unknown/filename ledger drift can be misreported by operator status. |
| AC-08 | PASS WITH CONDITION | Reference package is explicit, idempotent, conflict-aware, history-backed, and drift-rejecting. | Institutional authority remains provisional as correctly recorded. |
| AC-09 | FAIL | Environment refusal, collision handling, ownership records, and cleanup tests exist. | F06: a second active load reaches duplicate-key insertion rather than deterministic behavior; legacy runtime seed constants remain. |
| AC-10 | PASS | Migration/reference/startup preserve tested credentials and sessions; collisions prevent fixture overwrite. | — |
| AC-11 | FAIL | Script starts dependencies, migrates, loads reference data, starts application, and checks health. | F08: it does not execute the required existing smoke checks; clean-bootstrap proof is not a durable CI or repository artifact at the reviewed head. |
| AC-12 | PASS | Real PostGIS API and lifecycle jobs are green and execute the lifecycle integration suite. | — |
| AC-13 | FAIL | CI and restore script perform dump/restore and validate ledger/PostGIS. | F09: neither path asserts restored selected row counts/invariants match the source. |
| AC-14 | CONDITION | README/scripts explain the explicit lifecycle and host-safe path. | F08/F10: readiness and smoke behavior remain incomplete/misleading. |
| AC-15 | PASS | API and frontend workflows are green at the exact reviewed head. | — |

## 4. Open findings

### NLI-WO-001-F03 — Startup test does not provide the required schema fingerprint

**Class:** REQUIRED  
**Affected criterion:** AC-06  
**Observation:** `fingerprint()` records only the number of public tables and row counts for `users`, `auth_tokens`, `provinces`, `admin_units`, and `schema_migrations`. It does not hash or compare columns, types, defaults, constraints, indexes, extensions, or the other protected row-count classes.  
**Risk/consequence:** Startup could perform material DDL while preserving the number of tables and still pass the test.  
**Required resolution:** Build a deterministic schema fingerprint from approved catalog data—at minimum tables, columns/types/nullability/defaults, constraints, indexes, and extensions—and compare it before/after real API startup. Include controlled row counts for reference, user/session, fixture, and migration tables.  
**Disposition:** OPEN

### NLI-WO-001-F05 — Pilot transition proof is not representative or structurally complete

**Class:** BLOCKER  
**Affected criterion:** AC-05; R7  
**Observation:** Transition compatibility checks required table and column names plus one user invariant, but not column types, nullability/defaults, primary/foreign/unique/check constraints, required indexes, or other semantic relationships. The integration test creates the source schema from the new `000` migration, inserts only a province and user, and verifies only those counts plus the ledger. It does not prove preservation of roads, buildings, addresses/address records, submissions, evidence metadata, audit events, hashes, or relationships named by AC-05. `ensure_ledger()` also creates/commits ledger metadata before source compatibility rejection.  
**Risk/consequence:** A materially drifted pilot database could be labeled compatible or modified before rejection, and the required no-loss transition evidence is absent.  
**Required resolution:** Define a versioned compatibility fingerprint for the supported pre-WO schema including required types, constraints, indexes, PostGIS state, and selected semantic invariants. Use a representative pre-WO fixture/database containing every AC-05 entity class and assert before/after counts, selected hashes, and relationships. Validate compatibility before durable transition mutation, except for a clearly documented unavoidable ledger bootstrap that is itself safely reversible.  
**Disposition:** OPEN

### NLI-WO-001-F06 — Fixture lifecycle is not deterministic and legacy seed definitions remain

**Class:** BLOCKER  
**Affected criterion:** AC-09; work-order section 4.4  
**Observation:** The loader permits an existing user when active ownership exists, then executes a plain `INSERT INTO users` without `ON CONFLICT`; repeating the same active fixture load therefore fails with a duplicate key instead of producing deterministic state. No test covers a second load before cleanup. Separately, `services/api/app/data.py` still contains `DEMO_USERS` and extensive territory, road, building, address, assignment, submission, import, and published-pack example constants even though the controlled fixture package was introduced.  
**Risk/consequence:** Local/CI setup is not repeatable, and duplicate legacy fixture definitions inside the runtime package remain a future reintroduction path and an ambiguous source of authority.  
**Required resolution:** Make repeated load of the same owned active batch deterministic and tested, while continuing to fail on non-owned collisions. Remove demonstration identities and operational example records from the runtime package; retain only genuinely runtime configuration such as the module list, or move all examples to explicit fixture packages. Add source guards preventing their return.  
**Disposition:** OPEN

### NLI-WO-001-F08 — Clean bootstrap does not prove readiness and existing smoke checks

**Class:** REQUIRED  
**Affected criterion:** AC-11  
**Observation:** `bootstrap_local.sh` validates lifecycle status and API health but does not run the repository's existing smoke checks required by AC-11. The submitted clean-bootstrap proof is described as local files under `/tmp` and is not a durable CI artifact or committed evidence tied to the reviewed head.  
**Risk/consequence:** A stack can report health while protected workflows, API contracts, or frontend/operator smoke paths are broken.  
**Required resolution:** Add a repeatable clean-bootstrap verification lane or script that reaches migration/reference readiness, starts the stack, executes the relevant existing API/frontend smoke checks with controlled fixtures, cleans them, and records the result. Run it in CI where practical or publish a controlled artifact tied to the final head.  
**Disposition:** OPEN

### NLI-WO-001-F09 — Restore validation does not compare source and restored invariants

**Class:** BLOCKER  
**Affected criterion:** AC-13; R15  
**Observation:** `restore_drill.sh` separately collects restored and live row counts but never asserts equality. The CI lifecycle job restores the dump and asserts migration-row count, latest version, checksum population, and PostGIS only. It does not compare selected source/restored row counts, relationships, or hashes.  
**Risk/consequence:** A partial or semantically incomplete restore can be reported successful even when authoritative rows are missing or inconsistent.  
**Required resolution:** Capture source and restored invariant manifests and fail unless they match. Include at least the selected tables named by AC-05/restore policy, migration filenames/checksums, key foreign-key relationship counts, and representative evidence/reference hashes where available. Continue verifying temporary target removal. Add the same assertion to the CI dump/restore lane.  
**Disposition:** OPEN

### NLI-WO-001-F10 — Production readiness and operator status do not fail closed on all migration drift

**Class:** BLOCKER  
**Affected requirements:** work-order section 4.2; R5; R9; R14; AC-07/AC-14  
**Observation:** `production_readiness_status()` marks `explicit_migrations` as `ready` unconditionally and does not consume live migration status. `app.ops_status.migration_status()` detects checksum mismatch and pending versions but ignores unknown ledger versions and applied filename mismatch, while the CLI runner does detect those states.  
**Risk/consequence:** An authorized operator can receive a production-readiness or command-center result that understates migration drift, violating the fail-closed and truthful-diagnostics requirement.  
**Required resolution:** Use one shared migration-status evaluator or equivalent consistent logic. Production readiness must be non-ready for pending, checksum mismatch, filename mismatch, unknown ledger version, unreadable ledger, or missing configuration in a production context. Add API-level DB-backed tests for all drift classes.  
**Disposition:** OPEN

## 5. Resolved controls worth preserving

- Application lifespan no longer mutates schema or seeds data.
- `init_db()` is a throwing compatibility guard rather than a hidden bootstrap path.
- Migration runner checks content and filename drift and serializes application.
- Failed migrations are transactionally tested.
- Reference and fixture loaders refuse missing migration state and production fixture loading.
- Reference package history and drift rejection are implemented.
- Fixture cleanup tracks ownership rather than deleting reserved IDs blindly.
- API and frontend CI pass at the reviewed head.
- `000` is schema-only and the token data repair is explicit in `007`.

## 6. Evidence assessment

The evidence is now correctly framed as implementation-agent evidence and is substantially more reproducible. The green final-head workflows are accepted as valid evidence for the tests they actually run. They do not establish criteria that the tests or assertions omit, particularly representative pilot transition, true schema invariance, deterministic fixture reload, smoke-complete bootstrap, source/restored invariant equality, and fail-closed production-readiness reporting.

## 7. Decision

`REWORK REQUIRED`

The implementation may proceed on the current branch. Do not merge or mark the work order accepted until F03, F05, F06, F08, F09, and F10 are resolved and a new exact-head review is performed.

This outcome does not reverse the resolved Review 01 controls; it narrows the remaining work to the explicit gaps above.

## 8. Required follow-up

1. Resolve all six open findings on the same branch.
2. Update tests and evidence to the final implementation head.
3. Obtain green API and frontend workflows at that head.
4. Update the Review 01/02 resolution logs with fixing commits and evidence.
5. Request SDA Review 03.

## 9. Review 02 resolution log

| Finding | Agent response | Commit/evidence | SDA disposition | Date |
|---|---|---|---|---|
| F03 | Resolved in implementation: `infra/scripts/db_invariants.py` builds deterministic PostgreSQL schema manifests covering columns, types, nullability, defaults, constraints, indexes, and extensions; lifecycle startup tests compare full schema fingerprints and prove index mutation changes the fingerprint. | Fixing commit `17235b4ab320b550f245383333c003521c147953`; local evidence: `services/api/.venv/bin/python -m pytest -q` → `192 passed`; `tests/test_database_lifecycle_integration.py::test_schema_fingerprint_detects_column_index_constraint_and_extension_state`. | READY FOR SDA REVIEW 03 | 2026-07-13 |
| F05 | Resolved in implementation: transition compatibility now checks required table/column specs, types/nullability, required constraints/indexes, and PostGIS before ledger bootstrap; representative pre-WO fixture covers users/auth tokens, territories, roads, buildings, addresses, address points, citizen geotag submissions, address records/events, field assignments/submissions, import jobs/rows, publication packs/addresses, and audit logs; tests assert before/after counts, hashes, selected address-record invariants, relationships, and ledger versions. | Fixing commit `17235b4ab320b550f245383333c003521c147953`; local evidence: `services/api/tests/test_database_lifecycle_integration.py` → `15 passed`; transition tests `test_existing_pilot_transition_preserves_representative_counts_hashes_and_relationships` and `test_transition_rejects_structural_drift_before_ledger_bootstrap`. | READY FOR SDA REVIEW 03 | 2026-07-13 |
| F06 | Resolved in implementation: development fixture package owns the controlled smoke dataset; loader upserts already-owned active records deterministically and still rejects non-owned collisions; cleanup deletes owned records only; runtime `services/api/app/data.py` now contains only `MODULES`; source guard prevents legacy constants returning. | Fixing commit `17235b4ab320b550f245383333c003521c147953`; local evidence: `test_fixture_owned_records_reload_and_cleanup_are_deterministic`, `test_fixture_collision_refuses_non_owned_records`, `test_runtime_data_module_contains_no_seed_or_fixture_authority`; full backend suite `192 passed`. | READY FOR SDA REVIEW 03 | 2026-07-13 |
| F08 | Resolved in implementation: `bootstrap_local.sh` supports clean isolated DB bootstrap, reference/fixture load, host or compose app startup, existing admin smoke execution, and durable JSON report; API CI migration lifecycle now starts the API and runs `apps/admin-portal/scripts/admin-flow-smoke.mjs` before cleanup. | Fixing commit `17235b4ab320b550f245383333c003521c147953`; local evidence: isolated `addressing_bootstrap_wo001` run produced `/tmp/wo001-bootstrap-local-report.json` with `status=passed`, `migrations=current`, `fixtures_loaded=true`, `app_runtime=host`, `smoke_checks=passed`; frontend local `npm --prefix apps/admin-portal run test:ci` passed. | READY FOR SDA REVIEW 03 | 2026-07-13 |
| F09 | Resolved in implementation: `db_invariants.py` captures source/restored data manifests with counts, hashes, relationships, ledger metadata, reference/fixture hashes; `restore_drill.sh` and API CI dump/restore fail unless source and restored manifests match. | Fixing commit `17235b4ab320b550f245383333c003521c147953`; local evidence: backend suite `192 passed`; workflow YAML validation passed for `.github/workflows/api-ci.yml` and `.github/workflows/frontend-ci.yml`; CI lifecycle lane updated to compare `/tmp/wo001-source-invariants.json` and `/tmp/wo001-restored-invariants.json`. | READY FOR SDA REVIEW 03 | 2026-07-13 |
| F10 | Resolved in implementation: API and CLI share `infra/scripts/migration_state.py`; operator and production-readiness status fail closed for pending migrations, checksum mismatch, filename mismatch, unknown ledger versions, unreadable state, and missing production configuration. | Fixing commit `17235b4ab320b550f245383333c003521c147953`; local evidence: `test_operator_and_production_readiness_fail_closed_for_all_migration_drift` and `test_production_readiness_fails_closed_for_unreadable_state_and_missing_production_config`; full backend suite `192 passed`. | READY FOR SDA REVIEW 03 | 2026-07-13 |

## 10. Remote verification for Review 03 request

Final implementation head verified remotely: `0b41e11d1c0af846650084a030193876da0914ef`.

- API CI run `29284277801`: **success** — https://github.com/bechirobob/eg-addressing/actions/runs/29284277801
- Frontend CI run `29284277384`: **success** — https://github.com/bechirobob/eg-addressing/actions/runs/29284277384

PR #4 remains draft, open, and unmerged. SDA Review 03 requested after this evidence was recorded.
