# Three-Wave Delivery Plan

> **For Hermes:** Execute this plan directly in the `eg-addressing` workspace and verify each wave with API tests, container build checks, and live browser validation.

**Goal:** Finish the remaining three roadmap waves: real field-to-verification-to-registry workflow, full registry CRUD depth, and import/publication/reporting operations.

**Architecture:** Extend the existing FastAPI + PostgreSQL backbone instead of creating parallel demo logic. Persist field submissions, verification decisions, import jobs, and publication packs in PostgreSQL; expose them through authenticated endpoints; then replace the current demo Next.js pages with live operator panels that call the real API.

**Tech stack:** FastAPI, psycopg/PostgreSQL, Next.js App Router, React client components, Docker Compose.

---

## Delivery slices

### Wave 1 — Field → verification → registry
- Add DB tables and seed data for assignments, submissions, and verification reviews.
- Add endpoints to create/list submissions, list review queue, approve/reject/rework submissions, and verify published addresses.
- On approval, promote submission payload into real registry entities (road/building/address) where appropriate.
- Replace `/field` and `/verify` demo shells with live panels.

### Wave 2 — Full registry CRUD depth
- Add detail/update/archive flows for roads, buildings, and addresses.
- Add archive visibility/filtering and audit log coverage for those entities.
- Upgrade `/registry` from create/list starter surface into a full operator panel with edit/archive controls.

### Wave 3 — Import, publication, reporting
- Add import jobs + row staging with dry-run style validation and commit action.
- Add publication packs that can collect approved addresses and mark them officially published.
- Add reporting aggregates (territories, queue, verification, publication, imports) and a `/reports` dashboard.
- Upgrade `/exports` into the publication operations page.

## Files likely touched
- `services/api/app/data.py`
- `services/api/app/db.py`
- `services/api/app/main.py`
- `services/api/tests/test_app.py`
- `apps/admin-portal/app/field/page.tsx`
- `apps/admin-portal/app/verify/page.tsx`
- `apps/admin-portal/app/registry/page.tsx`
- `apps/admin-portal/app/exports/page.tsx`
- `apps/admin-portal/app/reports/page.tsx`
- `apps/admin-portal/components/*.tsx`
- `apps/admin-portal/components/site-data.ts`
- `apps/admin-portal/app/globals.css`

## Risks and mitigation
- **Schema drift with existing local DB volume** → use additive `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` / `CREATE TABLE IF NOT EXISTS` bootstrap migration steps.
- **Breaking working auth/territory flows** → keep existing auth contract and extend tests before live rebuild.
- **Frontend overreach** → keep UI operator-focused and tied to live endpoints, not decorative mockups.

## Verification
- Run API tests via pytest.
- Rebuild API/admin containers with Docker Compose.
- Verify `GET /api/v1/health` and targeted workflow endpoints with real HTTP calls.
- Validate browser flows: sign-in, field submission, approval/rejection, registry edit/archive, import commit, publication pack creation, reporting dashboard render.

## Expected outcome
A working pilot operations system with real field submission intake, review queue, registry promotion, CRUD depth across core entities, import/publication operations, and reporting dashboards backed by live API data.