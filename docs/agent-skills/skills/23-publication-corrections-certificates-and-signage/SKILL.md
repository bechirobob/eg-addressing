# Skill 23 — Publication, Corrections, Certificates, and Signage

## Use when

Use for registry-ready approval, publication requests, release batches, public lookup projections, correction/dispute resolution, revocation, certificates, QR verification, signage exports, or partner/public release.

## Objective

Ensure that only the exact authorized record version and projection is published, that public artifacts remain verifiable and revocable, and that corrections preserve history rather than rewriting it.

## Protected rule

```text
registry-ready ≠ approved for publication ≠ published/effective
```

Technical capability, feature flags, admin roles, generated documents, or simulated releases do not grant institutional authority.

## Procedure

1. Identify publication authority, submitting/reviewing roles, territorial scope, audience, purpose, and release environment.
2. Define prerequisites:
   - exact canonical record/version;
   - approved geometry/version where required;
   - completed validation/evidence;
   - no unresolved duplicate/dispute/hold;
   - public-code/alias eligibility;
   - independent approval/dual control;
   - effective date and reason.
3. Create an immutable release manifest containing exact versions, aliases, projection payloads, classification/redaction, hashes, generation time, authority, and audience.
4. Keep release items tied to immutable record versions and artifact versions—not mutable record pointers.
5. Define draft, approval-requested, approved, published, suspended, withdrawn, superseded, and corrected behavior.
6. Define public lookup/proof, certificate, QR, signage, export, and partner projection from the same authorized release source.
7. Define correction/dispute workflow:
   - intake and classification;
   - hold/public behavior;
   - evidence and review;
   - corrected version/supersession;
   - appeal/escalation;
   - replacement release;
   - prior release history.
8. Define revocation/suspension response and downstream partner/signage reconciliation.
9. Prevent training/staging/pilot artifacts from resembling official production outputs without unmistakable marking and technical locks.
10. Test self-approval denial, missing prerequisites, wrong version, unresolved hold, stale alias, duplicate release, partial failure, revocation, historical verification, QR/text verification, and re-publication after correction.
11. Audit every proposal, approval, release, download, generation, suspension, withdrawal, correction, and partner delivery.
12. Provide accessible, bilingual, print-stable documents and text alternatives for QR codes.

## Required evidence

- Authority and segregation matrix
- Publication prerequisite policy
- Immutable release/manifest schema
- Exact version/alias/projection tests
- Correction/dispute/hold timeline
- Revocation and historical verification tests
- Certificate/signage/QR accessibility and print evidence
- Partner/public reconciliation result
- Audit events and release hashes
- Institutional RFIs/conditions

## Stop and escalate when

- Publication authority or effective-date authority is not named.
- A record version, alias, geometry, or public projection is ambiguous.
- A correction would silently replace published history.
- Signage/certificate generation would occur from registry-ready or fixture data.
- A public release contains restricted or unapproved precision.

## Anti-patterns

- Publishing by toggling a row status without a manifest.
- Generating certificates from the current mutable record.
- Treating an admin role as publication authority.
- Reusing an old QR/proof after correction or revocation.
- Deleting withdrawn releases.
- Creating signage before official release.
- Calling a simulated publication pack official.
