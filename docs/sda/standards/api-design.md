# SDA Standard — API Design and Integration

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** public APIs, operator APIs, partner APIs, webhooks, batch exchange, and generated contracts

## 1. Contract authority

- OpenAPI is the authoritative HTTP contract and MUST be generated or maintained with the implementation.
- Generated frontend/client types MUST be reproducible and checked for drift in CI.
- Undocumented response fields, hidden required headers, and behavior that exists only in UI code are prohibited.
- Contract changes MUST state compatibility and migration effect.

## 2. API classes

Every endpoint MUST belong to an explicit class:

- **Public:** anonymous or low-assurance citizen access using approved public projections.
- **Operator:** authenticated government workflow access.
- **Administrative:** privileged platform, identity, or configuration access.
- **Partner:** machine-to-machine institutional access with explicit contract and scope.
- **Operational:** health, readiness, metrics, or controlled operator functions.

Classes MUST have separate authorization, abuse, data-projection, and observability policies. A route path alone is not the policy.

## 3. Versioning and compatibility

- Stable external APIs MUST be versioned.
- Backwards-compatible additions MAY remain in the current version.
- Removal, semantic change, field-type change, identifier change, or authorization change requires a transition plan and usually a new version.
- Deprecations MUST state replacement, notice date, end-of-support date, affected partners, and monitoring evidence.
- Internal implementation refactoring MUST preserve accepted external contracts unless a work order authorizes change.

## 4. Resource and action design

- Resource names and identifiers MUST use stable canonical semantics.
- State-changing operations that represent business decisions MAY use explicit action endpoints when ordinary CRUD would obscure authority and audit meaning.
- Workflow actions MUST validate allowed transitions and required approvals.
- `DELETE` MUST NOT imply physical erasure of official history unless retention policy and work order explicitly authorize it. Prefer archive, retire, revoke, or supersede semantics.
- Public codes and internal identifiers MUST not be conflated.

## 5. Requests and validation

- Input schemas MUST reject unknown or unsafe values where accidental acceptance would be risky.
- Length, format, ranges, enums, and cross-field invariants MUST be validated server-side.
- Sensitive fields MUST be explicitly modeled; generic unbounded JSON MUST NOT become a bypass around data governance.
- Coordinate order, units, time zones, encodings, and locale behavior MUST be documented.
- Client-supplied actor, authority, publication, or audit fields MUST NOT be trusted when the server can derive them.

## 6. Responses and projections

- Responses MUST use explicit projections by audience and purpose.
- Public responses MUST be allowlisted safe views, not internal records with a few fields removed.
- Restricted fields MUST not appear as `null` placeholders if their existence itself is sensitive.
- Timestamps use ISO 8601 with timezone.
- Enumerations and lifecycle states MUST be documented.
- Large binary evidence SHOULD be delivered through authorized, short-lived retrieval mechanisms or controlled streaming, not embedded in routine JSON responses.

## 7. Errors

Errors MUST provide:

- appropriate HTTP status;
- stable machine-readable error code;
- safe human-readable message;
- request/correlation identifier;
- field details for validation failures where safe.

Errors MUST NOT expose stack traces, SQL, object keys, tokens, credentials, internal hostnames, or unnecessary personal data. Authorization failures SHOULD avoid revealing whether an inaccessible restricted object exists.

## 8. Pagination, filtering, and sorting

- Collection endpoints MUST have bounded pagination.
- Maximum page sizes MUST be enforced server-side.
- Filters and sort keys MUST be allowlisted and documented.
- Counts that are expensive or disclose restricted totals require explicit policy.
- Cursor pagination SHOULD be used where mutable national-scale datasets make page-number consistency inadequate.
- Authorization scope MUST be applied before pagination and aggregation.

## 9. Idempotency, concurrency, and replay

- Retriable creation, import, publication, partner, and field-sync operations MUST support idempotency or safe duplicate detection.
- Idempotency keys require actor/client scope, expiry, request hash, and replay semantics.
- Updates to high-value records SHOULD use version/precondition controls to prevent lost updates.
- Duplicate submissions MUST produce a deterministic response rather than silently creating parallel official state.

## 10. Authentication and authorization

- Public, operator, administrative, and partner authentication mechanisms MUST be explicit.
- Authorization follows the identity standard and MUST be enforced on every operation and sensitive field projection.
- Partner clients use machine identities and scopes, not shared user credentials.
- Step-up authentication or dual approval is required for designated high-impact actions.
- Sensitive reads and exports may require purpose and case context.

## 11. Rate, quota, and resource controls

- Public and partner APIs require distributed controls compatible with multiple instances.
- Limits SHOULD cover requests, concurrent work, payload size, export volume, geospatial complexity, and storage use.
- Partner quotas MUST be attributable by client and institution.
- Timeouts and cancellation MUST prevent abandoned requests from consuming unbounded resources.
- Rate-limit responses MUST state safe retry behavior without disclosing defensive internals.

## 12. Partner integration

A partner contract MUST define:

- institution and accountable owner;
- approved purpose and data classes;
- environments and base URLs;
- identity and credential mechanism;
- endpoint and territorial/data scopes;
- rate/volume limits;
- schema/version and change process;
- retention, onward disclosure, and incident duties;
- support and service expectations;
- audit, suspension, revocation, and offboarding.

Direct database access is prohibited for ordinary partners.

## 13. Events and webhooks

- Durable business events MUST originate from committed authoritative state using an outbox or equivalent reliable pattern.
- Redis or in-memory queues MUST NOT be the sole record of an official event.
- Events require stable type, version, event ID, aggregate ID, occurred time, producer, classification, and trace/correlation context.
- Consumers MUST be able to handle duplicate delivery.
- Webhooks require signing, replay protection, delivery history, retry/backoff, suspension, and secret rotation.

## 14. Bulk exchange

- Imports are staged and validated before commit.
- Exports require purpose, selection, classification, authorization, schema version, hash, and expiry/retention where applicable.
- Large jobs SHOULD be asynchronous with status and cancellation controls.
- Download links MUST be short-lived and scoped.
- CSV/spreadsheet outputs require formula-injection defenses and identifier-preservation tests.

## 15. Observability

Every request MUST support a correlation/request ID. Protected and partner requests SHOULD record:

- subject/client and institution;
- effective permission/scope;
- route and result;
- duration and response class;
- rate/quota result;
- target or batch identifier where appropriate;
- audit event for sensitive business actions.

Logs MUST follow data-minimization and security standards.

## 16. Required evidence

An API-changing pull request MUST include:

- OpenAPI diff;
- generated client/type diff;
- compatibility classification;
- allow/deny authorization tests;
- validation, error, pagination, idempotency, and concurrency tests as applicable;
- public/restricted projection tests;
- rate/size/timeout effects;
- audit/observability evidence;
- partner transition notes where applicable;
- screenshots for changed user workflows.
