# Implementation Plan — NLI-WO-001 Review 03 Remediation

**Review:** `docs/sda/reviews/NLI-WO-001-review-03.md`  
**Scope:** Resolve only F08 and F10 on `nli/wo-001-controlled-database-lifecycle`; preserve already accepted Review 03 behavior.

## Finding map

### F08 — API container runtime dependency and default bootstrap proof

- Move the migration-state evaluator into an importable runtime package under `services/api/app` or another copied runtime package.
- Update `infra/scripts/migrate.py` and other CLI/invariant scripts to import the same package without API-side `sys.path` mutation.
- Remove `ops_status.py` dependency on `infra/scripts` path injection.
- Add an API CI image lane that builds `services/api/Dockerfile`, imports `app.main` inside the image, boots the image against the CI PostGIS service, and verifies:
  - `/api/v1/health`
  - `/api/v1/operator/migrations/status`
  - `/api/v1/operator/production-readiness`
- Prove the default containerized bootstrap path (`HOST_API=0`) works locally or by an equivalent CI Docker/Compose path.

### F10 — migration package parse failures fail closed

- Treat missing, empty, invalid filename, and duplicate migration versions as explicit migration package error states.
- Do not convert parsing failures into an empty expected migration list.
- Make `migrate.py apply` and `migrate.py status` exit non-zero before creating `schema_migrations` when no valid migration package exists.
- Ensure operator status and production readiness remain non-ready for missing/empty/invalid/duplicate migration package states.
- Add DB/API tests for the four error classes.

## Files likely touched

- `services/api/app/migration_state.py` or equivalent shared package
- `infra/scripts/migrate.py`
- `infra/scripts/db_invariants.py`
- `infra/scripts/restore_drill.sh` only if import path requires adjustment
- `services/api/app/ops_status.py`
- `services/api/app/security_posture.py` only if readiness response shape needs update
- `services/api/Dockerfile`
- `.github/workflows/api-ci.yml`
- `services/api/tests/test_database_lifecycle_integration.py`
- `docs/sda/reviews/NLI-WO-001-review-03.md`

## Risks and mitigation

- **Risk:** breaking host CLI imports while fixing container imports.  
  **Mitigation:** set repo root on CLI `sys.path` explicitly and run local backend lifecycle tests.
- **Risk:** false-positive readiness on malformed package.  
  **Mitigation:** model package errors as structured state and test API/operator/production-readiness responses.
- **Risk:** image test differs from Compose bootstrap.  
  **Mitigation:** build actual Dockerfile and run actual image; separately run `bootstrap_local.sh` with `HOST_API=0` where local Docker permits.

## Verification

1. `python3 -m py_compile` for modified Python modules/scripts.
2. Targeted lifecycle tests for migration package errors and image-safe imports.
3. Full API suite.
4. Frontend CI check to preserve accepted behavior.
5. Local Docker image import/boot proof if feasible.
6. Remote API and frontend workflows green at final PR head.
7. Review 03 resolution log and PR body/comment updated with exact commit and evidence.
