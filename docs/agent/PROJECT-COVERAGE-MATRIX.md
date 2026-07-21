# NLI Whole-Project Agent Skill Coverage Matrix

**Purpose:** Demonstrate that the canonical delivery-agent skill pack covers the complete National Location Infrastructure programme—not only a current work order, data model, or application section.

The pack has two layers:

- **S01–S16:** cross-cutting authority, discovery, planning, data/API/GIS/UI, testing, delivery, review, maintenance, operations, and self-audit;
- **S17–S31:** whole-project architecture, applications, product domains, integrations, analytics, platform, performance, adoption, and programme management.

Most substantive tasks invoke skills from both layers.

## 1. Repository surface coverage

| Repository area | Responsibility | Primary whole-project skills | Required cross-cutting skills |
|---|---|---|---|
| `apps/admin-portal` public routes | Citizen lookup, submission, tracking, corrections, public proof | S18, S20, S24 | S01, S03, S08–S12, S16 |
| `apps/admin-portal` protected routes | Registry, verification, field supervision, reports, publication, staff operations | S18, S21, S23, S24, S27 | S01, S03, S08–S13, S16 |
| `apps/field-app` | Enumerator/supervisor mobile capture and offline synchronization | S18, S22 | S01, S03, S06, S08–S12, S15, S16, S26, S29 |
| `services/api` | FastAPI contracts, use cases, policies, persistence, audit | S19 | S01–S13, S16–S25 as affected |
| `services/worker` | Exports, retries, notifications, reconciliation, long jobs | S26 | S01, S03, S08, S11, S12, S15, S16, S25, S27, S29 |
| `packages/ui` | Shared accessible design system | S18 | S01, S03, S10–S12, S16 |
| `packages/types` | Shared/generated contracts | S18, S19, S25 | S01, S03, S06, S08, S11, S12, S16 |
| `packages/config` | Typed environment/configuration utilities | S28 | S01, S03, S08, S11, S12, S15, S16 |
| `infra/migrations` | Controlled PostgreSQL/PostGIS schema authority | S19 | S01, S03, S06, S07, S09, S11, S12, S15, S16 |
| `infra/scripts` | Migration, backup, restore, bootstrap, batch/operator automation | S26, S28 | S01, S03, S07, S11, S12, S14–S16 |
| `infra/docker` / future ingress/IaC | Local stack and production platform topology | S28, S29 | S01, S03, S08, S11, S12, S15, S16 |
| `env` | Safe environment templates/configuration contracts | S28 | S01, S03, S08, S11, S15, S16 |
| `docs/sda` | Architecture authority, standards, ADRs, work orders, reviews, risks | S17, S31 | S01–S06, S11–S16 and affected domains |
| `docs` / `artifacts` | Training, architecture, reports, exports, evidence bundles | S27, S30 | S01, S03, S08–S12, S16, S24, S26 |
| `data` | Local disposable runtime state, never source authority | S28 | S01, S07, S08, S15, S16 |

## 2. NLI bounded-domain coverage

| Bounded domain | Capabilities | Skills |
|---|---|---|
| Identity and Trust | Human/service identities, memberships, roles, permissions, territorial scope, sessions, federation/MFA planning, delegated/break-glass access | S08, S17, S19, S21, S25, S28 |
| Administrative Geography | Country/province/district/municipality hierarchy, names/codes, boundaries, historical versions, scope mapping | S06, S09, S17, S19, S21 |
| Location Registry | Roads, buildings, entrances, units, landmarks, canonical records, IDs, versions, retirement | S06, S09, S19, S21, S23, S24 |
| Field Operations | Assignments, devices, teams, offline capture, synchronization, recapture, supervision | S22 | S08–S11, S15, S18, S19, S23, S26, S29, S30 |
| Evidence and Verification | Evidence custody, photos/documents/coordinates, duplicate/discrepancy review, quality, legal hold | S23 | S08, S09, S19, S21, S22, S26 |
| Publication and Corrections | Approval, release manifests, public projection, certificates, signage, disputes, appeals, revocation | S24 | S08–S12, S17–S21, S23, S25, S26 |
| Agency Integration | Partner institutions, service clients, APIs, webhooks, notifications, batch exchange, reconciliation | S25 | S08, S11, S12, S15, S17, S19, S26, S28, S29 |
| Audit, Reporting, Analytics | Audit events, KPIs, quality/SLA measures, governed extracts, statistics, accountability | S27 | S06, S08, S11, S15, S17, S19, S21–S26, S29, S31 |

## 3. Current platform module coverage

Current modules include `auth`, `territories`, `registry`, `field-workflow`, `verification`, `publication`, `reporting`, `citizen-geotagging`, `signage-export`, and `integrations`.

| Module | Primary whole-project skills | Supporting cross-cutting skills |
|---|---|---|
| `auth` | S17, S19, S28 | S01–S05, S08, S11–S16 |
| `territories` | S17, S19, S21 | S01–S09, S11–S16 |
| `registry` | S19, S21 | S01–S13, S16, S23, S24 |
| `field-workflow` | S19, S22, S23, S26 | S01–S16, S29, S30 |
| `verification` | S19, S23 | S01–S13, S16, S21, S22, S24 |
| `publication` | S19, S24 | S01–S16, S21, S23, S25–S31 |
| `reporting` | S19, S27 | S01–S16, S21–S26, S29, S31 |
| `citizen-geotagging` | S18, S20, S22 | S01–S13, S16, S19, S23, S29, S30 |
| `signage-export` | S24, S26 | S01–S16, S18, S19, S21, S28, S29 |
| `integrations` | S19, S25, S26 | S01–S16, S28, S29 |

## 4. User-role coverage

| Role family | Main workflows | Skills |
|---|---|---|
| Citizen/public | Lookup, submission, tracking, correction, proof, privacy/accessibility | S20 | S08–S12, S18, S24, S30 |
| Enumerator | Assignment, capture, GPS/evidence, offline save/sync, recapture | S22 | S08–S12, S18, S19, S23, S26, S29, S30 |
| Field supervisor | Assignment planning, quality review, exceptions, productivity | S22, S23 | S08–S12, S15, S18, S19, S21, S26, S27, S30 |
| Helpdesk/corrections agent | Search, intake, follow-up, routing, citizen-safe status | S21, S24, S30 | S08, S10, S18, S19, S23 |
| Municipal validator | Territorial review, geometry/evidence verification, recommendation | S21, S23 | S06–S12, S17, S19, S22, S24 |
| National registry administrator | Canonical governance, exceptions, versions, retirement | S21 | S04–S12, S16, S17, S19, S23, S24, S27 |
| Ministry reviewer/publication authority | High-impact review, release, revocation, accountability | S24 | S04, S08–S12, S16, S17, S21, S23, S27, S31 |
| Agency user/API client | Scoped exchange, reconciliation, quotas, support | S25 | S08, S11, S12, S15, S16, S19, S26, S28–S30 |
| Auditor/compliance | Audit search, evidence lineage, access/export oversight | S27 | S05, S08, S11, S15–S17, S19, S21–S26 |
| Platform/security operator | Deployment, secrets, monitoring, incident, backup, break glass | S28, S30 | S08, S11, S12, S14–S17, S29 |
| Programme owner/SDA | Priorities, architecture, risks, work orders, gates, benefits | S17, S31 | S01–S06, S11–S16 and affected domain skills |

## 5. Service lifecycle coverage

| Stage | Agent responsibilities | Skills |
|---|---|---|
| Discovery | Current-state audit, workflow observation, maturity/dependency inventory | S01, S02, S05, S16, S17, S31 |
| Architecture/requirements | Work orders, ADRs, RFIs, domain/data/API/security/platform design | S03, S04, S06, S08, S09, S17, S31 |
| Product/workflow design | Citizen, operator, field, agency, support workflows | S10, S18, S20–S25, S30 |
| Implementation | Frontend, backend, worker, database, integrations, infrastructure | S07–S12, S17–S29 |
| Verification | Unit, integration, PostGIS, contract, browser, security, performance, recovery | S08–S11, S15, S23, S29 |
| Release | Exact-head evidence, images, migration, runbooks, cutover, communication | S12, S15, S16, S24–S31 |
| Operation | Monitoring, support, incident, backups, partner service, field operations | S15, S22, S25, S28–S30 |
| Improvement | Analytics, feedback, backlog, risk/benefit review, architecture updates | S04, S13, S16, S17, S27, S30, S31 |

## 6. National-readiness coverage

| Concern | Responsible skills |
|---|---|
| Authority/governance | S01, S03, S04, S13, S16, S17, S24, S31 |
| Canonical data integrity | S05–S07, S09, S19, S21, S23 |
| Identity/scoped access | S08, S17, S19, S21, S25, S28 |
| Security/privacy/audit | S08, S11, S15, S17–S30 as affected |
| Spatial integrity | S06, S09, S19, S22, S23, S27 |
| Accessibility/bilingual service | S10, S18, S20–S25, S30 |
| Interoperability | S08, S17, S19, S25, S26, S28, S29 |
| Performance/national scale | S11, S15, S19, S26–S29 |
| Backup/disaster recovery | S07, S08, S11, S15, S26, S28, S29 |
| Adoption/operations | S10, S15, S18, S20–S31 |
| Evidence/auditability | S08, S11–S13, S16, S19–S27 |
| Programme sequencing/benefits | S17, S27, S30, S31 |

## 7. Common task recipes

### Citizen address-submission workflow

```text
S01, S03, S05, S08–S12, S16–S20, S23, S29, S30
```

### Offline field-capture release

```text
S01–S16 as triggered, S17–S19, S22, S23, S26, S28–S31
```

### Registry duplicate resolution

```text
S01–S13, S16, S17, S19, S21, S23, S24, S27, S29
```

### Official publication certificates/signage

```text
S01–S16, S17–S19, S21, S23–S26, S28–S31
```

### Utility-company partner API

```text
S01–S16, S17, S19, S21, S24–S26, S28–S31
```

### National analytics dashboard

```text
S01–S16, S17–S21, S23–S29, S31
```

### Production environment and DR exercise

```text
S01–S16, S17, S19, S25, S26, S28–S31
```

## 8. Future-service extension rule

When property, utilities, emergency dispatch, census, taxation, health, education, land, postal, or other national services are introduced:

1. map the service to existing NLI bounded domains and canonical location authority;
2. select cross-cutting and whole-project skills by effects;
3. add a new skill only when recurring procedures are not adequately covered;
4. update this matrix, manifest, and validator;
5. avoid creating an isolated architecture, identity model, GIS authority, or registry copy.
