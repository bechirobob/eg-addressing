# Skill 02 — Repository Reconnaissance

## Use when

Use before changing an unfamiliar area, reconstructing current behavior, responding to an SDA finding, or making a claim about what exists.

## Objective

Build an evidence-based current-state map of the affected system so implementation is based on reality rather than filenames, README claims, or assumed architecture.

## Required inputs

- Exact baseline commit/branch
- Active work order and findings
- Repository source, migrations, tests, CI, and controlled documentation
- Runtime/development environment where execution is required

## Procedure

1. Record exact commit and branch.
2. Inspect repository structure and locate every implementation surface affected by the task.
3. Trace the behavior end to end:
   - entry route/command;
   - authentication and authorization;
   - application/domain logic;
   - persistence and external dependencies;
   - audit/evidence effects;
   - response/UI/output;
   - tests and operations.
4. Inspect accepted migrations and current database behavior. Query a migrated PostgreSQL/PostGIS catalog when exact schema inventory matters.
5. Generate or inspect actual OpenAPI when route/request/response behavior matters.
6. Inspect existing tests, smoke checks, workflows, runbooks, and evidence—not only production code.
7. Identify competing authorities, duplicated concepts, hidden writers/readers, status strings, configuration paths, and generated artifacts.
8. Compare documentation claims with implementation and record discrepancies.
9. Produce an affected-file and dependency map.

## Required output

- Exact baseline
- Current component/data-flow map
- Affected domains and files
- Current invariants and known gaps
- Existing tests/evidence
- External dependencies
- Assumptions and unknowns
- Risks and likely RFIs

## Evidence standard

Prefer:

```text
runtime/database/OpenAPI execution → CI/artifact → source inspection → documentation
```

When sources disagree, describe the disagreement and identify the operational authority.

## Stop and escalate when

- Two implementations both appear authoritative.
- Current state cannot be reconstructed without real data or institutional input.
- Documentation presents a proposal as implemented behavior.
- An apparently unrelated component writes or authorizes the same state.

## Anti-patterns

- Searching for one function and assuming the whole workflow is understood.
- Treating file modification time as correctness.
- Assuming migrations match runtime without applying them.
- Assuming OpenAPI response fields exist when handlers return dynamic dictionaries.
- Ignoring scripts, CI, fixtures, restore tools, or operator paths.
