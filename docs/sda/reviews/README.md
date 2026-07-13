# SDA Review Records

This directory contains immutable, work-order-specific System Design Authority review and acceptance records.

## Naming

```text
<WORK-ORDER-ID>-review-<sequence>.md
```

Example:

```text
NLI-WO-001-review-01.md
```

Use `docs/sda/templates/sda-review.md`.

## Rules

- A review identifies the exact pull request and commit assessed.
- Findings use stable IDs and remain visible after resolution.
- Follow-up responses point to commits, tests, artefacts, or recorded decisions.
- A later review may supersede an outcome, but the earlier record is not erased.
- Acceptance applies only to the named work order, commit, evidence set, and environment boundary.
- Work-order acceptance does not automatically approve national production, official publication, sensitive-data release, or agency onboarding.
- Conditions and accepted risks must be copied to the risk register or an explicitly linked controlled record.

The first implementation review will be created after the agent opens the pull request for `NLI-WO-001`.
