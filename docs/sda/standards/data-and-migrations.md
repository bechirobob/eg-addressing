# SDA Standard — Data and Migrations

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** PostgreSQL/PostGIS schema, reference data, imports, fixtures, and all persistent state

The terms **MUST**, **MUST NOT**, **SHOULD**, and **MAY** are normative.

## 1. Canonical authority

- Numbered, version-controlled migrations under `infra/migrations/` MUST be the sole executable authority for production schema.
- Application startup MUST NOT create, alter, or drop schema; apply migrations; load reference data; or insert demonstration fixtures.
- Proposal documents and ORM/application models MAY describe intent but MUST NOT compete with the migration history.
- Every deployed database MUST expose migration version, filename, checksum, and applied timestamp.
- A changed checksum for an already-applied migration MUST fail readiness and deployment. Applied migrations are immutable; corrections use a new migration.

## 2. Migration structure

Each migration MUST:

- have a monotonic version and descriptive filename;
- state purpose, affected entities, compatibility assumptions, and recovery approach;
- be deterministic and safe for the intended source state;
- preserve data unless the work order explicitly authorizes controlled transformation or retirement;
- avoid implicit fixture or environment-specific values;
- record any required post-migration validation;
- be tested from an empty database and from the previous supported release state.

DDL SHOULD be transactional where PostgreSQL permits. Long-running or locking operations MUST include an operational plan, expected lock behavior, timing evidence, and interruption/recovery instructions.

## 3. Compatibility and deployment

Use expand–migrate–contract for changes that cannot be completed safely in one compatible deployment:

1. **Expand:** add compatible columns/tables/indexes and dual-read/write support where necessary.
2. **Migrate:** backfill with resumable, observable jobs and validation counts.
3. **Contract:** remove obsolete structures only after all supported application versions no longer depend on them.

A destructive or contract migration MUST NOT be combined with the first application release that stops using the old structure unless the SDA explicitly approves downtime and recovery controls.

Every breaking data change MUST document:

- affected API and export contracts;
- source and target record counts;
- null/invalid/duplicate handling;
- identifier preservation;
- recovery or forward-fix procedure;
- maximum tested dataset and duration.

## 4. Reference data

Reference data includes administrative units, controlled vocabularies, code systems, and other governed values used across records.

- Reference data MUST have a declared owner, source, version, effective date, and status.
- Loading reference data MUST be an explicit command or migration step, not an application side effect.
- Updates MUST preserve history or effective dating when past records depend on prior meaning.
- Official administrative data MUST NOT be replaced solely because an external map or unverified import differs.
- Localization fields MUST preserve approved Spanish and English names and aliases without changing stable codes.
- Production reference-data changes require validation evidence and, for authority-sensitive values, institutional approval.

## 5. Demonstration and test fixtures

- Demonstration, test, training, and smoke data MUST be clearly classified and separable from official or pilot-operational records.
- Production configuration MUST reject fixture-loading commands and default demonstration credentials.
- Fixtures MUST use reserved identifiers or metadata that allows complete, foreign-key-safe detection and removal.
- Tests MUST create their own isolated state or use deterministic fixture packages; they MUST NOT depend on undeclared developer database contents.
- UI labels such as “published” do not make fixture data official.

## 6. Identifiers

- Canonical entity identifiers MUST be stable, opaque, unique, and independent of mutable names.
- Public address/location codes MUST be separately modeled from internal identifiers.
- Reuse of a retired canonical identifier for a different real-world object is prohibited.
- Human-readable codes MUST have a formally approved grammar, normalization, collision, checksum/error-detection, issuance, and retirement policy before national use.
- Relationships MUST use foreign keys unless an approved integration-boundary reason prevents it.
- Free-text entity references MUST NOT substitute for canonical foreign keys.

## 7. Lifecycle and controlled vocabularies

- Status, type, source, accuracy, publication, and decision values MUST come from a documented controlled vocabulary.
- State transitions MUST be validated in the application/service layer and protected by database constraints where practical.
- `registry-ready`, `published`, `retired`, `superseded`, `disputed`, and equivalent authority states MUST have distinct semantics.
- Historical state MUST be represented by events/versions rather than silent overwrite.
- Date/time values MUST use timezone-aware UTC storage, with Africa/Malabo presentation where appropriate.

## 8. Data quality and constraints

The database MUST enforce invariant rules that protect national integrity, including as applicable:

- uniqueness and non-null requirements;
- valid coordinate ranges and geometry SRIDs;
- referential integrity;
- mutually exclusive or required relationships;
- publication prerequisites;
- active/retired record constraints;
- one-current-version rules;
- normalized search/index fields derived through controlled logic.

Validation performed only in a browser is insufficient.

## 9. Audit and provenance

Every authoritative record MUST make it possible to determine:

- origin/source;
- creation and update time;
- responsible actor or system;
- institutional and territorial context;
- validation and approval history;
- publication, correction, supersession, and retirement events;
- geometry/evidence provenance where applicable.

Bulk transformations MUST write a batch identifier and validation summary.

## 10. Imports and exports

- Imports MUST stage and validate before commit.
- The original source file, hash, source authority, mapping, validation errors, actor, and commit batch MUST be recorded.
- Import commits MUST be idempotent or detect duplicates safely.
- Exports MUST state schema version, selection criteria, classification, purpose, generating actor/client, timestamp, and expiry/retention where required.
- Spreadsheet/CSV exports MUST defend against formula injection and preserve identifier formatting.

## 11. Performance and indexing

- Indexes MUST correspond to measured or justified access paths.
- Spatial indexes MUST use geometry/geography types appropriate to the query.
- New high-volume queries require explain-plan evidence against representative scale.
- Migration backfills MUST be bounded, resumable, and observable.
- Denormalized search or analytics fields MUST be reproducible from authoritative data.

## 12. Required evidence

A database-changing pull request MUST include:

- migration files and checksums;
- before/after schema description;
- empty-database migration result;
- upgrade result from the previous supported version;
- data-validation queries and expected results;
- tests for constraints and state transitions;
- lock/duration evidence for material tables;
- backup/restore or recovery effect;
- API/type-contract changes;
- rollback or forward-recovery instructions;
- confirmation that ordinary API startup performs no schema or fixture mutation.

No migration is accepted solely because it runs on one developer database.
