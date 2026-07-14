# Skill 30 — Programme Planning, Roadmap, and Release Management

## Use when

Use for module maturity, roadmap, work-order sequencing, backlog, dependency planning, release trains, rollout waves, milestone review, benefits tracking, technical debt, or programme status.

## Objective

Convert the NLI vision into an evidence-based, dependency-aware delivery programme where progress is measured by accepted capability and operational readiness—not feature count alone.

## Procedure

1. Maintain the programme capability map:
   - NLI bounded domains;
   - product modules;
   - user roles/institutions;
   - environments;
   - readiness level;
   - open risks/RFIs;
   - accountable owners.
2. Assess module maturity using evidence-based stages:
   - not designed;
   - proposed;
   - implemented;
   - tested;
   - pilot-ready;
   - agency-ready;
   - publication-ready;
   - national-production-ready.
3. Build dependency order from architecture, data, identity, authority, infrastructure, operations, and institutional decisions.
4. Break strategy into SDA work orders with clear boundaries, acceptance criteria, evidence, and risk treatment.
5. Keep product backlog items linked to work orders, ADRs, risks, modules, roles, and benefits.
6. Distinguish critical-path blockers, enabling foundations, user-value features, operational readiness, and deferred enhancements.
7. Plan releases and rollout waves by artifact, environment, institution/region, migration, training, support, monitoring, and rollback readiness.
8. Define entry/exit gates for development, test, staging, controlled pilot, agency rollout, publication, and production.
9. Track progress by accepted outcomes, unresolved conditions, operational evidence, and institutional readiness.
10. Record dependencies on procurement, licensing, connectivity, data authority, identity provider, staffing, and government decisions without assuming they are resolved.
11. Review capacity, cost, risk, security, DR, support, adoption, and benefits before expanding rollout.
12. Produce truthful executive/programme reporting with exact dates, decisions, blockers, next work orders, and confidence.

## Required artifacts

- Capability/module maturity matrix
- Dependency and critical-path map
- Work-order roadmap
- Risk/RFI/decision dependencies
- Release and rollout calendar
- Entry/exit gate checklist
- Resource/owner matrix
- Benefits/outcome measures
- Technical debt and accepted-condition register
- Executive progress report

## Progress scoring rules

Overall progress must not be a simple average of feature completion. Weight critical readiness domains heavily:

- canonical data and migration safety;
- identity and scoped authority;
- security/privacy/audit;
- publication authority;
- GIS authority;
- production platform;
- operations and DR;
- institutional adoption.

A mature UI cannot compensate for a production-blocking identity or data-integrity gap.

## Stop and escalate when

- A release is scheduled before its prerequisites/owners exist.
- A module is called complete without accepted evidence.
- A rollout depends on unresolved authority, migration, security, or DR.
- A date is being promised despite an unbounded dependency.
- A programme score hides critical red risks behind many green low-risk features.

## Anti-patterns

- Roadmaps made only of feature names and dates.
- Calling an MVP milestone government production.
- Counting open PRs or lines of code as progress.
- Starting every workstream simultaneously.
- Ignoring training, support, data migration, monitoring, or rollback in release plans.
- Treating institutional approvals as automatic.
- Reporting “90% complete” while a P0 authority or recovery blocker remains.
