# National Digital Addressing Platform — Software Architecture Blueprint

**Goal:** Define a serious, scalable, government-grade software architecture for a National Digital Addressing System that supports address creation, validation, search, governance, field capture, mapping, and multi-agency integration.

**Architecture:** Use a **modular monolith** backed by **PostgreSQL + PostGIS**, with a **web admin platform**, **field capture application**, **integration API layer**, and **object storage** for field evidence. Start simple enough to ship a pilot, but structure the domains cleanly so the system can evolve into a larger national platform without a rewrite.

**Tech Stack:** Next.js + TypeScript (frontend), FastAPI (backend), PostgreSQL + PostGIS (data), Redis (cache/queue), S3-compatible object storage (media/files), Docker + reverse proxy for deployment.

---

## 1. Executive Summary

This platform should not be framed as a map website or a narrow software portal. It should be framed as a **national address registry and operational geospatial platform**.

The system must serve five core purposes:

1. Create and maintain the **official national address registry**.
2. Support **field capture and territorial verification**.
3. Provide **government workflow tools** for approval, correction, audit, and reporting.
4. Expose **trusted APIs and lookup services** to approved institutions.
5. Maintain enough **security, auditability, and operational discipline** to function as national infrastructure.

The software system should be designed to support the first pilot in Malabo and priority zones, but it must not paint itself into a corner technically. The pilot architecture should already reflect the shape of the eventual national platform.

---

## 2. Architecture Principles

### 2.1 Core design principles

- **Government owns the registry.** Vendors and contractors may support delivery, but the source of truth remains under government control.
- **Data model before visuals.** A pretty map with a weak registry is useless.
- **Modular monolith first.** Avoid premature microservices.
- **Offline-aware field operations.** The territory will not behave like a perfect office network.
- **Auditability is mandatory.** Every important change must be attributable.
- **Integrations come in layers.** Do not try to connect every ministry on day one.
- **Security by default.** Access should be role-based and logged.
- **Pilot-first, national-ready.** The first release proves the operating model; it is not a toy prototype.

### 2.2 Why modular monolith

A modular monolith is the best starting point because it gives:

- faster delivery for a pilot
- easier debugging and deployment
- lower operational complexity
- cleaner schema evolution
- less coordination overhead for a small initial team

Later, if usage or organizational scale demands it, specific modules can be extracted into standalone services.

---

## 3. System Context

### 3.1 High-level users

The platform serves several user groups:

- national registry administrators
- Ministry of Transportation and other lead agencies
- municipalities / district validators
- field enumerators
- field supervisors / QA reviewers
- helpdesk / correction desk staff
- approved institutional API consumers
- eventual public lookup users

### 3.2 Context diagram

```text
Field Enumerators / Supervisors
            |
            v
   Field Capture Application
            |
            v
   API Backend / Workflow Layer
            |
            v
 PostgreSQL + PostGIS + Object Storage
            |
   -------------------------------
   |              |              |
   v              v              v
Admin Portal   Reporting      Integration APIs
   |                              |
   v                              v
Government Users        Postal / Emergency / Utilities /
                        Planning / Land / Approved Partners
```

---

## 4. Logical Architecture

The recommended platform has **five software layers**.

### 4.1 Presentation layer

This includes all user-facing applications.

#### Components
- **Admin Portal** — for central government and authorized agency users
- **Field Capture App** — for enumerators and supervisors
- **Supervisor / QA Dashboard** — for review and approval workflows
- **Public / Institutional Lookup Portal** — for approved search and verification use cases

#### Recommendations
- Build with **Next.js + TypeScript**
- Use responsive web UI patterns
- Make field tooling a **PWA/mobile web app** first
- Use shared design tokens and shared auth/session model

### 4.2 Application layer

This is the backend platform that implements core business logic.

#### Recommended domains/modules
- **Auth & RBAC module**
- **Territory hierarchy module**
- **Address registry module**
- **Street naming & numbering rules module**
- **Field capture & sync module**
- **Approval / workflow module**
- **Search & verification module**
- **Map query / geospatial module**
- **Reporting & exports module**
- **Integration API module**
- **Audit & activity log module**
- **Notification module**

#### Backend recommendation
- **FastAPI** as the main backend
- One codebase with clean domain separation
- Internal services/modules inside the same application
- Background worker process for async tasks

### 4.3 Data layer

This holds structured and geospatial data.

#### Core technologies
- **PostgreSQL** for relational data
- **PostGIS** for spatial data
- **Redis** for caching, queue support, and ephemeral workflow state if needed
- **Object storage** for field photos, scanned documents, and export files

### 4.4 Integration layer

This exposes controlled access to external and institutional systems.

#### Integration targets
- postal systems
- emergency dispatch systems
- utility systems
- land / cadastre systems
- planning / permit systems
- tax systems
- approved private-sector consumers

#### Integration patterns
- REST APIs first
- API key / scoped token access
- audit logging for every integration client
- batch import/export where real-time integration is not ready

### 4.5 Infrastructure / operations layer

This keeps the platform alive and observable.

#### Components
- reverse proxy (Nginx or Caddy)
- Dockerized app services
- monitoring and logging stack
- backup automation
- scheduled jobs
- CI/CD pipeline
- secrets management
- SSL/TLS termination

---

## 5. Core Application Modules

### 5.1 Auth and access control

#### Responsibilities
- login/session management
- role-based permissions
- API credential issuance
- audit of privileged actions

#### Key roles
- `super_admin`
- `national_registry_admin`
- `ministry_reviewer`
- `municipal_validator`
- `field_supervisor`
- `enumerator`
- `helpdesk_agent`
- `agency_readonly`
- `api_client`

### 5.2 Territory hierarchy

#### Responsibilities
- define provinces, districts, municipalities, sectors, zones
- map spatial boundaries
- attach addresses and roads to administrative hierarchy
- support phased rollout by zone

### 5.3 Address registry

#### Responsibilities
- store official address records
- manage address formats and codes
- preserve version history
- track approval status and validity
- link addresses to buildings, plots, roads, and zones

### 5.4 Street naming and numbering engine

#### Responsibilities
- apply numbering conventions
- handle edge cases like compounds, corner plots, apartment blocks, and commercial floors
- generate official address strings
- generate short codes / reference codes if required
- track naming proposals and approvals

### 5.5 Field operations module

#### Responsibilities
- create assignments by zone
- capture GPS coordinates, forms, photos, and notes
- support offline storage and delayed sync
- enable supervisor review and rejection/correction
- track enumerator productivity and QA issues

### 5.6 Search and verification

#### Responsibilities
- full-text address search
- filtered search by province, district, road, code, building, status
- reverse lookup by coordinate
- verify whether an address is official / pending / disputed / retired
- support print-proof and lookup workflows later

### 5.7 Workflow and approvals

#### Responsibilities
- move records through states
- require human approval before publication
- support appeals, corrections, and resubmissions
- track reason codes for rejection or correction

### 5.8 Reporting and exports

#### Responsibilities
- coverage dashboards
- productivity metrics
- verification backlog
- unresolved disputes
- zone progress reports
- export approved data for agencies

### 5.9 Integration API module

#### Responsibilities
- expose search and verification endpoints
- expose address details to approved systems
- support bulk agency imports / reconciliation
- support future citizen and commercial integrations under approval

### 5.10 Audit module

#### Responsibilities
- log who changed what and when
- retain before/after values for critical changes
- record API client activity
- support compliance review and incident response

---

## 6. Data Architecture

This is the most important part of the whole system.

### 6.1 Core entities

The first serious schema should include at least:

- `countries`
- `provinces`
- `districts`
- `municipalities`
- `zones`
- `roads`
- `landmarks`
- `parcels`
- `buildings`
- `building_units`
- `addresses`
- `address_versions`
- `address_status_events`
- `field_assignments`
- `field_submissions`
- `submission_photos`
- `verification_events`
- `correction_requests`
- `signage_assets`
- `agency_clients`
- `api_credentials`
- `audit_logs`
- `users`
- `roles`
- `user_role_assignments`

### 6.2 Key data relationships

```text
Province -> District -> Municipality -> Zone
Zone -> Roads / Parcels / Buildings
Road -> Addresses
Building -> Address
Building -> Building Units
Address -> Verification Events
Address -> Status History
Field Submission -> Building / Road / Zone / Photos
Correction Request -> Address
Signage Asset -> Road / Zone / Address Group
Audit Log -> User / Entity / Action
```

### 6.3 Spatial requirements

Use PostGIS for:

- zone polygons
- district boundaries
- road geometry
- building points or polygons
- parcel polygons where available
- geospatial search
- distance-based duplicate checks
- map rendering support

### 6.4 Address lifecycle states

Recommended base states:

- `draft`
- `submitted`
- `under_review`
- `approved`
- `published`
- `disputed`
- `corrected`
- `retired`

Not every record must use every state, but the lifecycle must be explicit.

---

## 7. API Architecture

### 7.1 Internal APIs

Internal APIs are used by the admin portal and field app.

#### Key endpoint domains
- `/auth/*`
- `/territories/*`
- `/roads/*`
- `/buildings/*`
- `/addresses/*`
- `/field/*`
- `/workflows/*`
- `/reports/*`
- `/audits/*`
- `/integrations/*`

### 7.2 External APIs

Approved agencies and systems should get scoped access.

#### Likely external functions
- verify official address
- fetch official address by code
- reverse lookup by coordinate
- retrieve administrative metadata
- query approved address lists by zone
- submit reconciliation file or integration request

### 7.3 API standards

- version APIs from the start
- paginate all list endpoints
- require auth for all non-public endpoints
- log every export and privileged lookup
- apply rate limits
- validate all inputs

---

## 8. Field Capture Architecture

This is where the special-grade risk lives.

### 8.1 Field app requirements

The field app must support:

- offline capture
- draft save on device
- coordinate capture
- image upload
- zone assignment
- sync retries
- validation feedback
- supervisor comments

### 8.2 Sync model

#### Recommended sync pattern
- field user captures draft locally
- local queue stores unsynced changes
- sync runs when connection is available
- backend validates payload
- backend assigns status and logs event
- conflicts or duplicates go to review queue

### 8.3 Supervisor workflows

Supervisors should be able to:

- review recent submissions
- reject low-quality captures
- request correction
- approve for central validation
- track team progress by zone

---

## 9. Security Architecture

### 9.1 Core controls

- RBAC everywhere
- TLS everywhere
- encrypted backups
- password hashing with modern algorithm
- short-lived sessions for privileged users
- API credential scoping
- upload validation for media files
- full audit trail for changes and exports

### 9.2 Sensitive operations

These actions should be privileged and auditable:

- final address approval
- territory boundary edits
- road naming approval
- numbering-rule changes
- bulk data imports
- bulk exports
- user role changes
- API client provisioning

### 9.3 Future controls

As the platform matures, add:

- MFA for high-privilege roles
- SSO with government identity if available
- IP restrictions for sensitive admin interfaces
- approval dual-control for critical exports or mass changes

---

## 10. Deployment Blueprint

### 10.1 Pilot deployment model

For the first serious pilot, use a controlled VM/container stack.

#### Recommended pilot components
- `web-frontend` container
- `api-backend` container
- `worker` container
- `postgres-postgis` service
- `redis` service
- `object-storage` or managed equivalent
- reverse proxy with TLS

### 10.2 Environment model

At minimum:

- `dev`
- `staging`
- `production`

Recommended additions:

- `training`
- `demo/pilot-sandbox`

### 10.3 Deployment topology

```text
Internet / Internal Government Network
                |
                v
        Reverse Proxy / TLS
                |
      ------------------------
      |          |           |
      v          v           v
 Frontend      Backend     Worker
                  |
         -------------------
         |        |        |
         v        v        v
   PostgreSQL   Redis   Object Storage
     + PostGIS
```

### 10.4 Scaling path

#### Early pilot
- single VM or small cluster
- daily backups
- manual failover procedures documented

#### Growth stage
- split DB and app workloads
- introduce read replicas if needed
- strengthen monitoring and alerting
- formalize restore drills

#### National scale
- HA database strategy
- stronger DR posture
- regional failover planning if justified
- tighter network controls and operational segregation

---

## 11. Observability and Operations

### 11.1 Logging

Use structured logs for:

- API requests
- auth events
- workflow actions
- sync failures
- file uploads
- export jobs
- background jobs

### 11.2 Metrics

Track:

- total addresses captured
- approved vs pending addresses
- duplicate rate
- field sync success/failure
- average approval time
- correction backlog
- system uptime
- API response time
- active users by role
- zone coverage progress

### 11.3 Alerts

Set alerts for:

- DB health issues
- backup failures
- repeated sync failures
- worker queue backlog
- suspicious admin activity
- API abuse or spikes
- storage errors

---

## 12. Rollout Plan by Software Phase

### Phase 0 — Discovery and standard design

**Purpose:** Define the rules before code spreads bad assumptions.

#### Outputs
- address standard
- numbering policy
- territory model
- role model
- data dictionary
- pilot scope
- integration shortlist

### Phase 1 — Pilot MVP

**Purpose:** Build the minimum serious operational platform.

#### Build first
- auth/RBAC
- territory hierarchy
- road/building/address schema
- field capture app
- approval workflow
- search and verification
- basic map views
- audit logs
- basic reporting

### Phase 2 — Pilot hardening

**Purpose:** Make the MVP durable enough for real field operations.

#### Add
- offline sync improvement
- duplicate detection rules
- correction request workflow
- export tooling
- better dashboards
- supervisor QA tooling
- signage asset tracking

### Phase 3 — Institutional onboarding

**Purpose:** Connect the platform to government operations.

#### Add
- ministry/admin workflows
- emergency lookup patterns
- postal and utility API support
- reconciliation imports
- agency user management

### Phase 4 — National scale preparation

**Purpose:** Prove the platform can grow beyond the initial pilot geography.

#### Add
- stronger DR posture
- training environment
- performance tuning
- data lifecycle controls
- advanced reporting
- operational SOPs and maintenance tooling

---

## 13. What Not to Do Early

Avoid these traps:

- do not build microservices from day one
- do not start with a public-open API
- do not make the registry dependent on spreadsheets as source of truth
- do not overbuild GIS complexity before the pilot validates workflows
- do not integrate every ministry in phase 1
- do not skip audit logging
- do not treat offline sync as an afterthought

---

## 14. Ownership Model for the Software Team

If you are handling the software infrastructure, your likely responsibility stack is:

### Your lane
- architecture definition
- backend service design
- database architecture
- deployment model
- security model
- integration strategy
- workflow engine structure
- observability and operational readiness

### Other lanes to coordinate with
- legal/policy owners for standards and authority
- GIS/data collection leads
- field operations leadership
- ministry stakeholders
- signage / physical rollout teams
- hosting / ops administrators

---

## 15. Recommended Immediate Technical Deliverables

These are the best next artifacts to produce after this blueprint:

1. **Entity Relationship Model (ERM)**
2. **Role & Permission Matrix**
3. **Pilot MVP Scope Document**
4. **API Surface Definition**
5. **Deployment & Environment Specification**
6. **Field Sync and Conflict Resolution Spec**

---

## 16. Final Recommendation

The strongest technical starting posture is:

| Layer | Recommendation |
|---|---|
| Frontend | Next.js + TypeScript |
| Backend | FastAPI |
| Database | PostgreSQL + PostGIS |
| Media/File Storage | S3-compatible object storage |
| Cache / Queue | Redis |
| Job Processing | Worker service |
| Architecture style | Modular monolith |
| Deployment | Dockerized services behind reverse proxy |
| Mapping UI | MapLibre or Leaflet |
| Security baseline | RBAC + audit logs + scoped integrations |

This gives you a serious build path without overengineering the first release.

---

## 17. Plain-English Answer You Can Say Out Loud

If somebody asks you, *“So what is the software infrastructure going to look like?”*, the clean answer is:

> The platform will be built as a government-owned national address registry and geospatial operations system. It will have a central database with map support, a backend API layer, an admin portal for approvals and reporting, a field app for territorial capture and verification, and controlled integrations for agencies like transport, emergency services, utilities, and planning. We’ll start with a pilot-ready modular architecture that is secure, auditable, and able to scale into a national platform.

That’s the line.
