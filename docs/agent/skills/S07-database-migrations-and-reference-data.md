# S07 — Database Migrations and Reference Data

## Invoke when

- adding or changing executable schema;
- writing data migrations or backfills;
- changing the migration runner or ledger;
- loading reference data;
- changing development/test fixtures;
- modifying backup/restore expectations.

## Required inputs

- accepted NLI-WO-001 lifecycle controls;
- data-and-migrations standard;
- current migration ledger and checksums;
- source and target schema/model;
- representative data volumes;
- backup/restore and deployment procedures.

## Procedure

### 1. Preserve one schema authority

- migrations are the sole executable production schema authority;
- application startup, reference loaders, and fixture commands must not execute DDL;
- applied migration contents are immutable;
- corrections use new migrations.

### 2. Design migration sequence

Use:

```text
EXPAND → BACKFILL/MIGRATE → VALIDATE → CUTOVER → CONTRACT
```

For each migration record:

- source state;
- target state;
- compatibility window;
- lock and duration behavior;
- transaction boundary;
- interruption and rerun behavior;
- rollback or forward recovery.

### 3. Make execution safe

- acquire one migration lock before ledger creation or mutation;
- reject concurrent runners;
- fail on missing, empty, invalid, duplicate, unknown, filename-mismatched, or checksum-mismatched packages;
- never record failed migrations as applied;
- fail before ledger mutation when the migration package is invalid.

### 4. Design data transformations explicitly

Every backfill must state:

- source query and stable key;
- target query/row;
- controlled-value translations;
- crosswalk joins;
- idempotency key;
- exception queue;
- value, relationship, and count validation;
- performance batches;
- expected duration at representative scale.

### 5. Govern reference data

Reference packages require:

- package identity and checksum;
- source and authority;
- effective date and version;
- idempotent load behavior;
- immutable load history;
- conflict and lower-authority overwrite prevention;
- explicit status command that does not mutate schema.

### 6. Isolate fixtures

Fixtures must:

- be explicit and positively allowlisted by environment;
- refuse controlled production environments;
- be deterministic and ownership-tracked;
- preserve pre-existing records;
- clean only records owned by the fixture batch;
- remain visibly non-official.

### 7. Prove lifecycle in real PostGIS

CI must test:

- empty database creation;
- previous-version upgrade;
- checksum and filename drift;
- failed migration rollback;
- concurrent execution;
- pending migration readiness;
- startup invariance;
- reference package drift/idempotency;
- fixture collision/reload/cleanup;
- backup/restore ledger and invariant parity;
- actual API image/runtime where affected.

## Outputs

- immutable migration files;
- migration and data-transition plan;
- reference package and manifest;
- fixture package and ownership rules;
- CI evidence;
- deployment/recovery runbook updates.

## Stop or RFI conditions

Stop when:

- the target model is unaccepted;
- a destructive change lacks approved retention/authority;
- the backfill has unresolved values without an owned exception path;
- a migration requires editing an applied file;
- a runtime fix appears in a design-only work order;
- rollback is claimed but data/external effects make it unsafe;
- a reference source’s government authority is unknown.

## Evidence gate

Before merge:

- exact-head CI is green;
- empty and upgrade paths pass;
- startup performs no DDL/data seeding;
- negative lifecycle tests execute;
- backup/restore compares source and restored invariants;
- controlled evidence names exact migrations/checksums and recovery behavior.

## Anti-patterns

- Running the old bootstrap before migrations in an empty-database test.
- Creating tables in a reference or fixture command.
- Using table existence alone as a transition fingerprint.
- Releasing the migration lock between compatibility validation and transition.
- Deleting fixture IDs without proving batch ownership.
- Mixing a migration-runner bug fix into an unrelated design PR.
