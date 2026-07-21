# S19 — Backend Services and Domain Logic

## Invoke when

- changing FastAPI routes, application services, domain rules, or persistence;
- adding transactions, concurrency controls, idempotency, jobs, or audit events;
- refactoring backend modules or cross-domain behavior.

## Required inputs

- owning bounded domain and use case;
- current handlers, contracts, policies, queries, and tests;
- canonical data model and lifecycle rules;
- API/identity/security/audit standards;
- database and operations constraints.

## Procedure

1. Define command/query, actor context, permission/scope, preconditions, state transition, outputs, audit, and failure behavior.
2. Keep route handlers thin: validate contract, resolve identity/policy, call application service, map typed result/error.
3. Place invariants and transitions in domain/application services, not UI code or scattered route branches.
4. Define transaction, locking, concurrency, and lost-update behavior.
5. Use domain-owned persistence adapters and explicit cross-domain interfaces.
6. Preserve candidate/evidence versus canonical authority separation.
7. Make retriable writes idempotent or duplicate-safe.
8. Write authoritative state before dispatching external effects; use durable outbox/job records where needed.
9. Define typed safe errors without leaking SQL, topology, secrets, or personal data.
10. Add unit/domain, real database, authorization, concurrency, failure, idempotency, and contract tests.
11. Update OpenAPI, generated types, audit records, and operational documentation.
12. Measure query plans and resource behavior for material paths.

## Outputs

- use-case/sequence specification;
- domain/application service implementation;
- persistence and transaction design;
- API/OpenAPI changes;
- audit/outbox/job behavior;
- positive, negative, concurrency, and failure tests;
- query/performance evidence where required.

## Stop or RFI conditions

Stop when:

- a new role, state, data class, or authority is required;
- the use case spans domains without an owner/interface;
- required consistency cannot be preserved;
- external effects would occur before authoritative commit;
- a queue/cache would become the official workflow record.

## Evidence gate

Before review:

- domain invariants and transitions execute in tests;
- authorization is enforced at the backend and data path;
- transaction/idempotency/failure behavior is demonstrated;
- OpenAPI and generated clients are current;
- audit and external-effect sequencing are verifiable.

## Anti-patterns

- Large route functions containing policy, persistence, and workflow logic.
- Directly writing another domain’s tables for convenience.
- Returning raw database rows as public/operator contracts.
- Catching all exceptions and returning ambiguous success or generic failure.
- Mutating authority in read operations.
- Using in-memory state for multi-instance authority.
