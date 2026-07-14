# Skill 13 — Operations, Backup, and Disaster Recovery

## Use when

Use for environments, deployment, health/readiness, monitoring, capacity, backup, restore, incident handling, runbooks, failover, or external dependency continuity.

## Objective

Make the service observable, recoverable, and operable by named authorities under normal, degraded, and emergency conditions.

## Procedure

1. Identify service owner, institutional owner, data class, dependencies, support boundary, and environment.
2. Separate liveness, readiness, production-readiness, and business-authority readiness.
3. Define configuration/secrets and environment separation.
4. Define metrics, logs, traces, alerts, correlation IDs, ownership, and runbooks.
5. Define failure behavior for database, Redis, object storage, identity, geocoder/maps, queues, network, DNS, certificates, storage, and worker retries.
6. State service objectives or identify them as unresolved:
   - availability;
   - latency/throughput;
   - data freshness;
   - queue age;
   - RPO/RTO;
   - maintenance windows.
7. Model capacity assumptions for records, events, evidence, spatial queries, public/operator/partner concurrency, exports, logs, and backups.
8. Define backup scope for database, object storage, configuration, keys/secrets metadata, audit, and required projections.
9. Execute restore drills that validate:
   - schema/extensions/ledger;
   - selected row counts, hashes, relationships, and semantics;
   - evidence object/version/hash linkage;
   - identity/authorization reconstruction;
   - application startup and smoke;
   - monitoring;
   - temporary target cleanup.
10. Record actual recovery point and duration.
11. Update deploy, failure, incident, credential, publication-revocation, and reconstruction runbooks.
12. Ensure emergency changes preserve audit/evidence and receive post-incident follow-up.

## Required evidence

- Topology/configuration diff
- Service ownership and dependencies
- Health/readiness/metric/log/alert result
- Capacity assumptions and test result
- Backup manifest/integrity result
- Source/restored invariant comparison
- Recovery duration/data point
- Failure-mode test
- Deployment/rollback or forward-recovery runbook
- Residual RPO/RTO/authority RFIs

## Stop and escalate when

- A production SLA/RPO/RTO is being claimed without approval.
- Backup exists but restore cannot be demonstrated.
- Object/evidence recovery is excluded without authority.
- A dependency failure can create false official state.
- An emergency action would bypass audit or publication authority.

## Anti-patterns

- Treating `/health = ok` as production readiness.
- Validating restore only by table counts while ignoring hashes/relationships/evidence.
- Using ordinary application credentials to protect all backups.
- Assuming Redis or a queue is durable official history.
- Claiming high availability from a single-host Compose stack.
- Writing runbooks that have never been executed.
