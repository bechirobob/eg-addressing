# Starter Code Implementation Plan

**Goal:** Replace placeholder API/admin containers with a working FastAPI backend and Next.js admin starter that reflect the national addressing platform architecture.

**Architecture:** Keep the backend as a small modular FastAPI starter with seed data and health/meta endpoints. Keep the admin app as a clean Next.js TypeScript shell that reads backend status and presents the MVP modules. Run both through the isolated Docker Compose stack.

**Files likely touched:**
- `services/api/requirements.txt`
- `services/api/app/*.py`
- `services/api/tests/test_app.py`
- `services/api/Dockerfile`
- `apps/admin-portal/package.json`
- `apps/admin-portal/tsconfig.json`
- `apps/admin-portal/next.config.mjs`
- `apps/admin-portal/app/*`
- `apps/admin-portal/Dockerfile`
- `infra/docker/docker-compose.yml`
- `.dockerignore`
- `README.md`

**Expected outcome:** The isolated stack serves a real API and a real admin UI instead of placeholder processes.

**Risks and mitigation:**
- Compose regressions -> verify with `docker compose config`, rebuild, and curl endpoints.
- Frontend build-time fetch problems -> force dynamic runtime fetching.
- Huge dependency sprawl -> keep the starter lean and avoid extra libraries.

**Verification steps:**
- build containers successfully
- run API tests
- start stack cleanly
- curl API health/meta endpoints
- curl admin root and confirm rendered content
