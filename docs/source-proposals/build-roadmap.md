# National Digital Addressing Platform — Build Roadmap

## Goal
Deliver a pilot-ready national digital addressing platform that can support real field capture, official review, publication, and institutional verification in priority zones.

---

## Phase 0 — Standards and technical foundation (Week 1-2)

### Outcomes
- confirm address format and numbering rules
- confirm pilot geography and rollout zones
- confirm publication authority and workflow owners
- lock data model, API surface, and environment model

### Deliverables
- approved architecture blueprint
- schema.sql baseline
- OpenAPI MVP baseline
- repo scaffold
- design decisions register

### Risks
- vague governance
- unstable data rules
- trying to code before standards are settled

---

## Phase 1 — Platform foundation (Week 3-5)

### Build
- auth and RBAC
- territory hierarchy CRUD/read
- zone scoping
- audit log base middleware
- frontend shell for admin portal
- backend service skeleton
- DB migration pipeline

### Exit criteria
- users can log in
- scoped roles work
- territories can be loaded and queried
- every privileged action is logged

---

## Phase 2 — Registry core (Week 6-8)

### Build
- roads module
- buildings module
- address registry module
- address versioning
- status transition model
- address search and verification basics

### Exit criteria
- staff can create and edit roads/buildings/addresses
- address lifecycle states work cleanly
- search returns reliable pilot records

### Watch-outs
- duplicate building/address creation
- inconsistent naming conventions

---

## Phase 3 — Field operations (Week 9-11)

### Build
- field assignments
- field submission forms
- GPS capture structure
- photo upload flow
- supervisor review queue
- reject/correction workflow

### Exit criteria
- enumerators can submit records
- supervisors can accept/reject work
- submission evidence is stored and linked

### Watch-outs
- offline sync complexity
- oversized image uploads
- low-quality field data without review gates

---

## Phase 4 — Publication and reporting (Week 12-13)

### Build
- approve/publish address workflow
- verification endpoint
- coverage dashboard
- pending review backlog dashboard
- correction request intake

### Exit criteria
- official pilot addresses can be published
- ministry/admin users can verify records
- leadership can see pilot progress

---

## Phase 5 — Integrations and hardening (Week 14-16)

### Build
- scoped agency API access
- export jobs
- backup verification
- staging/training environment hardening
- performance tuning for pilot load
- audit review screens

### Exit criteria
- one or two approved institutions can consume verified data
- restores are tested
- production pilot runbook exists

---

## Workstreams in parallel

### Backend
- schema and migrations
- auth/RBAC
- registry services
- field workflow APIs
- reporting APIs

### Frontend
- admin portal shell
- registry management screens
- field-app screens
- review dashboards
- reporting views

### GIS / data
- boundary loading
- zone definitions
- road geometry ingestion
- building coordinate validation

### Ops
- environment provisioning
- CI/CD
- backups
- monitoring
- release controls

---

## Suggested backlog order
1. auth
2. territories
3. roads
4. buildings
5. addresses
6. field assignments
7. field submissions
8. review workflow
9. publication workflow
10. reporting
11. integrations
12. hardening

---

## Team recommendation
- 1 backend engineer
- 1 frontend engineer
- 1 GIS/data engineer
- 1 QA/product workflow owner
- 1 field-ops counterpart
- 1 government decision owner

---

## Definition of done for pilot
The pilot is done when:
- pilot zones are loaded
- field teams can capture and submit
- reviewers can approve and publish
- official records are searchable and verifiable
- exports/integration verification work for approved consumers
- backups, logs, and rollback steps are proven

---

## Plain-English summary
Build the foundation first, then the registry, then field ops, then publication, then integrations. If we try to do all of it in random order, the system turns cursed fast.
