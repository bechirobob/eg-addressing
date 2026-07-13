# Equatorial Guinea National Addressing Platform

Dedicated project workspace for the national digital addressing platform.

## Why this exists
This workspace isolates the addressing platform so code, documents, data, exports, and future services stay organized inside a dedicated project boundary.

## Isolation rules
- Keep all addressing-platform code inside this workspace.
- Keep project env files under `env/` only.
- Keep project-generated documents under `docs/` and `artifacts/`.
- Keep local service volumes under `data/`.
- Do not reuse shared app folders from other projects.
- Do not commit secrets or local runtime data.

## Structure
- `apps/admin-portal` — ministry/admin UI
- `apps/field-app` — mobile-first field capture UI
- `services/api` — FastAPI backend
- `services/worker` — background jobs
- `packages/` — shared types/ui/config
- `infra/docker` — local container orchestration
- `infra/scripts` — helper scripts
- `env` — environment templates
- `data` — local persistent service volumes
- `docs` — architecture and planning docs
- `artifacts` — generated PDFs, exports, diagrams

## Repo conventions
- Keep durable project docs in `docs/`.
- Keep generated presentation/reference assets in `artifacts/`.
- Keep local-only operator notes in `knowledge/` and never commit them.
- Keep secrets out of git; commit only templates under `env/`.
- Treat `data/` as disposable runtime state, not source.
- Use GitHub Actions for deterministic repo-local checks; keep live smoke checks as an operator lane.

## Current platform direction
- Frontend: Next.js + TypeScript
- Backend: FastAPI
- Database: PostgreSQL + PostGIS
- Queue/cache: Redis
- Storage: S3-compatible object storage or local dev storage
- Runtime shape: modular monolith first, not microservices on day one

## Current status
The isolated Docker stack is live and now serves real infrastructure plus starter application code.

## Current local stack
- Postgres/PostGIS on `5434`
- Redis on `6384`
- MinIO on `9100` / `9101`
- FastAPI on `8100`
- Next.js admin portal on `3100`

## Start or rebuild the project stack
```bash
cd /home/ubuntu/projects/eg-addressing
cp env/.env.example .env  # first time only; replace private values before use
sudo docker compose --env-file .env -f infra/docker/docker-compose.yml up -d --build
infra/scripts/bootstrap_local.sh
```

## Controlled database lifecycle
The API no longer creates schema or loads seed data during startup. Database state is controlled explicitly:

```bash
# Apply ordered migrations with checksum ledger and advisory lock
infra/scripts/run_migrations.sh apply

# Check migration readiness without mutating the database
infra/scripts/run_migrations.sh status

# Load governed province/admin-unit reference data idempotently
services/api/.venv/bin/python infra/scripts/load_reference_data.py load

# Optional local/test-only fixture users; refuses production/staging/pilot labels
APP_ENV=development EG_ALLOW_DEV_FIXTURES=YES \
  DEVELOPMENT_FIXTURE_PASSWORD='<generate-outside-git>' \
  services/api/.venv/bin/python infra/scripts/load_development_fixtures.py load
```

Existing pilot databases created before `NLI-WO-001` use:

```bash
infra/scripts/run_migrations.sh transition-pilot
```

Take a backup first. The transition validates required pilot tables, executes the idempotent `000` schema bridge, preserves existing `001–006` migration checksums, applies pending migrations, and fails closed on drift or checksum mismatch.
