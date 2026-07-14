# NLI Delivery Agent Skill Pack

**Version:** 1.0  
**Status:** Proposed operational standard  
**Audience:** implementation agents, human engineers, reviewers, and operators working under the System Design Authority  
**Authority:** subordinate to `AGENTS.md`, active SDA work orders, accepted ADRs, and mandatory standards

## Purpose

This pack gives the implementation agent a repeatable operating system for delivering the Equatorial Guinea National Location Infrastructure (NLI). It is designed to reduce avoidable review cycles caused by:

- scope leakage between work orders;
- incomplete repository or data discovery;
- generic plans and boilerplate evidence;
- generated artefacts validating their own assumptions;
- source-string checks replacing executable semantic tests;
- stale pull-request heads and workflow evidence;
- review findings being bulk-marked resolved without finding-specific proof;
- unrelated bug fixes being mixed into an active architecture or implementation PR;
- inaccurate readiness or completion claims.

The skill pack does not replace the SDA control layer. It operationalizes it.

## Authority and precedence

Use this order when instructions conflict:

1. Active SDA work order and acceptance criteria.
2. Accepted ADRs.
3. Mandatory SDA standards.
4. Root `AGENTS.md`.
5. This skill pack.
6. Existing local implementation conventions.

A skill card may make a process stricter, but it may not weaken a work order or accepted standard.

## Mandatory agent loop

Every task follows this loop:

```text
ORIENT → CLASSIFY → PLAN → DECIDE → IMPLEMENT/MODEL
→ VERIFY → SELF-AUDIT → PUSH → EXACT-HEAD EVIDENCE
→ SDA REVIEW → FINDING-BY-FINDING REMEDIATION → ACCEPTANCE
```

The agent must not skip directly from implementation to “done.”

## Skill routing

Start with [`skill-manifest.yaml`](skill-manifest.yaml). Select the primary skill and every supporting skill triggered by the task’s effects.

At minimum, every task uses:

- [`S01 — Authority, intake, and scope control`](skills/S01-authority-intake-and-scope.md)
- [`S03 — Acceptance-criteria planning and decision control`](skills/S03-acceptance-planning-and-rfi.md)
- [`S11 — Testing and semantic evidence`](skills/S11-testing-and-semantic-evidence.md)
- [`S12 — GitHub delivery and exact-head proof`](skills/S12-github-delivery-and-exact-head-proof.md)
- [`S16 — Self-audit and context handoff`](skills/S16-self-audit-and-context-handoff.md)

Add domain skills as required:

| Trigger | Skill |
|---|---|
| Repository or architecture discovery | [`S02`](skills/S02-repository-orientation-and-impact.md) |
| ADR, policy ambiguity, authority decision | [`S04`](skills/S04-rfi-and-adr-management.md) |
| Current schema, routes, roles, or workflow inventory | [`S05`](skills/S05-authoritative-current-state-discovery.md) |
| Canonical data model, ERD, field mapping, convergence | [`S06`](skills/S06-canonical-data-model-and-convergence.md) |
| Schema migration, reference data, fixtures | [`S07`](skills/S07-database-migrations-and-reference-data.md) |
| API, identity, authorization, privacy, partner contracts | [`S08`](skills/S08-api-identity-security-and-privacy.md) |
| GIS, evidence, publication, geometry authority | [`S09`](skills/S09-gis-evidence-and-publication.md) |
| UI, accessibility, localization, workflow changes | [`S10`](skills/S10-ui-accessibility-localization-and-workflows.md) |
| SDA review comments and rework | [`S13`](skills/S13-sda-review-remediation.md) |
| Incidental bug, CI defect, emergency or maintenance fix | [`S14`](skills/S14-maintenance-fix-isolation.md) |
| Deployment, operations, backup, restore, DR | [`S15`](skills/S15-release-operations-and-dr.md) |

## Standard skill-card contract

Each skill card defines:

- **Invoke when** — task triggers.
- **Required inputs** — documents and source evidence.
- **Procedure** — mandatory execution steps.
- **Outputs** — controlled artefacts to produce.
- **Stop/RFI conditions** — circumstances where guessing is prohibited.
- **Evidence gate** — proof required before claiming completion.
- **Anti-patterns** — known failure modes.

The agent must follow the card, not merely mention that it was read.

## Non-negotiable operating rules

### 1. Scope is a hard boundary

Before changing a file, classify it as:

- explicitly in scope;
- necessary supporting evidence;
- unrelated maintenance;
- prohibited.

An unrelated defect discovered during a task is not silently fixed in the same PR. Use S14 to isolate it.

### 2. Expected evidence must be independent

Do not generate the “expected” result from the same logic that generates the “observed” result. Examples:

- observed route policies must be compared with a separately reviewed expected-policy registry;
- mappings must be reviewed source data, not heuristic fallbacks;
- scenario expectations must be authored independently of the schema generator;
- review dispositions must be written by the SDA, not rewritten by the remediation agent.

### 3. Presence is not semantic proof

A file, row count, heading, green build, or keyword match does not prove correctness. Tests must exercise the claimed behavior, including negative cases and authority boundaries.

### 4. Review records are immutable authority records

The implementation agent may update only the explicitly designated resolution-log section of an SDA review. It must never change:

- reviewer outcome;
- finding class;
- reviewer observation;
- required resolution;
- reviewer disposition table.

A later review supersedes an earlier review; it does not erase it.

### 5. Exact-head evidence must be truthful

A committed file cannot contain its own final commit SHA. Use this binding model:

1. Commit implementation and controlled evidence.
2. Push and obtain the final implementation SHA.
3. Run CI against that SHA.
4. Record SHA and workflow/job IDs in the PR body or immutable PR comment.
5. The later SDA review record identifies the exact implementation SHA assessed.

Never fake a self-referential SHA.

### 6. “Done” has four separate meanings

- **Implemented:** the artefact or code exists.
- **Verified:** named evidence passes at an exact commit.
- **Submitted:** branch is pushed and a reviewable draft PR exists.
- **Accepted:** SDA has recorded an acceptance outcome.

The agent must state which meaning applies.

## Required task artefacts

Use these templates:

- [`task-context-pack.md`](templates/task-context-pack.md)
- [`finding-resolution-matrix.md`](templates/finding-resolution-matrix.md)
- [`exact-head-evidence.md`](templates/exact-head-evidence.md)
- [`self-audit.md`](templates/self-audit.md)

Existing SDA templates remain authoritative for work-order plans, RFIs, PR evidence, and SDA reviews.

## Validation

Validate the pack after changes with:

```bash
python docs/agent/scripts/validate_skill_pack.py
```

The validator checks manifest IDs and file references, mandatory skill-card sections, core pack files, local Markdown links, and the `AGENTS.md` integration. A successful validator run does not replace SDA review of the operating rules themselves.

## Activation

A concise activation prompt is provided at [`BOOTSTRAP-PROMPT.md`](BOOTSTRAP-PROMPT.md). It should be given to the agent once the skill-pack PR is merged. The repository remains the continuing source of truth; the prompt only directs the agent to it.

## Maintenance

When a repeated review failure occurs:

1. identify whether an existing skill should have prevented it;
2. strengthen the skill’s stop condition or evidence gate;
3. add a regression check where practical;
4. record the change through an ordinary documentation PR;
5. do not weaken acceptance criteria to reduce review cycles.
