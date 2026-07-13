# SDA Standard — Testing and Release

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** application, database, infrastructure, documentation, generated artefacts, and environment promotion

## 1. Principle

A change is not complete because code exists or a happy path works. Acceptance requires evidence proportional to the risk of the affected authority, data, workflow, and operations.

Tests MUST validate both permitted behavior and prohibited behavior. A passing CI run is necessary but not sufficient for national-production readiness.

## 2. Change classes

### Class A — National authority or trust

Includes identity, privileged access, official geometry, address/location identifiers, publication, bulk export, destructive operations, audit integrity, retention, and sensitive-data exposure.

Requires:

- explicit work order and SDA review;
- threat model and misuse cases;
- independent allow/deny and segregation-of-duty tests;
- migration/recovery evidence where data changes;
- workflow evidence by affected role;
- security and operational review;
- explicit acceptance record.

### Class B — Core platform

Includes schema, APIs, field workflows, evidence handling, integrations, deployment, availability, and substantial refactoring.

Requires work-order or approved-scope traceability, automated tests, compatibility analysis, operational evidence, and SDA review.

### Class C — Controlled maintenance

Includes compatible defect fixes, copy/localization corrections, and low-risk refactoring. Requires normal tests, review, and truthful impact statement. A change becomes Class A or B when its real effects cross those boundaries.

## 3. Test layers

Use the smallest useful test plus the higher-level evidence needed for confidence:

- static/type/schema checks;
- unit tests for domain rules;
- policy tests for authorization;
- database integration tests with real PostgreSQL/PostGIS;
- API contract and compatibility tests;
- component and workflow tests;
- end-to-end role-based tests;
- migration, backup, restore, and failure tests;
- performance, load, and capacity tests;
- security and abuse tests;
- accessibility, localization, and visual/workflow evidence;
- operational smoke and readiness tests.

Mocks MUST NOT replace real database, object storage, or identity-boundary tests where behavior depends on those systems.

## 4. Required core CI

Every pull request MUST run, as applicable:

- formatting/linting and type checks;
- backend tests;
- frontend build and tests;
- generated OpenAPI/client-type drift check;
- migration rehearsal against an empty PostgreSQL/PostGIS database;
- upgrade rehearsal from the previous supported schema for database changes;
- secret scanning;
- dependency review and vulnerability scanning;
- static application security analysis;
- container/image build and scan for deployable changes;
- documentation/link and controlled-record checks;
- repository-specific role, route, accessibility, localization, geometry, and design-system guards.

Required controls MUST NOT be deleted, weakened, skipped, or converted to warnings merely to obtain a green build.

## 5. Test data

- Tests MUST use isolated, deterministic, clearly non-official data.
- Production personal or evidentiary data is prohibited unless explicitly approved and de-identified for a controlled purpose.
- Test identifiers MUST not collide with production namespaces.
- Fixtures MUST include negative, boundary, duplicate, invalid-state, cross-scope, and recovery cases.
- Test cleanup MUST be reliable; cleanup failure is a test failure.

## 6. Database and migration testing

A schema-changing release MUST prove:

- complete creation from an empty database solely through migrations;
- successful upgrade from each supported source version;
- expected constraints and indexes;
- preserved identifiers and relationships;
- validated backfill counts and exception handling;
- acceptable lock/duration behavior at representative scale;
- application compatibility during the intended deployment sequence;
- recovery or forward-fix procedure;
- backup and restore compatibility.

Application startup mutation is a release failure.

## 7. Authorization and authority testing

For every protected action, test:

- unauthenticated denial;
- authenticated but unpermitted denial;
- wrong institution denial;
- wrong territory/data scope denial;
- invalid record-state denial;
- expired/revoked session or credential denial;
- permitted success;
- audit event and safe response behavior.

Class A workflows additionally require dual-control, self-approval prevention, and privilege-escalation tests where applicable.

## 8. API compatibility

- OpenAPI changes MUST be reviewed as part of the pull request.
- Generated types MUST match the committed contract.
- Backwards-compatible and breaking changes MUST be labeled.
- Partner-impacting changes require transition evidence and consumer tests where practical.
- Error, pagination, idempotency, retry, rate-limit, and timeout behavior MUST be tested when affected.

## 9. Workflow and UI evidence

Changed workflows MUST provide screenshots or equivalent browser evidence labeled with:

- route/workflow;
- role and scope;
- language;
- viewport/device class;
- environment;
- commit;
- date;
- data classification (fixtures only unless approved).

Critical paths must demonstrate keyboard access, focus, validation, error, loading, empty, denied, and completion states as applicable.

## 10. Performance and resilience

Performance-sensitive work MUST state targets before testing. Evidence may include:

- database query plans;
- API latency and throughput;
- concurrent users/clients;
- import/export duration;
- spatial query or tile load;
- object upload/download behavior;
- worker backlog and retry behavior;
- failure and recovery timing.

Do not claim national scale from small local fixtures.

## 11. Release artefacts and provenance

Controlled releases MUST use:

- reproducible builds from reviewed commits;
- pinned dependencies and base images;
- immutable versioned artefacts;
- SBOM for production artefacts;
- vulnerability disposition;
- build provenance and, for production, signed/verifiable artefacts;
- release notes mapping work orders, migrations, contracts, risks, and operator actions.

Production systems MUST deploy built artefacts, not mutable source mounts or `latest` images.

## 12. Environment promotion

Promote the same accepted artefact through:

```text
development → test → staging → controlled pilot → production
```

Promotion requires environment-specific configuration and secrets, not rebuilding different code.

Each promotion gate MUST check:

- configuration and secret readiness;
- migration status;
- dependency/service health;
- smoke and policy tests;
- monitoring and alerting;
- backup and recovery prerequisites;
- deployment label and publication locks;
- approved change window and operator ownership.

## 13. Rollback and forward recovery

Every release MUST state whether rollback is safe. When database or external effects make rollback unsafe, provide a tested forward-recovery plan.

Rollback/forward recovery MUST address:

- schema and data compatibility;
- queued jobs and idempotency;
- published artefacts and partner messages;
- object/evidence versions;
- caches and generated projections;
- credentials and configuration;
- audit continuity.

## 14. Release decision record

Release evidence MUST identify:

- work orders and accepted commits;
- environment and artefact versions;
- migrations;
- tests and known exceptions;
- security scan/SBOM status;
- backup/restore readiness;
- operator and approver;
- deployment, validation, and recovery steps;
- residual risks and conditions.

SDA acceptance of a work order does not itself authorize production deployment or official publication.

## 15. Required pull-request evidence

Use `docs/sda/templates/pull-request-evidence.md`. Missing evidence must be marked `NOT PROVIDED` with a reason; sections are not silently deleted.
