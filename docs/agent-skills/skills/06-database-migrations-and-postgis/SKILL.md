# Skill 06 — Database Migrations and PostGIS

## Use when

Use for schema, migration runners, reference data, fixtures, data transitions, PostGIS extensions/types/indexes, backup/restore compatibility, or migration readiness.

## Objective

Make database change explicit, reproducible, failure-safe, reversible or forward-recoverable, and governed by one migration authority.

## Protected rules

- Versioned migrations are the executable schema authority.
- Application startup must not create/alter schema or seed controlled data.
- Applied migrations are immutable and checksummed.
- PostgreSQL/PostGIS is authoritative.
- Reference data and fixtures have separate explicit lifecycles.
- Redis is never the authoritative business record.

## Procedure

1. Inspect current migration ledger, migration files, database version, extensions, and runtime readiness logic.
2. Build a disposable database from empty using the real migration command.
3. Query `pg_catalog`, constraints, indexes, and geometry metadata to establish the source state.
4. Design the migration using expand–migrate–contract where compatibility requires it.
5. Define locking, transaction, duration, concurrency, and failure behavior.
6. Define existing-data transformation, exceptions, crosswalks, and validation queries.
7. Define rollback versus forward recovery.
8. Keep reference-data packages explicit, versioned, source-attributed, and idempotent.
9. Keep fixtures explicit, positively environment-allowlisted, ownership-tracked, collision-safe, repeatable, and cleanable.
10. Add real PostgreSQL/PostGIS tests for:
    - empty build;
    - upgrade/transition;
    - checksum/filename drift;
    - failed migration and later-stop;
    - concurrent runners;
    - startup invariance;
    - pending/non-ready behavior;
    - credential/session preservation where affected;
    - backup/restore invariants.
11. Verify API/image/bootstrap behavior uses the explicit lifecycle.
12. Update runbooks, environment templates, and operator status.

## Required evidence

- Migration inventory/checksums
- Empty and upgrade results
- Source/target catalog or fingerprint
- Lock/concurrency result
- Before/after counts, hashes, and relationships
- Pending/drift/failure tests
- Reference/fixture tests
- Restore comparison
- Deployment/recovery sequence

## Stop and escalate when

- An applied migration must be edited.
- Existing data cannot be mapped without loss or authority.
- Source schema drift is outside the supported compatibility fingerprint.
- A long lock or downtime requires risk acceptance.
- A design-only work order would be changed to executable DDL.

## Anti-patterns

- Running old bootstrap DDL before migrations.
- Creating tables inside reference/fixture loaders.
- Marking a migration applied based only on table-name presence.
- Releasing and reacquiring the migration lock between compatibility check and application.
- Calling pseudo-SQL such as `ASSERT count(...)` executable evidence.
- Verifying restore only by migration version while ignoring authoritative row invariants.
