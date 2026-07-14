# Skill 03 — Work-Order Planning and Traceability

## Use when

Use whenever an SDA work order, numbered acceptance criteria, or review findings govern the task.

## Objective

Turn each requirement into a concrete change, validation, and evidence item before implementation begins.

## Required inputs

- Active work order
- Referenced ADRs and standards
- Current-state reconnaissance
- Applicable templates under `docs/sda/templates/`

## Procedure

1. Extract every requirement, acceptance criterion, prohibited approach, deliverable, dependency, and required evidence item.
2. Give each criterion a planned implementation/model location.
3. Specify the exact positive, negative, compatibility, failure, recovery, or scenario test required.
4. Identify files expected to be added, modified, removed, or generated.
5. Identify database, API, identity, security, GIS, UI, localization, operations, and documentation effects.
6. Sequence the work into independently reviewable checkpoints.
7. Identify decisions already authorized versus decisions requiring an ADR or RFI.
8. Define the evidence-binding method and exact-head closeout process.
9. Record applicable skills and change class.
10. Verify no criterion is represented only by a generic phrase or file-presence check.

## Required output

Use `docs/sda/templates/implementation-plan.md` and include a matrix like:

| Criterion | Planned change/decision | Exact file/section | Executed test/evidence | Risk/RFI |
|---|---|---|---|---|

Every criterion must appear once and may link to several tests.

## Quality checks

- Criteria must not all point to the same generic artifact.
- “Create design pack” is not a criterion plan.
- “Run CI” is not a test plan unless the exact CI assertion is named.
- Design criteria require semantic consistency checks, not just document presence.
- Migration criteria require real database behavior where specified.

## Stop and escalate when

- A criterion cannot be made testable.
- Two criteria require conflicting behavior.
- A prohibited approach appears necessary.
- Required authority or data is missing.
- The work order would need to be expanded materially.

## Anti-patterns

- Starting implementation with unmapped criteria.
- Marking all criteria `PASS` because one report is green.
- Copying the same evidence text into every row.
- Treating residual conditions as completed work.
- Deferring core architecture to the later implementer without an ADR/RFI.
