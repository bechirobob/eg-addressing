# National Digital Addressing Platform — Entity Relationship Model (ERM)

**Purpose:** Define the core data model for the national digital addressing platform so software, workflow, and integration teams operate against one shared structure.

**Database Recommendation:** PostgreSQL + PostGIS

---

## 1. Modeling Principles

- The **address** is the official published output, but it is derived from deeper territorial and building data.
- Spatial records must support both **point** and **polygon** geometries where available.
- Administrative hierarchy must be explicit and queryable.
- Every critical operational record should support **status history** and **auditability**.
- The system must distinguish between **captured data**, **approved data**, and **published official data**.

---

## 2. Core Domain Areas

The model is split into these logical domains:

1. **Identity & Access**
2. **Administrative Geography**
3. **Physical Network / Territory**
4. **Address Registry**
5. **Field Operations**
6. **Workflow & Verification**
7. **Signage & Asset Tracking**
8. **Integration & API Access**
9. **Audit & Reporting**

---

## 3. Core Entities

## 3.1 Identity & Access

### `users`
Stores all human platform users.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| full_name | text | User display name |
| email | text unique | Login/email identity |
| phone | text nullable | Optional secondary contact |
| password_hash | text | Secure credential hash |
| status | enum | active, suspended, invited, archived |
| created_at | timestamptz | Creation time |
| updated_at | timestamptz | Last update |

### `roles`
Role catalog.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| code | text unique | e.g. `super_admin` |
| name | text | Human-friendly name |
| description | text | Role purpose |

### `user_role_assignments`
Many-to-many link between users and roles.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| user_id | UUID FK -> users.id | User |
| role_id | UUID FK -> roles.id | Role |
| scope_type | text nullable | national, province, district, zone |
| scope_id | UUID nullable | Scoped territory if applicable |
| assigned_at | timestamptz | When assigned |
| assigned_by | UUID FK -> users.id | Assigning admin |

---

## 3.2 Administrative Geography

### `countries`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| code | text unique | Country code |
| name | text | Country name |

### `provinces`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| country_id | UUID FK -> countries.id | Parent country |
| code | text unique | Province code |
| name | text | Province name |
| geom | geometry(MultiPolygon) | Spatial boundary |

### `districts`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| province_id | UUID FK -> provinces.id | Parent province |
| code | text unique | District code |
| name | text | District name |
| geom | geometry(MultiPolygon) | Spatial boundary |

### `municipalities`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| district_id | UUID FK -> districts.id | Parent district |
| code | text unique | Municipality code |
| name | text | Municipality name |
| geom | geometry(MultiPolygon) | Spatial boundary |

### `zones`
Operational rollout units and neighborhood/service sectors.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| municipality_id | UUID FK -> municipalities.id | Parent municipality |
| code | text unique | Zone code |
| name | text | Zone name |
| zone_type | text | neighborhood, sector, pilot-zone, etc. |
| rollout_status | enum | planned, active, paused, completed |
| geom | geometry(MultiPolygon) | Spatial boundary |

---

## 3.3 Physical Network / Territory

### `roads`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| zone_id | UUID FK -> zones.id | Operational zone |
| road_code | text unique | Internal reference code |
| official_name | text nullable | Approved road/street name |
| provisional_name | text nullable | Pre-approval name |
| road_type | text | avenue, street, lane, boulevard, etc. |
| naming_status | enum | proposed, under_review, approved, retired |
| geom | geometry(MultiLineString) | Road geometry |

### `landmarks`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| zone_id | UUID FK -> zones.id | Parent zone |
| name | text | Landmark name |
| landmark_type | text | school, hospital, market, ministry, etc. |
| geom | geometry(Point) | Coordinate |

### `parcels`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| zone_id | UUID FK -> zones.id | Parent zone |
| parcel_ref | text nullable | Cadastre/parcel reference |
| ownership_status | text nullable | Optional land-state metadata |
| geom | geometry(MultiPolygon) | Parcel geometry |

### `buildings`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| zone_id | UUID FK -> zones.id | Parent zone |
| parcel_id | UUID nullable FK -> parcels.id | Optional parcel link |
| primary_road_id | UUID nullable FK -> roads.id | Main fronting road |
| building_type | text | residential, commercial, mixed, public |
| building_name | text nullable | Optional named building |
| floor_count | integer nullable | Optional |
| occupancy_status | text nullable | occupied, vacant, under_construction |
| geom | geometry(Point or Polygon) | Building location |

### `building_units`
For apartments, shops, offices, suites, etc.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| building_id | UUID FK -> buildings.id | Parent building |
| unit_code | text | Unit reference |
| unit_type | text | apartment, suite, shop, office |
| floor_label | text nullable | Floor/level |
| status | enum | draft, approved, retired |

---

## 3.4 Address Registry

### `addresses`
The official or candidate address record.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| building_id | UUID nullable FK -> buildings.id | Linked building |
| building_unit_id | UUID nullable FK -> building_units.id | Linked unit |
| road_id | UUID nullable FK -> roads.id | Linked road |
| zone_id | UUID FK -> zones.id | Parent zone |
| address_code | text unique | Official short/reference code |
| address_line_1 | text | Primary formatted address |
| address_line_2 | text nullable | Secondary formatted line |
| numbering_value | text | Main number/identifier |
| postal_code | text nullable | If policy applies |
| status | enum | draft, submitted, approved, published, disputed, retired |
| is_official | boolean | Official publication flag |
| published_at | timestamptz nullable | Publication time |

### `address_versions`
History of substantive changes.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| address_id | UUID FK -> addresses.id | Parent address |
| version_no | integer | Incrementing version |
| snapshot_json | jsonb | Address snapshot |
| change_reason | text | Why it changed |
| changed_by | UUID FK -> users.id | Actor |
| changed_at | timestamptz | Change time |

### `address_status_events`
Tracks lifecycle transitions.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| address_id | UUID FK -> addresses.id | Address |
| from_status | text nullable | Previous status |
| to_status | text | New status |
| note | text nullable | Context |
| acted_by | UUID FK -> users.id | User |
| acted_at | timestamptz | Event time |

---

## 3.5 Field Operations

### `field_assignments`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| zone_id | UUID FK -> zones.id | Assigned zone |
| assigned_user_id | UUID FK -> users.id | Enumerator/supervisor |
| assignment_type | text | survey, review, QA, signage-check |
| status | enum | assigned, active, completed, cancelled |
| starts_at | timestamptz nullable | Optional |
| ends_at | timestamptz nullable | Optional |

### `field_submissions`
Raw or semi-structured field captures.

| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| assignment_id | UUID FK -> field_assignments.id | Parent assignment |
| submitted_by | UUID FK -> users.id | Enumerator |
| zone_id | UUID FK -> zones.id | Zone |
| building_id | UUID nullable FK -> buildings.id | Linked building if matched |
| road_id | UUID nullable FK -> roads.id | Linked road if matched |
| payload_json | jsonb | Captured form payload |
| gps_geom | geometry(Point) | Captured coordinate |
| sync_status | enum | local_only, synced, failed, conflicted |
| review_status | enum | draft, submitted, accepted, rejected, needs_correction |
| submitted_at | timestamptz | Submission time |

### `submission_photos`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| field_submission_id | UUID FK -> field_submissions.id | Parent submission |
| storage_key | text | Object storage path |
| photo_type | text | frontage, sign, landmark, evidence |
| captured_at | timestamptz nullable | Photo time |

---

## 3.6 Workflow & Verification

### `verification_events`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| address_id | UUID nullable FK -> addresses.id | Optional linked address |
| field_submission_id | UUID nullable FK -> field_submissions.id | Optional source submission |
| verification_type | text | field, desk, supervisor, agency |
| outcome | enum | passed, failed, disputed, escalated |
| note | text nullable | Notes |
| verified_by | UUID FK -> users.id | Reviewer |
| verified_at | timestamptz | Event time |

### `correction_requests`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| address_id | UUID FK -> addresses.id | Target address |
| requester_type | text | citizen, agency, internal |
| requester_name | text nullable | Requester name |
| requester_contact | text nullable | Contact channel |
| issue_type | text | typo, wrong-road, wrong-number, duplicate, etc. |
| description | text | Request detail |
| status | enum | submitted, under_review, approved, rejected, resolved |
| created_at | timestamptz | Creation time |
| resolved_at | timestamptz nullable | Resolution time |

---

## 3.7 Signage & Asset Tracking

### `signage_assets`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| zone_id | UUID FK -> zones.id | Parent zone |
| road_id | UUID nullable FK -> roads.id | Related road |
| address_id | UUID nullable FK -> addresses.id | Optional linked address/group |
| asset_type | text | street-sign, zone-marker, building-number-plate |
| asset_code | text unique | Asset identifier |
| install_status | enum | planned, fabricated, installed, damaged, replaced |
| storage_or_vendor_ref | text nullable | Vendor / batch ref |
| geom | geometry(Point) | Installed location |

---

## 3.8 Integration & API Access

### `agency_clients`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| name | text | Agency/client name |
| agency_type | text | ministry, utility, emergency, private |
| status | enum | active, paused, revoked |
| contact_name | text nullable | Primary contact |
| contact_email | text nullable | Contact email |

### `api_credentials`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| agency_client_id | UUID FK -> agency_clients.id | Parent client |
| credential_hash | text | Stored securely |
| scope_json | jsonb | Allowed endpoints/scope |
| status | enum | active, rotated, revoked |
| created_at | timestamptz | Issued time |
| expires_at | timestamptz nullable | Optional expiry |

---

## 3.9 Audit & Reporting

### `audit_logs`
| Field | Type | Notes |
|---|---|---|
| id | UUID PK | Primary key |
| actor_user_id | UUID nullable FK -> users.id | Human actor |
| actor_client_id | UUID nullable FK -> agency_clients.id | API actor |
| entity_type | text | address, road, user, export, etc. |
| entity_id | UUID nullable | Entity identifier |
| action | text | create, update, approve, export, etc. |
| before_json | jsonb nullable | Pre-change state |
| after_json | jsonb nullable | Post-change state |
| ip_address | inet nullable | Source IP |
| created_at | timestamptz | Event time |

---

## 4. Critical Relationships Summary

```text
Country -> Province -> District -> Municipality -> Zone
Zone -> Road / Landmark / Parcel / Building / SignageAsset / FieldAssignment
Parcel -> Building
Road -> Building (primary relationship)
Building -> BuildingUnit
Building / BuildingUnit / Road / Zone -> Address
Address -> AddressVersion / AddressStatusEvent / VerificationEvent / CorrectionRequest
FieldAssignment -> FieldSubmission
FieldSubmission -> SubmissionPhoto / VerificationEvent
AgencyClient -> APICredential
User / AgencyClient -> AuditLog
```

---

## 5. Recommended Indexes

At minimum, create indexes on:

- all foreign keys
- `addresses.address_code`
- `addresses.status`
- `roads.official_name`
- `zones.code`
- `field_submissions.sync_status`
- `correction_requests.status`
- `audit_logs.created_at`
- PostGIS spatial indexes on all geometry columns

Use trigram/full-text support later for fuzzy address search if needed.

---

## 6. ERM Notes for Pilot Scope

For the first pilot, these tables are **must-have**:

- users
- roles
- user_role_assignments
- provinces
- districts
- municipalities
- zones
- roads
- buildings
- addresses
- address_versions
- field_assignments
- field_submissions
- submission_photos
- verification_events
- correction_requests
- agency_clients
- api_credentials
- audit_logs

These can be introduced in the second wave if needed:

- parcels
- building_units
- landmarks
- signage_assets
- advanced export / reporting materializations

---

## 7. Plain-English Summary

The data model should treat the **address** as the official published record, but the platform must also store the territory, roads, buildings, field evidence, workflow state, and audit trail underneath it. That is what makes the system a real national registry instead of a spreadsheet with map pins.
