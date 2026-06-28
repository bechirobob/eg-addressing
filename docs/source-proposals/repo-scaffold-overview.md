# Repository Scaffold Overview

This starter repository has been created as a planning scaffold for the national digital addressing platform.

## Included directories

```text
apps/
  admin-portal/
  field-app/
services/
  api/
  worker/
packages/
  ui/
  config/
  types/
infra/
  docker/
  nginx/
  scripts/
docs/
```

## Purpose of each area

- `apps/admin-portal` — operational portal for registry admins, ministry reviewers, validators, and helpdesk users
- `apps/field-app` — field capture application for enumerators and supervisors
- `services/api` — main FastAPI backend
- `services/worker` — background jobs for exports, retries, and async processing
- `packages/ui` — shared design tokens and reusable components
- `packages/config` — shared runtime/config utilities
- `packages/types` — shared contracts and generated types
- `infra/docker` — Dockerfiles and compose manifests later
- `infra/nginx` — reverse proxy configuration later
- `infra/scripts` — helper scripts for local/dev/ops tasks later
- `docs` — copied architecture and product documents later

## Immediate next coding moves

1. add DB migration tooling
2. scaffold FastAPI service structure
3. scaffold Next.js admin portal shell
4. define shared environment variables
5. connect auth + role model

## Why this scaffold matters

It gives the project clean domain separation before implementation starts, so the build does not collapse into one giant cursed folder.
