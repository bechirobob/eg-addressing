# S08 — API, Identity, Security, and Privacy

## Invoke when

- adding or changing an API operation or field;
- changing authentication, sessions, roles, permissions, scopes, or service clients;
- exposing public, operator, partner, or administrative data;
- handling identity, contact, precise location, evidence, or other sensitive information;
- changing rate limits, error behavior, exports, or machine integration.

## Required inputs

- actual OpenAPI document;
- independently reviewed route-policy registry;
- identity-and-access, API, security, and audit standards;
- data classification and projection rules;
- current handlers, dependencies, domain policies, and database queries.

## Procedure

### 1. Identify the API class

Classify every operation:

- public;
- operator;
- administrative;
- partner/machine;
- operational.

State the approved purpose and data projection.

### 2. Model authorization precisely

For each operation record:

```text
HTTP method
path
operation ID
exact handler
source span
authentication mode
all allowed roles
institution membership
territorial/data scope
record-state policy
purpose/approval context
step-up or dual-control requirement
```

Observed implementation and expected policy must be independent.

### 3. Build field-level contracts

For every request, success response, and error field define:

- type and requiredness;
- semantic meaning;
- classification;
- exact target field/projection;
- release prerequisite;
- redaction/generalization;
- compatibility impact;
- adapter and deprecation rule;
- test.

Dynamic dictionary responses must receive explicit schemas or executable contract fixtures. Do not label them as empty envelopes.

### 4. Enforce authorization at the data path

- apply scope before query pagination/counting;
- verify object-level authorization;
- prevent existence disclosure where required;
- audit sensitive reads, exports, role changes, evidence access, and denials;
- keep UI hiding separate from server authorization.

### 5. Protect credentials and sessions

- modern password hashing and per-user salts;
- hashed/revocable sessions or refresh tokens;
- secure cookies and CSRF controls where used;
- absolute/inactivity expiry;
- MFA/step-up for privileged actions when required;
- no secrets or tokens in URLs, logs, screenshots, or evidence.

### 6. Design abuse and privacy controls

- distributed rate/abuse controls for multi-instance systems;
- bounded payloads, timeouts, exports, and geospatial work;
- explicit public allowlisted projections;
- data minimization and purpose limitation;
- production data prohibited from ordinary lower environments;
- idempotency/replay protection for retriable writes.

### 7. Validate allow and deny behavior

Test:

- anonymous access;
- authenticated but unpermitted access;
- wrong role;
- wrong institution;
- wrong territorial/data scope;
- invalid record state;
- expired/revoked session;
- allowed success;
- audit and safe error projection.

## Outputs

- method/path/operation authorization matrix;
- reviewed field-level API projection contracts;
- allow/deny test suite;
- privacy/security impact;
- OpenAPI and generated-client updates;
- audit-event evidence.

## Stop or RFI conditions

Stop when:

- a new role, permission, scope, data class, partner purpose, public field, or bulk export lacks authority;
- authorization is inferred from a route name or UI visibility;
- the successful response shape cannot be enumerated;
- classification is assigned only from field-name keywords;
- expected route policy is generated from the observed parser;
- shared human credentials or plaintext/replayable tokens are proposed.

## Evidence gate

Before review:

- every operation is keyed by method, path, operation, and handler;
- all roles are captured;
- expected policy is independently reviewed;
- every field has explicit classification and target projection;
- allow/deny cases execute;
- generated clients match OpenAPI;
- audit and error behavior are verified.

## Anti-patterns

- Storing expected policies by path only.
- Capturing only the first `_require_role` argument.
- Calling logout public because it does not invoke the standard current-user helper.
- Deferring target projections to a future unspecified adapter.
- Treating HTTP 200 as proof that the correct fields were returned.
- Using generic “government-internal” for every unknown field.
