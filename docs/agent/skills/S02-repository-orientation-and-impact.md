# S02 — Repository Orientation and Impact Analysis

## Invoke when

- entering an unfamiliar domain or module;
- planning a cross-cutting change;
- conducting an architecture audit;
- changing dependencies, data flows, workflows, or operational behavior;
- review findings reveal that the initial impact assessment was incomplete.

## Required inputs

- repository tree and current branch;
- architecture baseline and target architecture;
- active work order;
- current tests, workflows, migrations, API routes, and operator scripts;
- current PR diff, if remediation.

## Procedure

### 1. Identify bounded domains

Map the task to one or more NLI domains:

- Identity and Trust;
- Administrative Geography;
- Location Registry;
- Field Operations;
- Evidence and Verification;
- Publication and Corrections;
- Agency Integration;
- Audit, Reporting, and Analytics;
- Platform Operations.

### 2. Identify execution surfaces

Inventory affected:

- frontend routes/components;
- API routes and models;
- application/domain services;
- database tables, migrations, and queries;
- workers and queues;
- Redis/cache behavior;
- object storage and evidence metadata;
- GIS/map/geocoder behavior;
- generated contracts;
- CI workflows;
- runbooks and operator commands.

### 3. Build a writer-reader matrix

For each affected entity or artefact, record:

| Object | Writers | Readers | Authority | Public/protected projection | Failure effect |
|---|---|---|---|---|---|

Do not infer authority merely from the number of readers or current table name.

### 4. Trace data and control flow

Follow the complete path:

```text
input → validation → authorization → domain decision → persistence
→ audit/evidence → async work → projection/export/publication → recovery
```

Identify every trust boundary and external dependency.

### 5. Identify compatibility surfaces

Check:

- API/OpenAPI clients;
- generated TypeScript types;
- CSV/export consumers;
- public codes and URLs;
- stored workflow/status values;
- database readers outside the main API;
- operational scripts and reports;
- training material and screenshots.

### 6. Identify hidden operational effects

Ask whether the change affects:

- application startup;
- deployment sequence;
- data backfill;
- backup/restore;
- worker retry/idempotency;
- monitoring/alerts;
- secrets or configuration;
- local development/bootstrap;
- field/offline behavior.

## Outputs

- domain and component map;
- writer-reader-authority matrix;
- trust-boundary/data-flow summary;
- compatibility inventory;
- expected changed-file list;
- risks and unknowns.

## Stop or RFI conditions

Stop when:

- two components both appear authoritative for the same fact;
- a data writer is found outside the planned change boundary;
- an undocumented external consumer may break;
- a status or identifier meaning is ambiguous;
- an operational script mutates state outside the accepted lifecycle;
- current behavior cannot be established from source and executable evidence.

## Evidence gate

The implementation plan must cite concrete source paths for:

- every writer;
- every public/protected projection;
- every relevant database object;
- every compatibility surface;
- every operational script affected.

## Anti-patterns

- Searching only for filenames and ignoring runtime imports or generated artefacts.
- Reviewing API code without persistence and operational scripts.
- Treating a UI route list as a workflow model.
- Assuming a proposal document is the operational architecture.
- Refactoring a large module without first mapping domain responsibilities and external contracts.
