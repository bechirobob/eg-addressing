# NLI-WO-001 — Closeout Record

**Work order:** [`NLI-WO-001 — Controlled Database and Reference-Data Lifecycle`](NLI-WO-001-controlled-database-lifecycle.md)  
**Status:** `ACCEPTED WITH RECORDED CONDITIONS`  
**Issued:** 2026-07-13  
**Accepted:** 2026-07-13  
**Merged:** 2026-07-13  
**Implementation PR:** `#4`  
**Reviewed implementation commit:** `4fbdfd72277296ee0649de55c1bd7be039af3b07`  
**Acceptance record:** [`NLI-WO-001-review-04.md`](../reviews/NLI-WO-001-review-04.md)  
**Merge commit:** `ed29525b9d1246adc7aeb8408832e356f139eafb`  
**Primary risk disposition:** `SDA-RISK-001 CLOSED`; `SDA-RISK-004 remains open`

## 1. Accepted outcome

The accepted implementation establishes:

- versioned, ordered, checksummed PostgreSQL/PostGIS migrations as the executable schema authority;
- non-mutating API startup with respect to schema, reference data, and development fixtures;
- explicit, separate reference-data and non-production fixture lifecycles;
- fail-closed behavior for pending, mismatched, unknown, missing, empty, invalid-name, and duplicate-version migration packages;
- serialized migration execution and transactional failure handling;
- representative pre-WO pilot transition checks and preservation evidence;
- deterministic schema/data invariant manifests;
- real PostGIS integration tests, smoke checks, and source/restored invariant comparison;
- actual API Docker image build, import, boot, authentication, health, migration-status, and production-readiness verification;
- truthful operator migration status and production-readiness behavior.

## 2. Recorded conditions

### C01 — Real pilot transition remains a controlled operational change

The accepted transition mechanism must not be run against an operational pilot database as an informal developer action. A real transition requires:

- an identified source database and approved change window;
- verified backup;
- captured pre-transition schema/data invariant manifest;
- named operator/execution context;
- captured and compared post-transition manifest;
- application, migration, smoke, and restore verification;
- retained change and recovery evidence.

### C02 — Reference-data authority remains provisional

The loader, package, checksum, history, and drift controls are accepted. The current administrative reference package is not thereby declared final national authority. Approval must come from the responsible government data/GIS authority with recorded source and effective date.

### C03 — Acceptance is not production or publication authorization

The closeout does not authorize:

- national-production deployment;
- official address publication, certificates, signage, or partner release;
- real citizen or agency onboarding;
- broad privileged access;
- declaration that the current operational data model is the canonical NLI model.

## 3. Preserved controls

Future work must preserve:

- migration-only schema authority;
- application-startup invariance;
- immutable applied migration files and checksum/filename verification;
- explicit reference and fixture commands;
- production fixture refusal;
- operator fail-closed migration reporting;
- real PostGIS lifecycle CI;
- API image-runtime verification;
- backup/restore invariant comparison.

A future work order may extend these controls but must not silently weaken or remove them.

## 4. Follow-up

- `NLI-WO-002` establishes the canonical National Location Infrastructure data model and convergence plan.
- `SDA-RISK-004` remains a P0 production blocker until one model is accepted and its controlled implementation is complete.
- Identity, publication, production platform, GIS governance, evidence governance, and national disaster-recovery risks remain assigned to later work orders.
