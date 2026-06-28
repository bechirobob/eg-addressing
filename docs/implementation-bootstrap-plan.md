# EG Addressing Isolated Workspace Bootstrap Plan

> **For Hermes:** Use this workspace as the only implementation root for the addressing platform.

**Goal:** Stand up a clean, dedicated workspace for the national addressing platform with container boundaries, env isolation, and project-specific docs/data separation.

**Architecture:** Start with one project root and one compose stack. Keep app code, volumes, specs, and exports together inside that boundary. Delay real runtime start until Docker/Podman is installed.

**Files likely touched:**
- `README.md`
- `.gitignore`
- `env/.env.example`
- `infra/docker/docker-compose.yml`
- `infra/scripts/import_existing_artifacts.sh`
- `docs/project-container-strategy.md`

**Expected outcome:** A dedicated project home ready for containerized development without mixing with other projects.

**Risks and mitigation:**
- No runtime installed yet -> prepare reproducible compose files now.
- Existing addressing files are scattered -> provide import script.
- Future mixing risk -> enforce one project root and local data directories.

**Verification steps:**
- confirm workspace directories exist
- confirm compose file exists
- confirm env template exists
- confirm import script exists and is executable-ready
