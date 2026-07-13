# ADR-002 — PostgreSQL/PostGIS Is the Authoritative NLI System of Record

**Status:** Accepted  
**Date:** 2026-07-13  
**Decision authority:** System Design Authority  
**Related risks:** SDA-RISK-004, SDA-RISK-007, SDA-RISK-008, SDA-RISK-010

## Context

The NLI needs transactional integrity, referential constraints, record history, spatial querying, and auditable publication workflows. The current platform already uses PostgreSQL with PostGIS, while Redis supports cache/queue behavior and S3-compatible storage holds evidence objects.

Introducing multiple authoritative databases at this stage would create reconciliation, distributed consistency, backup, and governance burdens without a demonstrated need.

## Decision

PostgreSQL/PostGIS will be the authoritative transactional and spatial system of record for the NLI until an accepted ADR states otherwise.

It will hold:

- canonical entity identifiers and relationships;
- administrative hierarchy and geometry versions;
- roads, buildings, entrances, addressable objects, and location records;
- lifecycle state, versions, status events, corrections, and publication state;
- identity assignment, role/permission/scope metadata;
- evidence metadata, hashes, classification, retention, and object references;
- approval and audit events;
- partner/client registration and contract metadata.

S3-compatible object storage will hold binary evidence and generated controlled artefacts. PostgreSQL will hold their authoritative metadata, hash, ownership, classification, lifecycle, and relationship to decisions.

Redis may hold only reconstructable cache, rate-limit, lock, queue, and coordination data. Loss of Redis must not erase or fabricate official state.

Analytical stores, search indexes, map tiles, and reporting read models may be introduced as derived projections. They must be reproducible, purpose-limited, monitored for freshness, and incapable of directly mutating canonical state.

## Spatial implications

- Canonical geometries use typed PostGIS columns with enforced SRID and spatial indexes.
- Raw citizen, field, imported, and map-derived observations retain provenance and validation state.
- Promotion to authoritative geometry is an explicit workflow and event.
- Metric calculations use documented projected or geodesic methods.

## Consequences

### Positive

- strong transactional and referential integrity;
- one recovery boundary for registry state and authority history;
- mature spatial capabilities;
- simpler audit, migration, and consistency model;
- reduced operational complexity during initial national rollout.

### Constraints

- application modules must avoid uncontrolled cross-domain table access;
- PostgreSQL scaling, partitioning, indexing, and connection management require deliberate capacity planning;
- object recovery must be coordinated with database metadata;
- derived systems require lineage and reconciliation.

### Risks

A single authoritative platform can become a bottleneck or large blast radius if operated as a single host. This decision therefore depends on production high availability, point-in-time recovery, isolated backups, and tested failover rather than adding databases to mask weak operations.

## Follow-up

- NLI-WO-001 establishes migration-only schema authority.
- NLI-WO-002 defines the canonical data model and data dictionary.
- NLI-WO-005 defines production database topology and security.
- NLI-WO-006 defines full geometry governance.
- NLI-WO-008 defines recovery objectives and end-to-end restoration.
