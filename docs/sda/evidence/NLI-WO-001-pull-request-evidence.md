# Pull Request Evidence — NLI-WO-001 Review-01 Remediation

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Implementation plan:** `docs/sda/implementation-plans/NLI-WO-001-controlled-database-lifecycle.md`  
**Review addressed:** `docs/sda/reviews/NLI-WO-001-review-01.md`  
**Branch:** `nli/wo-001-controlled-database-lifecycle`  
**Remediation code commit:** `c2322a0`  
**Final implementation commit verified remotely:** `555514347b9a243c5a1691a9a38ac1695edd9fff`  
**Remote API CI:** https://github.com/bechirobob/eg-addressing/actions/runs/29278041290  
**Remote frontend CI:** https://github.com/bechirobob/eg-addressing/actions/runs/29278041293  
**Prepared by:** implementation agent

> This evidence does not claim SDA acceptance. It records implementation-agent evidence for SDA Review 02. The exact implementation commit `555514347b9a243c5a1691a9a38ac1695edd9fff` had green remote API and frontend workflows before this documentation closeout update.

## 1. Outcome

Resolved SDA Review 01 findings F01–F09 in the controlled database lifecycle implementation:

- Removed executable application schema creation/seed path from ordinary runtime code.
- Added DB-backed PostgreSQL/PostGIS integration tests for checksum drift, filename drift, failed migrations, concurrent migration execution, startup invariance, pending readiness, credential/session preservation, existing-pilot transition, reference-data drift, and fixture ownership/cleanup.
- Made reference-data and fixture commands fail clearly when migrations are missing; neither creates schema.
- Added immutable reference-data load history and same-package drift rejection.
- Added fixture package ownership records and collision-safe cleanup.
- Strengthened transition compatibility checks and holds the migration advisory lock through validation and application.
- Isolated auth-token expiry repair into `007_lifecycle_metadata_hardening.sql`; `000` is schema-only again.
- Fixed local bootstrap path and proved it from an isolated clean Compose project with API health.
- Split API CI into API tests and a dedicated migration lifecycle job with dump/restore ledger proof.

Readiness boundary: PR remains draft and requires SDA Review 02. No merge, production deployment, official publication, agency onboarding, or real citizen data migration is authorized by this evidence.

## 2. Acceptance criteria status

| Criterion | Status | Implementation | Evidence/test | Remaining condition |
|---|---|---|---|---|
| AC-01 | READY FOR SDA REVIEW | Empty DB created by ordered migrations `000–007`; `000` schema-only; PostGIS installed. | `test_empty_postgis_database_migrates_with_full_ledger` passed; lifecycle CI job applies migrations. | Remote CI must pass at final PR head. |
| AC-02 | READY FOR SDA REVIEW | Ledger stores version, filename, checksum, applied time, context; filename drift now detected. | `test_empty_postgis_database_migrates_with_full_ledger`; `test_checksum_and_filename_drift_make_status_non_current`. | None known. |
| AC-03 | READY FOR SDA REVIEW | Checksum mismatch blocks status/apply. | DB-backed checksum drift test passed. | None known. |
| AC-04 | READY FOR SDA REVIEW | Failed migrations run transactionally; advisory lock serializes concurrent runners; transition lock held through validation/apply. | `test_failed_migration_rolls_back_and_does_not_continue`; `test_concurrent_migration_execution_uses_single_ledger`; transition test. | None known. |
| AC-05 | READY FOR SDA REVIEW | Transition validates required tables/columns/semantic user invariant and rejects drift before applying. | `test_existing_pilot_transition_preserves_counts_and_rejects_drift`. | Compatibility fingerprint is explicit but can be expanded by SDA if more invariants are desired. |
| AC-06 | READY FOR SDA REVIEW | FastAPI startup does not call schema/data bootstrap; runtime bootstrap DDL removed. | `test_api_startup_does_not_change_schema_or_rows`; source guard tests. | None known. |
| AC-07 | READY FOR SDA REVIEW | Pending migrations report non-current and API startup does not auto-apply. | `test_pending_migration_readiness_does_not_auto_apply`. | None known. |
| AC-08 | READY FOR SDA REVIEW | Reference data loader/status require migrated schema, preserve history, reject drift, second load is no-op. | `test_reference_data_missing_migrations_status_and_drift`; lifecycle CI reference status/load/status. | Institutional authority of reference package remains provisional by package metadata. |
| AC-09 | READY FOR SDA REVIEW | Fixture definitions live in `infra/fixtures`; load refuses production; collisions fail; cleanup deletes only owned records. | `test_fixture_missing_migrations_collision_ownership_and_cleanup`; `test_fixture_owned_records_cleanup`. | None known. |
| AC-10 | READY FOR SDA REVIEW | Migrate/reference/startup preserve user hash/role/active/session; fixtures cannot overwrite reserved collisions. | `test_credentials_and_sessions_survive_migrate_and_reference_load`; fixture collision test. | None known. |
| AC-11 | READY FOR SDA REVIEW | Bootstrap starts services, creates configured DB when needed, uses host-safe connection, migrates, loads reference, starts app, checks API health. | Isolated clean bootstrap proof: `bootstrap_local: ok`; health JSON `{"status":"ok","service":"eg-addressing-api","version":"0.1.0","environment":"local"}`. | None known. |
| AC-12 | READY FOR SDA REVIEW | Remote API workflow has PostGIS env during tests and dedicated lifecycle job. | API CI success at `555514347b9a243c5a1691a9a38ac1695edd9fff`: https://github.com/bechirobob/eg-addressing/actions/runs/29278041290 | None known. |
| AC-13 | READY FOR SDA REVIEW | Restore validation now expects 8-row ledger/latest `007`; lifecycle CI performs dump/restore and checks ledger/PostGIS. | API lifecycle job success in https://github.com/bechirobob/eg-addressing/actions/runs/29278041290 | None known. |
| AC-14 | READY FOR SDA REVIEW | Docs/scripts updated for host-safe bootstrap and explicit lifecycle. | Bootstrap proof and updated README/script behavior. | PR body records final workflow URLs after push. |
| AC-15 | READY FOR SDA REVIEW | Backend and frontend gates pass locally and remotely. | Backend `187 passed, 5 warnings`; frontend `test:ci` passed; remote API CI and frontend CI succeeded at `555514347b9a243c5a1691a9a38ac1695edd9fff`. | None known. |

## 3. Review-01 finding resolution summary

| Finding | Agent response | Fixing commit/evidence | Remaining condition/RFI |
|---|---|---|---|
| F01 | API CI configuration now provides PostGIS env during tests and has a dedicated lifecycle job, so lifecycle evidence is not skipped by the API test step. | Commit `c2322a0`; path-portability follow-up `5555143`; remote API CI success: https://github.com/bechirobob/eg-addressing/actions/runs/29278041290. | None known. |
| F02 | Evidence and PR body are updated for Review-01 remediation and no longer mark unsupported criteria as accepted by SDA. | This evidence file; PR body updated with final implementation commit and workflow URLs. | None known. |
| F03 | Added real DB-backed tests for checksum drift, failed migrations, concurrency, startup invariance, pending readiness, and credential/session preservation. | Commit `c2322a0`; `services/api/tests/test_database_lifecycle_integration.py`; local `11 passed`. | None known. |
| F04 | Removed `_ensure_schema`; disabled `init_db`; removed app startup import; loaders no longer execute DDL and fail with `missing-migrations`. | Commit `c2322a0`; source guards; integration missing-migration tests. | `init_db()` remains only as a throwing compatibility guard, not executable bootstrap. |
| F05 | Transition now checks required columns/semantic user invariant and applies while holding one advisory lock. | Commit `c2322a0`; `test_existing_pilot_transition_preserves_counts_and_rejects_drift`. | SDA may require additional invariants; current fingerprint is explicit. |
| F06 | Fixture definitions moved to `infra/fixtures`; ownership table records created records; collisions fail; cleanup deletes only owned records. | Commit `c2322a0`; fixture collision and cleanup tests. | None known. |
| F07 | Reference status is read-only for schema; loader preserves history and rejects same package ID checksum drift. | Commit `c2322a0`; reference drift/missing migration tests. | Package remains provisional-government-reference pending institutional source approval. |
| F08 | Bootstrap now starts services, converts Docker-host `.env` connection to host-safe variables, creates DB if needed, runs lifecycle, starts app, and checks health. | Commit `c2322a0`; isolated clean bootstrap proof output in `/tmp/wo001-bootstrap.log` and `/tmp/wo001-bootstrap-health.json`. | None known. |
| F09 | `000` no longer contains `UPDATE`; data repair isolated in `007`; runner detects filename drift; CI lifecycle includes dump/restore ledger proof. | Commit `c2322a0`; schema-only source guard; filename drift test; remote API lifecycle job success: https://github.com/bechirobob/eg-addressing/actions/runs/29278041290. | None known. |

## 4. Change inventory since Review 01

### Added

- `infra/migrations/007_lifecycle_metadata_hardening.sql` — lifecycle metadata hardening and explicit auth-token expiry backfill.
- `infra/fixtures/development-fixtures-v1.json` — non-production fixture package.
- `services/api/tests/test_database_lifecycle_integration.py` — real PostgreSQL/PostGIS lifecycle integration suite.

### Modified

- `.github/workflows/api-ci.yml` — PostGIS env for API tests, dedicated lifecycle job, dump/restore ledger proof.
- `infra/migrations/000_current_operational_schema.sql` — removed auth-token data update; added metadata tables for empty DB creation.
- `infra/scripts/migrate.py` — filename drift detection, transition compatibility fingerprint, atomic transition lock.
- `infra/scripts/load_reference_data.py` — no DDL; missing-migration failure; expected-vs-loaded status; immutable history; drift rejection.
- `infra/scripts/load_development_fixtures.py` — no DDL; package-driven fixtures; ownership/collision/cleanup controls.
- `infra/scripts/bootstrap_local.sh` — starts services, host-safe DB connection, DB creation, app health check.
- `infra/scripts/restore_drill.sh` — validates latest `007` and 8 migration ledger rows.
- `services/api/app/db.py` — removed executable schema/seed bootstrap from runtime module.
- `services/api/app/main.py` — removed stale `init_db` import.
- `services/api/tests/test_app.py`, `test_database_lifecycle.py` — updated guards for migration-only authority.

## 5. Verification commands and results

| Command/check | Environment | Result |
|---|---|---|
| `python3 -m py_compile infra/scripts/migrate.py infra/scripts/load_reference_data.py infra/scripts/load_development_fixtures.py services/api/app/db.py services/api/app/main.py` | local | PASS |
| `bash -n infra/scripts/run_migrations.sh infra/scripts/bootstrap_local.sh infra/scripts/restore_drill.sh` | local | PASS |
| Workflow YAML parse for `.github/workflows/api-ci.yml` | local | PASS |
| `POSTGRES_HOST=127.0.0.1 ... pytest -q tests/test_database_lifecycle_integration.py -vv` | local Docker PostGIS | PASS — `11 passed` |
| `POSTGRES_HOST=127.0.0.1 ... pytest -q` | local Docker PostGIS | PASS — `187 passed, 5 warnings` |
| `npm --prefix apps/admin-portal run generate:api-types` | local | PASS — 105 operations generated |
| `git diff --exit-code apps/admin-portal/components/apiTypes.ts` | local | PASS — no diff |
| `npm --prefix apps/admin-portal run test:ci` | local | PASS |
| Isolated clean bootstrap with temp compose/env/data | local Docker | PASS — `bootstrap_local: ok`; API health returned `status: ok` |

## 6. Known limitations / RFIs

| Item | Severity | Status |
|---|---|---|
| Reference package authority is provisional by metadata. | Low | Remaining institutional data-governance condition, not an implementation blocker. |
| Exact remote workflow evidence is available for the implementation commit. | Low | API and frontend workflows are linked above. |
| Self-referential evidence closeout commit SHA cannot be embedded inside itself. | Low | This file records the exact final implementation commit verified remotely; this later evidence closeout is documentation-only. |

## 7. Agent declaration

- [x] Every Review-01 finding F01–F09 has a recorded response and evidence.
- [x] No required control was disabled to pass checks.
- [x] No secrets or production personal/evidence data were committed.
- [x] Criteria are marked `READY FOR SDA REVIEW`, not SDA-accepted `PASS`.
- [x] PR #4 remains draft and must not be merged before SDA Review 02.
