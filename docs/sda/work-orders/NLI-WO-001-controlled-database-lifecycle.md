# NLI-WO-001 — Controlled Database and Reference-Data Lifecycle

**Status:** ISSUED — implementation may begin after this SDA control pack is merged to `main`  
**Priority:** P0 production blocker  
**Issued:** 2026-07-13  
**Authority:** System Design Authority  
**Implementation branch:** `nli/wo-001-controlled-database-lifecycle`  
**Primary risks:** SDA-RISK-001 and SDA-RISK-004  
**Related decisions:** ADR-001, ADR-002, ADR-003  
**Readiness boundary:** controlled pilot engineering; this work order does not authorize national production or official publication

## 1. Objective

Remove database schema creation, schema alteration, reference-data loading, and demonstration-fixture mutation from ordinary FastAPI/API startup.

After acceptance:

- a new empty PostgreSQL/PostGIS database can be built deterministically through the controlled migration process;
- an existing pilot database has a documented, tested transition path that preserves its data;
- API and worker startup are non-mutating with respect to schema, reference data, and fixtures;
- migrations, reference data, and development fixtures have separate explicit lifecycles;
- controlled environments refuse demonstration fixture loading and default demonstration credentials;
- CI proves the behavior against real PostgreSQL/PostGIS;
- migration state is observable and pending/mismatched state is never silently corrected by application startup.

This work creates a controlled foundation for NLI-WO-002. It does not finalize the national canonical data model.

## 2. Current condition

At the baseline commit:

- FastAPI lifespan calls `init_db()`;
- `services/api/app/db.py` creates/alters tables and upserts reference and demonstration data;
- migrations `001` through `006` exist, but `001` is a marker and later migrations assume bootstrap-created tables;
- `ops_status.py` expects a `schema_migrations` ledger;
- demonstration identities and pilot records are defined in application source;
- local Docker startup depends on application initialization to make the database usable.

The implementation agent MUST inspect the current branch again before planning and must not assume this description is exhaustive.

## 3. Mandatory reading

Before coding, read:

- repository `AGENTS.md`;
- `docs/sda/charter.md`;
- `docs/sda/architecture-baseline.md`;
- `docs/sda/target-reference-architecture.md`;
- `docs/sda/risk-register.md`;
- `docs/sda/adrs/ADR-001-modular-monolith.md`;
- `docs/sda/adrs/ADR-002-postgresql-postgis-system-of-record.md`;
- `docs/sda/adrs/ADR-003-migration-only-schema-lifecycle.md`;
- `docs/sda/standards/data-and-migrations.md`;
- `docs/sda/standards/security.md`;
- `docs/sda/standards/testing-and-release.md`;
- `docs/sda/standards/operations-and-disaster-recovery.md`;
- `docs/sda/standards/documentation-and-records.md`.

Submit an implementation plan using `docs/sda/templates/implementation-plan.md` before changing implementation files.

## 4. In scope

### 4.1 Migration authority

- Introduce or complete an explicit migration runner appropriate to the repository's SQL migration approach.
- The runner may bootstrap only its own migration-ledger metadata.
- Preserve checksums and immutability of already-applied migration files.
- Provide a versioned, deterministic migration path that builds the full current operational schema from an empty PostGIS database before dependent migrations execute.
- Provide safe behavior for an existing pilot database in which tables may already exist and migrations may already be recorded.
- Detect pending versions, checksum mismatch, failed application, and incompatible source state.

### 4.2 Non-mutating application startup

- Remove mutating schema/reference/fixture behavior from API lifespan and normal worker/application startup.
- Startup may validate connectivity and expose state; it may not repair or apply database changes.
- Define liveness separately from readiness. Pending or mismatched migrations must make the relevant readiness/production-readiness check non-ready while preserving truthful diagnostics.

### 4.3 Reference data

- Separate governed reference data from application code and from demonstration fixtures.
- Provide an explicit versioned load/update command for current provinces, administrative units, and other required governed seed values.
- Record source/version metadata or a manifest sufficient to audit what reference-data package was loaded.
- Make loading idempotent while preserving stable identifiers and avoiding unauthorized overwrite of operational edits.
- Document which current values are authoritative, provisional, map-referenced, or pilot routing data; do not silently upgrade their authority.

### 4.4 Development, training, and test fixtures

- Move demonstration identities and example operational records behind a separate explicit fixture command/package.
- Restrict that command to approved non-production environments through positive allowlisting and production refusal.
- Preserve deterministic local/test setup and foreign-key-safe cleanup.
- Ensure fixture records are detectable as non-official and cannot be confused with production publication.
- Remove default credential dependence from controlled-environment startup.

### 4.5 Developer and operator workflow

- Provide explicit commands/scripts for:
  - migration status;
  - migrate/apply;
  - reference-data status/load;
  - development fixture load/cleanup;
  - complete local bootstrap;
  - controlled transition of an existing pilot database.
- Update Docker/local setup so convenience scripts invoke the explicit lifecycle rather than relying on API startup.
- Update runbooks and environment templates with safe sequencing.

### 4.6 CI and tests

- Add real PostgreSQL/PostGIS CI coverage for empty creation, upgrade/transition, non-mutating startup, readiness, reference data, and fixture guards.
- Preserve existing backend/frontend and repository quality checks.

## 5. Out of scope

Do not use this work order to:

- replace the full schema with `docs/source-proposals/schema.sql`;
- finalize UUID strategy, national address-code grammar, parcels, building units, agency clients, or complete geometry governance;
- implement the national RBAC/ABAC model;
- redesign public/operator workflows unrelated to migration/readiness;
- introduce microservices, Kubernetes, a new database, or a new ORM solely for this task;
- claim national-production readiness;
- enable official publication;
- delete or rewrite existing pilot data without an approved transition and evidence.

Necessary compatibility scaffolding may be added, but broader model changes belong to NLI-WO-002 or later work orders.

## 6. Prohibited approaches

- Do not edit an already-applied migration and update its checksum.
- Do not retain application startup DDL “as a fallback” in controlled environments.
- Do not create a second untracked schema snapshot that competes with migrations.
- Do not mark migrations applied without verifying the actual schema/source state.
- Do not solve empty-database creation only by running the old `init_db()` first.
- Do not load fixtures based only on a weak negative check such as `APP_ENV != production`; use explicit approved environment allowlisting and production safeguards.
- Do not retain source-controlled usable default passwords for controlled environments.
- Do not make CI pass by disabling existing migration/readiness checks.
- Do not treat reference data, map suggestions, local-area labels, and demonstration records as equivalent authority classes.
- Do not auto-migrate independently in every API replica.

If the ordering/ledger state of existing migrations prevents a safe single-authority solution without changing an applied file, raise an RFI before implementation.

## 7. Functional requirements

### R1 — Migration ledger

The migration mechanism MUST record unique version, filename, SHA-256 checksum, applied time, and execution identity/context where practical. Duplicate versions are invalid.

### R2 — Deterministic ordering

Migration ordering MUST be explicit and validated. Empty-database application MUST execute prerequisites before migrations that create dependent indexes/columns.

### R3 — Atomicity and failure

Each migration MUST use transactional execution where supported. Failure MUST stop subsequent migrations, return non-zero status, preserve an actionable error, and never record a failed migration as applied.

### R4 — Concurrency

The migration runner MUST prevent concurrent migration execution using an advisory lock or equivalent database control.

### R5 — Drift

A checksum mismatch or unknown/incompatible ledger state MUST block migration and readiness pending operator/SDA resolution.

### R6 — Empty database

An empty PostGIS database MUST reach the complete current supported schema solely through the explicit migration command.

### R7 — Existing database transition

A documented command/process MUST inspect and transition the current pilot schema without deleting operational data. It must distinguish “already structurally present and safely baselined” from “missing/incompatible.”

### R8 — Startup invariance

Starting and stopping the API against a migrated database MUST leave schema, migration ledger, reference-data rows, user rows, and pilot fixture counts unchanged except ordinary runtime/session/health effects explicitly identified by tests.

### R9 — Pending migration behavior

Starting the API against a database with a pending migration MUST NOT apply it. Readiness/status MUST report the pending state accurately.

### R10 — Reference-data lifecycle

Reference data MUST be explicit, versioned, idempotent, and auditable. Loading it must not silently overwrite a locally governed value with a lower-authority source.

### R11 — Fixture isolation

Development/training/test fixtures MUST load only through an explicit command in an approved environment, be detectable, and clean up safely. Production attempts MUST fail closed.

### R12 — Credential safety

Controlled startup MUST not create or reset demonstration passwords. Existing controlled accounts must not be overwritten by reference/fixture loading.

### R13 — Local usability

A documented local bootstrap command MUST produce a usable development stack by explicitly running migrations, reference data, and optional development fixtures in that order.

### R14 — Operational visibility

Migration and reference-data status MUST be available to authorized operators without exposing credentials, SQL, internal secrets, or unnecessary topology.

### R15 — Backup/restore compatibility

Existing database backup and restore scripts/drills MUST continue to work, and restore validation MUST include migration-ledger integrity.

## 8. Acceptance criteria

### AC-01 — Empty PostGIS creation

In a clean CI environment, an empty PostgreSQL/PostGIS database is built through the migration command alone. All current operational tables, required extensions, constraints, and indexes exist. No API import/startup bootstrap is called.

### AC-02 — Full ordered ledger

The resulting ledger contains one entry for every expected migration with unique version, filename, correct checksum, and applied timestamp. Migration status reports `current`.

### AC-03 — Applied migration immutability

Changing the contents of a previously applied migration in a controlled test produces a checksum-mismatch failure and non-ready status; the runner does not rewrite the ledger.

### AC-04 — Failure and concurrency safety

Tests prove a failed migration is not recorded and later migrations do not run. A concurrent second runner cannot apply the same migration simultaneously.

### AC-05 — Existing pilot transition

A representative database matching the pre-work-order operational schema is transitioned successfully. Before/after counts and selected hashes/relationships prove no unintended loss of users, territories, roads, buildings, addresses/address records, submissions, evidence metadata, and audit events.

### AC-06 — API startup is schema-invariant

A schema fingerprint and controlled row-count snapshot taken before and after API startup/shutdown show no DDL, migration, reference-data, user, or fixture mutation attributable to startup.

### AC-07 — Pending migration is not auto-applied

With one known migration pending, API startup succeeds or fails only according to documented liveness behavior, does not apply the migration, and reports non-ready/pending status truthfully.

### AC-08 — Reference data is explicit and idempotent

The reference-data command records/returns package version, loads required values, and produces no unintended changes on a second run. A conflicting lower-authority update is rejected or surfaced for controlled resolution.

### AC-09 — Fixtures are isolated

An approved development/test environment can explicitly load and clean fixtures deterministically. Fixture records are identifiable. A production-labeled environment refuses fixture load and does not create default users/passwords.

### AC-10 — Existing credentials are preserved

Migration, reference-data load, and ordinary startup do not reset an existing user's password hash, role, activation state, or sessions except where an explicit test command deliberately manages fixtures in an allowed environment.

### AC-11 — Local bootstrap remains usable

The documented local bootstrap path starts required services, applies migrations, loads reference data, optionally loads development fixtures, and reaches passing health/readiness and existing smoke checks.

### AC-12 — CI uses real PostgreSQL/PostGIS

GitHub Actions or equivalent repository CI runs the empty-build, migration, transition, startup-invariance, readiness, reference, and fixture-guard tests against a real PostGIS service.

### AC-13 — Backup and restore remain valid

A backup created after migration restores into a disposable database. The restored database has a current, checksum-valid ledger and matching selected row counts/invariants. The temporary target is removed.

### AC-14 — Documentation and operator safety

README/runbooks/environment templates describe exact commands, environment guards, deployment sequence, failure handling, and recovery. No document instructs operators to rely on API startup for schema or fixture setup.

### AC-15 — Existing quality gates pass

Backend tests, frontend CI/contract checks, migration status, source/role/accessibility/design guards affected by the change, and relevant smoke tests pass. Skipped checks require an explicit blocker and cannot be presented as acceptance.

## 9. Required implementation evidence

The pull request MUST use `docs/sda/templates/pull-request-evidence.md` and include:

- accepted/revised implementation plan;
- migration inventory and checksums;
- empty-database CI output;
- representative existing-database transition method and before/after validation;
- schema-fingerprint startup-invariance result;
- pending/checksum/failure/concurrency test results;
- reference-data manifest/status and idempotency result;
- fixture allow/refuse/cleanup evidence;
- exact local bootstrap commands and result;
- OpenAPI/generated-type diff if operator endpoints change;
- security/threat note covering migration authority, fixture abuse, and credentials;
- backup/restore-drill result including ledger validation;
- screenshots only if operator migration/readiness UI changes, labeled under the UI standard;
- residual risks and all RFIs.

## 10. Expected implementation shape

The agent may refine names, but the repository should end with clearly separated concepts equivalent to:

```text
infra/migrations/          immutable ordered schema changes
infra/reference-data/      governed versioned reference package(s)
infra/fixtures/ or tests/  explicit non-production fixtures
infra/scripts/             migrate/status/reference/fixture/bootstrap commands
services/api/              non-mutating runtime and readiness inspection
.github/workflows/         real PostGIS migration/transition CI
```

The exact migration runner may be a small maintained Python/SQL tool or an established migration framework if justified. Adding a framework requires dependency, compatibility, and operational rationale; it must not trigger a broad ORM rewrite.

## 11. Agent checkpoint before code

The agent's first response after reading this work order MUST provide:

1. acceptance-criterion-mapped implementation plan;
2. proposed migration ordering/baseline strategy that preserves existing `001`–`006` checksums;
3. existing-database transition strategy;
4. exact files expected to change;
5. CI/test design;
6. risks and RFIs.

Do not begin implementation until this plan has been produced in the agent's working context. A separate human confirmation is not required for choices already authorized here; unresolved reserved decisions require an RFI.

## 12. Review and completion

The implementation agent opens a pull request from `nli/wo-001-controlled-database-lifecycle` and provides the required evidence. The SDA reviews the exact head commit and creates `docs/sda/reviews/NLI-WO-001-review-01.md`.

Possible outcomes:

- `ACCEPTED`
- `ACCEPTED WITH RECORDED CONDITIONS`
- `REWORK REQUIRED`
- `REJECTED — ARCHITECTURAL REDESIGN REQUIRED`

This work order closes SDA-RISK-001 only after accepted evidence proves the behavior. SDA-RISK-004 remains open until the canonical data model is accepted under NLI-WO-002.
