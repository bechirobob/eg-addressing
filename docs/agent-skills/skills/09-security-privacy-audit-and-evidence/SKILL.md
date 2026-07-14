# Skill 09 — Security, Privacy, Audit, and Evidence

## Use when

Use for sensitive data, identity, sessions, uploads, evidence objects, audit events, publication, exports, retention, legal hold, secrets, privileged actions, or external services.

## Objective

Identify trust and data risks before implementation, enforce least privilege and data minimization, and preserve attributable evidence without leaking or silently destroying sensitive information.

## Procedure

1. Identify assets, actors, trust boundaries, data classes, and approved purpose.
2. Classify every affected field/object as public, government-internal, restricted, highly restricted, or security-internal.
3. Identify collection, use, disclosure, export, retention, deletion, and recovery paths.
4. Threat-model affected flows:
   - broken authorization;
   - credential/session compromise;
   - injection and unsafe parsing;
   - upload/path/malware risk;
   - enumeration and bulk extraction;
   - tampering and audit concealment;
   - external-service privacy or availability;
   - backup and key compromise.
5. Apply least privilege, deny by default, scoped credentials, safe projections, validation, rate/resource controls, and secure failure.
6. For evidence objects define:
   - stable evidence ID;
   - object version/key;
   - hash, size, verified media type;
   - source/capture actor/time;
   - classification;
   - related case/record;
   - access/review history;
   - retention and legal hold;
   - replacement/supersession;
   - recovery verification.
7. Define audit events with subject/client, institution, permission/scope, action, target, result, reason, correlation ID, and safe change summary.
8. Exclude secrets, tokens, passwords, sensitive payloads, and unnecessary personal data from logs/evidence.
9. Add allow/deny, redaction, tamper/integrity, abuse, upload, export, retention, and recovery tests.
10. Record residual risk and correct decision owner.

## Required evidence

- Threat/abuse analysis
- Field/object classification inventory
- Authorization and sensitive-projection tests
- Audit-event schema/result
- Secret/dependency/security scan results
- Evidence hash/version/access tests
- Retention/hold/disposition implications
- Export manifest and access evidence where applicable
- Incident/containment/recovery notes

## Stop and escalate when

- Collection purpose or lawful/institutional authority is missing.
- A new sensitive field or public projection is proposed.
- Retention/deletion behavior is unclear.
- Evidence would be overwritten or deleted silently.
- A security exception or shared credential is required.
- Production data would enter a lower environment.

## Anti-patterns

- Public responses built by removing a few known fields from internal objects.
- Hashing raw data and discarding it while claiming no-loss preservation.
- Logging entire request/response bodies by default.
- Shared human accounts or machine use of human credentials.
- Storing retrievable session-token values.
- Audit events that say only “updated.”
- Evidence replacement without version history.
