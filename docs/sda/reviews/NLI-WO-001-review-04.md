# SDA Review — NLI-WO-001 — Review 04

**Work order:** `docs/sda/work-orders/NLI-WO-001-controlled-database-lifecycle.md`  
**Pull request:** `#4 — Implement controlled database lifecycle`  
**Reviewed implementation commit:** `4fbdfd72277296ee0649de55c1bd7be039af3b07`  
**Reviewer:** System Design Authority  
**Review date:** 2026-07-13  
**Outcome:** `ACCEPTED WITH RECORDED CONDITIONS`

## 1. Review boundary

Review 04 assessed only the two findings left open by Review 03 and confirmed that the controls accepted in Reviews 01–03 remain present.

Reviewed evidence included:

- runtime-packaged migration-state evaluator;
- API Docker image build, import, boot, authentication, health, migration-status, and production-readiness checks;
- shared API/CLI migration-package parser and evaluator;
- CLI behavior before database connection and ledger creation;
- operator and production-readiness fail-closed behavior;
- DB-backed tests for missing, empty, invalid-name, and duplicate-version migration packages;
- exact-head API and frontend workflow results.

Independent workflow verification at the reviewed implementation head:

- API CI run `29289730248`: **success**
  - `api-tests`: success
  - `migration-lifecycle`: success
  - `api-image-runtime`: success
- Frontend CI run `29289730238`: **success**

The API image job built `services/api/Dockerfile`, imported `app.main` inside the resulting image, booted the image against PostGIS, authenticated using controlled fixture credentials, and received successful responses from health, migration-status, and production-readiness endpoints.

## 2. Review 03 finding disposition

| Finding | Review 04 disposition | Assessment |
|---|---|---|
| F08 | RESOLVED | The evaluator now lives in `services/api/app/migration_state.py`, is included by the existing Dockerfile application copy, and is imported directly by API code. The repository script is only a compatibility entrypoint. Exact-head CI builds and boots the actual image and exercises protected operator endpoints. |
| F10 | RESOLVED | Missing, non-directory, empty, invalid-name, and duplicate-version migration packages produce explicit non-current package-error states. CLI status/apply fail before database connection or ledger creation. Operator and production-readiness paths remain non-ready, with DB-backed parameterized tests covering the required package failures. |

## 3. Acceptance-criterion decision

| Criterion | Decision | Evidence/condition |
|---|---|---|
| AC-01 | PASS | Empty PostGIS database is created solely through ordered migrations and required schema is exercised in CI. |
| AC-02 | PASS | Complete ordered ledger records version, filename, checksum, applied time, and execution context and reports current. |
| AC-03 | PASS | Content and filename drift fail closed without rewriting applied ledger state. |
| AC-04 | PASS | Failed migration rollback/later-stop and concurrent-runner serialization are DB-tested. |
| AC-05 | PASS WITH OPERATIONAL CONDITION | Representative pre-WO transition preserves named entity classes, hashes, relationships, and canonical fields. Any real pilot transition must still use the documented backup, change control, and captured before/after manifests. |
| AC-06 | PASS | Deterministic schema/data manifests are identical before and after real API startup. |
| AC-07 | PASS | Pending and invalid/missing migration packages are not auto-applied and report non-ready truthfully. |
| AC-08 | PASS WITH INSTITUTIONAL CONDITION | Reference loading is explicit, versioned, idempotent, history-backed, conflict-aware, and drift-rejecting. The package remains provisional until the responsible government data authority approves its source and status. |
| AC-09 | PASS | Fixtures are explicit, positively environment-allowlisted, production-refusing, deterministic, ownership-tracked, collision-safe, and cleanable. |
| AC-10 | PASS | Existing password hash, role, activation state, and sessions are preserved by migration, reference-data, and startup paths. |
| AC-11 | PASS | Controlled bootstrap/lifecycle starts dependencies, migrates, loads data, runs smoke behavior, and reaches health; the actual API image runtime is independently verified in CI. |
| AC-12 | PASS | Real PostgreSQL/PostGIS CI covers API, migration lifecycle, transition, startup invariance, readiness, reference data, fixtures, and image runtime. |
| AC-13 | PASS | Dump/restore compares source and restored invariant manifests and verifies migration ledger, PostGIS state, and target cleanup. |
| AC-14 | PASS | Operator documentation and runtime status now describe and enforce the explicit lifecycle and fail-closed package behavior. |
| AC-15 | PASS | API, lifecycle, image-runtime, frontend, generated-contract, and repository quality gates are green at the reviewed implementation head. |

## 4. Architecture and standards assessment

- **ADR-001 — Modular monolith:** compliant; no unauthorized deployment decomposition was introduced.
- **ADR-002 — PostgreSQL/PostGIS system of record:** compliant.
- **ADR-003 — Migration-only schema lifecycle:** satisfied for the accepted work-order boundary.
- **Data and migrations:** explicit, ordered, checksummed, serialized, failure-safe, and non-mutating at application startup.
- **Security:** production fixture refusal and default-password controls remain in place; this work order does not accept the broader pilot-grade identity architecture.
- **Testing and release:** real PostGIS, negative-path, transition, image-runtime, smoke, and restore evidence are present.
- **Operations and DR:** lifecycle and restore controls are materially improved; national RPO/RTO and full-service DR remain governed by later work orders.
- **Documentation:** implementation evidence is tied to the reviewed head and does not claim production or publication authority.

## 5. Recorded conditions

### C01 — Real pilot transition remains a controlled operational change

Acceptance validates the transition mechanism and representative evidence. It does not itself authorize execution against an operational pilot database. Before a real transition:

- identify the exact source database and approved change window;
- create and verify a backup;
- capture the pre-transition schema/data invariant manifest;
- run `transition-pilot` using named operator identity/context;
- capture and compare the post-transition manifest;
- run application, migration, and restore smoke checks;
- retain the change record and recovery evidence.

### C02 — Reference-data authority remains provisional

Technical loading and drift controls are accepted. The current administrative reference package must not be relabeled as final national authority without approval from the responsible government data/GIS authority and the source/effective-date record required by the data standard.

### C03 — Acceptance is not production or publication authorization

This decision accepts NLI-WO-001 only. It does not authorize:

- national-production deployment;
- official address publication, certificates, signage, or partner release;
- real citizen or agency onboarding;
- broad privileged access;
- declaration that the current data model is the canonical NLI model.

### C04 — Reviewed-head integrity

Acceptance applies to implementation commit `4fbdfd72277296ee0649de55c1bd7be039af3b07` plus this review record. Any subsequent implementation change before merge requires ordinary CI and review; any material change to accepted behavior requires SDA re-review.

## 6. Risks and follow-up

- `SDA-RISK-001` — runtime schema/reference/fixture mutation: **treatment accepted; close when PR #4 is merged to `main`**.
- `SDA-RISK-004` — competing/canonical data-model authority: **remains open** and moves to NLI-WO-002.
- Pilot-grade identity, national deployment topology, GIS governance, evidence governance, release supply-chain, and national DR risks remain open under their assigned future work orders.
- Advisory: future public-safe/operator error shaping should avoid exposing absolute filesystem paths when the package-error detail is not operationally necessary.

## 7. Decision

`ACCEPTED WITH RECORDED CONDITIONS`

NLI-WO-001 has satisfied its controlled implementation and evidence boundary. The source may be merged to `main` after normal exact-head checks and inclusion of this acceptance record.

This acceptance establishes a migration-only database lifecycle foundation for the next work order; it does not make the overall platform national-production-ready.

## 8. Next controlled work

After merge:

1. record NLI-WO-001 as accepted and close SDA-RISK-001;
2. preserve the accepted migration and startup controls;
3. issue NLI-WO-002 — Canonical National Location Data Model;
4. perform any real pilot transition under condition C01 rather than as an untracked developer action.

## 9. Review 04 resolution log

| Finding | Resolution | Evidence | SDA disposition | Date |
|---|---|---|---|---|
| F08 | Runtime evaluator moved into `app`; actual Docker image built, imported, booted, authenticated, and queried in CI. | Commit `4fbdfd72277296ee0649de55c1bd7be039af3b07`; API run `29289730248`, job `api-image-runtime`. | RESOLVED | 2026-07-13 |
| F10 | Invalid/missing migration packages fail before ledger creation and produce non-ready API/production status. | Commit `4fbdfd72277296ee0649de55c1bd7be039af3b07`; parameterized CLI/API tests; API run `29289730248`. | RESOLVED | 2026-07-13 |
