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

Before modifying files:

1. Read `docs/sda/README.md`.
2. Read the active work order in `docs/sda/work-orders/`.
3. Read every standard and ADR referenced by that work order.
4. Inspect the current implementation and tests affected by the work.
5. Read `docs/agent/README.md`, `docs/agent/master-operating-protocol.md`, and `docs/agent/skill-manifest.yaml`.
6. Select every agent skill triggered by the task’s effects and read the corresponding cards under `docs/agent/skills/`.
7. Create a task context pack using `docs/agent/templates/task-context-pack.md`.
8. Return a concise implementation or modelling plan mapped to every acceptance criterion before making changes.

## Agent skill routing

Every task must use:

- `S01` — authority, intake, and scope control;
- `S03` — acceptance-criteria planning and decision control;
- `S11` — testing and semantic evidence;
- `S12` — GitHub delivery and exact-head proof;
- `S16` — self-audit and context handoff.

Add domain skills from `docs/agent/skill-manifest.yaml` based on actual effects, not the task title. A database effect invokes S07; an API/auth/sensitive-data effect invokes S08; a GIS/evidence/publication effect invokes S09; and a user-visible workflow invokes S10.

An SDA review finding invokes S13 before remediation. An unrelated defect discovered during active work invokes S14 and must be isolated into a separately governed maintenance path.

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
- Classify anticipated paths as in scope, supporting evidence, separate maintenance, or prohibited before editing them.
- Identify database, API, security, workflow, deployment, localization, accessibility, and operational effects before implementation.
- Preserve backwards compatibility unless the work order explicitly authorizes a breaking change and supplies a transition plan.
- Use explicit controlled vocabularies and state transitions. Do not create status strings ad hoc.
- Preserve the restrained, human-designed interface direction. Avoid decorative dashboard patterns, unnecessary cards, gradients, shadows, glass effects, and excessive interaction steps.
- Spanish and English support must be complete for affected workflows, not limited to navigation chrome.
- Prefer simple, supportable technology over novelty.
- Add tests with the implementation rather than after it.
- Maintain independent sources for observed and expected evidence. Do not generate both with the same logic.
- Never suppress or weaken a failing control merely to make CI pass.
- Never mix an unrelated runtime, migration, security, or operations fix into a design-only or otherwise incompatible work-order PR.

## Testing and evidence conduct

- A file, heading, row count, keyword match, or green CI run is not semantic proof by itself.
- Negative tests must execute the forbidden action and fail for the expected reason.
- No-loss claims must compare values, relationships, authority, exceptions, and counts.
- Generated artefacts must be portable, deterministic, non-self-modifying, and validated by parsing or real execution.
- Expected policy, mappings, scenario outcomes, and review dispositions must be maintained independently from observed generation.
- Evidence must identify what was executed, what was inferred, what was not tested, and what authority remains pending.

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

## SDA review remediation

When the SDA records findings:

- read the complete latest review before changing files;
- use `docs/agent/templates/finding-resolution-matrix.md`;
- resolve each finding with a finding-specific root cause, correction, regression test, commit, and evidence;
- preserve all previously accepted controls;
- update only the explicitly designated resolution-log section of a review record;
- never edit the reviewer outcome, finding text, required resolution, or reviewer disposition;
- use agent status `READY FOR SDA REVIEW`; only the SDA may mark a finding resolved or accepted.

## Pull-request evidence contract

Every implementation pull request must reference its work order and include:

- acceptance-criterion status, one criterion at a time;
- changed files and affected domains;
- database migration and rollback/forward-recovery details;
- API and generated-contract changes;
- tests executed and their results;
- screenshots for changed user workflows at required widths and roles;
- security, privacy, accessibility, localization, deployment, and operational effects;
- residual risks, limitations, and deferred items;
- RFIs and approved deviations.

A statement such as “done” is not evidence. Point to a commit, migration, test, screenshot, trace, report, or documented review result.

Before requesting review, use `docs/agent/templates/exact-head-evidence.md` and verify the remote branch, PR draft state, exact implementation SHA, workflow run IDs, job IDs, changed-path scope, and evidence limitations.

A committed file cannot contain its own final commit SHA. Record the final implementation SHA and workflow/job IDs in the PR body or an immutable PR comment; the later SDA review record must identify the exact implementation SHA assessed. Never fabricate a self-referential SHA.

## Completion and claims

Implementation completion is not SDA acceptance. The SDA records one of:

- `ACCEPTED`
- `ACCEPTED WITH RECORDED CONDITIONS`
- `REWORK REQUIRED`
- `REJECTED — ARCHITECTURAL REDESIGN REQUIRED`

Use accurate readiness language:

- **implemented** means code or a model exists;
- **verified** means named evidence exists at an exact commit;
- **submitted** means the remote branch and reviewable PR exist;
- **tested** means named automated or manual evidence exists;
- **pilot-ready** means controlled pilot criteria are satisfied;
- **agency-ready** means scoped institutional access and operational controls are satisfied;
- **publication-ready** means authority, data, audit, and release gates are satisfied;
- **national-production-ready** requires an explicit SDA and Programme Owner decision.

Before saying “done,” requesting SDA review, or handing work to another agent, complete `docs/agent/templates/self-audit.md` and report:

```text
Implementation/model status:
Verification status and exact SHA:
Remote submission status:
SDA status:
Open findings/RFIs:
Separate maintenance dependencies:
Readiness boundary:
Exact next action:
```
