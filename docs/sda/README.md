# System Design Authority

This directory is the version-controlled control layer for the Equatorial Guinea National Location Infrastructure (NLI). It defines how architecture is decided, how implementation work is issued, what evidence is required, and how a change becomes accepted.

The national addressing platform is the first service on the NLI. The present implementation remains a controlled pilot until an explicit production-readiness decision is recorded.

## Authority and document order

Read documents in this order:

1. [`../../AGENTS.md`](../../AGENTS.md) — mandatory repository-wide instructions.
2. [`charter.md`](charter.md) — authority, governance, and decision process.
3. The active work order under [`work-orders/`](work-orders/).
4. Accepted decisions under [`adrs/`](adrs/).
5. Mandatory engineering standards under [`standards/`](standards/).
6. [`target-reference-architecture.md`](target-reference-architecture.md).
7. [`architecture-baseline.md`](architecture-baseline.md) and [`risk-register.md`](risk-register.md).

When these documents conflict, the precedence rules in `AGENTS.md` apply. Material ambiguity must be raised as an RFI rather than resolved by assumption.

## Current control state

- SDA charter: **established**
- Current-state baseline: **v0.1**
- Target reference architecture: **v0.1**
- Risk register: **active and controlled**
- Accepted implementation work: [`NLI-WO-001 — Controlled Database and Reference-Data Lifecycle`](work-orders/NLI-WO-001-closeout.md)
- Active design-authority work order: [`NLI-WO-002 — Canonical National Location Data Model`](work-orders/NLI-WO-002-canonical-national-location-data-model.md)
- National production status: **not approved**
- Official publication authority: **not established in the executable workflow**

## Directory structure

```text
docs/sda/
  README.md
  charter.md
  architecture-baseline.md
  target-reference-architecture.md
  risk-register.md
  standards/       Mandatory engineering rules
  adrs/            Accepted architecture decisions
  work-orders/     Issued directives and immutable closeout records
  templates/       Required evidence and RFI formats
  reviews/         SDA acceptance and rework records
```

## Controlled delivery cycle

1. **Issue** — the SDA creates a work order with scope, constraints, acceptance criteria, and required evidence.
2. **Plan** — the implementation agent maps its plan to every acceptance criterion before coding or modelling.
3. **Implement or model** — changes are made on a dedicated branch with tests, migrations, diagrams, and documentation appropriate to the work order.
4. **Evidence** — the pull request records criterion-by-criterion proof, operational effects, and residual risk.
5. **Review** — the SDA classifies findings as Blocker, Required, Advisory, Accepted Risk, or Architecture Decision Required.
6. **Correct** — the implementation agent resolves each finding with a commit, test, evidence item, RFI, or risk request.
7. **Decide** — the SDA records `ACCEPTED`, `ACCEPTED WITH RECORDED CONDITIONS`, `REWORK REQUIRED`, or `REJECTED — ARCHITECTURAL REDESIGN REQUIRED`.
8. **Institutionalize** — durable decisions are moved into standards or ADRs so future work inherits them.

Implementation completion is not acceptance. Passing CI is required evidence, not sole proof of government readiness.

## Change classes

- **Class A — National authority or trust:** identity, publication, address-code grammar, official geometry, data classification, bulk exports, destructive operations, institutional scope. Requires explicit SDA approval and enhanced evidence.
- **Class B — Core platform:** schema, APIs, workflows, evidence handling, integrations, deployment, resilience. Requires a work order or explicit inclusion in an approved work order.
- **Class C — Controlled maintenance:** compatible defect fixes, copy/localization corrections, and low-risk refactoring. Requires normal tests and review. A change becomes Class A or B when its real effects cross those boundaries.

Any uncertainty about class is resolved upward.

## Readiness language

Use readiness terms precisely:

- `implemented`: code exists;
- `tested`: named evidence exists;
- `pilot-ready`: controlled pilot gates are satisfied;
- `agency-ready`: scoped institutional access and operations are satisfied;
- `publication-ready`: authority, audit, data, and release gates are satisfied;
- `national-production-ready`: explicitly approved by the SDA and Programme Owner.

## Templates

- [`templates/implementation-plan.md`](templates/implementation-plan.md)
- [`templates/rfi.md`](templates/rfi.md)
- [`templates/pull-request-evidence.md`](templates/pull-request-evidence.md)
- [`templates/sda-review.md`](templates/sda-review.md)

Do not create informal substitutes for these records when a controlled template applies.
