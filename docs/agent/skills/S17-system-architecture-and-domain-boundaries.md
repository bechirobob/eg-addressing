# S17 — System Architecture and Domain Boundaries

## Invoke when

- changing repository or deployment architecture;
- defining bounded domains, trust zones, module ownership, or dependency direction;
- adding a service, worker, database, integration boundary, or asynchronous flow;
- considering microservice extraction or cross-domain data access.

## Required inputs

- target reference architecture and accepted ADRs;
- current repository/component map;
- data ownership and source-of-truth register;
- trust-zone, identity, security, operations, and DR standards;
- affected work order and module owners.

## Procedure

1. Identify affected bounded domains and accountable owners.
2. Document components, data flows, trust boundaries, deployment units, and external dependencies.
3. For each domain define ownership of routes/contracts, use cases, rules, persistence, authorization, audit, tests, and documentation.
4. Confirm one authoritative owner for every entity and state.
5. Define allowed cross-domain interfaces; minimize direct writes to another domain’s tables.
6. Define transaction boundaries, durable events, idempotency, reconciliation, and failure behavior.
7. Map public, operator, partner, data, operations, and security zones.
8. Preserve the modular monolith unless an accepted ADR justifies extraction.
9. For any proposed extraction, document measured scale/isolation/ownership need plus identity, consistency, deployment, observability, backup, and recovery.
10. Add dependency/conformance checks where practical.

## Outputs

- architecture/context/component diagrams;
- domain ownership matrix;
- trust-boundary and data-flow map;
- interface/dependency register;
- transaction/event/job design;
- ADR/RFI and transition plan;
- architecture conformance evidence.

## Stop or RFI conditions

Stop when:

- two modules claim the same canonical data;
- a new database/service/gateway lacks an ADR;
- cross-domain writes bypass the owning domain;
- Redis, a queue, analytics store, or frontend cache would become authoritative;
- a public/operator/partner trust zone is blurred;
- service extraction is justified only by fashion or file size.

## Evidence gate

Before review:

- every affected domain has an owner and interface;
- canonical data ownership is singular;
- trust zones and authority boundaries are explicit;
- transaction, failure, audit, operations, and recovery behavior are documented;
- any new deployment boundary has an ADR and executable/operational evidence plan.

## Anti-patterns

- Calling a tightly coupled application a modular monolith without ownership rules.
- Sharing internal database tables as integration contracts.
- Hiding distributed transactions behind vague eventual-consistency language.
- Splitting services before identity, observability, deployment, and recovery exist.
- Creating a second registry, identity store, or publication authority in another module.
