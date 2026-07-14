# S31 — Programme Planning, Roadmap, and Release Management

## Invoke when

- assessing module maturity, roadmap, backlog, dependencies, milestones, release trains, or rollout waves;
- creating work-order sequence, programme status, benefits, technical debt, or progress scores;
- preparing pilot, agency, publication, or production gates.

## Required inputs

- NLI bounded-domain and module map;
- current work orders, reviews, risks, RFIs, ADRs, and evidence;
- institutional owners and dependencies;
- environment, migration, training, support, security, capacity, and DR readiness;
- expected programme outcomes/benefits.

## Procedure

1. Maintain capability map by domain, module, role, environment, owner, readiness, evidence, risk, and RFI.
2. Assess maturity as not designed, proposed, implemented, tested, pilot-ready, agency-ready, publication-ready, or national-production-ready.
3. Build dependency order across architecture, data, identity, authority, infrastructure, operations, adoption, and institutional decisions.
4. Convert strategy into bounded SDA work orders with acceptance criteria and risk treatment.
5. Link backlog items to work orders, ADRs, risks, modules, roles, dependencies, and benefits.
6. Separate critical blockers, enabling foundations, user-value features, operational readiness, and deferred enhancements.
7. Plan releases/rollout waves by artifact, environment, institution/region, migration, training, support, monitoring, and rollback.
8. Define entry/exit gates for development, test, staging, pilot, agency rollout, publication, and production.
9. Track progress by accepted outcomes, unresolved conditions, operational evidence, and institutional readiness—not feature count.
10. Record procurement, licensing, connectivity, data authority, identity provider, staffing, and policy dependencies without assuming resolution.
11. Review cost/capacity/risk/security/DR/support/adoption/benefits before expansion.
12. Produce truthful programme reporting with exact dates, decisions, blockers, confidence, and next action.

## Outputs

- capability/module maturity matrix;
- dependency and critical-path map;
- work-order roadmap and backlog traceability;
- risk/RFI/decision dependencies;
- release/rollout calendar and gates;
- owner/resource/benefit matrix;
- technical-debt/condition register;
- executive programme status.

## Stop or RFI conditions

Stop when:

- a release is scheduled before prerequisites/owners exist;
- a module is called complete without accepted evidence;
- rollout depends on unresolved authority, migration, security, or DR;
- a date is promised despite an unbounded dependency;
- a progress score hides critical red risks behind many low-risk features.

## Evidence gate

Before review:

- all modules/domains/roles/environments have evidence-based maturity;
- dependencies and critical path are explicit;
- rollout gates include migration, identity, security, training, support, monitoring, and recovery;
- progress statements distinguish implemented, verified, submitted, and accepted;
- benefits, owners, risks, confidence, and next actions are traceable.

## Anti-patterns

- Roadmaps made only of features and dates.
- Calling an MVP milestone government production.
- Counting lines, commits, or open PRs as progress.
- Starting every workstream simultaneously.
- Ignoring training, support, migration, monitoring, or rollback.
- Treating institutional approval as automatic.
- Reporting 90% complete with open P0 blockers.
