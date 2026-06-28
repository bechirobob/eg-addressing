# National Digital Addressing Platform — Role & Permission Matrix

**Purpose:** Define who can do what inside the national digital addressing platform so the system is governable, secure, and auditable.

---

## 1. Design Principles

- Every access right should be granted by role, not ad hoc habit.
- Sensitive actions must be limited, logged, and reviewable.
- Field users should only see the territory and tasks assigned to them.
- No single low-level operator should be able to silently alter official published records.
- Read access and write access must be clearly separated.

---

## 2. Primary Roles

| Role Code | Role Name | Primary Purpose |
|---|---|---|
| `super_admin` | Platform Super Administrator | Technical ownership, environment control, highest emergency authority |
| `national_registry_admin` | National Registry Administrator | Owns official registry publication and data governance |
| `ministry_reviewer` | Ministry Reviewer | Reviews and approves policy/operational records at ministry level |
| `municipal_validator` | Municipal Validator | Validates local records and territorial correctness |
| `field_supervisor` | Field Supervisor | Oversees enumerators and quality control |
| `enumerator` | Field Enumerator | Captures data in the territory |
| `helpdesk_agent` | Helpdesk / Corrections Agent | Receives and processes correction requests |
| `agency_readonly` | Agency Read-Only User | Searches and views approved records |
| `api_client` | API Client Identity | Machine access for approved systems |
| `auditor` | Audit/Compliance User | Reads logs, exports, and activity evidence without operational edit rights |

---

## 3. Permission Domains

Permissions should be grouped by domain:

1. **User & access administration**
2. **Territory administration**
3. **Road / naming administration**
4. **Building and address management**
5. **Field operations**
6. **Workflow / approvals**
7. **Correction handling**
8. **Reporting & exports**
9. **Integration/API management**
10. **Audit & compliance**
11. **Environment / platform operations**

---

## 4. High-Level Permission Matrix

Legend:
- `Y` = allowed
- `L` = limited / scoped only
- `N` = not allowed
- `A` = allowed with explicit approval workflow or dual review

| Capability | Super Admin | National Registry Admin | Ministry Reviewer | Municipal Validator | Field Supervisor | Enumerator | Helpdesk | Agency Readonly | API Client | Auditor |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Create users | Y | L | N | N | N | N | N | N | N | N |
| Assign roles | Y | L | N | N | N | N | N | N | N | N |
| Suspend users | Y | L | N | N | N | N | N | N | N | N |
| Edit territory boundaries | A | A | L | L | N | N | N | N | N | N |
| Create road records | Y | Y | L | L | L | L | N | N | N | N |
| Approve official road names | A | Y | A | L | N | N | N | N | N | N |
| Create building records | Y | Y | L | L | L | L | N | N | N | N |
| Submit address candidates | Y | Y | L | L | L | L | N | N | N | N |
| Approve official addresses | A | Y | A | L | N | N | N | N | N | N |
| Publish official addresses | A | Y | A | N | N | N | N | N | N | N |
| Retire/dispute official addresses | A | Y | A | L | N | N | L | N | N | Y |
| Create field assignments | Y | Y | L | L | Y | N | N | N | N | N |
| Submit field captures | Y | Y | L | L | Y | Y | N | N | N | N |
| Review field captures | Y | Y | L | L | Y | N | N | N | N | Y |
| Reject / return field work | Y | Y | L | L | Y | N | N | N | N | Y |
| Process correction requests | Y | Y | L | L | L | N | Y | N | N | Y |
| Search approved records | Y | Y | Y | Y | Y | L | Y | Y | Scoped | Y |
| Export approved data | A | A | L | L | N | N | L | N | Scoped | Y |
| Create API clients | Y | L | N | N | N | N | N | N | N | N |
| Rotate/revoke API credentials | Y | L | N | N | N | N | N | N | N | N |
| View audit logs | Y | Y | L | N | N | N | N | N | N | Y |
| Manage deployments / environments | Y | N | N | N | N | N | N | N | N | N |

---

## 5. Detailed Role Definitions

## 5.1 Super Admin

### Purpose
Technical and operational platform owner with emergency authority.

### Allowed actions
- create/suspend users
- assign roles
- configure environment-level settings
- manage integrations and credentials
- override workflow in exceptional circumstances
- view all audit logs
- manage backups, deployment, and incident response

### Restrictions
- should not routinely perform normal address approvals unless necessary
- all privileged actions must be audited

---

## 5.2 National Registry Admin

### Purpose
Owns the official address registry and publication process.

### Allowed actions
- manage official address records
- approve and publish official addresses
- approve/retire disputed records
- manage numbering rules and address formatting
- review territory and naming changes
- authorize data exports at registry level

### Restrictions
- no direct infrastructure management
- major boundary changes should still require workflow control and evidence

---

## 5.3 Ministry Reviewer

### Purpose
Provides ministry-level approval/review on sensitive records, policies, or strategic workflows.

### Allowed actions
- review official address approval batches
- review strategic naming or territorial decisions
- view reports and dashboards
- approve certain sensitive changes where workflow requires it

### Restrictions
- should not perform general low-level editing
- should not manage user accounts or environments

---

## 5.4 Municipal Validator

### Purpose
Validates local correctness and territorial reality.

### Allowed actions
- review roads/buildings/addresses in assigned municipality
- validate local naming and numbering proposals
- flag errors or disputes
- review correction requests within scope

### Restrictions
- cannot globally publish national records
- cannot edit outside assigned scope

---

## 5.5 Field Supervisor

### Purpose
Runs day-to-day field operations.

### Allowed actions
- create or manage enumerator assignments in scoped zones
- review submissions
- request correction from enumerators
- approve submissions into higher review stage
- track productivity and quality metrics

### Restrictions
- cannot publish official addresses
- cannot alter high-level standards

---

## 5.6 Enumerator

### Purpose
Captures field data on the territory.

### Allowed actions
- view assigned zones/tasks
- create draft field submissions
- upload photos and evidence
- resubmit corrected work
- view own submission status

### Restrictions
- cannot approve records
- cannot export registry data
- cannot edit work outside assignment scope

---

## 5.7 Helpdesk Agent

### Purpose
Handles corrections and support requests from citizens/agencies.

### Allowed actions
- log correction requests
- categorize issues
- assign requests for review
- communicate status internally
- view approved records needed to process tickets

### Restrictions
- cannot directly publish official record changes without workflow

---

## 5.8 Agency Read-Only User

### Purpose
Authorized institutional viewer.

### Allowed actions
- search approved official records
- view approved address details in scope
- view verification status where permitted

### Restrictions
- no editing
- no workflow actions
- no privileged exports without approval

---

## 5.9 API Client

### Purpose
Machine-to-machine integration identity.

### Allowed actions
- call specific scoped endpoints
- retrieve only authorized data classes
- submit integration-specific reconciliation payloads if permitted

### Restrictions
- no UI login
- no unrestricted read access
- all calls rate-limited and audited

---

## 5.10 Auditor

### Purpose
Independent oversight and compliance review.

### Allowed actions
- read audit logs
- inspect workflow histories
- review export events
- review approval histories and access changes

### Restrictions
- no operational editing
- no environment management

---

## 6. Sensitive Actions Requiring Elevated Control

These actions should require additional safeguards:

- official publication of address batches
- mass retirement or correction of addresses
- boundary edits
- numbering-rule changes
- bulk data imports
- bulk exports
- API client creation
- role assignment to privileged roles
- user suspension at national level

### Recommended controls
- explicit approval workflow
- dual-review for high-impact changes
- mandatory reason/comment entry
- immutable audit log entry

---

## 7. Scope Model

Roles should support territorial scoping.

### Scope examples
- national
- province
- district
- municipality
- zone

A municipal validator in Malabo should not automatically gain authority in Bata.

---

## 8. Implementation Guidance

## 8.1 Recommended permission model
Use:

- **roles** for broad authority groupings
- **scoped assignments** for territorial boundaries
- **policy checks** at API/service layer
- **audit logging** for every privileged action

## 8.2 Minimal permission keys
Suggested permission families:

- `users.manage`
- `roles.assign`
- `territories.edit`
- `roads.create`
- `roads.approve`
- `buildings.manage`
- `addresses.submit`
- `addresses.approve`
- `addresses.publish`
- `field.assign`
- `field.submit`
- `field.review`
- `corrections.process`
- `reports.view`
- `exports.run`
- `api_clients.manage`
- `audit.view`
- `platform.manage`

---

## 9. Pilot Recommendation

For the first pilot, you can launch with these real working roles:

- super_admin
- national_registry_admin
- municipal_validator
- field_supervisor
- enumerator
- helpdesk_agent
- agency_readonly
- api_client

You can add ministry_reviewer and auditor workflows as governance hardens.

---

## 10. Plain-English Summary

The permission model should make sure that the people capturing data are not the same people silently publishing national records, and the people viewing the system are not automatically allowed to export or rewrite it. That separation is what keeps the platform trustworthy.
