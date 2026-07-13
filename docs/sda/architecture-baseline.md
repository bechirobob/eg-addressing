# NLI Current-State Architecture Baseline

**Baseline version:** 0.1  
**Repository:** `bechirobob/eg-addressing`  
**Baseline commit:** `c22c0d43670d4300f7fce65bdcebba307a0fc270`  
**Assessment boundary:** source repository and documented pilot runtime  
**Readiness statement:** controlled pilot; not approved for national production

## 1. Purpose

This document records the architecture as it exists at the baseline commit. It is descriptive, not an endorsement of every implementation choice. Target decisions are defined separately in the reference architecture, standards, ADRs, and work orders.

## 2. Strategic framing

The existing product is a national digital addressing platform. The target programme framing is the Equatorial Guinea National Location Infrastructure (NLI), with addressing as its first service.

The intended foundation may later support property and land administration, utilities, emergency dispatch, census and statistics, postal modernization, taxation, health and education mapping, and other authorized location-dependent public services. Those future uses do not authorize premature collection, exposure, or coupling of their data today.

## 3. Repository and component shape

The repository is organized as a modular-monolith workspace:

```text
apps/admin-portal   Next.js public, operator, and administrative portal
apps/field-app      planned/mobile field application workspace
services/api        FastAPI HTTP application and persistence logic
services/worker     planned background-work workspace
packages/types      shared/generated contracts workspace
packages/ui         shared UI workspace
packages/config     shared configuration workspace
infra/docker        local Docker Compose runtime
infra/migrations    numbered SQL migration files
infra/scripts       backup, restore, audit, and operator scripts
docs                programme, proposal, training, and formal records
artifacts           generated proof and output bundles
```

Most implemented behavior currently resides in the Next.js portal and a single FastAPI application. The field application and worker are not yet independent mature services.

## 4. Runtime topology

The documented local runtime contains:

- Next.js portal;
- FastAPI API;
- PostgreSQL 16 with PostGIS;
- Redis;
- MinIO/S3-compatible storage.

Docker Compose runs these components on one host with local filesystem-backed volumes and loopback port bindings. This is suitable for isolated development and controlled pilot operation, not a national high-availability topology.

No separate API gateway, identity provider, service mesh, analytics platform, map-tile platform, centralized secrets service, or independent notification service is confirmed in the baseline.

## 5. Logical domains represented

The baseline contains functionality for:

- public address lookup and proof;
- citizen location/geotag submission and tracking;
- correction requests;
- staff authentication and administration;
- provinces, administrative units, and territories;
- roads, buildings, and addresses;
- field assignments, submissions, evidence, and review;
- verification, duplicate handling, and registry-ready workflows;
- canonical address records and event history;
- imports, publication packs, certificates, signage exports, and reports;
- audit logs, migration status, restore-drill status, and production-readiness summaries.

The module coverage is substantial for a pilot, but domain boundaries are not consistently separated in code or data ownership.

## 6. Data and persistence baseline

### Operational schema authority

The application currently creates and alters much of its schema through startup code in `services/api/app/db.py`. Numbered SQL migrations exist, but the first migration is a baseline marker acknowledging that the initial schema was application-created.

A separate proposal schema under `docs/source-proposals/schema.sql` describes a richer target-like model with UUIDs, explicit geographic hierarchy, scoped role assignments, geometry, versions, agency clients, and richer audit records. It is not the operational schema.

The result is three competing sources of schema intent:

1. application bootstrap DDL;
2. numbered operational migrations;
3. the proposal schema.

This is a production blocker until one controlled migration history becomes authoritative.

### Main operational entities

The observed operational model includes:

- `provinces` and hierarchical `admin_units`;
- `territories` used for routing and rollout areas;
- `roads`, `buildings`, and `addresses`;
- `address_points`;
- `citizen_geotag_submissions`;
- canonical `address_records` and `address_record_events`;
- `field_assignments` and `field_submissions`;
- evidence metadata and object references;
- `address_corrections`;
- import jobs and rows;
- publication packs and their address membership;
- users, auth tokens, and audit logs.

Identifiers and status fields are primarily text values. Several status vocabularies are enforced in API models or workflow code rather than database constraints.

### Spatial baseline

PostGIS is present. Canonical address records can hold WGS84 point geography and have a GiST index. Raw citizen coordinates are deliberately retained as evidence rather than automatically treated as official geometry.

Official administrative boundaries, road centerlines, building footprints, entrances, parcels, geometry versioning, accuracy classes, and topology governance are not yet complete.

### Reference and fixture data

Application startup upserts provinces, administrative routing units, demonstration users, territories, roads, buildings, addresses, assignments, imports, and publication examples from Python source data.

Although environment flags can reject default passwords and fixtures can be cleaned up, normal application startup remains coupled to data mutation.

## 7. Identity and authorization baseline

The active pilot role model contains:

- `admin`;
- `editor`;
- `viewer`;
- `agency_viewer`.

Protected API routes perform server-side role checks. This is an important positive control.

Current limitations include:

- global roles rather than institutional or territorial scope;
- no implemented organization membership model;
- no explicit permission-key model;
- no mature service-account/API-client lifecycle in the operational schema;
- no confirmed MFA or government identity federation;
- fixed demonstration credentials in source;
- a fixed application-wide password salt;
- directly stored session-token values.

A legacy role-permission matrix provides useful target input but is not the enforced model.

## 8. Public, protected, and authority boundaries

### Public zone

Public routes support territory options, submission, tracking, lookup, correction reporting, and proof/verification functions. Public rate limiting is implemented in process memory.

### Protected operator zone

Authenticated staff routes support registry, field, verification, reporting, staff management, imports, exports, publication preparation, and operator status.

### Authority boundary

The implementation distinguishes internal `registry-ready` status from public publication and signage. Publication release is feature-gated and operational text warns that institutional authority is still external. This separation must be preserved and strengthened.

### External dependencies

The baseline uses OpenStreetMap Nominatim for reverse-geocoding suggestions. Suggestions are marked as requiring review. Production licensing, availability, caching, privacy, service limits, and offline continuity remain governance concerns.

## 9. API baseline

The FastAPI application exposes more than one hundred routes across public, operator, registry, field, verification, reporting, publication, and operations functions.

Positive characteristics:

- OpenAPI generation;
- generated frontend API types;
- server-side authorization checks;
- pagination helpers for several collections;
- public-safe response shaping and sensitive-detail sanitization;
- request IDs and basic security headers.

Constraints:

- large application module with many domain responsibilities;
- no confirmed partner API gateway or mature machine identity model;
- public rate limiting is per-process and non-distributed;
- no formal API deprecation or compatibility policy yet;
- inconsistent distinction between internal record identifiers and public codes remains possible.

## 10. User-experience baseline

The portal includes public and protected routes for login, geotagging, tracking, verification, registry, records, field work, territories, reports, exports, signage, operations, and staff administration.

The repository has extensive guards for copy, role visibility, route ownership, accessibility controls, desktop workflows, API types, official geometry, design-system consistency, and public proof behavior.

A fresh, centralized workflow screenshot pack by role, viewport, route, commit, and date is still missing.

## 11. Security and evidentiary baseline

Positive controls include:

- HttpOnly secure-cookie mode and CSRF protection options;
- security headers;
- server-side role checks;
- upload size/content-type restrictions and blocked extensions;
- object hashes for evidence;
- audit events for many sensitive actions;
- explicit production-readiness checks;
- secrets excluded from committed runtime configuration.

Material gaps include:

- pilot-grade password and session storage;
- no confirmed MFA, federation, privileged-access management, or break-glass controls;
- no confirmed object lock, malware scanning, legal hold, or governed retention;
- no confirmed centralized SIEM, tamper-evident audit storage, or security incident workflow;
- no confirmed SAST, dependency review, container scanning, SBOM, artefact signing, or secret scanning release gates;
- development fallback credentials and unpinned runtime images in local Compose.

## 12. Operations and resilience baseline

The repository contains:

- health and production-readiness endpoints;
- migration-status reporting;
- database backup scripts producing checksummed custom-format dumps;
- a restore drill into a disposable database with row-count comparison;
- operator command-center and restore-drill status surfaces;
- API and frontend GitHub Actions workflows.

Not yet established as national controls:

- approved service-level objectives;
- recovery-time and recovery-point objectives;
- point-in-time recovery;
- geographically separate encrypted backups;
- object-storage recovery exercises;
- infrastructure-as-code production reconstruction;
- high availability and failover;
- centralized metrics, tracing, alerting, and incident command;
- capacity and load targets.

## 13. Baseline strengths to preserve

- modular-monolith direction rather than premature microservices;
- PostgreSQL/PostGIS foundation;
- separation of raw evidence from canonical official geometry;
- server-side authorization checks;
- internal approval separated from official publication;
- deliberate pilot versus production language;
- contract generation between backend and frontend;
- backup and restore-drill discipline;
- restrained interface and workflow-quality controls;
- bilingual training and formal-document work.

## 14. Priority baseline risks

1. Runtime schema and fixture mutation.
2. Pilot-grade identity and global-role authorization.
3. Competing schema authorities.
4. Single-host development topology.
5. Incomplete GIS and evidence governance.
6. Incomplete release supply-chain assurance.
7. Missing national resilience objectives and topology.
8. Large implementation modules with weak bounded-domain separation.

Detailed ownership and treatment are maintained in `risk-register.md`.

## 15. Unknowns requiring future evidence

- actual deployed environments and infrastructure outside the repository;
- current database volumes and growth profile;
- concurrent-user and partner-API expectations;
- national registry and publication authority;
- legal classification, retention, and residency requirements;
- government identity and directory capabilities;
- authoritative administrative boundary and road datasets;
- connectivity conditions for field teams;
- operational staffing and support model;
- current monitoring, backup storage, and incident procedures outside source control.

Unknowns are not assumed safe. They must be resolved through work orders, RFIs, institutional decisions, or evidence collection.
