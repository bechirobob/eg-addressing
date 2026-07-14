# NLI Whole-Project Skill Coverage Matrix

**Purpose:** Prove that the implementation-agent skills system covers the complete National Location Infrastructure programme, not only a current work order or one technical section.

## 1. Repository surface coverage

| Repository area | Responsibility | Primary skills | Supporting skills |
|---|---|---|---|
| `apps/admin-portal` public routes | Citizen lookup, geotag submission, tracking, corrections, public proof | 17, 19 | 08, 09, 10, 11, 12, 23 |
| `apps/admin-portal` protected routes | Registry, verification, field supervision, reports, publication, staff/admin operations | 17, 20, 22, 23, 26 | 08, 09, 11, 12, 29 |
| `apps/field-app` | Enumerator/supervisor mobile capture and offline synchronization | 17, 21 | 07, 09, 10, 11, 12, 18, 25, 28 |
| `services/api` | Domain-oriented FastAPI application, contracts, authorization, persistence | 18 | 07, 08, 09, 10, 12, 16, 20–24 |
| `services/worker` | Exports, notifications, retries, synchronization, reconciliation, long jobs | 25 | 09, 12, 13, 18, 24, 26, 28 |
| `packages/ui` | Shared design system, accessible components, visual consistency | 17 | 11, 12 |
| `packages/types` | Generated/shared API and domain contracts | 08, 18 | 07, 12, 17, 24 |
| `packages/config` | Typed configuration and environment utilities | 27 | 09, 12, 13, 18 |
| `infra/migrations` | Controlled PostgreSQL/PostGIS schema authority | 06 | 07, 10, 12, 13, 18 |
| `infra/scripts` | Migration, backup, restore, bootstrap, evidence, operator automation | 06, 13, 25, 27 | 05, 09, 12, 14 |
| `infra/docker` / future ingress/IaC | Local stack and production platform topology | 27 | 09, 12, 13, 28 |
| `env` | Safe environment templates and configuration contracts | 27 | 09, 12, 13 |
| `docs/sda` | Architecture authority, standards, ADRs, work orders, reviews, risks | 04, 14, 15, 16, 30 | all applicable domain skills |
| `docs` / `artifacts` | Training, architecture, generated reports, exports, evidence bundles | 14, 26, 29 | 09, 11, 12, 23, 25 |
| `data` | Local disposable runtime state; never source authority | 06, 27 | 09, 13 |

## 2. NLI bounded-domain coverage

| NLI bounded domain | Capabilities covered | Primary skills |
|---|---|---|
| Identity and Trust | Human/service identities, memberships, roles, permissions, territorial scope, sessions, MFA/federation planning, delegated and break-glass access | 08, 09, 16, 18, 24, 27 |
| Administrative Geography | Country/province/district/municipality hierarchy, names/codes, boundaries, historical versions, scope mapping | 07, 10, 16, 18, 20 |
| Location Registry | Roads, buildings, entrances, units, landmarks, canonical records, IDs, versions, corrections, retirement | 07, 10, 18, 20, 22, 23 |
| Field Operations | Assignments, teams, devices, areas, offline capture, synchronization, recapture, supervision | 21 | 09, 10, 17, 18, 25, 28, 29 |
| Evidence and Verification | Evidence metadata/custody, photos/documents/coordinates, duplicate and discrepancy review, quality, legal hold | 09, 22 | 10, 18, 20, 21, 25 |
| Publication and Corrections | Approval, release batches, public projections, certificates, signage, disputes, appeals, revocation | 23 | 08, 09, 17, 18, 20, 22, 25 |
| Agency Integration | Partner institutions, service clients, scoped APIs, webhooks, batch exchange, notification, reconciliation | 24 | 08, 09, 18, 25, 27, 28 |
| Audit, Reporting, and Analytics | Audit events, KPIs, data quality, SLAs, governed extracts, national statistics and accountability | 09, 26 | 07, 18, 20–25, 28, 30 |

## 3. Current platform module coverage

The current API module registry includes `auth`, `territories`, `registry`, `field-workflow`, `verification`, `publication`, `reporting`, `citizen-geotagging`, `signage-export`, and `integrations`.

| Current module | Primary skills | Required cross-cutting controls |
|---|---|---|
| `auth` | 08, 18 | 01–05, 09, 12–15, 16, 27 |
| `territories` | 07, 10, 18, 20 | 01–06, 09, 12–16 |
| `registry` | 07, 18, 20 | 01–10, 12–16, 23 |
| `field-workflow` | 18, 21, 22, 25 | 01–12, 13–16, 28, 29 |
| `verification` | 18, 22 | 01–16, 20, 21, 23 |
| `publication` | 18, 23 | 01–16, 20, 22, 24–28 |
| `reporting` | 18, 26 | 01–09, 12–16, 20–25, 28, 30 |
| `citizen-geotagging` | 17, 19, 21 | 01–12, 14–16, 18, 22, 28, 29 |
| `signage-export` | 23, 25 | 01–15, 17, 18, 20, 27, 28 |
| `integrations` | 18, 24, 25 | 01–10, 12–16, 27, 28 |

## 4. User-role coverage

| Role family | Main workflows | Primary skills |
|---|---|---|
| Citizen/public user | Lookup, submission, tracking, correction, proof, privacy and accessibility | 19 | 08–12, 17, 23, 29 |
| Enumerator | Assignment, capture, GPS/evidence, offline save, sync, recapture | 21 | 08–12, 17, 18, 22, 25, 28, 29 |
| Field supervisor | Assignment planning, quality review, exception handling, productivity | 21, 22 | 08–13, 17, 18, 20, 25, 26, 29 |
| Helpdesk/corrections agent | Search, case intake, follow-up, correction routing, citizen-safe status | 20, 23, 29 | 08, 09, 11, 17, 18, 22 |
| Municipal validator | Territorial case review, geometry/evidence verification, approval recommendation | 20, 22 | 07–12, 16, 18, 21, 23 |
| National registry administrator | Canonical registry governance, exceptions, versioning, retirement | 20 | 04–10, 12–16, 18, 22, 23, 26 |
| Ministry reviewer/publication authority | High-impact review, release approval, revocation, accountability | 23 | 04, 08, 09, 12–16, 20, 22, 26, 30 |
| Agency user/API client | Scoped lookup/exchange, reconciliation, quotas, support | 24 | 08, 09, 12–15, 18, 25, 27, 28 |
| Auditor/compliance user | Audit search, evidence lineage, access review, export oversight | 09, 26 | 08, 13–16, 20–25 |
| Platform/security operator | Deployment, secrets, monitoring, incident, backup, break glass | 27, 29 | 08, 09, 12–16, 28 |
| Programme owner/SDA | Priorities, architecture, risks, work orders, gates, release decisions | 14, 16, 30 | 01–05, 12, 15 and affected domain skills |

## 5. Service lifecycle coverage

| Lifecycle stage | Agent responsibilities | Primary skills |
|---|---|---|
| Discovery | Current-state audit, workflow observation, module maturity, dependency inventory | 01, 02, 16, 30 |
| Architecture and requirements | Work orders, ADRs, RFIs, domain/data/API/security/platform design | 03, 04, 07–10, 14, 16, 30 |
| Product/workflow design | Citizen, operator, field, agency and support workflows | 11, 17, 19–24, 29 |
| Implementation | Frontend, backend, worker, database, integration, infrastructure | 06–10, 16–18, 21–28 |
| Verification | Unit, integration, PostGIS, contract, browser, security, performance, recovery | 09–13, 22, 28 |
| Release | Exact-head evidence, images, migrations, runbooks, cutover, communications | 05, 12–15, 23–30 |
| Operation | Monitoring, support, incident, backups, partner service, field operations | 13, 21, 24, 27–29 |
| Improvement | Analytics, feedback, backlog, risk/benefit review, architecture updates | 14–16, 26, 29, 30 |

## 6. National-readiness coverage

| Readiness concern | Skills responsible |
|---|---|
| Authority and governance | 03, 04, 14, 15, 16, 23, 30 |
| Canonical data integrity | 06, 07, 10, 18, 20, 22 |
| Identity and scoped access | 08, 09, 16, 18, 20, 24, 27 |
| Security and privacy | 08, 09, 12, 13, 17–29 as affected |
| Spatial integrity | 07, 10, 18, 21, 22, 26 |
| Accessibility and bilingual service | 11, 17, 19–24, 29 |
| Interoperability | 08, 18, 24, 25, 27, 28 |
| Performance and national scale | 12, 13, 18, 25–28 |
| Backup and disaster recovery | 06, 09, 12, 13, 25, 27, 28 |
| Operational adoption | 11, 13, 17, 19–30 |
| Evidence and auditability | 09, 12, 14, 15, 18–26 |
| Programme sequencing and benefits | 16, 26, 29, 30 |

## 7. Common task-to-skill recipes

### Add a citizen address-submission workflow

```text
01, 02, 03, 05, 07, 08, 09, 10, 11, 12, 14, 15,
16, 17, 18, 19, 22, 28, 29
```

### Build an offline field-capture release

```text
01–05, 07–15,
16–18, 21, 22, 25, 27–30
```

### Implement registry duplicate resolution

```text
01–10, 12, 14, 15,
16, 18, 20, 22, 23, 26, 28
```

### Add official publication certificates and signage

```text
01–15,
16–18, 20, 22–25, 27–30
```

### Add a utility-company partner API

```text
01–10, 12–16,
18, 20, 23–25, 27, 28, 29, 30
```

### Introduce a national analytics dashboard

```text
01–09, 11–16,
17, 18, 20–26, 27, 28, 30
```

### Prepare a production environment and DR exercise

```text
01–06, 08, 09, 12–16,
18, 24, 25, 27–30
```

## 8. Coverage maintenance rule

When a new module or future national service is introduced—property registry, utilities, emergency dispatch, census, taxation, health, education, land, postal, or statistics—the agent must:

1. map it to existing NLI bounded domains;
2. identify required horizontal and vertical skills;
3. add a new domain skill only when recurring procedures are not adequately covered;
4. update this matrix, the router, and relevant work-order templates;
5. avoid creating a separate isolated architecture or data authority.

This keeps the skills system extensible across the full National Location Infrastructure rather than limited to the addressing product alone.
