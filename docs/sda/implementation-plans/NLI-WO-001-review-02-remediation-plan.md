# Implementation Plan — NLI-WO-001 Review 02 Remediation

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Review:** `docs/sda/reviews/NLI-WO-001-review-02.md`  
**Branch:** `nli/wo-001-controlled-database-lifecycle`  
**Status:** implementation plan for rework  
**Prepared:** 2026-07-13

## Objective

Resolve Review 02 open findings F03, F05, F06, F08, F09, and F10 without weakening resolved Review 01 controls, without claiming SDA acceptance, and without merging PR #4.

## Finding map

| Finding | Planned resolution | Primary files | Evidence |
|---|---|---|---|
| F03 | Add deterministic PostgreSQL schema fingerprint covering extensions, tables, columns/types/nullability/defaults, constraints, indexes, selected row counts, and startup before/after invariance. | `infra/scripts/db_invariants.py`, lifecycle tests | Real PostGIS startup invariance test fails on DDL drift and passes unchanged startup. |
| F05 | Add versioned pre-WO compatibility fingerprint and representative transition fixture containing users/sessions, provinces/admin units/territories, roads, buildings, addresses, address records/events, citizen submissions, field assignments/submissions, evidence metadata, audit logs, import/publication rows. Validate before mutation where possible and assert before/after counts, hashes, and relationships. | `infra/scripts/migrate.py`, lifecycle tests | Real PostGIS transition test with entity-class counts, hash manifest, FK relationship counts, and drift rejection. |
| F06 | Make same owned active fixture package reload deterministic; preserve fail-closed behavior for non-owned collisions. Remove runtime demo/operational seed constants from `services/api/app/data.py`; keep only governed reference/routing config actually used by runtime; add source guards. | fixture script/package, `data.py`, tests | Load-load-cleanup DB test and source guard test. |
| F08 | Add clean bootstrap verification that runs existing API/frontend smoke checks where applicable, cleans smoke data, and writes durable evidence tied to commit. Run it through CI or publish CI artifact. | `bootstrap_local.sh`, new smoke verifier, workflows/evidence | CI clean-bootstrap/smoke artifact or exact run evidence at final head. |
| F09 | Add source/restored invariant manifests and fail restore unless counts, relationships, checksums, and selected hashes match; verify target cleanup. | `infra/scripts/restore_drill.sh`, invariant helper, CI lifecycle | Restore drill test/CI step comparing source and restored manifests. |
| F10 | Share migration-status evaluator between CLI/operator/readiness or equivalent; fail closed for pending, checksum mismatch, filename mismatch, unknown ledger version, unreadable ledger, and missing production config. | `infra/scripts/migration_state.py`, `ops_status.py`, `security_posture.py`, tests | DB-backed API readiness/operator status tests for all drift classes. |

## Risks and mitigations

- **Risk:** representative fixture becomes too broad and brittle. **Mitigation:** use a narrow but complete fixture with one row per AC-05 entity class and deterministic hashes.
- **Risk:** docs-only evidence commits skip CI. **Mitigation:** keep `docs/sda/**` in API/frontend workflow path filters and verify exact final PR head.
- **Risk:** removing runtime constants breaks UI/source guards. **Mitigation:** move examples to explicit fixture/reference packages and keep tests focused on runtime imports.
- **Risk:** production-readiness checks become noisy in local dev. **Mitigation:** fail closed only for production configuration checks when `APP_ENV=production`; always fail closed on migration drift/unreadable state.

## Verification sequence

1. Add/adjust RED tests for F03/F05/F06/F09/F10.
2. Implement invariant/fingerprint helpers and wire tests.
3. Run targeted PostGIS lifecycle tests.
4. Run full API suite with PostGIS env.
5. Run frontend generated-contract and `test:ci`.
6. Commit code/tests, update evidence/review logs, push.
7. Verify API and frontend GitHub Actions at final head.
8. Update PR body and request SDA Review 03 while keeping PR #4 draft/open/not merged.

## Boundaries

This plan does not authorize national production, official publication, destructive migration of real citizen data, new external services, or PR merge.
