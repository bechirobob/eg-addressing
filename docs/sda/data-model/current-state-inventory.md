# Current-State Inventory — NLI-WO-002

**Status:** Draft inventory for SDA review  
**Source of truth inspected:** executable migrations `000–007`, current API persistence/query/publication/geospatial functions, and governance documents.

## 1. Current executable schema tables

| Table | Current role | Authority class | Target disposition |
|---|---|---|---|
| `reference_data_loads` | Records loaded reference packages. | Operational metadata | Retain as reference-load ledger; align package authority and checksums. |
| `reference_data_load_history` | Historical reference-load records. | Audit/operational metadata | Retain with source authority fields. |
| `development_fixture_batches` | Controlled fixture batch ledger. | Non-production fixture metadata | Retain for dev/test only; never canonical. |
| `development_fixture_records` | Fixture record ownership ledger. | Non-production fixture metadata | Retain for cleanup/validation only. |
| `provinces` | Province code/name reference. | Reference geography | Fold into `administrative_unit` level `province`; preserve province-code compatibility. |
| `admin_units` | Generic hierarchy beneath provinces. | Reference geography | Normalize into controlled administrative hierarchy with type, source, effective dates. |
| `users` | Local pilot users. | Identity/operations | Outside location model except actor references. |
| `auth_tokens` | Local sessions. | Security/session | Outside location model. |
| `audit_logs` | Generic audit events. | Audit authority | Keep as global audit; canonical location events should reference audit/event model. |
| `territories` | Operational/routing areas and pilot areas. | Operational area, not legal geography | Replace/rename conceptually as `operational_area`; link to admin units. |
| `roads` | Road registry-ish operational records. | Candidate/canonical mixed | Split into `road`, `road_segment`, `road_name`, and candidate/evidence lifecycle. |
| `buildings` | Building records tied to road/territory. | Candidate/canonical mixed | Split into `addressable_object`, `building`, `entrance/access_point`. |
| `addresses` | Legacy structured address table. | Legacy address authority collision | Compatibility/source table during convergence; not second canonical authority. |
| `address_points` | Active point for legacy `addresses`. | Geometry evidence/canonical mixed | Migrate into geometry version model linked to canonical location record. |
| `address_corrections` | Public correction requests. | Evidence/workflow | Retain as correction/dispute cases linked to canonical record or candidate. |
| `citizen_geotag_submissions` | Public citizen intake and review lifecycle. | Candidate/evidence | Keep as intake/evidence source feeding canonical decision. |
| `address_records` | Current canonical case-file layer. | Current canonical registry anchor | Evolve into sole canonical location/address record authority. |
| `address_record_events` | Timeline for address records. | Audit/event | Retain/evolve into typed canonical event timeline. |
| `field_assignments` | Field work assignment. | Operational workflow | Keep operational; link evidence to candidate/canonical entities. |
| `field_submissions` | Field evidence/candidate records. | Evidence/workflow | Keep evidence; do not become canonical without approval event. |
| `import_jobs` | Import batch metadata. | Operational ingestion | Evolve into governed source package/job model. |
| `import_rows` | Imported row details. | Raw/source evidence | Preserve raw lineage; not canonical. |
| `publication_packs` | Publication/export grouping. | Publication workflow | Retain as publication release package; must target canonical records. |
| `publication_pack_addresses` | Pack to legacy address relation. | Publication workflow | Migrate to canonical record release items. |

## 2. Current canonical and publication behavior

Current implementation has three address-like authorities:

1. `addresses` with `public_code`, `publication_state`, and `verification_status`.
2. `citizen_geotag_submissions` with `grid_code`, review status, GPS, and optional publication state through `status`.
3. `address_records` with `address_code`, structured columns, `record_bundle`, and PostGIS `geom`.

NLI-WO-002 target: `address_records`/successor canonical registry concept becomes the sole canonical authority. `addresses` becomes compatibility/source legacy during transition. Citizen geotag rows remain candidate/evidence only.

## 3. Current geospatial behavior

- `address_records` has WGS84 `latitude`, `longitude`, optional `accuracy_meters`, and `geom geography(Point, 4326)` from migration `005`.
- `upsert_address_record_from_geotag` sets `geom` on insert/update using `ST_SetSRID(ST_MakePoint(longitude, latitude), 4326)::geography`.
- `find_nearby_address_records` uses `ST_DWithin` and `ST_Distance` over `geom`.
- `address_points` stores active points for legacy `addresses` as numeric WGS84 fields.
- Field submissions store `spatial_evidence` JSONB and may include point/line evidence but are not canonical geometry.

## 4. Current lifecycle collisions

The current system uses status strings across several meanings: intake state, field state, canonical readiness, public release, publication pack state, and verification status. Design target separates these into controlled state machines.

## 5. Source proposal usage

`docs/source-proposals/schema.sql` contains useful concepts: level-specific admin geography, roads/landmarks/parcels/buildings/units, address versions, status events, signage assets, agency clients, and audit logs. It is non-authoritative because it conflicts with existing migrations and would create a second canonical authority if copied wholesale.
