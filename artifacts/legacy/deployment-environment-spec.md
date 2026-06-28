# National Digital Addressing Platform — Deployment & Environment Specification

**Purpose:** Define how the platform should be deployed, separated by environment, secured operationally, and prepared for pilot-to-national growth.

---

## 1. Deployment Goals

The deployment model must:

- support a serious pilot without overengineering
- separate development from production
- keep government data protected
- support backups and restore
- provide observability and operational control
- leave room for national-scale hardening later

---

## 2. Recommended Architecture Style

**Recommended starting posture:** Dockerized services in a controlled VM or small cluster environment behind a reverse proxy.

This is the best early balance of:
- simplicity
- maintainability
- deployment speed
- operational realism
- future scaling flexibility

Do not start with Kubernetes unless there is already a strong operational team and a real need.

---

## 3. Core Deployable Components

At minimum, deploy these components:

| Component | Purpose |
|---|---|
| `frontend` | Next.js admin/public UI |
| `backend` | FastAPI application and core business logic |
| `worker` | Background jobs, exports, sync processing |
| `postgres` | Primary relational database |
| `postgis` | Spatial extension enabled on PostgreSQL |
| `redis` | Cache / queue / transient state |
| `object-storage` | Field photos, evidence, exports |
| `reverse-proxy` | TLS termination, routing, headers |
| `backup-job` | Scheduled backups and retention management |

In practice, PostGIS is part of PostgreSQL, but it is called out here because it is mission-critical to the architecture.

---

## 4. Environment Model

## 4.1 Required environments

### `dev`
For active engineering work.

### `staging`
For pre-production validation, stakeholder review, and QA.

### `production`
For live pilot operations and official data.

## 4.2 Recommended additional environments

### `training`
For ministry and field-team training without production risk.

### `demo`
For safe demonstrations, onboarding, and controlled presentations.

---

## 5. Environment Responsibilities

| Environment | Main Use | Data Type | Who Uses It |
|---|---|---|---|
| Dev | Engineering work | synthetic/test | engineers |
| Staging | QA and release validation | scrubbed or controlled sample | engineers, QA, reviewers |
| Training | user practice | controlled training data | ministry users, field teams |
| Demo | presentations | controlled demo data | leadership demos |
| Production | live pilot operations | official operational data | authorized live users |

---

## 6. Network & Traffic Flow

```text
Users / Agency Clients
         |
         v
Reverse Proxy / TLS
         |
  ----------------------
  |         |          |
  v         v          v
Frontend  Backend    Worker API Hooks
              |
      -------------------
      |        |        |
      v        v        v
   Postgres   Redis   Object Storage
    + PostGIS
```

---

## 7. Deployment Topology Recommendation

## 7.1 Pilot topology

For the pilot, you can run on:

- one strong VM for app services plus one DB VM, or
- a small managed/cloud stack with separated DB/storage

### Recommended split
- **App Node**: frontend, backend, worker, reverse proxy
- **DB Node**: PostgreSQL/PostGIS
- **Object Storage**: managed or self-hosted compatible storage

This is enough to be serious without becoming ops theatre.

## 7.2 Growth topology

When load or importance grows:

- separate frontend/backend scaling
- isolate worker processing
- add DB read replica if needed
- harden backup and DR process
- segment internal admin traffic if required

---

## 8. Containerization Guidance

Each application component should be separately containerized.

### Recommended images/services
- `frontend`
- `backend`
- `worker`
- `nginx` or `caddy`

### Why
- easier deployments
- repeatable environments
- simpler rollback
- clearer runtime boundaries

---

## 9. Configuration & Secrets

### 9.1 Configuration principles
- config via environment variables or managed config store
- no secrets committed to git
- separate secrets per environment
- rotation path for API credentials and service credentials

### 9.2 Secret classes
- database credentials
- object storage credentials
- session/auth secrets
- SMTP/notification credentials if used
- integration API client secrets
- backup destination credentials

---

## 10. Data Storage & Backups

## 10.1 Primary data
- PostgreSQL + PostGIS as system of record
- object storage for media/evidence/exports

## 10.2 Backup requirements
- nightly full DB backups
- point-in-time recovery strategy if feasible
- object storage backup/replication policy
- retention policy by environment

### Suggested baseline
- dev: short retention
- staging/training/demo: moderate retention
- production: strong retention with tested restore plan

## 10.3 Restore discipline
Backups do not count unless restore has been tested.

Minimum standard:
- scheduled restore tests
- documented recovery steps
- named owner for backup success/failure monitoring

---

## 11. Logging, Monitoring, and Alerting

## 11.1 Logging
Capture structured logs for:
- login events
- API requests
- approval actions
- field sync failures
- export jobs
- integration access
- worker task failures

## 11.2 Monitoring
Track:
- CPU / memory / disk
- DB health
- API latency
- search latency
- queue backlog
- storage usage
- backup success/failure
- sync failure rate
- uptime

## 11.3 Alerting
Alert on:
- DB unavailable
- backup failure
- worker backlog spike
- repeated sync failures
- storage exhaustion
- suspicious admin activity
- TLS expiry risk

---

## 12. Security Posture

### 12.1 Baseline controls
- TLS everywhere
- locked-down admin interfaces
- least-privilege credentials
- encrypted secrets storage
- protected backups
- audited privileged actions
- secure headers at reverse proxy

### 12.2 Access separation
- production access only for authorized ops/admins
- staging/training/demo isolated from prod credentials
- no direct casual DB access for day-to-day users

### 12.3 Hardening path
Later, add:
- MFA for privileged users
- IP allowlists for admin surfaces
- network segmentation
- WAF or additional gateway controls if needed

---

## 13. Release & Change Management

### 13.1 Release path
Recommended path:

1. develop in `dev`
2. validate in `staging`
3. train or showcase in `training` / `demo` if needed
4. release to `production`

### 13.2 Minimum release gates
- schema migrations reviewed
- smoke tests pass
- critical workflow tests pass
- backup job healthy
- rollback path known

### 13.3 Rollback expectation
Every production release should have:
- previous image/build reference
- rollback instructions
- migration impact note

---

## 14. Suggested CI/CD Flow

At minimum:
- lint
- tests
- build frontend/backend images
- push artifacts
- deploy to staging
- manual or controlled promotion to production

Do not allow uncontrolled direct production changes from developer laptops.

---

## 15. Disaster Recovery / Continuity

## 15.1 What DR should cover
- DB corruption or loss
- object storage failure
- host failure
- deployment failure
- network outage affecting pilot operations

## 15.2 Minimum pilot DR posture
- daily DB backup
- exportable recovery package
- documented restore steps
- fallback contact and decision owner

## 15.3 National-scale DR posture later
- stronger recovery objectives
- secondary environment or failover posture
- formal continuity drills
- leadership-visible readiness metrics

---

## 16. Environment-Specific Recommendations

## Dev
- use synthetic data
- easier logging access
- shorter retention
- fast iteration

## Staging
- mirrors production architecture as closely as reasonable
- used for UAT and release verification
- no real uncontrolled production writes

## Training
- stable scenarios for ministry and field training
- resettable data
- no real pilot records

## Demo
- polished walkthrough data
- safe public-facing or leadership-friendly environment

## Production
- official pilot operations only
- strongest controls and backup discipline

---

## 17. Pilot Recommendation Summary

For the pilot, the clean deployment recommendation is:

- Dockerized frontend, backend, worker, reverse proxy
- PostgreSQL + PostGIS as primary DB
- Redis for queue/cache
- S3-compatible object storage
- dev, staging, training, demo, and production environments as appropriate
- nightly backups with restore verification
- structured logs, monitoring, and alerting

---

## 18. Plain-English Summary

The deployment should be simple enough to run reliably during the pilot but disciplined enough to protect official government data. That means separate environments, containerized services, a proper Postgres/PostGIS core, controlled backups, and clear release/rollback practice — not random manual changes and vibes.
