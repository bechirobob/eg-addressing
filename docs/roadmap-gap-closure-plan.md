# Roadmap Gap Closure Plan

**Goal:** Close the most immediate Phase 1 and early Phase 2 roadmap gaps by turning the current territory starter into a more complete admin workflow, adding real auth/RBAC scaffolding, and shipping first registry-core management surfaces.

**Architecture:** Keep the backend as a lean FastAPI modular starter backed by PostgreSQL via `psycopg`, with seed/bootstrap logic still in place for now. Extend the existing Next.js admin portal with small focused management routes and client components instead of adding new apps or dependencies.

**Tech Stack:** FastAPI, PostgreSQL, psycopg, Next.js App Router, TypeScript, Docker Compose, Playwright MCP/browser verification.

---

## What will be done
- Add territory detail fetch + update flow.
- Add territory archive control and hide archived records by default.
- Add search/filter controls on the territory registry page.
- Add real demo auth login, bearer token checks, RBAC enforcement, and audit log base.
- Add starter registry-core management surfaces for roads, buildings, and addresses.
- Re-verify all built routes/endpoints against the roadmap and report remaining gaps plainly.

## Why this approach
- It follows the roadmap backlog order instead of random feature drift.
- It improves the current real stack instead of creating mock parallel modules.
- It gives us a stronger proof base for Phase 1 completion while opening the door into Phase 2.
- It keeps diffs contained and avoids dependency sprawl.

## Files likely touched
- `services/api/app/main.py`
- `services/api/app/db.py`
- `services/api/app/data.py`
- `services/api/tests/test_app.py`
- `apps/admin-portal/app/territories/page.tsx`
- `apps/admin-portal/components/TerritoryAdminPanel.tsx`
- `apps/admin-portal/components/site-data.ts`
- `apps/admin-portal/app/globals.css`
- `apps/admin-portal/app/login/page.tsx`
- `apps/admin-portal/app/registry/page.tsx`
- `apps/admin-portal/components/*`
- `docs/roadmap-gap-closure-plan.md`

## Risks and mitigation
- **Risk:** Auth work balloons into a full identity system.  
  **Mitigation:** build a small seeded demo-auth system with bearer tokens and explicit role checks.
- **Risk:** Registry-core expansion becomes fake UI.  
  **Mitigation:** each new screen must hit a real API endpoint backed by Postgres.
- **Risk:** Regressions in the existing live stack.  
  **Mitigation:** keep expanding the API test suite and verify in Docker after each slice.
- **Risk:** We claim roadmap progress too early.  
  **Mitigation:** end with a blunt roadmap verification table showing done vs partial vs missing.

## Verification steps
- Run API tests after each backend slice.
- Rebuild Docker containers after UI/API changes.
- Use live browser verification for the admin routes.
- Query the live API directly with `curl`.
- Query Postgres directly where persistence matters.
- Produce a final roadmap status table backed by observed routes/endpoints/tests.
