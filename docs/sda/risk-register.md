# NLI System Design Authority Risk Register

**Version:** 0.1  
**Baseline:** `c22c0d43670d4300f7fce65bdcebba307a0fc270`  
**Status:** Active

## Rating and status

- **P0:** blocks formal national-production approval or presents an immediate authority, security, integrity, or recoverability concern.
- **P1:** must be resolved before broad agency or publication readiness.
- **P2:** controlled architectural or operational debt that must be scheduled and monitored.

Statuses: `OPEN`, `TREATMENT IN PROGRESS`, `EVIDENCE REQUIRED`, `ACCEPTED RISK`, `CLOSED`, `SUPERSEDED`.

## Active risks

| ID | Priority | Risk | Consequence | Required treatment | Accountable authority | Status |
|---|---|---|---|---|---|---|
| SDA-RISK-001 | P0 | API startup creates/alters schema and loads reference/demo data. | A routine restart can mutate controlled state; deployments are not reproducible or independently approved. | Make versioned migrations the sole schema authority; separate reference data and development fixtures; add empty-database CI rehearsal. | SDA / Platform Engineering | TREATMENT IN PROGRESS — NLI-WO-001 |
| SDA-RISK-002 | P0 | Password and session implementation is pilot-grade. | Credential compromise, session replay, weak privileged-account assurance, and failure to meet government identity expectations. | Modern per-user password hashing, hashed session/refresh tokens, MFA, federation plan, credential rotation, and removal of source demo identities from production lifecycle. | Security Authority / SDA | OPEN — NLI-WO-003 |
| SDA-RISK-003 | P0 | Authorization uses four global role strings without institutional or territorial scope. | Users can receive broader authority than their institution, assignment, or municipality permits; segregation of duties cannot be expressed. | Implement organization membership, explicit permissions, RBAC+ABAC scope, record-state policy, and dual control. | Registry Governance / SDA | OPEN — NLI-WO-003 |
| SDA-RISK-004 | P0 | Operational DDL, migrations, and proposal schema compete as data-model authorities. | Schema drift, incompatible migrations, ambiguous identifiers, and inability to prove the canonical national model. | Converge one canonical model and one forward migration history with data dictionary and transition plan. | Data Authority / SDA | OPEN — NLI-WO-002 |
| SDA-RISK-005 | P0 | Local single-host Docker Compose topology may be mistaken for production architecture. | Single points of failure, weak isolation, unpinned runtime components, and inadequate national continuity. | Establish production reference topology, immutable images, managed secrets, HA data services, monitoring, backup, and failover. | Platform Operations / SDA | OPEN — NLI-WO-005 |
| SDA-RISK-006 | P0 | Official publication authority remains external and unnamed in the executable workflow. | Technical operators could publish without lawful authority, or valid records may remain indefinitely blocked. | Define institutional roles, dual approval, effective/revocation events, publication evidence, and named authority. | Programme Owner / Registry Authority | OPEN — NLI-WO-004 |
| SDA-RISK-007 | P1 | GIS governance covers canonical points but not full national geometry lifecycle. | Incorrect boundaries, roads, entrances, buildings, distance claims, or public maps may be treated as authoritative. | Define geometry classes, CRS rules, provenance, accuracy, topology, versioning, promotion, disputes, and licensing. | National GIS/Data Authority | OPEN — NLI-WO-006 |
| SDA-RISK-008 | P1 | Evidence storage lacks confirmed national retention, object-lock, malware, legal-hold, and access-governance controls. | Evidence may be altered, lost, retained unlawfully, disclosed inappropriately, or fail chain-of-custody review. | Govern evidence metadata, classification, encryption, versioning, object lock, scanning, retention, access audit, legal hold, and recovery. | Security / Records Authority | OPEN — NLI-WO-004 |
| SDA-RISK-009 | P1 | CI does not yet prove full software-supply-chain and migration safety. | Vulnerable dependencies, unsigned images, stale contracts, unsafe migrations, or secrets may reach controlled environments. | Add migration rehearsal, dependency and secret review, SAST, container scanning, SBOM, signed artefacts, provenance, and risk-based gates. | Platform Engineering / Security | OPEN — NLI-WO-005 |
| SDA-RISK-010 | P1 | Backup/restore scripts exist, but approved RPO/RTO, PITR, off-site recovery, object restoration, and full failover are unproven. | Extended outage or unrecoverable registry/evidence loss during a national incident. | Define service tiers and recovery objectives; test database, object, key, configuration, and complete-service recovery. | Platform Operations / Programme Owner | OPEN — NLI-WO-008 |
| SDA-RISK-011 | P1 | Public rate limiting is in process memory and external geocoding continuity is not governed. | Multi-instance limits are inconsistent; abuse or external service failure can degrade citizen workflows. | Move shared controls to governed infrastructure; define privacy, caching, limits, fallback, licensing, and graceful degradation. | Platform Engineering / GIS Authority | OPEN — NLI-WO-005 and NLI-WO-006 |
| SDA-RISK-012 | P2 | API and persistence modules contain many domain responsibilities. | Change coupling, slower review, inconsistent policy enforcement, and higher regression risk. | Refactor by bounded domain within the modular monolith; preserve contracts while extracting application services and policy modules. | Engineering Lead / SDA | OPEN — staged across work orders |
| SDA-RISK-013 | P1 | Central workflow evidence pack by role, route, viewport, commit, and date is missing. | Operational burden, excessive clicks, inaccessible paths, and role leakage may remain unseen despite component guards. | Create repeatable desktop/mobile workflow capture and acceptance evidence for all critical roles. | Product Operations / SDA | EVIDENCE REQUIRED |
| SDA-RISK-014 | P1 | Data classification, retention, residency, and privacy authority are not yet formally recorded. | Sensitive identity/location data may be over-collected, over-retained, exported, or hosted without proper authority. | Establish data inventory, classification, purpose, lawful authority, retention schedule, residency, disclosure, and deletion controls. | Programme Owner / Legal-Privacy Authority | OPEN — NLI-WO-004 |
| SDA-RISK-015 | P1 | Capacity, availability, and field-connectivity assumptions are not quantified. | Architecture may fail under national load or intermittent island/mainland connectivity. | Establish record volumes, concurrency, throughput, map/storage growth, device sync, SLOs, and load/failure tests. | Programme Owner / Platform Operations | OPEN — NLI-WO-005 and NLI-WO-008 |

## Risk treatment rules

1. A work order must reference every risk it treats.
2. Closing a risk requires evidence, not only a code change.
3. A risk remains open when implementation exists but migration, operations, authority, or recovery evidence is missing.
4. Accepted risk requires an accountable owner, rationale, affected environment, expiry/review date, and compensating controls.
5. The Implementation Agent may propose risk treatment but may not accept programme risk.
6. New discoveries receive a new stable ID; existing IDs are not silently repurposed.

## Initial release blockers

National production cannot be approved while any of the following remain unresolved or unaccepted by the correct authority:

- SDA-RISK-001 through SDA-RISK-006;
- inability to restore authoritative database and evidence state;
- absence of named security, registry, GIS/data, and publication authorities;
- failure to demonstrate scoped privileged access and auditability;
- unapproved canonical data model and address/location identifier standard.
