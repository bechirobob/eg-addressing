# S24 — Publication, Corrections, Certificates, and Signage

## Invoke when

- changing registry-ready approval, publication requests, release batches, or public projections;
- adding corrections, disputes, revocation, certificates, QR verification, or signage exports;
- releasing data to citizens, agencies, postal, emergency, or other partners.

## Required inputs

- publication/correction ADRs and authority decisions;
- exact canonical record/version and alias model;
- evidence, geometry, hold, and audit rules;
- public/partner projection contracts;
- certificate/signage accessibility and artifact requirements.

## Procedure

1. Identify publication authority, submitting/reviewing roles, territorial scope, audience, purpose, and release environment.
2. Enforce prerequisites: exact record/version, approved geometry where required, completed evidence/validation, no unresolved duplicate/dispute/hold, eligible alias, independent approval, effective date, and reason.
3. Create an immutable release manifest with exact versions, aliases, payloads, classification/redaction, hashes, authority, audience, and generation time.
4. Tie release items to immutable versions/artifacts, not mutable current pointers.
5. Define draft, approval-requested, approved, published, suspended, withdrawn, superseded, and corrected behavior.
6. Generate public lookup, proof, certificate, QR, signage, export, and partner outputs from the same authorized release source.
7. Define correction/dispute intake, hold/public behavior, review, corrected version, replacement release, appeal, and historical verification.
8. Define suspension/revocation and downstream reconciliation.
9. Keep pilot/training outputs unmistakably non-official and technically locked.
10. Test self-approval denial, missing prerequisites, wrong version/alias, unresolved hold, duplicate release, partial failure, revocation, historical proof, QR/text verification, and corrected re-release.
11. Audit proposals, approvals, releases, generation, downloads, suspensions, withdrawals, corrections, and deliveries.

## Outputs

- publication authority and segregation matrix;
- prerequisite policy;
- immutable release/manifest contract;
- correction/dispute/hold state model;
- certificate/signage/QR artifacts;
- revocation/reconciliation and audit evidence.

## Stop or RFI conditions

Stop when:

- publication/effective-date authority is not named;
- exact version, alias, geometry, or projection is ambiguous;
- correction would overwrite published history;
- signage/certificate would use fixture, registry-ready, or unpublished data;
- public release contains restricted or unapproved precision.

## Evidence gate

Before review:

- exact version/alias/projection and dual-control tests pass;
- all missing-prerequisite and self-approval cases fail;
- release history, correction, revocation, and downstream reconciliation are reconstructable;
- documents are accessible, bilingual, print-stable, and text-verifiable;
- institutional conditions/RFIs are explicit.

## Anti-patterns

- Publishing by toggling one row status.
- Generating certificates from a mutable current record.
- Treating an admin role or feature flag as authority.
- Reusing old QR/proof after correction.
- Deleting withdrawn releases.
- Creating signage before official release.
