# Skill 08 — API, Identity, and Authorization

## Use when

Use for API routes/contracts, authentication, sessions, roles, permissions, institutional or territorial scope, service clients, partner APIs, exports, or public/operator projections.

## Objective

Keep API behavior contractually explicit and ensure every protected operation is authorized server-side using the correct identity, institution, role, permission, scope, record state, and purpose.

## Procedure

1. Generate the actual OpenAPI document from the exact implementation head.
2. Inventory every operation by:
   - HTTP method and path;
   - operation ID and exact handler;
   - request/path/query/header/body fields;
   - successful and error response fields;
   - authentication mode;
   - all allowed roles/permissions/scopes;
   - audit and rate-limit behavior.
3. Derive observed policy from exact handler/dependency boundaries, not route-name keywords or fixed source windows.
4. Compare observed policy to an independently reviewed expected-policy registry.
5. Distinguish:
   - public;
   - optional authentication;
   - session-required;
   - authenticated;
   - role/permission-required;
   - service-client;
   - step-up/dual approval.
6. For each field, define classification, target projection, release prerequisite, compatibility impact, adapter, deprecation rule, and test.
7. Define explicit response models for dynamic dictionary responses or maintain controlled response-shape fixtures/tests.
8. Enforce authorization before retrieval, pagination, aggregation, export, evidence access, or mutation.
9. Test unauthenticated, wrong-role, wrong-institution, wrong-scope, wrong-record-state, revoked/expired credential, and permitted cases.
10. Verify session/token storage, revocation, CSRF/cookie behavior, audit, and safe error responses when affected.
11. Regenerate client types and verify contract drift.

## Required evidence

- Exact OpenAPI diff
- Method+path+handler policy matrix
- Independent expected-policy comparison
- Complete allowed role/permission/scope set
- Request/response/error field projection map
- Allow/deny/cross-scope tests
- Session/revocation tests where affected
- Generated client/type result
- Audit and abuse controls

## Stop and escalate when

- A new role, permission, scope, institution, or machine identity is required.
- Public versus protected classification is unclear.
- A partner use case lacks approved purpose/data scope.
- The current global role model cannot express the required authority.
- A dynamic response cannot be documented without changing the API contract.

## Anti-patterns

- Keying policies only by path when methods differ.
- Recording only the first role passed to a role-check function.
- Generating the expected policy from the observed policy in the same run.
- Treating logout/session revocation as public because it does not call the normal user helper.
- Treating UI hiding as authorization.
- Representing a successful dynamic response as an empty envelope.
- Using a generic “adapter will resolve later” target for every response field.
