# Skill 27 — Infrastructure, Environments, and Platform Engineering

## Use when

Use for Docker/container images, ingress/TLS, networks, environment separation, secrets, infrastructure as code, databases, Redis, object storage, deployment, patching, platform access, or production topology.

## Objective

Provide reproducible, secure, observable, supportable environments that separate development, test, staging, controlled pilot, and production while preserving accepted application and data controls.

## Procedure

1. Identify environment, service owners, trust zones, data classes, dependencies, and availability/recovery expectations.
2. Define environment separation for:
   - accounts/projects/networks;
   - domains/certificates;
   - databases/buckets/Redis;
   - credentials/keys/identity clients;
   - logs/monitoring/backups;
   - publication controls.
3. Define infrastructure through reviewable version-controlled configuration.
4. Build pinned, immutable, scanned container images traceable to reviewed commits.
5. Define ingress, TLS, firewall/security-group rules, service identities, least-privilege filesystem/process settings, and administrative entry paths.
6. Keep PostgreSQL/PostGIS, Redis, object storage, and management interfaces non-public.
7. Define secrets/key management, rotation, revocation, recovery, and environment-specific injection.
8. Define database HA/PITR, object-storage durability/versioning/retention, and Redis non-authoritative failure behavior.
9. Define health/readiness, metrics/logs/traces/alerts, deployment labels, and environment identity.
10. Define deployment sequence, migration job, smoke checks, rollback/forward recovery, maintenance, and patch ownership.
11. Add infrastructure/config validation, image build/runtime, secret scan, vulnerability scan, network/policy, and environment-identity tests.
12. Maintain runbooks for deploy, restore, credentials, dependency outage, capacity, and full reconstruction.

## Required evidence

- Environment/topology diagram
- Infrastructure/config diff
- Image provenance/version/scan result
- Network and trust-zone policy
- Secret/key lifecycle evidence
- Database/object/Redis configuration
- Deploy/migration/smoke/recovery runbook
- Monitoring/alert evidence
- Environment separation and label tests
- Reconstruction/DR compatibility

## Stop and escalate when

- Production would use a single-host development topology without accepted risk.
- A secret or management service would be public or source-controlled.
- An unpinned `latest` image is proposed for controlled deployment.
- Publication could be enabled by environment mislabelling.
- Infrastructure changes require downtime or data migration outside the work order.

## Anti-patterns

- Rebuilding different application code for each environment.
- Mutable source mounts in production.
- Shared credentials across environments.
- Public Postgres/Redis/MinIO administration.
- Manual console changes with no controlled configuration reconciliation.
- Health checks that ignore migration or dependency readiness.
- Treating local Compose as the national production reference.
