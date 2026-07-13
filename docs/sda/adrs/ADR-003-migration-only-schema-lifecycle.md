# ADR-003 — Use an Explicit Migration-Only Schema and Reference-Data Lifecycle

**Status:** Accepted  
**Date:** 2026-07-13  
**Decision authority:** System Design Authority  
**Related risks:** SDA-RISK-001, SDA-RISK-004  
**Primary implementation:** NLI-WO-001

## Context

The baseline FastAPI lifespan calls database initialization. The initialization path creates/alters schema and upserts reference and demonstration data. Numbered SQL migrations also exist, while a separate proposal schema expresses additional design intent.

This prevents a deployment from proving which schema and reference data were approved. It also means a routine application restart can mutate controlled state.

## Decision

- Versioned, immutable, checksummed migration files are the sole production schema authority.
- Migrations run as explicit release actions before compatible application activation.
- Ordinary API and worker startup must not execute DDL, apply migrations, seed reference data, or load fixtures.
- The application may inspect migration state and fail readiness when required migrations are missing or checksums mismatch.
- Reference data is managed through explicit, versioned, auditable load/update commands with declared source and ownership.
- Development/training/test fixtures use a separate, environment-guarded command and reserved metadata/identifiers.
- Controlled pilot and production environments refuse demonstration fixture loading and default credentials.
- Already-applied migration files are never edited; corrections use a new migration.

## Deployment behavior

A deployment follows:

1. validate artefact, configuration, backup, and target migration state;
2. run approved migrations through the release process;
3. validate schema/checksums and required reference-data version;
4. deploy/start compatible application artefacts;
5. run readiness and smoke checks;
6. monitor and execute rollback or forward recovery if required.

For incompatible changes, use expand–migrate–contract across releases.

## Reference-data behavior

Official administrative units and controlled vocabularies must record source, version/effective date, and authority. They are not ordinary fixtures. Updates preserve stable codes and historical meaning.

## Consequences

### Positive

- reproducible empty-database creation;
- auditable release responsibility;
- predictable startup and horizontal scaling;
- safe checksum and drift detection;
- clear separation of official reference data from examples;
- testable upgrade and recovery paths.

### Costs

- initial extraction of bootstrap DDL into migrations;
- transition tooling for existing databases;
- dedicated local developer setup commands;
- more deliberate release sequencing.

### Prohibited shortcut

Keeping startup DDL “only as a fallback” is not acceptable in controlled environments because it preserves two authorities. Local convenience must call the same migration runner explicitly.

## Follow-up

NLI-WO-001 implements this decision without attempting to finalize the entire canonical NLI model. NLI-WO-002 then evolves that controlled baseline through new migrations.
