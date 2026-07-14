# Skill 18 — Backend Services and Domain Logic

## Use when

Use for FastAPI routes, application services, domain rules, persistence adapters, transactions, background-command dispatch, error handling, or backend refactoring.

## Objective

Implement explicit domain behavior inside the modular monolith with clear contracts, transaction boundaries, authorization, audit, and testable persistence.

## Procedure

1. Identify owning bounded domain and application use case.
2. Define request/command/query, actor context, permission/scope, preconditions, state transition, outputs, audit, and failure behavior.
3. Keep route handlers thin:
   - parse/validate contract;
   - resolve identity/authorization;
   - call application service;
   - map domain result/error to API response.
4. Put invariants and transition rules in domain/application services, not browser code or scattered route branches.
5. Define transaction boundary and locking/concurrency behavior.
6. Use explicit persistence adapters/queries owned by the domain. Avoid uncontrolled cross-domain table writes.
7. Preserve canonical versus evidence/candidate separation.
8. Make retriable writes idempotent or duplicate-safe.
9. Emit audit events and durable outbox/job records where external or asynchronous effects follow commit.
10. Define typed errors and safe response mapping without stack/SQL/secret leakage.
11. Add unit/domain, real database, authorization, concurrency, failure, idempotency, and contract tests.
12. Update OpenAPI/generated types and operator/runbook documentation.
13. Measure query plans and resource behavior for high-volume paths.

## Backend structure expectations

Each domain should own:

```text
routes/contracts
application services/use cases
domain rules and transitions
authorization policies
persistence adapters/queries
audit events
jobs/events
tests and documentation
```

## Required evidence

- Use-case/sequence description
- Contract and OpenAPI diff
- Domain invariant/state tests
- Database transaction/concurrency result
- Authorization allow/deny tests
- Idempotency/duplicate behavior
- Audit/outbox evidence
- Query-plan/performance result where material
- Failure/recovery behavior

## Stop and escalate when

- A route requires a new authority, role, state, or data class.
- The use case spans domains without an explicit owner/interface.
- A transaction cannot preserve required consistency.
- External side effects would occur before authoritative commit.
- A background queue would become the only record of official state.

## Anti-patterns

- Large route functions containing persistence, policy, and workflow logic.
- Adding a table query directly from another domain because it is convenient.
- Returning raw database rows to public/operator clients.
- Catching all exceptions and returning success or generic 500 without audit.
- Mutating state in GET/read paths.
- Using in-memory state for multi-instance authority or rate control.
- Dispatching notifications/publication before the database transaction commits.
