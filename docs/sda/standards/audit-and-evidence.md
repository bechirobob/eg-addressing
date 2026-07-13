# SDA Standard — Audit, Evidence, and Publication Records

**Version:** 0.1  
**Status:** Mandatory  
**Applies to:** audit events, field/citizen evidence, approvals, corrections, publication, exports, and evidentiary access

## 1. Purpose

The platform must make significant actions attributable, reviewable, and reconstructable. Audit logs are not general debug logs, and evidence objects are not ordinary attachments. Both require controlled semantics, integrity, access, retention, and recovery.

## 2. Audit-event model

Every material audit event MUST contain, as applicable:

- stable event ID;
- event type and schema version;
- occurred and recorded timestamps;
- actor subject or service identity;
- institution, effective role, permission, and territorial/data scope;
- action and result;
- target entity, record version, batch, or evidence ID;
- request/correlation and source channel;
- reason, approval, case, or work-order context where required;
- safe before/after summary or change set;
- environment and originating service.

Event types MUST use a controlled vocabulary. Free-form prose alone is insufficient for automated oversight.

## 3. Events requiring audit

At minimum, audit:

- authentication, MFA, recovery, session, and credential activity;
- role, permission, institution, scope, and user lifecycle changes;
- protected and sensitive data reads where policy requires;
- evidence upload, view, download, replacement, classification, hold, and deletion/retirement;
- field submission, review, recapture, duplicate, and verification decisions;
- canonical record creation, correction, supersession, dispute, and retirement;
- imports, validation overrides, commits, and reconciliation;
- exports, reports containing restricted data, and bulk retrieval;
- publication proposal, approval, release, revocation, and signage/certificate generation;
- configuration, migration, deployment, backup, restore, and break-glass activity;
- authorization denials and security-control events relevant to investigation.

## 4. Audit integrity

- Audit events MUST be append-only to ordinary application roles.
- Corrections to an audit record use a linked corrective event; existing evidence is not rewritten silently.
- Audit storage MUST have restricted administration, retention, backup, and integrity controls.
- High-value events SHOULD be forwarded to an independently controlled security/audit system.
- Database administrators MUST NOT be the only people capable of detecting or concealing privileged activity.
- Clock synchronization and correlation IDs are mandatory for reliable timelines.

## 5. Sensitive content and redaction

Audit records MUST NOT contain:

- passwords, tokens, secrets, private keys, recovery codes, or full authorization headers;
- unneeded full identity-document values;
- evidence object bytes;
- unnecessary personal contact details;
- unrestricted request/response payload dumps.

Sensitive audit fields may be restricted or pseudonymized, but the record must remain sufficiently attributable for authorized investigation.

## 6. Evidence record

Every evidence object MUST have a database metadata record containing at minimum:

- stable evidence ID;
- related case/submission/record and evidence type;
- object bucket/key and object version;
- SHA-256 or approved content hash;
- byte size and verified media type;
- source/capture method and capture time;
- uploader/collector/service identity and institution;
- territorial scope;
- classification;
- review status and reviewer;
- retention class, destruction eligibility, and legal-hold state;
- creation, access, replacement/supersession, and disposition events.

Object keys are operational internals and SHOULD NOT be exposed in normal API responses.

## 7. Evidence ingestion

Evidence ingestion MUST:

- enforce payload and per-case limits;
- verify content rather than trusting filename or declared media type;
- assign server-generated safe object names;
- calculate and persist a content hash;
- scan for malware in controlled environments;
- store objects in non-executable delivery context;
- reject prohibited or unsupported content safely;
- record failure without producing a misleading accepted case state;
- preserve the original object when transformations or previews are created.

## 8. Chain of custody

For evidence used in verification or an official decision, the system MUST reconstruct:

- who collected or submitted it;
- when and where it was captured where authorized;
- how it entered the platform;
- hash and object version at each material step;
- who accessed, reviewed, accepted, rejected, or superseded it;
- which decision or canonical record relied on it;
- whether it was placed on hold, exported, or disposed.

A replacement is a new evidence version linked to the prior item, not an invisible overwrite.

## 9. Access and disclosure

- Evidence access follows least privilege, purpose, institution, scope, and case state.
- Bulk evidence download is prohibited unless explicitly authorized by work order and policy.
- Sensitive evidence views/downloads MUST be audited.
- Temporary retrieval URLs MUST be short-lived, scope-limited, and non-transferable where possible.
- Public proof pages MUST use approved derived artefacts and public projections, not direct evidence-object access.

## 10. Retention, legal hold, and disposition

- Every audit/evidence class MUST map to an approved retention rule before national production.
- Legal or investigation hold overrides ordinary disposition.
- Disposition MUST be authorized, auditable, and verifiable across primary, replicated, and backup systems according to policy.
- “Delete” in a user interface MUST NOT imply immediate irreversible erasure when retention or official-history duties apply.
- Expired temporary exports and working artefacts SHOULD be removed automatically with evidence of disposition.

## 11. Approval and publication record

Official publication requires an immutable decision trail containing:

- proposed record/version or batch;
- validation and quality evidence;
- submitting actor and institution;
- independent reviewer(s) and authority scope;
- required reasons/conditions;
- decision timestamps and effective date;
- released public projection and schema/version;
- publication identifier, hash, or manifest;
- revocation/correction path;
- any signage/certificate/partner artefacts generated from the release.

`Registry-ready` means internally validated for the next authority step. It MUST NOT automatically trigger public publication, official certificates, signage fabrication, or partner release.

## 12. Corrections and disputes

- Correction requests retain original report, source, classification, and contact handling rules.
- Official records are corrected through version/supersession events, not silent mutation.
- A dispute state MUST preserve the currently effective public behavior explicitly; the system must not improvise whether the prior version remains visible.
- Rejection, resolution, and escalation require reason and authorized actor.
- Citizens and agencies receive only public-safe status information.

## 13. Exports as evidence-bearing actions

Each material export MUST record:

- requesting subject/client and institution;
- purpose and approval;
- query/selection criteria and data classification;
- schema and code-list versions;
- record count and generated time;
- file hash, size, storage reference, and expiry;
- download/access events;
- disposition where required.

The export manifest MUST allow later determination of what was released without retaining an ungoverned duplicate indefinitely.

## 14. Recovery and continuity

- Database and object-storage recovery MUST preserve evidence-to-metadata linkage and hashes.
- Restore drills MUST validate representative evidence objects, versions, permissions, and audit timelines, not only table row counts.
- Key recovery and access-control reconstruction are part of evidentiary recovery.
- Missing or mismatched objects MUST be detected and escalated.

## 15. Required evidence

Changes affecting audit, evidence, correction, export, or publication MUST include:

- event/schema definitions;
- allow/deny access tests;
- integrity/hash and replacement/version tests;
- audit redaction tests;
- approval/segregation-of-duty tests;
- retention/hold/disposition implications;
- object-storage failure and recovery tests;
- public-projection tests;
- representative timeline or manifest evidence;
- residual legal/institutional RFIs.
