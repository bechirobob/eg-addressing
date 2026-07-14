# NLI Implementation Agent Skills System

**Status:** Proposed operating capability for repository agents  
**Authority:** Subordinate to root `AGENTS.md`, active SDA work orders, accepted ADRs, and mandatory standards  
**Purpose:** Make implementation work faster, more consistent, and easier to review without weakening government-grade controls

## 1. Why this exists

The repository already defines what must be protected. This skills system defines **how the implementation agent should repeatedly perform the work**.

It converts recurring activities into reusable procedures so the agent does not rediscover the same process in every task. The skills are deliberately tool-agnostic: an agent may use a GitHub connector, shell, editor, browser automation, database client, or CI system, but the required reasoning, evidence, and stop conditions remain the same.

A skill does not override the active work order. It helps execute that work order correctly.

## 2. Operating loop

Every task follows this loop:

```text
ORIENT → CLASSIFY → PLAN → IMPLEMENT/MODEL → VALIDATE → EVIDENCE → REVIEW → REMEDIATE → CLOSE
```

1. **Orient:** identify repository, branch, exact baseline, active work order, applicable standards, and current evidence.
2. **Classify:** determine change class, affected domains, authority boundary, and required skills.
3. **Plan:** map every acceptance criterion to files, tests, evidence, risks, and RFIs.
4. **Implement/model:** make only authorized changes in reviewable increments.
5. **Validate:** execute real positive, negative, migration, security, accessibility, spatial, recovery, or semantic checks appropriate to the work.
6. **Evidence:** bind claims to an exact commit, test, artifact, query, screenshot, or controlled decision.
7. **Review:** submit a draft PR using the repository evidence contract.
8. **Remediate:** resolve each SDA finding with specific evidence; never overwrite reviewer disposition.
9. **Close:** verify exact-head CI, scope, documentation, residual risk, and readiness language.

## 3. Mandatory routing

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

Multiple skills normally apply. A database-backed API change, for example, usually requires skills 01, 02, 03, 05, 06, 08, 09, 12, 14, and 15.

## 4. Change-class minimums

### Class A — National authority or trust

Identity, publication, public codes, official geometry, bulk export, sensitive data, destructive operations, privileged access, audit integrity, or retention.

Minimum skills:

```text
01, 02, 03, 04, 05, 08 or 10, 09, 12, 14, 15
```

Requires an explicit work order or written SDA authority, threat/abuse analysis, negative authorization tests, institutional/territorial scope analysis, and exact-head SDA evidence.

### Class B — Core platform

Schema, APIs, field workflows, evidence handling, integrations, deployment, resilience, or material refactoring.

Minimum skills:

```text
01, 02, 03, 05, applicable domain skills, 12, 14, 15
```

### Class C — Controlled maintenance

Compatible bug fixes, copy/localization corrections, dependency maintenance, or low-risk refactoring with no authority/data-model effect.

Minimum skills:

```text
01, 02, 05, 12, 15
```

Uncertainty is classified upward.

## 5. Skill invocation record

The implementation plan must contain:

```text
Skills invoked:
- 01-task-intake-and-routing — why
- 06-database-migrations-and-postgis — why
- 12-testing-ci-and-release-evidence — why

Skills considered but not applicable:
- 11-ui-workflows-accessibility-and-localization — no user-visible change
```

A missing skill is not automatically a defect, but the agent must be able to explain why a material domain was not assessed.

## 6. Evidence hierarchy

From strongest to weakest:

1. Real environment/database/browser/runtime execution tied to an exact commit.
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

## 7. Exact-head rule

Evidence applies to the commit that produced it.

A committed document cannot contain its own final commit SHA without changing that SHA. Use this non-circular chain:

```text
implementation commit → exact-head CI → immutable PR comment/metadata → SDA review record
```

The SDA review record names the implementation commit and receives a later, separate commit SHA.

## 8. Boundary rule

When unrelated work is discovered:

- stop expanding the active scope;
- document the defect;
- classify it;
- create a separate branch/PR or RFI;
- preserve a valid fix without contaminating the active work order.

A good fix in the wrong work order is still a scope violation.

## 9. Completion rule

The agent may say **implementation complete** only when:

- every acceptance criterion has a truthful status;
- required skills were completed;
- no required check was disabled;
- exact-head evidence exists;
- the branch and PR scope match the work order;
- documentation and generated contracts are current;
- RFIs and residual risks are explicit;
- the PR remains in the state required by the work order.

The agent must not say **accepted**, **publication-ready**, or **national-production-ready** unless the required authority has recorded that decision.

## 10. Files

```text
docs/agent-skills/
  README.md
  AGENT-BOOTSTRAP.md
  FAILURE-PREVENTION.md
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
```

## 11. Adoption

The root `AGENTS.md` points every implementation agent to this system. The active task should always be governed by:

```text
AGENTS.md
→ active SDA work order
→ referenced ADRs and standards
→ applicable skills
→ implementation plan
→ exact-head evidence
→ SDA review
```
