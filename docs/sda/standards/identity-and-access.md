# SDA Standard — Identity and Access

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** human users, institutions, service identities, sessions, authorization, and privileged access

## 1. Core model

Access decisions MUST evaluate more than a global role. The target policy input is:

```text
subject + institution + role + permission + scope
+ record state + purpose + approval context + environment
```

A user may have multiple institutional assignments, but each assignment MUST be explicit, scoped, effective-dated, and auditable.

## 2. Identity sources

- Government identity federation SHOULD use a standards-based provider through OIDC or SAML when an approved government capability is available.
- Local continuity accounts MAY exist for approved operational resilience, but MUST be separately governed, strongly authenticated, and regularly reviewed.
- Shared human accounts are prohibited.
- A person's identity MUST be distinct from their employment, institution, role, and territorial assignments.
- Identity proofing level and source MUST be recorded for privileged accounts.

## 3. Authentication

- Privileged, administrative, publication-capable, audit, and security accounts MUST use MFA.
- Passwords, where used, MUST be processed with a maintained password-security library using a modern adaptive algorithm and per-user salts.
- Fixed application-wide password salts and reversible password storage are prohibited.
- Default credentials MUST NOT be valid in controlled pilot, agency, or production environments.
- Login, failure, lockout, MFA, recovery, and credential-change events MUST be audited without logging secret material.
- Brute-force and credential-stuffing controls MUST be distributed across application instances and designed to avoid easy denial of service against a named user.

## 4. Sessions and tokens

- Human browser sessions SHOULD use Secure, HttpOnly, SameSite cookies with CSRF protection.
- Session and refresh token values MUST NOT be stored in retrievable plaintext; store one-way hashes or equivalent non-replayable references.
- Sessions MUST have absolute expiry, inactivity policy, revocation, device/client context where lawful, and last-use visibility.
- Role, scope, password, MFA, suspension, or institutional-membership changes MUST revoke or re-evaluate affected sessions.
- Sensitive actions MAY require recent authentication or step-up MFA.
- Tokens MUST never appear in URLs, logs, audit details, screenshots, or error responses.

## 5. Authorization

- Authorization MUST be enforced server-side for every protected operation and sensitive read.
- UI visibility is usability only; it is not an access control.
- Deny is the default.
- Permissions MUST use stable keys such as `addresses.publish`, not page names or ad hoc role checks.
- Policies MUST consider territorial/data scope and the state of the target record.
- Collection and item queries MUST enforce scope in the data access path; filtering unauthorized rows after retrieval is insufficient.
- Sensitive exports and evidence reads MUST record purpose and approval where required.

## 6. Initial national role families

The following are target responsibility families, not automatic permissions:

- platform super administrator;
- national registry administrator;
- ministry reviewer;
- municipal validator;
- field supervisor;
- enumerator;
- helpdesk/corrections agent;
- agency read-only user;
- API client identity;
- auditor/compliance user;
- security operator;
- platform operator.

Technical operations, registry approval, publication, and audit duties MUST be separable. A platform administrator MUST NOT automatically receive authority to publish official addresses.

## 7. Scope model

Supported scope levels SHOULD include:

- national;
- institution;
- province;
- district;
- municipality;
- zone or campaign;
- assignment;
- dataset or data product;
- individual case/record where exceptional access is required.

Scopes MUST be stable references, not free-text labels. Parent scope does not automatically grant every child action unless policy explicitly defines inheritance.

## 8. Segregation of duties

High-impact actions MUST support dual control or independent approval, including as defined by policy:

- official publication;
- national boundary or code changes;
- mass correction, retirement, or deletion;
- bulk exports of sensitive or full-registry data;
- privileged role assignment;
- service-account creation and credential issuance;
- emergency override;
- changes to retention, audit, or security controls.

The actor who captures a record SHOULD NOT be the sole actor who validates and publishes it.

## 9. Delegated administration

- Delegated administrators may act only inside their institution and approved scope.
- They MUST NOT create permissions, expand their own authority, or assign a role beyond their delegation.
- Privileged assignment changes require reason, effective dates, approving actor, and audit event.
- Access reviews MUST be supported by institution, role, permission, scope, inactivity, and privilege level.

## 10. Service identities and API clients

- Machines use dedicated service identities, never human credentials.
- Each client MUST have an owner institution, approved purpose, endpoint/data scopes, environment, expiry, status, and contact.
- Credentials MUST be generated securely, displayed once where applicable, stored only as hashes, rotated, revocable, and never committed.
- Mutual TLS, signed client assertions, or equivalent higher-assurance controls SHOULD be considered for high-trust government integrations.
- All client calls MUST be attributable, rate-limited, monitored, and auditable.
- Production and non-production credentials MUST be separate.

## 11. Privileged and emergency access

- Privileged access MUST be time-bound where feasible and use separate administrative context.
- Break-glass access requires a named incident, strong authentication, reason, approval where possible, full audit, and post-use review.
- Emergency accounts MUST be protected and tested without routine use.
- Database or object-storage administrator access MUST NOT be used as an ordinary application workflow.

## 12. Lifecycle

The platform MUST support:

- invite/provision;
- identity verification;
- institution and scope assignment;
- activation;
- privilege elevation and expiry;
- suspension;
- transfer between institutions/scopes;
- termination/deprovisioning;
- credential and session revocation;
- periodic recertification.

Orphaned accounts and assignments are prohibited.

## 13. Audit and privacy

- Authentication and authorization events MUST be auditable while minimizing unnecessary personal data.
- Audit records MUST include subject, institution, effective role/permission/scope, action, target, result, reason where required, time, and request/correlation ID.
- Sensitive access, evidence viewing, full-record viewing, exports, role changes, and failed policy decisions require enhanced logging.
- Audit interfaces MUST not reveal password hashes, tokens, recovery secrets, or unnecessary identity-document data.

## 14. Required evidence

Identity or authorization changes require:

- updated role/permission/scope matrix;
- server-side policy tests for allow and deny cases;
- cross-scope isolation tests;
- session revocation tests;
- privileged-action and dual-control tests where applicable;
- audit-event evidence;
- migration and compatibility plan;
- affected UI screenshots by role;
- threat analysis and residual risks;
- confirmation that no route relies solely on client-side hiding.
