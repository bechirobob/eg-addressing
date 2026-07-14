# NLI Implementation Agent Skills System

**Status:** Proposed operating capability for repository agents  
**Authority:** Subordinate to root `AGENTS.md`, active SDA work orders, accepted ADRs, and mandatory standards  
**Purpose:** Make implementation work faster, more consistent, and easier to review across the **entire National Location Infrastructure programme** without weakening government-grade controls

## 1. Why this exists

The repository already defines what must be protected. This skills system defines **how the implementation agent should repeatedly perform the work across every layer and product domain**.

It converts recurring activities into reusable procedures so the agent does not rediscover the same process in every task. The skills are deliberately tool-agnostic: an agent may use a GitHub connector, shell, editor, browser automation, database client, mapping tools, object storage, or CI system, but the required reasoning, evidence, and stop conditions remain the same.

A skill does not override the active work order. It helps execute that work order correctly.

## 2. Two-layer competency model

The system has two complementary layers.

### Layer A — Cross-cutting delivery and governance skills (`01–15`)

These govern how the agent receives work, investigates the repository, plans, controls scope, tests, documents, submits evidence, and responds to SDA review.

They apply across all modules.

### Layer B — Whole-project product and platform skills (`16–30`)

These govern the actual product, domain, architecture, application, integration, analytics, infrastructure, operations, adoption, and programme-delivery work needed to build and sustain the complete NLI.

Most substantive tasks require skills from **both layers**.

Example:

```text
Build offline field synchronization
→ 01 intake
→ 02 reconnaissance
→ 03 work-order traceability
→ 05 scope/exact-head control
→ 07 data semantics
→ 09 security/privacy/evidence
→ 10 GIS
→ 12 CI/evidence
→ 16 architecture/domain boundaries
→ 18 backend services
→ 21 field/offline operations
→ 25 worker/batch processing
→ 28 performance/resilience
→ 15 PR remediation
```

## 3. Operating loop

Every task follows this loop:

```text
ORIENT → CLASSIFY → PLAN → IMPLEMENT/MODEL → VALIDATE → EVIDENCE → REVIEW → REMEDIATE → CLOSE
```

1. **Orient:** identify repository, branch, exact baseline, active work order, applicable standards, current evidence, and affected product domains.
2. **Classify:** determine change class, affected trust zones, authority boundary, and required cross-cutting/domain skills.
3. **Plan:** map every acceptance criterion to files, product behavior, tests, evidence, risks, and RFIs.
4. **Implement/model:** make only authorized changes in reviewable increments.
5. **Validate:** execute real positive, negative, migration, security, accessibility, spatial, recovery, performance, workflow, or semantic checks appropriate to the work.
6. **Evidence:** bind claims to an exact commit, test, artifact, query, screenshot, trace, projection, runbook exercise, or controlled decision.
7. **Review:** submit a draft PR using the repository evidence contract.
8. **Remediate:** resolve each SDA finding with specific evidence; never overwrite reviewer disposition.
9. **Close:** verify exact-head CI, scope, documentation, residual risk, module ownership, and readiness language.

## 4. Mandatory routing — cross-cutting skills

Before changing files, the agent must select the applicable skills and record them in the implementation plan.

| Trigger | Required skill |
|---|---|
| Any new task or ambiguous instruction | `01-task-intake-and-routing` |
| Unfamiliar repository area or current-state uncertainty | `02-repository-reconnaissance` |
| Active work order or acceptance criteria | `03-work-order-planning-and-traceability` |
| Architecture choice, ambiguity, authority question, new dependency/state/data class | `04-rfi-and-architecture-decisions` |
| Branch creation, scope boundary, exact-head proof, or unrelated defect discovered | `05-scope-git-and-exact-head-control` |
| Schema, migration, reference data, fixtures, PostGIS, or data transition | `06-database-migrations-and-postgis` |
| Canonical entities, field mappings, vocabularies, temporal model, or convergence plan | `07-data-model-and-semantic-consistency` |
| API route, OpenAPI, identity, roles, permissions, scopes, sessions, or partner integration | `08-api-identity-and-authorization` |
| Threats, privacy, evidence objects, audit, retention, export, or sensitive data | `09-security-privacy-audit-and-evidence` |
| Geometry, boundaries, CRS, accuracy, provenance, geocoding, or spatial quality | `10-gis-and-geometry-governance` |
| UI workflow, forms, role experience, accessibility, localization, screenshots | `11-ui-workflows-accessibility-and-localization` |
| Tests, CI, negative cases, release gates, deterministic generation, image/runtime proof | `12-testing-ci-and-release-evidence` |
| Health, readiness, backup, restore, runbooks, capacity, incident, DR | `13-operations-backup-and-disaster-recovery` |
| Documentation, ADRs, RFIs, work orders, controlled records, claims | `14-controlled-documentation-and-decisions` |
| Draft PR, evidence matrix, SDA findings, rework, acceptance preparation | `15-pr-evidence-and-review-remediation` |

## 5. Mandatory routing — whole-project product and platform skills

| Project surface or task | Required domain skill |
|---|---|
| System architecture, bounded domains, trust zones, module ownership, dependency direction | `16-system-architecture-and-domain-boundaries` |
| Next.js portal, shared UI, browser state, design system, client data access | `17-frontend-applications-and-design-system` |
| FastAPI application services, domain logic, persistence adapters, transactions | `18-backend-services-and-domain-logic` |
| Public lookup, citizen submission, tracking, corrections, proof, privacy notices | `19-citizen-portal-and-public-services` |
| Registry administration, case files, roads/buildings/addresses, operators, approvals | `20-registry-operations-and-case-management` |
| Enumerator/supervisor workflows, devices, assignments, GPS capture, offline sync | `21-field-operations-mobile-and-offline-sync` |
| Verification, duplicate detection, evidence review, quality, discrepancy resolution | `22-verification-quality-and-evidence-review` |
| Publication, correction, disputes, certificates, proofs, signage, revocation | `23-publication-corrections-certificates-and-signage` |
| Agencies, service clients, partner APIs, webhooks, notifications, reconciliation | `24-agency-integrations-notifications-and-interoperability` |
| Imports, exports, worker jobs, queues, retries, bulk processing, generated artifacts | `25-import-export-worker-and-batch-processing` |
| Reports, KPIs, dashboards, analytics, statistical extracts, data products | `26-reporting-analytics-and-national-data-products` |
| Environment topology, containers, ingress, secrets, infrastructure as code, deployment | `27-infrastructure-environments-and-platform-engineering` |
| Load, latency, capacity, scaling, caching, queues, failure tolerance, resilience | `28-performance-scalability-and-resilience` |
| Helpdesk, support, training, runbooks, adoption, operational change and user readiness | `29-support-training-and-change-adoption` |
| Roadmap, backlog, sequencing, dependencies, release trains, module maturity, benefits | `30-programme-planning-roadmap-and-release-management` |

Multiple domain skills may apply. A publication feature with a new public certificate may require skills 17, 18, 20, 23, 24, 25, 27, 28, and 29 in addition to the cross-cutting skills.

## 6. Complete project coverage

The project coverage matrix is maintained at:

```text
docs/agent-skills/PROJECT-COVERAGE-MATRIX.md
```

It maps:

- repository areas;
- NLI bounded domains;
- product modules;
- user roles;
- service lifecycle stages;
- national-readiness concerns;
- required skill combinations.

No feature or module should be treated as “outside the skills system.” If a new project surface appears, update the matrix and add or revise the appropriate skill before the capability becomes a recurring implementation pattern.

## 7. Change-class minimums

### Class A — National authority or trust

Identity, publication, public codes, official geometry, bulk export, sensitive data, destructive operations, privileged access, audit integrity, retention, or institutional scope.

Minimum skills:

```text
01, 02, 03, 04, 05, 08 or 10, 09, 12, 14, 15
+ every affected project-domain skill from 16–30
```

Requires an explicit work order or written SDA authority, threat/abuse analysis, negative authorization tests, institutional/territorial scope analysis, operational impact, and exact-head SDA evidence.

### Class B — Core platform or product domain

Schema, APIs, citizen/operator/field workflows, evidence handling, integrations, worker jobs, analytics, deployment, resilience, or material refactoring.

Minimum skills:

```text
01, 02, 03, 05, applicable cross-cutting skills, 12, 14, 15
+ every affected project-domain skill from 16–30
```

### Class C — Controlled maintenance

Compatible bug fixes, copy/localization corrections, dependency maintenance, or low-risk refactoring with no authority/data-model effect.

Minimum skills:

```text
01, 02, 05, 12, 15
+ the directly affected application/platform skill
```

Uncertainty is classified upward.

## 8. Skill invocation record

The implementation plan must contain:

```text
Skills invoked:
- 01-task-intake-and-routing — new work order task
- 12-testing-ci-and-release-evidence — exact-head proof required
- 17-frontend-applications-and-design-system — operator portal changes
- 20-registry-operations-and-case-management — registry approval workflow changes

Skills considered but not applicable:
- 21-field-operations-mobile-and-offline-sync — no field/mobile behavior changes
- 26-reporting-analytics-and-national-data-products — no reporting projection changes
```

A missing skill is not automatically a defect, but the agent must be able to explain why a material domain was not assessed.

## 9. Evidence hierarchy

From strongest to weakest:

1. Real environment/database/browser/device/runtime execution tied to an exact commit.
2. Deterministic CI job tied to an exact commit.
3. Reproducible local command with retained artifact and environment description.
4. Static semantic validation against authoritative metadata.
5. Source inspection.
6. File presence, string presence, counts, or prose claim.

Lower-level evidence cannot substitute for higher-level evidence when the work order explicitly requires execution.

Examples:

- A source string saying an advisory lock exists is not a concurrency test.
- A SQL file parsing is not proof that it creates a valid PostGIS schema.
- Seven scenario names are not seven scenario tests.
- A `PASS` report is not evidence unless every claimed assertion is actually executed.
- A hidden UI control is not authorization evidence.
- A route existing is not proof that the citizen or operator workflow is usable.
- A queue job definition is not proof of idempotent retry and reconciliation.
- A dashboard screenshot is not proof that the analytical data product is governed or reproducible.

## 10. Exact-head rule

Evidence applies to the commit that produced it.

A committed document cannot contain its own final commit SHA without changing that SHA. Use this non-circular chain:

```text
implementation commit → exact-head CI → immutable PR comment/metadata → SDA review record
```

The SDA review record names the implementation commit and receives a later, separate commit SHA.

## 11. Boundary rule

When unrelated work is discovered:

- stop expanding the active scope;
- document the defect;
- classify it;
- create a separate branch/PR or RFI;
- preserve a valid fix without contaminating the active work order.

A good fix in the wrong work order is still a scope violation.

## 12. Completion rule

The agent may say **implementation complete** only when:

- every acceptance criterion has a truthful status;
- required cross-cutting and domain skills were completed;
- no required check was disabled;
- exact-head evidence exists;
- the branch and PR scope match the work order;
- documentation and generated contracts are current;
- affected modules, roles, workflows, integrations, and operational paths are assessed;
- RFIs and residual risks are explicit;
- the PR remains in the state required by the work order.

The agent must not say **accepted**, **publication-ready**, or **national-production-ready** unless the required authority has recorded that decision.

## 13. Files

```text
docs/agent-skills/
  README.md
  AGENT-BOOTSTRAP.md
  FAILURE-PREVENTION.md
  PROJECT-COVERAGE-MATRIX.md
  skills/
    01-task-intake-and-routing/SKILL.md
    02-repository-reconnaissance/SKILL.md
    03-work-order-planning-and-traceability/SKILL.md
    04-rfi-and-architecture-decisions/SKILL.md
    05-scope-git-and-exact-head-control/SKILL.md
    06-database-migrations-and-postgis/SKILL.md
    07-data-model-and-semantic-consistency/SKILL.md
    08-api-identity-and-authorization/SKILL.md
    09-security-privacy-audit-and-evidence/SKILL.md
    10-gis-and-geometry-governance/SKILL.md
    11-ui-workflows-accessibility-and-localization/SKILL.md
    12-testing-ci-and-release-evidence/SKILL.md
    13-operations-backup-and-disaster-recovery/SKILL.md
    14-controlled-documentation-and-decisions/SKILL.md
    15-pr-evidence-and-review-remediation/SKILL.md
    16-system-architecture-and-domain-boundaries/SKILL.md
    17-frontend-applications-and-design-system/SKILL.md
    18-backend-services-and-domain-logic/SKILL.md
    19-citizen-portal-and-public-services/SKILL.md
    20-registry-operations-and-case-management/SKILL.md
    21-field-operations-mobile-and-offline-sync/SKILL.md
    22-verification-quality-and-evidence-review/SKILL.md
    23-publication-corrections-certificates-and-signage/SKILL.md
    24-agency-integrations-notifications-and-interoperability/SKILL.md
    25-import-export-worker-and-batch-processing/SKILL.md
    26-reporting-analytics-and-national-data-products/SKILL.md
    27-infrastructure-environments-and-platform-engineering/SKILL.md
    28-performance-scalability-and-resilience/SKILL.md
    29-support-training-and-change-adoption/SKILL.md
    30-programme-planning-roadmap-and-release-management/SKILL.md
```

## 14. Adoption

The root `AGENTS.md` points every implementation agent to this system. The active task should always be governed by:

```text
AGENTS.md
→ active SDA work order
→ referenced ADRs and standards
→ applicable cross-cutting skills
→ applicable project-domain skills
→ implementation plan
→ exact-head evidence
→ SDA review
```
