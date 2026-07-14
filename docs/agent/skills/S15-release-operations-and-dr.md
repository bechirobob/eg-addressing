# S15 — Release, Operations, and Disaster Recovery

## Invoke when

- changing deployment, environments, containers, configuration, secrets, observability, backups, restore, failover, or runbooks;
- making pilot-, agency-, publication-, or production-readiness claims;
- changing migrations or long-running/background jobs;
- handling an incident or emergency release.

## Required inputs

- operations/DR, security, testing/release standards;
- accepted work order and release class;
- current deployment topology and environment configuration;
- service owners and dependency inventory;
- RPO/RTO/SLO decisions, if approved;
- backup, restore, and incident runbooks.

## Procedure

### 1. Define the release boundary

Record:

- environment;
- artefact/commit;
- work orders and migrations;
- operator and approver;
- deployment window;
- data and authority effects;
- publication lock state;
- rollback or forward-recovery strategy.

### 2. Verify immutable artefacts and configuration

- build from reviewed commit;
- pin dependencies/base images;
- keep secrets outside source;
- use environment-specific credentials;
- verify configuration before deployment;
- generate SBOM/provenance/signature when required.

### 3. Verify operational readiness

Check:

- liveness versus readiness;
- migrations and reference package status;
- database/PostGIS connectivity;
- object storage and Redis degradation behavior;
- metrics, logs, traces, alerts, and dashboards;
- capacity and storage headroom;
- external dependency fallbacks;
- support/escalation ownership.

### 4. Define failure behavior

For each dependency describe:

- expected failure mode;
- user/operator effect;
- retry/idempotency behavior;
- authority/data-integrity protection;
- alert and owner;
- recovery action.

Loss of Redis must not erase official state. External geocoder failure must not fabricate authority. Object-storage failure must not falsely accept evidence.

### 5. Prove backup and restore

Capture and compare:

- source and restored migration ledger;
- selected row counts and semantic invariants;
- evidence object versions/hashes and metadata links;
- audit timelines;
- keys/secrets/configuration recovery;
- identity/authorization reconstruction;
- actual RPO point and recovery duration;
- cleanup of disposable restore target.

### 6. Validate deployment sequence

```text
preflight → backup → migration/release action → deploy artefact
→ readiness → smoke/policy checks → monitoring → decision
```

Document abort criteria and forward recovery.

### 7. Manage incidents

Record incident ID, lead, timeline, affected data/services, containment, evidence preservation, credential decisions, recovery validation, communication, and corrective work orders.

## Outputs

- release record and deployment plan;
- topology/configuration diff;
- readiness/observability evidence;
- failure-mode tests;
- backup/restore or DR report;
- updated runbooks;
- explicit readiness boundary.

## Stop or RFI conditions

Stop when:

- production topology or owner is undefined;
- RPO/RTO or service level is being claimed without approval;
- backup exists but restore is untested;
- schema/data change lacks recovery;
- production secrets/default credentials are unsafe;
- publication could be enabled without named authority;
- monitoring has no owner or actionable runbook;
- an environment rebuild depends on mutable/manual undocumented state.

## Evidence gate

Before a readiness claim:

- same accepted artefact passed through required environments;
- exact migrations and configuration are verified;
- alerts/runbooks/owners exist;
- representative failure and recovery tests pass;
- backup/restore preserves authoritative and evidence state;
- residual risks and conditions are recorded;
- SDA/Programme Owner approval exists for the claimed readiness level.

## Anti-patterns

- Calling Docker Compose a national production topology.
- Using a health endpoint as production-readiness proof.
- Reporting a successful restore from row counts alone.
- Claiming high availability without failover evidence.
- Rebuilding different artefacts for each environment.
- Treating SDA work-order acceptance as automatic deployment/publication approval.
