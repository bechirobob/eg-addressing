# EG National Location Infrastructure — Agent Instructions

These instructions apply to every automated or human implementation task in this repository.

## Programme posture

This repository is being developed as the foundation of Equatorial Guinea's National Location Infrastructure (NLI). The national addressing platform is the first service on that infrastructure. Treat the system as long-lived civic infrastructure, not as a disposable MVP or a generic SaaS product.

The current implementation is a controlled pilot. Do not describe it as official national production unless the System Design Authority (SDA) has recorded that decision and the required evidence exists.

## Decision authority

- **Programme Owner:** sets programme priorities, institutional assumptions, policy direction, and risk acceptance.
- **System Design Authority:** owns architecture, standards, work orders, acceptance criteria, technical decisions, and government-readiness gates.
- **Implementation Agent:** designs within approved boundaries, writes code and migrations, tests the work, records evidence, and raises ambiguities. It does not independently redefine national architecture.

Use this precedence order when instructions conflict:

1. The active SDA work order and its acceptance criteria.
2. Accepted Architecture Decision Records under `docs/sda/adrs/`.
3. Mandatory standards under `docs/sda/standards/`.
4. The target reference architecture.
5. The current-state architecture baseline.
6. Existing repository conventions and local implementation patterns.

Do not guess when a material conflict remains. Raise an RFI using `docs/sda/templates/rfi.md`.

## Required reading before implementation

Before modifying code or controlled design artifacts:

1. Read `docs/sda/README.md`.
2. Read the active work order in `docs/sda/work-orders/`.
3. Read every standard and ADR referenced by that work order.
4. Read `docs/agent-skills/README.md`.
5. Read `docs/agent-skills/PROJECT-COVERAGE-MATRIX.md` and `docs/agent-skills/FAILURE-PREVENTION.md`.
6. Read `docs/agent-skills/skills-manifest.json` or its rendered routing table.
7. Select and read every applicable `docs/agent-skills/skills/*/SKILL.md` module from both the cross-cutting and whole-project domain layers.
8. Inspect the current implementation, workflows, tests, migrations, contracts, infrastructure, runbooks, and evidence affected by the work.
9. Return a concise implementation plan mapped to every acceptance criterion before making changes.

## Required skill routing

The repository skills system has two layers:

- **Cross-cutting delivery and governance skills `01–15`** — intake, reconnaissance, planning, architecture decisions, scope/Git control, migrations, semantic data design, API/identity, security/privacy, GIS, UI/accessibility, CI/evidence, operations/DR, documentation, and SDA remediation.
- **Whole-project product and platform skills `16–30`** — system architecture, frontend, backend, citizen services, registry operations, field/offline work, verification, publication, integrations, worker/batch processing, analytics, infrastructure, performance, adoption, and programme planning.

Before changing files, the agent must record in its implementation plan:

```text
Cross-cutting skills invoked:
- <skill> — why it applies

Project-domain skills invoked:
- <skill> — why it applies

Skills considered but not applicable:
- <skill> — why it does not apply
```

Use the routing table in `docs/agent-skills/README.md` and the complete module/role/lifecycle map in `docs/agent-skills/PROJECT-COVERAGE-MATRIX.md`.

A task is not fully routed until the agent has assessed all affected:

- repository areas;
- NLI bounded domains;
- public/operator/field/partner applications;
- user roles and institutional scopes;
- data/API/GIS/security/infrastructure surfaces;
- release, operation, training, support, and recovery paths.

Skills are subordinate to the active work order and SDA authority; they never authorize work outside the approved scope.

For a fresh or reset agent session, use `docs/agent-skills/AGENT-BOOTSTRAP.md` as the operating instruction.

## Protected architecture rules

The following rules may not be bypassed without an explicit SDA decision:

- Retain a modular monolith unless an ADR authorizes a different deployment boundary.
- PostgreSQL/PostGIS is the authoritative transactional and spatial system of record.
- Redis is non-authoritative and may hold only reconstructable cache, queue, or coordination data.
- S3-compatible storage holds evidence objects; database records hold their authoritative metadata, hashes, ownership, classification, and lifecycle state.
- Application startup must not create or alter schema, seed reference data, or load demonstration fixtures in controlled environments.
- Schema changes must be versioned, reviewable migrations applied through an explicit release process.
- Public citizen workflows must remain separated from protected operator and administrative workflows.
- Authentication and authorization must be enforced server-side. Interface visibility is not an authorization control.
- Sensitive identity, location, evidence, publication, export, and administrative actions must be audited.
- Official publication, certificates, signage, or partner release must remain locked until the required institutional authority is recorded.
- No new external service, database, framework, identity provider, geocoder, map source, workflow state, metric, public data product, or data class may be introduced silently.
- Secrets, private keys, production credentials, personal data extracts, runtime volumes, and local operator notes must not be committed.
- Analytical stores, integrations, worker queues, frontend caches, and local field storage must not become competing canonical authorities.

## Implementation conduct

For each work order:

- Work on the branch named by the work order, or use `nli/<work-order-id>-<description>` when no branch is specified.
- Keep changes inside the approved scope.
- Identify architecture, database, API, identity, security, GIS, frontend, backend, citizen, operator, field, integration, analytics, deployment, localization, accessibility, training, support, and operational effects before implementation.
- Preserve backwards compatibility unless the work order explicitly authorizes a breaking change and supplies a transition plan.
- Use explicit controlled vocabularies and state transitions. Do not create status strings ad hoc.
- Preserve the restrained, human-designed interface direction. Avoid decorative dashboard patterns, unnecessary cards, gradients, shadows, glass effects, and excessive interaction steps.
- Spanish and English support must be complete for affected workflows, not limited to navigation chrome.
- Prefer simple, supportable technology over novelty.
- Add tests with the implementation rather than after it.
- Never suppress a failing control merely to make CI pass.
- Separate unrelated defects into their own issue/branch/PR. A correct fix in the wrong work order is a scope violation.
- Bind evidence to the exact implementation head using the sequence defined in the skills system; do not fabricate a self-referential commit SHA.
- Include deployment, monitoring, backup/recovery, support, training, and rollout consequences when the change affects operational capability.

## Request for Information

Raise an RFI before proceeding when the work would require any of the following:

- changing address-code grammar or identifier semantics;
- changing administrative hierarchy or territorial authority;
- changing publication or approval authority;
- adding or exposing a sensitive data field;
- changing retention, archival, or deletion behavior;
- adding an external dependency or service with operational or licensing impact;
- introducing a new role, permission, scope, workflow state, metric authority, or partner purpose;
- changing the authoritative data source;
- accepting data loss, downtime, compatibility breakage, or a security exception.

An RFI must state the question, why a decision is needed, options considered, the agent's recommendation, and the consequence of no decision.

## Pull-request evidence contract

Every implementation pull request must reference its work order and include:

- acceptance-criterion status, one criterion at a time;
- cross-cutting and project-domain skills invoked and completed;
- changed files, bounded domains, modules, user roles, environments, and affected workflows;
- database migration and rollback/forward-recovery details;
- API and generated-contract changes;
- frontend/backend/field/worker/integration/analytics effects where applicable;
- tests executed and their results;
- screenshots for changed user workflows at required widths and roles;
- security, privacy, accessibility, localization, deployment, operational, training, support, and rollout effects;
- residual risks, limitations, and deferred items;
- RFIs and approved deviations.

A statement such as “done” is not evidence. Point to a commit, migration, test, screenshot, trace, report, browser/device run, restore exercise, or documented review result.

## Review remediation

When resolving SDA findings:

- read the full controlled review record;
- update only the designated agent resolution-log section;
- do not rewrite reviewer outcome, finding class, observation, required resolution, or disposition;
- give each finding its own root cause, fixing commit, exact evidence, and residual condition;
- do not bulk-stamp every finding with the same generic report;
- rerun required checks at the new exact implementation head;
- reassess all affected project-domain skills rather than fixing only the visible code line.

## Completion and claims

Implementation completion is not SDA acceptance. The SDA records one of:

- `ACCEPTED`
- `ACCEPTED WITH RECORDED CONDITIONS`
- `REWORK REQUIRED`
- `REJECTED — ARCHITECTURAL REDESIGN REQUIRED`

Use accurate readiness language:

- **implemented** means code or controlled design exists;
- **tested** means named automated or manual evidence exists;
- **ready for SDA review** means the implementation and evidence are submitted at an exact head;
- **pilot-ready** means controlled pilot criteria are satisfied;
- **agency-ready** means scoped institutional access and operational controls are satisfied;
- **publication-ready** means authority, data, audit, and release gates are satisfied;
- **national-production-ready** requires an explicit SDA and Programme Owner decision.
