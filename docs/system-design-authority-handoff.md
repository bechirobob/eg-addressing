# GPT Architect Handoff — EG National Location Infrastructure

> Purpose: give the external GPT architect enough current-state evidence to review the project as a national programme / System Design Authority candidate, without exposing secrets or hidden agent prompts.

## 1. Repository access

- GitHub SSH remote: `git@github.com:bechirobob/eg-addressing.git`
- Browser URL: `https://github.com/bechirobob/eg-addressing`
- Branch: `main`
- Current commit: `b043593`
- Working tree at handoff time: clean

## 2. Product framing

- Current product: National Digital Addressing Platform for Equatorial Guinea.
- Strategic reframing proposed by architecture agent: National Location Infrastructure (NLI), with addressing as first service.
- Company/brand for official/IP/company documents: BeCoreOps.
- Responsible founder for IP packet: Benjamin Bob Bechiro.
- Posture: controlled pilot and government-grade implementation planning, not yet national production-ready.

## 3. Runtime architecture

- `postgres` — PostgreSQL/PostGIS database
- `redis` — Redis cache/queue support
- `minio` — S3-compatible object storage for evidence/files
- `api` — FastAPI backend
- `admin` — Next.js admin/public portal

Local ports from README / compose:
- Postgres/PostGIS: `5434`
- Redis: `6384`
- MinIO: `9100` / console `9101`
- FastAPI: `8100`
- Next.js admin/public portal: `3100`

## 4. Source tree overview

```text
apps/admin-portal       Next.js public/admin/operator portal
apps/field-app          mobile-first field capture app placeholder/workspace
services/api            FastAPI backend and database access layer
services/worker         background jobs workspace
packages/types          shared type definitions
packages/ui             shared UI package workspace
packages/config         shared config workspace
infra/docker            Docker Compose runtime
infra/migrations        SQL migrations / PostGIS hardening
infra/scripts           deployment and operational scripts
docs                    formal docs, proposals, training, IP PDFs
artifacts               generated/local proof bundles (mostly ignored)
knowledge               local mission logs, not for GitHub
```

## 5. Frontend routes discovered

- `/admin/staff`
- `/code/[code]`
- `/exports`
- `/field`
- `/geotag`
- `/issue`
- `/login`
- `/operations-runbook`
- `/`
- `/proof/[code]`
- `/records`
- `/registry`
- `/reports`
- `/signage`
- `/territories`
- `/track`
- `/verify`

## 6. API endpoint inventory

Total discovered FastAPI routes: `105`

- `GET /`
- `GET /api/v1/health`
- `GET /api/v1/meta`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`
- `GET /api/v1/admin/users`
- `POST /api/v1/admin/users`
- `PATCH /api/v1/admin/users/{user_id}`
- `POST /api/v1/admin/users/{user_id}/disable`
- `POST /api/v1/admin/users/{user_id}/revoke-sessions`
- `GET /api/v1/territories/provinces`
- `GET /api/v1/provinces`
- `GET /api/v1/admin-units`
- `GET /api/v1/public/territory-options`
- `GET /api/v1/territories`
- `GET /api/v1/territories/{territory_id}`
- `POST /api/v1/territories`
- `PATCH /api/v1/territories/{territory_id}`
- `DELETE /api/v1/territories/{territory_id}`
- `GET /api/v1/audit-logs`
- `GET /api/v1/roads`
- `GET /api/v1/roads/{road_id}`
- `POST /api/v1/roads`
- `PATCH /api/v1/roads/{road_id}`
- `DELETE /api/v1/roads/{road_id}`
- `GET /api/v1/buildings`
- `GET /api/v1/buildings/{building_id}`
- `POST /api/v1/buildings`
- `PATCH /api/v1/buildings/{building_id}`
- `DELETE /api/v1/buildings/{building_id}`
- `GET /api/v1/addresses`
- `GET /api/v1/addresses/{address_id}`
- `POST /api/v1/addresses`
- `PATCH /api/v1/addresses/{address_id}`
- `DELETE /api/v1/addresses/{address_id}`
- `GET /api/v1/field/assignments`
- `GET /api/v1/field/geotag-tasks`
- `POST /api/v1/field/geotag-tasks/{submission_id}/status`
- `POST /api/v1/field/geotag-tasks/{submission_id}/evidence`
- `GET /api/v1/field/submissions`
- `POST /api/v1/field/spatial-evidence/enrich`
- `POST /api/v1/field/submissions`
- `POST /api/v1/field/submissions/{submission_id}/evidence-files`
- `GET /api/v1/field/submissions/{submission_id}/evidence-history`
- `POST /api/v1/field/submissions/{submission_id}/evidence-review`
- `GET /api/v1/field/submissions/{submission_id}/evidence-files/{file_id}`
- `POST /api/v1/field/submissions/{submission_id}/under-review`
- `POST /api/v1/field/submissions/{submission_id}/approve`
- `POST /api/v1/field/submissions/{submission_id}/reject`
- `POST /api/v1/field/submissions/{submission_id}/rework`
- `GET /api/v1/verification/lookup`
- `GET /api/v1/public/verification/{query}`
- `GET /api/v1/public/issuance/{query}`
- `GET /api/v1/public/address-code/{code}`
- `GET /api/v1/public/address-code/{code}/record`
- `POST /api/v1/public/corrections`
- `POST /api/v1/public/geotag/preview`
- `POST /api/v1/public/geotag/road-suggestion`
- `POST /api/v1/public/geotag-submissions`
- `GET /api/v1/public/geotag-submissions/{submission_id}/tracking`
- `GET /api/v1/public/tracking/{lookup_code}`
- `GET /api/v1/address-records/search`
- `GET /api/v1/address-records/export`
- `GET /api/v1/address-records/nearby`
- `GET /api/v1/address-records/holds`
- `GET /api/v1/address-records/{address_code}`
- `GET /api/v1/address-records/{address_code}/certificate`
- `GET /api/v1/geotag-submissions`
- `GET /api/v1/geotag-submissions/automation/summary`
- `GET /api/v1/geotag-submissions/automation/sla-drilldown`
- `GET /api/v1/geotag-submissions/duplicates/summary`
- `GET /api/v1/geotag-submissions/{submission_id}/certificate`
- `GET /api/v1/geotag-submissions/{submission_id}/history`
- `POST /api/v1/geotag-submissions/{submission_id}/identity`
- `POST /api/v1/geotag-submissions/{submission_id}/under-review`
- `POST /api/v1/geotag-submissions/{submission_id}/field-check`
- `POST /api/v1/geotag-submissions/{submission_id}/registry-ready`
- `POST /api/v1/geotag-submissions/{submission_id}/publication-simulation`
- `POST /api/v1/geotag-submissions/{submission_id}/publish`
- `POST /api/v1/geotag-submissions/{submission_id}/reject`
- `POST /api/v1/geotag-submissions/{submission_id}/duplicate-decision`
- `POST /api/v1/geotag-submissions/{submission_id}/road-suggestion`
- `GET /api/v1/signage/export`
- `GET /api/v1/signage/pack`
- `GET /api/v1/address-corrections`
- `POST /api/v1/address-corrections/{correction_id}/under-review`
- `POST /api/v1/address-corrections/{correction_id}/resolve`
- `POST /api/v1/address-corrections/{correction_id}/reject`
- `GET /api/v1/imports/jobs`
- `GET /api/v1/imports/jobs/{job_id}/rows`
- `POST /api/v1/imports/jobs`
- `POST /api/v1/imports/jobs/{job_id}/commit`
- `GET /api/v1/publication/packs`
- `POST /api/v1/publication/packs`
- `POST /api/v1/publication/packs/{pack_id}/publish`
- `GET /api/v1/operator/command-center`
- `GET /api/v1/operator/postgis/readiness`
- `GET /api/v1/operator/migrations/status`
- `GET /api/v1/operator/production-readiness`
- `GET /api/v1/operator/demo-fixtures/status`
- `POST /api/v1/operator/demo-fixtures/cleanup`
- `GET /api/v1/operator/restore-drill/latest`
- `GET /api/v1/reporting/summary`
- `GET /api/v1/pilot-readiness/summary`

## 7. Database / persistence

### Migration files

- `infra/migrations/001_schema_migration_baseline.sql`
- `infra/migrations/002_government_grade_indexes_and_guards.sql`
- `infra/migrations/003_canonical_address_records.sql`
- `infra/migrations/004_registry_ready_not_signage_ready.sql`
- `infra/migrations/005_address_record_postgis_geometry.sql`
- `infra/migrations/006_address_record_retirement_policy.sql`

### Tables discovered from `services/api/app/db.py`

#### `provinces`
Key columns observed:
- `code TEXT PRIMARY KEY`
- `name TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

#### `admin_units`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `level TEXT NOT NULL`
- `code TEXT NOT NULL UNIQUE`
- `parent_id TEXT REFERENCES admin_units(id)`
- `province_code TEXT REFERENCES provinces(code)`
- `name_es TEXT NOT NULL`
- `name_en TEXT NOT NULL`
- `status TEXT NOT NULL DEFAULT 'active'`
Relationships observed:
- `parent_id` → `admin_units.id`
- `province_code` → `provinces.code`

#### `users`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `username TEXT NOT NULL UNIQUE`
- `full_name TEXT NOT NULL`
- `role TEXT NOT NULL`
- `password_hash TEXT NOT NULL`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

#### `auth_tokens`
Key columns observed:
- `token TEXT PRIMARY KEY`
- `user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `expires_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `revoked_at TIMESTAMPTZ`
- `last_seen_at TIMESTAMPTZ`
Relationships observed:
- `user_id` → `users.id`

#### `audit_logs`
Key columns observed:
- `id BIGSERIAL PRIMARY KEY`
- `actor_user_id TEXT`
- `actor_username TEXT`
- `actor_role TEXT`
- `action TEXT NOT NULL`
- `entity_type TEXT NOT NULL`
- `entity_id TEXT NOT NULL`
- `details TEXT NOT NULL DEFAULT '{}'`

#### `territories`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `name TEXT NOT NULL UNIQUE`
- `province_code TEXT NOT NULL REFERENCES provinces(code)`
- `admin_unit_id TEXT REFERENCES admin_units(id)`
- `type TEXT NOT NULL`
- `readiness TEXT NOT NULL`
- `is_archived BOOLEAN NOT NULL DEFAULT FALSE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
Relationships observed:
- `province_code` → `provinces.code`
- `admin_unit_id` → `admin_units.id`

#### `roads`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `name TEXT NOT NULL UNIQUE`
- `territory_id TEXT NOT NULL REFERENCES territories(id)`
- `status TEXT NOT NULL`
- `length_km TEXT NOT NULL`
- `spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb`
- `is_archived BOOLEAN NOT NULL DEFAULT FALSE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
Relationships observed:
- `territory_id` → `territories.id`

#### `buildings`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `label TEXT NOT NULL UNIQUE`
- `territory_id TEXT NOT NULL REFERENCES territories(id)`
- `road_id TEXT NOT NULL REFERENCES roads(id)`
- `status TEXT NOT NULL`
- `usage TEXT NOT NULL`
- `spatial_evidence JSONB NOT NULL DEFAULT '{}'::jsonb`
- `is_archived BOOLEAN NOT NULL DEFAULT FALSE`
Relationships observed:
- `territory_id` → `territories.id`
- `road_id` → `roads.id`

#### `addresses`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `formatted TEXT NOT NULL UNIQUE`
- `territory_id TEXT NOT NULL REFERENCES territories(id)`
- `road_id TEXT NOT NULL REFERENCES roads(id)`
- `building_id TEXT NOT NULL REFERENCES buildings(id)`
- `province_code TEXT NOT NULL REFERENCES provinces(code)`
- `public_code TEXT`
- `issuance_method TEXT NOT NULL DEFAULT 'manual'`
Relationships observed:
- `territory_id` → `territories.id`
- `road_id` → `roads.id`
- `building_id` → `buildings.id`
- `province_code` → `provinces.code`
- `superseded_by_address_id` → `addresses.id`

#### `address_points`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `address_id TEXT NOT NULL REFERENCES addresses(id) ON DELETE CASCADE`
- `latitude DOUBLE PRECISION NOT NULL`
- `longitude DOUBLE PRECISION NOT NULL`
- `accuracy_meters DOUBLE PRECISION`
- `source_method TEXT NOT NULL DEFAULT 'manual'`
- `is_active BOOLEAN NOT NULL DEFAULT TRUE`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
Relationships observed:
- `address_id` → `addresses.id`

#### `address_corrections`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `address_id TEXT REFERENCES addresses(id)`
- `public_code TEXT`
- `query TEXT NOT NULL`
- `correction_type TEXT NOT NULL`
- `reason TEXT NOT NULL`
- `note TEXT NOT NULL DEFAULT ''`
- `reporter_name TEXT`
Relationships observed:
- `address_id` → `addresses.id`

#### `citizen_geotag_submissions`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `territory_id TEXT REFERENCES territories(id)`
- `address_label TEXT NOT NULL`
- `citizen_name TEXT`
- `citizen_contact TEXT`
- `dip_last4 TEXT`
- `identity_verification_status TEXT NOT NULL DEFAULT 'unverified'`
- `identity_document_verified BOOLEAN NOT NULL DEFAULT FALSE`
Relationships observed:
- `territory_id` → `territories.id`

#### `address_records`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `address_code TEXT NOT NULL UNIQUE`
- `source_submission_id TEXT REFERENCES citizen_geotag_submissions(id)`
- `province_code TEXT REFERENCES provinces(code)`
- `territory_id TEXT REFERENCES territories(id)`
- `address_label TEXT NOT NULL`
- `status TEXT NOT NULL`
- `publication_state TEXT NOT NULL DEFAULT 'not-public'`
Relationships observed:
- `source_submission_id` → `citizen_geotag_submissions.id`
- `province_code` → `provinces.code`
- `territory_id` → `territories.id`

#### `address_record_events`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `address_record_id TEXT NOT NULL REFERENCES address_records(id) ON DELETE CASCADE`
- `event_type TEXT NOT NULL`
- `actor_id TEXT`
- `actor_username TEXT`
- `actor_role TEXT`
- `details JSONB NOT NULL DEFAULT '{}'::jsonb`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
Relationships observed:
- `address_record_id` → `address_records.id`

#### `field_assignments`
Key columns observed:
- `assignment_id TEXT PRIMARY KEY`
- `territory_id TEXT NOT NULL REFERENCES territories(id)`
- `territory TEXT NOT NULL`
- `task TEXT NOT NULL`
- `team TEXT NOT NULL`
- `priority TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
Relationships observed:
- `territory_id` → `territories.id`

#### `field_submissions`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `assignment_id TEXT REFERENCES field_assignments(assignment_id)`
- `territory_id TEXT NOT NULL REFERENCES territories(id)`
- `submission_type TEXT NOT NULL`
- `candidate_name TEXT NOT NULL`
- `candidate_status TEXT NOT NULL`
- `notes TEXT NOT NULL DEFAULT ''`
- `submitted_by TEXT NOT NULL`
Relationships observed:
- `assignment_id` → `field_assignments.assignment_id`
- `territory_id` → `territories.id`

#### `import_jobs`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `name TEXT NOT NULL`
- `source_name TEXT NOT NULL`
- `status TEXT NOT NULL DEFAULT 'draft'`
- `imported_count INTEGER NOT NULL DEFAULT 0`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

#### `import_rows`
Key columns observed:
- `job_id TEXT NOT NULL REFERENCES import_jobs(id) ON DELETE CASCADE`
- `row_number INTEGER NOT NULL`
- `submission_type TEXT NOT NULL`
- `territory_id TEXT NOT NULL REFERENCES territories(id)`
- `candidate_name TEXT NOT NULL`
- `candidate_status TEXT NOT NULL`
- `notes TEXT NOT NULL DEFAULT ''`
- `validation_status TEXT NOT NULL`
Relationships observed:
- `job_id` → `import_jobs.id`
- `territory_id` → `territories.id`

#### `publication_packs`
Key columns observed:
- `id TEXT PRIMARY KEY`
- `name TEXT NOT NULL`
- `status TEXT NOT NULL`
- `audience TEXT NOT NULL`
- `created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`
- `updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()`

#### `publication_pack_addresses`
Key columns observed:
- `publication_pack_id TEXT NOT NULL REFERENCES publication_packs(id) ON DELETE CASCADE`
- `address_id TEXT NOT NULL REFERENCES addresses(id)`
Relationships observed:
- `publication_pack_id` → `publication_packs.id`
- `address_id` → `addresses.id`

## 8. Current module status — conservative

| Module | Status | Evidence / note |
|---|---|---|
| Citizen Portal | Pilot-grade / substantial | Public home, geotag submission, issue/correction, tracking, public code/proof pages exist. |
| Government/Admin Portal | Pilot-grade / substantial | Registry, field, verify, territories, reports, exports, signage, records, staff admin pages exist. |
| Agency Portal | Minimal / partial | agency_viewer role exists historically; current separate agency UX is not full multi-agency scoping. |
| Address Engine | Pilot-grade / substantial | National address-code generation/validation and address record workflows exist; grammar still needs formal national freeze. |
| GIS / Spatial | Partial progressing | PostGIS stack, address point geometry, spatial evidence, nearby/readiness endpoints; national basemap/geometry governance not complete. |
| Reports / Audit | Pilot-grade / substantial | Reporting summary, audit logs, exports, readiness endpoints exist; enterprise analytics remains future work. |
| Analytics | Missing / early | Operational summaries exist; full analytics/BI layer not implemented. |
| Notification Service | Missing / not confirmed | No dedicated notification service confirmed in inspected structure. |
| Publication / Signage | Pilot-grade / governed simulation | Publication packs, simulation, admin-only publish, proof/cert/signage endpoints exist; real authority approval remains external. |
| Training / IP docs | Strong documentation lane | Bilingual training manuals and Malabo IP registration pack exist as PDFs/sources. |

## 9. Roles and permissions

### Implemented / active pilot role names observed

- `admin`
- `editor`
- `viewer`
- `agency_viewer`

### Target national role model from legacy role-permission matrix

- `super_admin`
- `national_registry_admin`
- `ministry_reviewer`
- `municipal_validator`
- `field_supervisor`
- `enumerator`
- `helpdesk_agent`
- `agency_readonly`
- `api_client`
- `auditor`

Important gap: current implementation has a simplified pilot role model. National programme architecture should replace/extend this with scoped institutional roles, agency IDs, province/municipality scope, explicit permission keys, and audit events for sensitive reads/exports.

## 10. Quality / verification commands

From `apps/admin-portal/package.json`:

- `npm run build` → `next build`
- `npm run test:copy` → `node scripts/page-copy-guard.mjs`
- `npm run test:role-auth` → `node scripts/role-auth-guard.mjs`
- `npm run test:route-ownership` → `node scripts/route-ownership-guard.mjs`
- `npm run test:smoke` → `node scripts/admin-flow-smoke.mjs`
- `npm run test:registry-actions` → `node scripts/registry-action-guard.mjs`
- `npm run test:verification-queue` → `node scripts/verification-queue-guard.mjs`
- `npm run test:official-geometry` → `node scripts/official-geometry-guard.mjs`
- `npm run test:spanish-leaks` → `node scripts/spanish-leak-guard.mjs`
- `npm run test:a11y-controls` → `node scripts/accessibility-control-guard.mjs`
- `npm run test:ci` → `npm run build && npm run test:role-auth && npm run test:registry-actions && npm run test:api-types`
- `npm run test` → `npm run test:copy && npm run test:role-auth && npm run test:route-ownership && npm run test:registry-actions && npm run test:verification-queue && npm run test:official-geometry && npm run test:spanish-leaks && npm run test:a11y-controls && npm run test:api-types && npm run test:data-command && npm run test:smoke`
- `npm run test:design-system` → `node scripts/design-system-freeze-guard.mjs`
- `npm run test:quality` → `npm run test:spanish-leaks && npm run test:a11y-controls && npm run test:official-geometry && npm run test:api-types && npm run test:data-command && npm run test:route-ownership && npm run test:density && npm run test:source-size && npm run test:external-docs && npm run test:field-desktop && npm run test:verify-desktop && npm run test:desktop-workbench && npm run test:login-desktop && npm run test:design-system && npm run test:public-proof && npm run test:operations-runbook`
- `npm run test:source-size` → `node scripts/source-size-guard.mjs`
- `npm run test:external-docs` → `node scripts/external-docs-hygiene-guard.mjs`
- `npm run generate:api-types` → `node scripts/generate-api-types.mjs`
- `npm run test:api-types` → `node scripts/api-types-guard.mjs`
- `npm run test:data-command` → `node scripts/data-command-guard.mjs`
- `npm run test:density` → `node scripts/density-guard.mjs`
- `npm run test:field-desktop` → `node scripts/field-desktop-workbench-guard.mjs`
- `npm run test:verify-desktop` → `node scripts/verify-desktop-workbench-guard.mjs`
- `npm run test:desktop-workbench` → `node scripts/desktop-workbench-guard.mjs`
- `npm run test:login-desktop` → `node scripts/login-desktop-access-guard.mjs`
- `npm run test:public-proof` → `node scripts/public-proof-qr-guard.mjs`
- `npm run test:operations-runbook` → `node scripts/operations-runbook-guard.mjs`

Backend dependencies: FastAPI, Uvicorn, Pydantic, psycopg, pytest, httpx.

## 11. Existing formal document packages

- Government submission package: `docs/becoreops-government-submission-v2/`
- Bilingual training manuals: `docs/training/manuals/`
- Malabo IP registration pack: `docs/ip-registration-malabo/`
- API source proposal/spec: `docs/source-proposals/openapi.yaml`
- Legacy architecture and permission references: `artifacts/legacy/`

## 12. Screenshot / visual evidence locations

Current screenshots are not centralized as one official set. Useful existing locations:
- `artifacts/training-previews/`
- `artifacts/ip-registration-malabo/previews/`
- historical QA/closeout artifacts under `artifacts/` and `.hermes` paths mentioned in closeout notes

Recommended next collaboration task: generate a fresh workflow screenshot pack for each major route at desktop and mobile widths, labelled by route, role, date, and commit.

## 13. Engineering handbook seed — safe shareable version

The implementation agent follows these project-level standards for EG Addressing/NLI work:

1. Treat the system as national civic infrastructure, not a generic web app.
2. Use a modular monolith first: Next.js frontend, FastAPI backend, PostgreSQL/PostGIS, Redis, S3-compatible storage.
3. Keep public citizen workflows separate from protected operator/admin workflows.
4. Sensitive identity, GPS, evidence, publication, and export actions must be protected server-side and audited.
5. Keep UI restrained and human-designed: no SaaS dashboard tropes, no decorative gradient soup, no pills/cards/screens for formal documents, no shadows/glassmorphism.
6. Spanish/English support must be real localization, not chrome-only translation.
7. Official publication/certificates/signage must stay locked behind approval governance until authorized.
8. Use PostGIS and structured evidence for field/location workflows; avoid making free-text labels the source of truth.
9. Keep `knowledge/`, secrets, local data, generated QA clutter, and runtime volumes out of GitHub.
10. Verify before claiming done: tests/build/API/browser/screenshot evidence depending on the lane.
11. Do not ship AI/process/tooling fingerprints in official docs, commits, PDFs, comments, or project files.
12. Separate controlled pilot readiness from national production readiness in all claims.

Hidden system/persona prompts are not included. The architect should improve this shareable handbook into a formal System Design Authority manual.

## 14. Recommended System Design Authority workstreams

1. Define NLI reference architecture and domain boundaries.
2. Produce canonical data model and ER diagram from current schema + target model.
3. Replace pilot role model with national RBAC/ABAC permission architecture.
4. Define publication governance and legal/state authority workflow.
5. Formalize address-code grammar and GIS standards.
6. Define integration/API gateway strategy for agencies and future services.
7. Define security architecture: identity, sessions, MFA, secrets, audit, incident response, backups, DR.
8. Define scale targets: records, concurrent users, API throughput, map tiles, object storage, analytics.
9. Define release gates and acceptance criteria for government-grade features.
10. Create a fresh screenshot/workflow evidence pack for architecture review.
