# ADR-001 — Use a Modular Monolith as the Initial NLI Application Architecture

**Status:** Accepted  
**Date:** 2026-07-13  
**Decision authority:** System Design Authority  
**Related risks:** SDA-RISK-005, SDA-RISK-012

## Context

The platform already uses a Next.js portal, FastAPI backend, PostgreSQL/PostGIS, Redis, and S3-compatible storage. The programme needs strong domain boundaries, national reliability, and institutional governance, but it does not yet have measured scale or independent teams that justify the cost of many distributed services.

Premature microservices would add network failure, distributed transactions, deployment and observability burden, duplicated security policy, and harder local/pilot operation before those costs solve a demonstrated problem.

At the same time, the existing API and persistence modules contain many responsibilities. Retaining one deployable application must not mean retaining one undifferentiated codebase.

## Decision

The initial NLI application will be a **modular monolith** with explicit bounded domains:

- Identity and Trust;
- Administrative Geography;
- Location Registry;
- Field Operations;
- Evidence and Verification;
- Publication and Corrections;
- Agency Integration;
- Audit, Reporting, and Analytics.

Domains will be separated through route modules, application services/use cases, domain rules, authorization policies, persistence adapters, events, tests, and documentation.

Supporting processes may be deployed separately where operationally appropriate:

- web/public and operator portal;
- API process;
- worker process for long-running/retriable work;
- PostgreSQL/PostGIS;
- Redis for reconstructable cache/queue/coordination;
- object storage for evidence and controlled artefacts.

Independent microservices require a new ADR and measured justification.

## Extraction criteria

A domain may be considered for independent deployment when one or more are demonstrated:

- materially different scaling or availability needs;
- security or regulatory isolation that process/module boundaries cannot satisfy;
- independently owned release cadence and team accountability;
- sustained operational contention or blast-radius concern;
- technology requirement that cannot be supported safely within the monolith;
- partner-facing boundary needing distinct lifecycle and isolation.

Before extraction, data ownership, transaction boundaries, idempotency, event delivery, observability, deployment, and recovery must be defined.

## Consequences

### Positive

- simpler transactions around the authoritative registry;
- lower operational complexity during controlled pilot and early national rollout;
- consistent security and audit policy;
- easier local development, testing, migration, and recovery;
- deliberate domain design without forced network boundaries.

### Constraints

- modules must not access each other's internal persistence arbitrarily;
- cross-domain behavior uses explicit application interfaces/events;
- large files and shared utility layers must be reduced over time;
- worker jobs remain idempotent and traceable to authoritative state;
- Redis cannot become the sole business-event or workflow record.

### Risks

Without enforcement, “modular monolith” could become a label for a tightly coupled application. Work orders and reviews must therefore require domain ownership and interface evidence.

## Follow-up

- Refactor incrementally within functional work orders; no broad rewrite is authorized.
- Record module ownership and dependency rules as the canonical data model and authorization architecture are implemented.
