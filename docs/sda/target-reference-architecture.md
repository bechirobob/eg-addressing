# NLI Target Reference Architecture

**Version:** 0.1  
**Status:** Direction approved; implementation incremental  
**Scope:** National Location Infrastructure and the addressing service  
**Current production status:** Not approved

## 1. Architectural objective

The NLI will provide a trusted, reusable national foundation for creating, validating, governing, publishing, and exchanging location records. The addressing service is the first bounded service built on that foundation.

The architecture must support national scale without requiring premature distributed complexity. It must preserve legal and institutional authority, evidence, auditability, spatial integrity, bilingual access, controlled agency integration, and recoverable operations.

## 2. Governing principles

1. **Authority before publication.** Technical capability does not grant institutional authority.
2. **One authoritative record, many authorized uses.** Services consume governed location identifiers and records rather than building isolated address copies.
3. **Evidence is not automatically truth.** Citizen, field, map, and imported observations remain attributable evidence until validated into canonical records.
4. **Modular monolith first.** Clear domains and interfaces come before independent deployment units.
5. **PostgreSQL/PostGIS as system of record.** Transactional and authoritative spatial state remains in one governed platform until an ADR approves otherwise.
6. **Explicit lifecycle.** Records move through controlled, auditable states; status strings are not invented ad hoc.
7. **Scoped authority.** Access depends on institution, role, permission, territory, record state, and purpose.
8. **Secure and private by design.** Sensitive identity, location, evidence, and access data are minimized and protected.
9. **Interoperability by contract.** APIs and exports are versioned, documented, bounded, and observable.
10. **Operational evidence.** Readiness claims require tests, monitoring, restore evidence, and named ownership.
11. **Offline and constrained-network awareness.** Field and regional operations must tolerate intermittent connectivity without corrupting authority.
12. **Evolution without erasure.** Records are versioned, superseded, retired, or corrected; official history is not silently overwritten.

## 3. Logical domain model

The initial modular monolith will separate these bounded domains in code, database ownership conventions, API modules, tests, and documentation.

### 3.1 Identity and Trust

Responsibilities:

- human identities and institutional memberships;
- government federation and local continuity accounts where approved;
- roles, permissions, territorial scopes, and delegated administration;
- MFA, session management, service accounts, and credential lifecycle;
- privileged-access and break-glass controls.

This domain decides who or what is acting. It does not decide whether a location record is substantively correct.

### 3.2 Administrative Geography

Responsibilities:

- country, province, district, municipality, zone, and other approved administrative units;
- authoritative names, codes, hierarchy, validity dates, and boundary versions;
- mapping between institutional authority and territorial scope;
- disputed or pending boundary state.

Administrative geography is reference authority, not a free-form tagging system.

### 3.3 Location Registry

Responsibilities:

- roads and other named access networks;
- parcels where legally and operationally authorized;
- buildings, entrances, units, landmarks, and addressable objects;
- canonical addresses and national location identifiers;
- record versions, status events, supersession, correction, retirement, and publication state;
- public and restricted record projections.

This domain is the authoritative transactional core.

### 3.4 Field Operations

Responsibilities:

- assignments, areas, teams, devices, and enumerator scope;
- offline-capable capture packages and synchronization;
- field submissions, recapture, supervisor review, and productivity evidence;
- location quality, GPS accuracy, and capture provenance.

Field submissions are evidence and candidates until accepted through registry governance.

### 3.5 Evidence and Verification

Responsibilities:

- evidence metadata, hashes, classifications, storage references, and custody;
- photos, documents, coordinates, map suggestions, and verification events;
- duplicate detection, quality signals, discrepancy resolution, and legal hold;
- evidence access and disclosure logging.

Binary objects live in governed object storage. Their authoritative metadata and lifecycle remain in PostgreSQL.

### 3.6 Publication and Corrections

Responsibilities:

- approval workflows and segregation of duties;
- publication batches, certificates, proofs, signage, and public projections;
- correction requests, disputes, appeals, supersession, and retirement;
- release authority, effective dates, revocation, and publication audit.

`Registry-ready` and `published` remain distinct states.

### 3.7 Agency Integration

Responsibilities:

- registered partner institutions and approved use cases;
- machine identities, scopes, rate limits, quotas, and credential rotation;
- versioned APIs, event subscriptions, batch exchange, and reconciliation;
- partner audit, data minimization, and service-level reporting.

No partner receives unrestricted database access.

### 3.8 Audit, Reporting, and Analytics

Responsibilities:

- append-only security and business events;
- operational reports, SLA measures, data-quality measures, and accountability views;
- governed analytical extracts and de-identified or aggregated data products;
- export authorization, lineage, and usage evidence.

The analytical plane must not become an ungoverned second registry.

## 4. Application structure

The initial target remains a modular monolith with deployable supporting processes:

```text
portal/public          public lookup, submission, tracking, and corrections
portal/operator        protected registry, field, verification, and administration
api                    domain-oriented FastAPI application
worker                 asynchronous exports, notifications, reconciliation, and long jobs
postgres/postgis       authoritative transactional and spatial state
redis                  reconstructable cache, queue, locks, and rate-limit coordination
object-storage         classified evidence and generated controlled artefacts
```

Inside the API, each domain should own:

- routes and contracts;
- application services/use cases;
- domain rules and state transitions;
- persistence adapters and queries;
- authorization policies;
- audit events;
- tests and documentation.

Cross-domain behavior uses explicit application interfaces. Direct table access across domains should be minimized and documented.

Microservices may be considered only when a measured scaling, isolation, ownership, or regulatory need justifies the operational cost and an ADR records the transition.

## 5. Trust zones

### Public access zone

Contains public web entry points, public APIs, bot/rate controls, and minimal public projections. It must not expose operator APIs, object-storage credentials, internal identifiers unnecessarily, or sensitive evidence.

### Government operator zone

Contains authenticated staff workflows. Access is institutionally and territorially scoped. High-impact actions require step-up authentication and approval where defined.

### Partner integration zone

Contains API gateway functions, machine identity, contract enforcement, quotas, partner-specific scopes, and exchange monitoring. Partner traffic is separable from public and operator traffic.

### Data zone

Contains PostgreSQL/PostGIS, object storage, Redis, backup services, and key-management integration. Network access is restricted to authorized application and operations paths.

### Operations and security zone

Contains deployment control, monitoring, audit/SIEM integration, secrets management, backup control, and break-glass procedures. Operational administrators do not automatically receive registry-publication authority.

## 6. Deployment reference

Production deployment must provide:

- redundant application instances behind TLS ingress;
- pinned, scanned, immutable container images;
- managed or highly available PostgreSQL/PostGIS with point-in-time recovery;
- resilient S3-compatible storage with encryption, versioning, retention controls, and recovery evidence;
- Redis configured only for non-authoritative workloads with failure-tolerant application behavior;
- centralized secrets and key management;
- separated development, test, staging, controlled pilot, and production environments;
- centralized logs, metrics, traces, alerting, and audit forwarding;
- infrastructure defined through controlled, reviewable configuration;
- documented capacity, scaling, backup, failover, and maintenance procedures.

A single-host Compose stack remains a development/pilot convenience and is not the production reference.

## 7. Data architecture

### Authoritative records

PostgreSQL/PostGIS holds:

- canonical identifiers;
- administrative hierarchy and geometry versions;
- registry entities and lifecycle state;
- identity authorization metadata;
- evidence metadata and hashes;
- approval, publication, correction, and audit events;
- partner contracts and machine-identity metadata.

### Evidence objects

Object storage holds binary evidence and generated controlled artefacts. Every object must have a database record containing at minimum:

- stable evidence ID;
- object key and version;
- content hash and size;
- media type;
- source and capture time;
- uploader/actor and institutional scope;
- classification;
- related case or record;
- retention and legal-hold state;
- access history or auditable access events.

### Cache and queue data

Redis data must be reconstructable. Loss of Redis may delay work but must not create false official state or erase the authoritative workflow history.

### Analytics

Analytical stores or BI tools may be introduced later through governed, reproducible extracts. They receive purpose-limited data and lineage metadata; they do not directly mutate the registry.

## 8. Identity and authorization architecture

Authorization evaluates:

```text
subject + institution + role + permission + territorial/data scope
+ record state + purpose + approval context + environment
```

The model supports:

- national, province, district, municipality, zone, assignment, and dataset scopes;
- multiple institutional memberships per person where authorized;
- least privilege and time-bound elevated access;
- segregation of capture, validation, approval, publication, audit, and platform operations;
- machine identities with endpoint/data scopes, expiry, rotation, and revocation;
- mandatory MFA for privileged and publication-capable accounts;
- auditable emergency access.

## 9. Spatial architecture

The NLI distinguishes:

- authoritative administrative geometries;
- authoritative registry geometries;
- observed field geometries;
- citizen-submitted geometries;
- map-derived suggestions;
- generalized public geometries.

Each geometry carries provenance, method, source authority, capture time, accuracy/quality, CRS, validation state, and version. Geometry promotion is an explicit workflow.

WGS84 (`EPSG:4326`) is the exchange baseline. Appropriate projected CRS choices for measurement and national operations must be formally documented before metric-area or distance authority is claimed.

## 10. Integration architecture

- External contracts are exposed through versioned APIs or controlled batch exchange.
- OpenAPI is authoritative for HTTP contracts.
- API clients use machine credentials, not shared human accounts.
- Idempotency is required for retriable writes.
- Partner-specific scopes, quotas, rate limits, and audit are mandatory.
- Changes follow deprecation and transition policy.
- Bulk exports require approval, classification, purpose, expiry, and an audit record.
- Future events/webhooks use an outbox or equivalent durable pattern; Redis alone is not the event record.

## 11. Availability and continuity

Availability targets will be set by service tier. Until formally approved, implementations must avoid claiming an SLA.

The architecture must support:

- graceful degradation when geocoding, map, notification, Redis, or partner services fail;
- queued retry for non-interactive work;
- no silent loss of accepted submissions;
- idempotent synchronization from field clients;
- database and object-storage recovery;
- tested environment reconstruction;
- planned island/mainland and constrained-connectivity operations.

## 12. Transition sequence

The controlled transition is:

1. remove schema and fixture mutation from API startup;
2. establish migration-only database authority;
3. converge the canonical NLI data model;
4. implement institutional and territorial authorization;
5. strengthen audit, evidence, and publication governance;
6. establish production deployment and security controls;
7. formalize GIS geometry and address-code standards;
8. introduce governed partner integration;
9. establish national operations, DR, and analytical controls.

Each transition is delivered by a separate work order and acceptance record. Broad rewrites that skip the controlled sequence are not authorized.
