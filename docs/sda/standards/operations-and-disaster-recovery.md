# SDA Standard — Operations and Disaster Recovery

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** environments, deployment, monitoring, capacity, backup, recovery, incident response, and service ownership

## 1. Operational ownership

Every production-capable service MUST have:

- named technical and institutional owner;
- service purpose and data classification;
- support hours and escalation path;
- dependencies and trust boundaries;
- health, readiness, metrics, logs, alerts, and runbooks;
- backup/recovery responsibilities;
- maintenance and patching owner;
- capacity and continuity assumptions.

An endpoint that reports `ok` is not an operational model.

## 2. Environment separation

Development, test, staging, controlled pilot, and production MUST be separate security and data boundaries.

- Credentials, keys, databases, buckets, domains, and identity clients MUST be environment-specific.
- Production data MUST NOT flow into lower environments without approved de-identification and traceability.
- Environment labels MUST be visible and accurate; production MUST refuse pilot/staging identity.
- Publication controls MUST default to disabled outside an explicitly authorized release environment.
- Administrative access paths and audit retention MUST be defined per environment.

## 3. Infrastructure control

- Production infrastructure MUST be described through reviewable, version-controlled configuration.
- Runtime images and packages MUST be pinned, scanned, immutable, and traceable to a reviewed commit.
- Configuration MUST be validated before deployment; secrets remain outside source control.
- Manual console changes require an incident/change record and must be reconciled into controlled configuration.
- Single-host Docker Compose is permitted for local development or bounded pilot use only; it is not the production reference.

## 4. Availability architecture

Production design MUST address:

- redundant application instances;
- health-aware load balancing and graceful termination;
- database high availability and connection management;
- resilient object storage;
- non-authoritative Redis failure behavior;
- external geocoder/map/notification degradation;
- maintenance without unplanned authority or data loss;
- regional/connectivity conditions for islands, mainland, municipalities, and field devices.

No availability percentage may be claimed until service tiers and measurement rules are approved.

## 5. Observability

### Metrics

Services MUST expose business and technical metrics appropriate to their role, including:

- request volume, latency, error and saturation;
- database connections, locks, slow queries, replication and storage;
- object-storage errors, capacity, integrity, and latency;
- queue depth, age, retry, failure, and dead-letter state;
- authentication, denial, rate-limit, import/export, publication, and evidence events;
- field synchronization and unresolved workflow backlog;
- backup age and restore-drill status.

### Logs and traces

- Structured logs MUST use request/correlation IDs and controlled event names.
- Logs MUST be centralized, access controlled, retained, and protected from routine alteration.
- Sensitive data and secrets MUST be redacted at source.
- Distributed tracing MAY be used, but trace payloads must follow data classification.

### Alerts

Every alert MUST have an owner, severity, threshold/rationale, response action, and review process. Alerts that are routinely ignored must be fixed or removed through controlled change.

## 6. Service objectives

Before broad agency or national production, define for each service tier:

- service hours and availability target;
- latency and throughput objectives;
- data freshness;
- maximum acceptable queue age;
- recovery time objective (RTO);
- recovery point objective (RPO);
- maintenance windows;
- dependency assumptions;
- measurement source and reporting period.

The Programme Owner approves service-level trade-offs; the SDA verifies architectural feasibility and evidence.

## 7. Capacity and scaling

Capacity plans MUST state assumptions for:

- canonical records and version/event growth;
- citizen and field submissions;
- evidence object count, size, and retention;
- concurrent public, operator, and partner users;
- search and spatial query load;
- imports, exports, certificates, and signage batches;
- audit/log growth;
- offline synchronization peaks;
- backup size and restore duration.

Scale tests MUST use representative distributions and data complexity, not only row counts.

## 8. Backup standard

Authoritative database, object storage, configuration, keys/secrets metadata, and necessary audit state MUST be recoverable.

Backups MUST provide:

- encryption in transit and at rest;
- access separate from ordinary application credentials;
- automated schedule and monitored completion;
- integrity hash or platform verification;
- retention according to approved policy;
- at least one isolated/off-site or geographically separate copy for production;
- point-in-time recovery for the production database when approved RPO requires it;
- protected backup catalog and documented restore prerequisites.

Backup creation without restore proof is insufficient.

## 9. Restore and disaster-recovery testing

Restore drills MUST test, at representative scale:

- database schema, data, extensions, constraints, and migrations;
- record counts and selected semantic invariants;
- object/evidence existence, version, hash, and metadata linkage;
- audit timelines;
- application configuration and secrets/key recovery;
- identity and authorization reconstruction;
- generated/public projections where necessary;
- service startup, smoke tests, and monitoring;
- target cleanup and evidence report.

Drills MUST record actual recovery duration and data point achieved. National production requires scheduled end-to-end exercises, not only disposable database restoration.

## 10. Failure behavior

- Loss of Redis MUST NOT erase official state.
- External geocoder/map failure MUST degrade to capture and later review, not block valid evidence or invent authority.
- Object-storage failure MUST prevent false evidence acceptance and support safe retry.
- Database unavailability MUST fail writes clearly and avoid ambiguous client success.
- Worker retries MUST be idempotent and bounded.
- Partial publication or export failure MUST be detectable, reconcilable, and revocable.
- Clock, DNS, certificate, storage, network, and dependency failures must be represented in operational testing.

## 11. Change and deployment operations

Every controlled deployment MUST have:

- approved artefact, commit, work orders, and release record;
- operator and change window;
- preflight configuration, backup, migration, dependency, and capacity checks;
- deployment sequence;
- validation and smoke checks;
- monitoring period and abort criteria;
- rollback or forward-recovery steps;
- communication/escalation plan;
- post-deployment evidence.

Schema migrations are run as explicit release actions, never as ordinary API startup behavior.

## 12. Incident management

Incidents MUST have:

- stable incident ID, severity, lead, and timeline;
- affected services, records, institutions, and data classes;
- containment and authority decisions;
- communication and escalation path;
- preservation of security/evidence records;
- recovery validation;
- root-cause and contributing-factor analysis;
- corrective work orders and owners.

Emergency actions use audited break-glass access. Restoration of service does not close an incident until data integrity and official-state consequences are assessed.

## 13. Runbooks

At minimum, maintain tested runbooks for:

- deploy and validate;
- database migration failure;
- database backup and restore;
- object-storage failure and recovery;
- expired/compromised credentials or keys;
- identity-provider outage;
- Redis/queue failure;
- external map/geocoder outage;
- high error/latency or capacity exhaustion;
- evidence integrity mismatch;
- incorrect publication or export revocation;
- security incident and break-glass access;
- full environment reconstruction.

Runbooks MUST state prerequisites, safe commands, expected output, verification, rollback, and escalation.

## 14. Required evidence

Operationally material changes require:

- topology/configuration diff;
- dependency and failure-mode analysis;
- health/readiness/metrics/log/alert evidence;
- capacity effect;
- backup and recovery effect;
- deployment and recovery procedure;
- representative failure test;
- security and access-control implications;
- updated runbooks and ownership;
- unresolved RPO/RTO or institutional RFIs.
