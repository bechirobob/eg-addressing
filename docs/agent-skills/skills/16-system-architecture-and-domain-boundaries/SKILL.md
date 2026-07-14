# Skill 16 — System Architecture and Domain Boundaries

## Use when

Use for repository architecture, bounded domains, modular-monolith structure, trust zones, service/data ownership, dependency direction, synchronous/asynchronous boundaries, or proposed service extraction.

## Objective

Keep the NLI coherent as one governed platform while allowing modules to evolve independently without creating duplicate authority, uncontrolled coupling, or premature distributed complexity.

## Architectural baseline

The initial target is a modular monolith with supporting processes:

```text
public/operator portals
FastAPI domain application
worker process
PostgreSQL/PostGIS
Redis for reconstructable coordination
object storage for governed evidence/artifacts
```

## Procedure

1. Identify affected bounded domains and accountable owners.
2. Document current components, data flows, trust zones, dependencies, and deployment units.
3. For each domain define ownership of:
   - routes/contracts;
   - application services/use cases;
   - domain rules and state transitions;
   - persistence adapters/tables;
   - authorization policies;
   - audit events;
   - tests and documentation.
4. Confirm one authoritative data owner for every entity and state.
5. Define allowed cross-domain interfaces; minimize direct table access across domains.
6. Identify synchronous calls, durable events, background jobs, and reconciliation paths.
7. Define transaction boundaries, idempotency, failure behavior, and observability.
8. Map public, operator, partner, data, operations, and security trust zones.
9. Assess whether the change preserves the modular monolith or requires an ADR.
10. Consider service extraction only when measured scaling, isolation, ownership, or regulatory need justifies it.
11. Define transition sequencing, compatibility, recovery, and ownership.
12. Add architecture/dependency validation where practical.

## Required artifacts

- Context/component/domain diagram
- Trust-boundary and data-flow map
- Domain ownership matrix
- Interface/dependency map
- Transaction/event/job boundaries
- Failure and recovery behavior
- ADR/RFI for material architecture choices
- Migration/transition sequence
- Architecture conformance tests or lint rules where applicable

## Service-extraction criteria

A separate service requires evidence of at least one:

- materially different scaling or availability need;
- security/regulatory isolation requirement;
- independent ownership and release cadence;
- measured contention or blast-radius problem;
- technology need that cannot be safely supported in the monolith;
- partner boundary requiring independent lifecycle.

Before extraction define data ownership, consistency, event delivery, identity, monitoring, deployment, backup, and DR.

## Stop and escalate when

- Two modules claim the same canonical data.
- A new database/service/gateway is proposed without an ADR.
- Cross-domain direct writes bypass the owning domain.
- Redis/queue/cache would become authoritative.
- A public/operator/partner trust zone is blurred.
- A service split is justified only by fashion or file size.

## Anti-patterns

- Calling one large module a modular monolith without ownership boundaries.
- Creating microservices before defining domains and operations.
- Sharing internal tables as an integration contract.
- Hiding distributed transactions behind eventual-consistency language.
- Duplicating identity, publication, or registry authority in separate modules.
- Architecture diagrams with no transaction, failure, security, or ownership semantics.
