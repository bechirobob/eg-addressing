# S28 — Infrastructure, Environments, and Platform Engineering

## Invoke when

- changing containers, ingress/TLS, networks, environments, secrets, IaC, deployment, or patching;
- configuring PostgreSQL/PostGIS, Redis, object storage, identity clients, logs, monitoring, or backups;
- preparing staging, pilot, or production topology.

## Required inputs

- target deployment/reference architecture;
- environment, security, operations, and DR standards;
- service/data owners and classifications;
- build/deploy/migration/runtime contracts;
- capacity, availability, and recovery requirements or RFIs.

## Procedure

1. Identify environment, owners, trust zones, dependencies, data classes, and recovery expectations.
2. Separate accounts/networks/domains/databases/buckets/credentials/logs/backups/publication controls by environment.
3. Define infrastructure through version-controlled reviewable configuration.
4. Build pinned, immutable, scanned images traceable to reviewed commits.
5. Define ingress, TLS, firewall, runtime identities, least privilege, filesystems, and administrative entry paths.
6. Keep database, Redis, object-storage administration, and management interfaces non-public.
7. Define secrets/key generation, injection, rotation, revocation, and recovery.
8. Define database HA/PITR, object durability/versioning/retention, and Redis failure behavior.
9. Define health/readiness/production-readiness, metrics/logs/traces/alerts, and environment identity.
10. Define deployment, explicit migration action, smoke, rollback/forward recovery, maintenance, and patch ownership.
11. Test configuration, image runtime, network/policy, secret scanning, environment labels, dependency failure, and reconstruction.

## Outputs

- environment/topology and trust-zone diagrams;
- infrastructure/configuration source;
- image provenance and scan evidence;
- network, identity, secret, and data-service policies;
- deployment/migration/smoke/recovery runbooks;
- monitoring and reconstruction evidence.

## Stop or RFI conditions

Stop when:

- production would rely on an unaccepted single-host topology;
- secrets or management services are public/source-controlled;
- unpinned images are proposed;
- environment mislabelling could enable publication;
- infrastructure change needs downtime/data migration outside scope.

## Evidence gate

Before review:

- environment separation and labels are verified;
- images are immutable, scanned, and booted;
- network/secrets/data services meet policy;
- explicit migration and deploy/recovery paths execute;
- monitoring/alerting and reconstruction ownership are named.

## Anti-patterns

- Rebuilding different code per environment.
- Mutable source mounts in production.
- Shared credentials across environments.
- Public Postgres/Redis/object-admin endpoints.
- Manual console changes without reconciliation.
- Calling local Compose the production reference.
