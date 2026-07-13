# API Projection Map

**Status:** Draft for SDA review

## 1. Current route groups

| Current route group | Current source | Target projection |
|---|---|---|
| `/api/v1/public/address-code/{code}` | `address_codes.py`, `public_address_code_record_lookup`, `address_records`, geotag fallback, legacy `addresses`. | Public code projection from canonical `location_record` plus release state. Geotag/legacy fallback removed after convergence. |
| `/api/v1/public/address-code/{code}/record` | Current public code record lookup. | Same public projection, redacted by publication release. |
| `/api/v1/public/verification/{query}` | Legacy `addresses` where publication_state=`published`. | Public verification projection from canonical release. |
| `/api/v1/public/geotag-submissions` | `citizen_geotag_submissions`. | Candidate intake API; remains non-canonical. |
| `/api/v1/public/tracking/{lookup_code}` | geotag/candidate tracking. | Candidate tracking projection with no canonical/public leak. |
| `/api/v1/address-records/search` | `address_records`. | Operator registry search over canonical records. |
| `/api/v1/address-records/{address_code}` | `address_records` case file. | Protected canonical case-file projection. |
| `/api/v1/address-records/nearby` | `address_records.geom`. | Protected/controlled spatial query; public version requires release policy. |
| `/api/v1/address-records/export` | `address_record_export`. | Publication/export projection filtered by release item and classification. |
| `/api/v1/signage/export` / `pack` | `address_records` export with published status. | Signage projection from publication release items only. |
| `/api/v1/publication/packs` | `publication_packs`, legacy `addresses`. | Publication release workflow targeting canonical records. |
| `/api/v1/geotag-submissions/.../publish` | geotag status -> `published`, upsert `address_records`. | Future release workflow must separate canonical approval from public release. |

## 2. API contract rule for WO-002

This phase changes no routes, OpenAPI, generated types, or runtime contract. It documents target projections for later implementation.

## 3. Projection classes

| Projection | Fields allowed | Fields forbidden by default |
|---|---|---|
| Public lookup | public code, released label, approved coarse/precise location, public status. | citizen contact, DIP, evidence objects, reviewer notes, unpublished geometry, operational routing internals. |
| Operator case file | canonical fields, source/provenance, evidence metadata, state history. | secrets, full identity docs unless separately authorized. |
| Partner API | approved subset by partner scope/release. | unrestricted case file, internal notes, unrelated records. |
| Publication/signage | released code, label, signage text, approved geometry/area. | unpublished candidates and internal registry-only rows. |
| Audit/evidence | event and evidence metadata for authorized users. | public access. |

## 4. Transition compatibility

During expand–migrate–contract, existing routes may continue to read legacy tables through compatibility views/adapters, but the target authority must be canonical `location_record`/`address_records` successor. No endpoint should choose between multiple authorities without explicit precedence and evidence.
