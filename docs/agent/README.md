# NLI Delivery Agent Skill Pack

**Version:** 2.0  
**Status:** Proposed operational standard  
**Audience:** implementation agents, human engineers, reviewers, and operators working under the System Design Authority  
**Authority:** subordinate to `AGENTS.md`, active SDA work orders, accepted ADRs, and mandatory standards

## Purpose

This pack gives the implementation agent a repeatable operating system for delivering the **complete Equatorial Guinea National Location Infrastructure programme**.

It covers:

- authority, scope, current-state discovery, planning, semantic evidence, GitHub delivery, review remediation, maintenance isolation, operations, and self-audit;
- system architecture, public/operator/field applications, backend services, citizen and registry workflows, verification, publication, integrations, workers, analytics, infrastructure, performance, adoption, and programme planning.

It is designed to reduce avoidable review cycles caused by scope leakage, incomplete discovery, generic evidence, self-validating artefacts, simulated tests, stale heads, mixed maintenance fixes, incomplete operational planning, and inaccurate readiness claims.

The skill pack does not replace the SDA control layer. It operationalizes it.

## Authority and precedence

Use this order when instructions conflict:

1. Active SDA work order and acceptance criteria.
2. Accepted ADRs.
3. Mandatory SDA standards.
4. Root `AGENTS.md`.
5. This skill pack.
6. Existing local implementation conventions.

A skill may make a process stricter, but it may not weaken a work order or accepted standard.

## Mandatory agent loop

```text
ORIENT → CLASSIFY → PLAN → DECIDE → IMPLEMENT/MODEL
→ VERIFY → SELF-AUDIT → PUSH → EXACT-HEAD EVIDENCE
→ SDA REVIEW → FINDING-BY-FINDING REMEDIATION → ACCEPTANCE
```

The agent must not skip directly from implementation to “done.”

## Two-layer skill model

### Layer A — Cross-cutting delivery and governance (`S01–S16`)

These skills govern how every task is authorized, investigated, planned, implemented, tested, submitted, reviewed, separated from maintenance, operated, and handed off.

At minimum, every task uses:

- [`S01 — Authority, intake, and scope control`](skills/S01-authority-intake-and-scope.md)
- [`S03 — Acceptance-criteria planning and decision control`](skills/S03-acceptance-planning-and-rfi.md)
- [`S11 — Testing and semantic evidence`](skills/S11-testing-and-semantic-evidence.md)
- [`S12 — GitHub delivery and exact-head proof`](skills/S12-github-delivery-and-exact-head-proof.md)
- [`S16 — Self-audit and context handoff`](skills/S16-self-audit-and-context-handoff.md)

Add cross-cutting skills based on effects:

| Trigger | Skill |
|---|---|
| Repository or architecture discovery | [`S02`](skills/S02-repository-orientation-and-impact.md) |
| ADR, policy ambiguity, authority decision | [`S04`](skills/S04-rfi-and-adr-management.md) |
| Current schema, routes, roles, or workflow inventory | [`S05`](skills/S05-authoritative-current-state-discovery.md) |
| Canonical data model, ERD, mapping, convergence | [`S06`](skills/S06-canonical-data-model-and-convergence.md) |
| Schema migration, reference data, fixtures | [`S07`](skills/S07-database-migrations-and-reference-data.md) |
| API, identity, authorization, privacy, partner contract | [`S08`](skills/S08-api-identity-security-and-privacy.md) |
| GIS, evidence, geometry authority, publication | [`S09`](skills/S09-gis-evidence-and-publication.md) |
| UI, accessibility, localization, workflow | [`S10`](skills/S10-ui-accessibility-localization-and-workflows.md) |
| SDA review findings and rework | [`S13`](skills/S13-sda-review-remediation.md) |
| Incidental bug, CI defect, emergency/maintenance fix | [`S14`](skills/S14-maintenance-fix-isolation.md) |
| Deployment, operations, backup, restore, DR | [`S15`](skills/S15-release-operations-and-dr.md) |

### Layer B — Whole-project product and platform (`S17–S31`)

These skills ensure the agent can work across the entire project, not only a specific architecture or data-model section.

| Project surface | Skill |
|---|---|
| System architecture, bounded domains, trust zones, module ownership | [`S17`](skills/S17-system-architecture-and-domain-boundaries.md) |
| Next.js/TypeScript portals, shared UI, browser state, design system | [`S18`](skills/S18-frontend-applications-and-design-system.md) |
| FastAPI services, domain logic, persistence, transactions | [`S19`](skills/S19-backend-services-and-domain-logic.md) |
| Citizen lookup, submission, tracking, corrections, public proof | [`S20`](skills/S20-citizen-portal-and-public-services.md) |
| Registry operations, case files, roads/buildings/addresses, bulk actions | [`S21`](skills/S21-registry-operations-and-case-management.md) |
| Enumerator/supervisor mobile and offline synchronization | [`S22`](skills/S22-field-operations-mobile-and-offline-sync.md) |
| Verification, duplicates, quality, evidence review, recapture | [`S23`](skills/S23-verification-quality-and-evidence-review.md) |
| Publication, corrections, certificates, QR, signage, revocation | [`S24`](skills/S24-publication-corrections-certificates-and-signage.md) |
| Agency APIs, service clients, webhooks, notifications, reconciliation | [`S25`](skills/S25-agency-integrations-notifications-and-interoperability.md) |
| Imports, exports, workers, queues, retries, batch processing | [`S26`](skills/S26-import-export-worker-and-batch-processing.md) |
| Reporting, KPIs, analytics, statistics, national data products | [`S27`](skills/S27-reporting-analytics-and-national-data-products.md) |
| Environments, containers, ingress, secrets, IaC, deployment | [`S28`](skills/S28-infrastructure-environments-and-platform-engineering.md) |
| Load, capacity, scaling, caching, backpressure, resilience | [`S29`](skills/S29-performance-scalability-and-resilience.md) |
| Helpdesk, training, onboarding, release communication, adoption | [`S30`](skills/S30-support-training-and-change-adoption.md) |
| Roadmap, backlog, dependencies, releases, rollout, programme status | [`S31`](skills/S31-programme-planning-roadmap-and-release-management.md) |

Most substantive work requires skills from both layers. Select skills by **effects**, not by task title.

## Whole-project coverage matrix

Use [`PROJECT-COVERAGE-MATRIX.md`](PROJECT-COVERAGE-MATRIX.md) to verify coverage of:

- repository areas;
- NLI bounded domains;
- current modules;
- user roles and institutions;
- discovery, design, implementation, verification, release, operation, and improvement;
- authority, data integrity, security, GIS, accessibility, interoperability, scale, DR, adoption, and programme sequencing.

No project module or future national service is outside the skill pack. When a new recurring surface appears, update the matrix, manifest, validator, and relevant skill cards.

## Standard skill-card contract

Each skill card defines:

- **Invoke when** — task triggers.
- **Required inputs** — controlled documents and source evidence.
- **Procedure** — mandatory execution steps.
- **Outputs** — controlled artefacts to produce.
- **Stop/RFI conditions** — circumstances where guessing is prohibited.
- **Evidence gate** — proof required before claiming completion.
- **Anti-patterns** — known failure modes.

The agent must follow the card, not merely mention it.

## Non-negotiable operating rules

### 1. Scope is a hard boundary

Before changing a file, classify it as explicitly in scope, supporting evidence, unrelated maintenance, or prohibited. Use S14 for unrelated defects.

### 2. Expected evidence must be independent

Do not generate expected policy, mappings, scenarios, or dispositions from the same logic that generates observed results.

### 3. Presence is not semantic proof

A file, count, heading, route, dashboard, queue definition, or green build does not prove correctness. Execute the claimed behavior, including negative, failure, recovery, authority, and scenario cases.

### 4. Review records are immutable authority records

The implementation agent may update only the designated resolution-log section. It must not alter reviewer outcome, finding, required resolution, or disposition.

### 5. Exact-head evidence must be truthful

Use:

```text
implementation commit → exact-head CI → PR comment/metadata → SDA review record
```

Never fabricate a self-referential SHA.

### 6. Canonical authority remains singular

Frontend caches, local field stores, Redis, queues, integrations, analytics, exports, and partner systems must not become competing registry, identity, GIS, evidence, or publication authorities.

### 7. Operational completion is part of delivery

Where applicable, include migration, infrastructure, observability, backup/recovery, training, support, partner communication, performance, and rollout gates—not only code.

### 8. “Done” has four separate meanings

- **Implemented:** the artefact/code exists.
- **Verified:** named evidence passes at an exact commit.
- **Submitted:** branch is pushed and a reviewable PR exists.
- **Accepted:** SDA recorded acceptance.

State which meaning applies.

## Required task artefacts

Use these templates:

- [`task-context-pack.md`](templates/task-context-pack.md)
- [`finding-resolution-matrix.md`](templates/finding-resolution-matrix.md)
- [`exact-head-evidence.md`](templates/exact-head-evidence.md)
- [`self-audit.md`](templates/self-audit.md)

Existing SDA templates remain authoritative for work-order plans, RFIs, PR evidence, and SDA reviews.

The task context pack must name:

- selected S01–S16 skills;
- selected S17–S31 skills;
- affected repository areas, domains, modules, roles, trust zones, environments, and lifecycle stages;
- skills considered but not applicable and why.

## Validation

Validate the pack after changes with:

```bash
python docs/agent/scripts/validate_skill_pack.py
```

The validator checks skill IDs/files, required card sections, links, whole-project coverage, manifest routing, and `AGENTS.md` integration. A passing validator does not replace SDA review of the operating rules.

## Activation

Use [`BOOTSTRAP-PROMPT.md`](BOOTSTRAP-PROMPT.md) after merge. The repository remains the continuing source of truth; the prompt directs the agent to it.

## Maintenance

When repeated delivery or domain failures occur:

1. identify the skill that should have prevented the failure;
2. strengthen its stop condition, procedure, or evidence gate;
3. add a regression check where practical;
4. update the coverage matrix and manifest if a project surface is missing;
5. record the change through an ordinary documentation PR;
6. never weaken acceptance criteria merely to reduce review cycles.
