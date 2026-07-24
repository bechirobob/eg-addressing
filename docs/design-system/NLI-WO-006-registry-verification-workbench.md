# NLI-WO-006 — Registry and Verification Government Workbench

**Status:** Implementation in progress  
**Design authority:** BGEDS 1.0  
**Functional baseline:** `850b91cd36644f8c72cb71120159bdd6430fa548`

## Objective

Move Address Registry and Verification into the protected government shell as a continuous queue–record–evidence–decision workflow while preserving the existing API, role, audit, lifecycle, and publication authorities.

## Operating model

Routine list loading, filtering, routing context, evidence checks, and status presentation are automated. Operators intervene for exceptions, corrections, evidence decisions, registry creation, and archive actions.

## Registry workspace

The registry workspace MUST provide:

- authoritative address, road, and building registers;
- one search surface across the active register;
- territorial and publication-state filtering;
- queue/list selection with a stable selected-record inspector;
- controlled create operations for editors and administrators;
- archive operations restricted to administrators;
- explicit handoff to verification for records requiring evidence decisions;
- cookie-session and bearer-session support;
- no false implication that registry-ready means published.

## Verification workspace

The verification workspace MUST provide:

- only submitted and under-review records in the active decision queue;
- stable selected submission and evidence inspector;
- evidence completeness and review-state summaries;
- protected evidence download and per-file decisions;
- approve, rework, reject, and under-review transitions through existing endpoints;
- promotion handoff back to the registry after approval;
- public-trust lookup kept secondary to operational review;
- decision disabling reasons visible before action.

## Preserved authority

This work order does not change database schema, migrations, API contracts, authentication rules, authorization rules, audit requirements, lifecycle state definitions, publication controls, citizen capture, or production configuration.

## Evidence gates

- frontend build and all existing guards;
- registry and verification workbench source guard;
- exact-head browser evidence on desktop, tablet, and mobile;
- role-denial confirmation for viewer and agency-viewer roles;
- no public/citizen regression;
- no AI/ChatGPT attribution;
- official coat of arms, navigation icons, and BeCoreOps delivery attribution retained.
