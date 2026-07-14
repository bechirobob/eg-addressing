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
4. Read `docs/agent-skills/README.md` and `docs/agent-skills/FAILURE-PREVENTION.md`.
5. Select and read every applicable `docs/agent-skills/skills/*/SKILL.md` module.
6. Inspect the current implementation and tests affected by the work.
7. Return a concise implementation plan mapped to every acceptance criterion before making changes.

## Required skill routing

The repository skills system defines repeatable procedures for intake, reconnaissance, planning, architecture decisions, scope/Git control, migrations, data modelling, APIs and authorization, security/privacy, GIS, UI/accessibility, CI/release, operations/DR, documentation, and SDA review remediation.

Before changing files, the agent must record in its implementation plan:

```text
Skills invoked:
- <skill> — why it applies

Skills considered but not applicable:
- <skill> — why it does not apply
```

Use the routing table in `docs/agent-skills/README.md`. Skills are subordinate to the active work order and SDA authority; they never authorize work outside the approved scope.

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
- No new external service, database, framework, identity provider, geocoder, map source, workflow state, or data class may be introduced silently.
- Secrets, private keys, production credentials, personal data extracts, runtime volumes, and local operator notes must not be committed.

## Implementation conduct

For each work order:

- Work on the branch named by the work order, or use `nli/<work-order-id>-<description>` when no branch is specified.
- Keep changes inside the approved scope.
- Identify database, API, security, workflow, deployment, localization, accessibility, and operational effects before implementation.
- Preserve backwards compatibility unless the work order explicitly authorizes a breaking change and supplies a transition plan.
- Use explicit controlled vocabularies and state transitions. Do not create status strings ad hoc.
- Preserve the restrained, human-designed interface direction. Avoid decorative dashboard patterns, unnecessary cards, gradients, shadows, glass effects, and excessive interaction steps.
- Spanish and English support must be complete for affected workflows, not limited to navigation chrome.
- Prefer simple, supportable technology over novelty.
- Add tests with the implementation rather than after it.
- Never suppress a failing control merely to make CI pass.
- Separate unrelated defects into their own issue/branch/PR. A correct fix in the wrong work order is a scope violation.
- Bind evidence to the exact implementation head using the sequence defined in the skills system; do not fabricate a self-referential commit SHA.

## Request for Information

Raise an RFI before proceeding when the work would require any of the following:

- changing address-code grammar or identifier semantics;
- changing administrative hierarchy or territorial authority;
- changing publication or approval authority;
- adding or exposing a sensitive data field;
- changing retention, archival, or deletion behavior;
- adding an external dependency or service with operational or licensing impact;
- introducing a new role, permission, scope, or workflow state;
- changing the authoritative data source;
- accepting data loss, downtime, compatibility breakage, or a security exception.

An RFI must state the question, why a decision is needed, options considered, the agent's recommendation, and the consequence of no decision.

## Pull-request evidence contract

Every implementation pull request must reference its work order and include:

- acceptance-criterion status, one criterion at a time;
- skills invoked and completed;
- changed files and affected domains;
- database migration and rollback/forward-recovery details;
- API and generated-contract changes;
- tests executed and their results;
- screenshots for changed user workflows at required widths and roles;
- security, privacy, accessibility, localization, deployment, and operational effects;
- residual risks, limitations, and deferred items;
- RFIs and approved deviations.

A statement such as “done” is not evidence. Point to a commit, migration, test, screenshot, trace, report, or documented review result.

## Review remediation

When resolving SDA findings:

- read the full controlled review record;
- update only the designated agent resolution-log section;
- do not rewrite reviewer outcome, finding class, observation, required resolution, or disposition;
- give each finding its own root cause, fixing commit, exact evidence, and residual condition;
- do not bulk-stamp every finding with the same generic report;
- rerun required checks at the new exact implementation head.

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
