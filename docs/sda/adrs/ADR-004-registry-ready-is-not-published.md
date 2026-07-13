# ADR-004 — Registry-Ready Is Not Officially Published

**Status:** Accepted  
**Date:** 2026-07-13  
**Decision authority:** System Design Authority; institutional publication authority remains to be named  
**Related risks:** SDA-RISK-006, SDA-RISK-008, SDA-RISK-014

## Context

The platform can review field/citizen evidence, create canonical address records, generate proofs/certificates, prepare signage, and expose public/partner projections. Technical ability to perform these actions must not be confused with legal or institutional authority to publish an official national record.

The baseline already distinguishes `registry-ready` from publication and contains release feature flags. That distinction must become a durable authority boundary.

## Decision

`Registry-ready` means that a record has completed the defined internal validation required to be presented to the authorized publication process. It does not mean publicly released, legally effective, signage-authorized, or partner-distributable.

Official publication requires:

- a canonical record and immutable version;
- required validation and evidence quality;
- territorial and institutional scope checks;
- absence or explicit resolution of blocking duplicate, dispute, correction, hold, or geometry conditions;
- named approving authority with effective permission and scope;
- independent approval/dual control where policy requires;
- mandatory reason/decision metadata;
- release batch/manifest and public projection;
- immutable audit event, effective timestamp, and revocation/correction path.

A feature flag, administrator role, database state edit, generated certificate, or successful simulation is not publication authority.

## State separation

At minimum, implementation and documentation must preserve distinct semantics for:

- evidence submitted;
- under review;
- needs field verification or recapture;
- registry-ready;
- publication proposed/pending approval where implemented;
- published/effective;
- disputed or on hold;
- corrected/superseded;
- revoked/retired/rejected.

The public behavior of disputed, corrected, superseded, and revoked records must be defined explicitly rather than inferred.

## Output controls

- Public lookup, partner APIs, official certificates, publication packs, and physical signage consume only approved published projections.
- Registry-ready records may be visible only to authorized internal users and clearly labeled as not public/officially released.
- Simulation and training artefacts must be marked and technically prevented from being mistaken for official outputs.
- Publication rollback is modeled as revocation, correction, or supersession with history; published history is not silently deleted.

## Consequences

### Positive

- preserves lawful and institutional authority;
- prevents premature public or partner release;
- enables controlled pilot review without false official claims;
- creates traceable publication and correction history.

### Constraints

- the Programme Owner must identify publication authority and approval policy before publication readiness;
- UI, API, exports, certificates, signage, and partner integrations must honor the same state boundary;
- operators need clear held/pending queues and reasons;
- emergency correction/revocation needs a governed workflow.

## Follow-up

- NLI-WO-004 will formalize approval, evidence, retention, corrections, and publication governance.
- NLI-WO-003 will implement scoped publication permissions and segregation of duties.
- Until those work orders are accepted and authority is named, publication release remains locked.
